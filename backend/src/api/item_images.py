import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path

from ..database import get_db
from ..models import Item, ItemImage, ImageType
from ..schemas import ItemImageCreate, ItemImageUpdate, ItemImageResponse, ItemImageList
from ..config import settings

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("data/item_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file: UploadFile):
    """Validate uploaded file type and size."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Allowed types: {ALLOWED_TYPES}"
        )
    
    # Check file size by reading content
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size / 1024 / 1024:.2f}MB). Max size: 10MB"
        )


@router.get("", response_model=ItemImageList)
def list_item_images(
    item_id: int,
    skip: int = 0,
    limit: int = 100,
    image_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all images for an item, optionally filtered by type."""
    # Verify item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    query = db.query(ItemImage).filter(ItemImage.item_id == item_id).order_by(ItemImage.sort_order, ItemImage.created_at)
    
    if image_type:
        try:
            image_type_enum = ImageType(image_type)
            query = query.filter(ItemImage.image_type == image_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed types: {[t.value for t in ImageType]}"
            )
    
    total = query.count()
    images = query.offset(skip).limit(limit).all()
    
    result_images = [
        ItemImageResponse(
            id=img.id,
            item_id=img.item_id,
            url=img.url,
            image_type=img.image_type.value,
            caption=img.caption,
            sort_order=img.sort_order,
            created_at=img.created_at
        )
        for img in images
    ]
    
    return ItemImageList(images=result_images, total=total)


@router.get("/{image_id}", response_model=ItemImageResponse)
def get_item_image(image_id: int, db: Session = Depends(get_db)):
    """Get a specific item image by ID."""
    img = db.query(ItemImage).filter(ItemImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return ItemImageResponse(
        id=img.id,
        item_id=img.item_id,
        url=img.url,
        image_type=img.image_type.value,
        caption=img.caption,
        sort_order=img.sort_order,
        created_at=img.created_at
    )


@router.post("", response_model=ItemImageResponse)
def create_item_image(
    item_id: int,
    image_type: str = Form("physical"),
    caption: Optional[str] = Form(None),
    sort_order: int = Form(0),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and create a new item image."""
    # Verify item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Validate file
    validate_file(file)
    
    # Validate image type
    try:
        image_type_enum = ImageType(image_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type. Allowed types: {[t.value for t in ImageType]}"
        )
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create database record
    # Use relative path from backend directory
    relative_url = f"data/item_images/{unique_filename}"
    
    img = ItemImage(
        item_id=item_id,
        url=relative_url,
        image_type=image_type_enum,
        caption=caption,
        sort_order=sort_order
    )
    
    db.add(img)
    db.commit()
    db.refresh(img)
    
    return ItemImageResponse(
        id=img.id,
        item_id=img.item_id,
        url=img.url,
        image_type=img.image_type.value,
        caption=img.caption,
        sort_order=img.sort_order,
        created_at=img.created_at
    )


@router.patch("/{image_id}", response_model=ItemImageResponse)
def update_item_image(
    image_id: int,
    image_data: ItemImageUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing item image metadata."""
    img = db.query(ItemImage).filter(ItemImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    
    update_data = image_data.model_dump(exclude_unset=True)
    
    # Validate image type if provided
    if "image_type" in update_data and update_data["image_type"]:
        try:
            update_data["image_type"] = ImageType(update_data["image_type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed types: {[t.value for t in ImageType]}"
            )
    
    for key, value in update_data.items():
        setattr(img, key, value)
    
    db.commit()
    db.refresh(img)
    
    return ItemImageResponse(
        id=img.id,
        item_id=img.item_id,
        url=img.url,
        image_type=img.image_type.value,
        caption=img.caption,
        sort_order=img.sort_order,
        created_at=img.created_at
    )


@router.delete("/{image_id}")
def delete_item_image(image_id: int, db: Session = Depends(get_db)):
    """Delete an item image and its file."""
    img = db.query(ItemImage).filter(ItemImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete file if it exists
    if img.url and not img.url.startswith("http"):
        file_path = Path(img.url)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Warning: Failed to delete file {img.url}: {e}")
    
    # Delete database record
    db.delete(img)
    db.commit()
    
    return {"message": "Image deleted successfully"}


@router.post("/reorder")
def reorder_images(
    item_id: int,
    image_ids: List[int],
    db: Session = Depends(get_db)
):
    """Reorder images for an item."""
    # Verify item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update sort order
    for index, image_id in enumerate(image_ids):
        img = db.query(ItemImage).filter(
            ItemImage.id == image_id,
            ItemImage.item_id == item_id
        ).first()
        if img:
            img.sort_order = index
    
    db.commit()
    
    return {"message": "Images reordered successfully"}
