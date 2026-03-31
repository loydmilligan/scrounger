from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Tag
from ..schemas import TagCreate, TagUpdate, TagResponse, TagList

router = APIRouter()


@router.get("", response_model=TagList)
def list_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all tags, optionally filtered."""
    query = db.query(Tag).order_by(Tag.name)
    
    total = query.count()
    tags = query.offset(skip).limit(limit).all()
    
    # Add item count to each tag
    result_tags = []
    for tag in tags:
        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at,
            "item_count": len(tag.items) if tag.items else 0
        }
        result_tags.append(TagResponse(**tag_dict))
    
    return TagList(tags=result_tags, total=total)


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """Get a specific tag by ID."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        item_count=len(tag.items) if tag.items else 0
    )


@router.post("", response_model=TagResponse)
def create_tag(tag_data: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    # Check if name already exists
    existing = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    tag = Tag(**tag_data.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        item_count=0
    )


@router.patch("/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag_data: TagUpdate, db: Session = Depends(get_db)):
    """Update an existing tag."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    update_data = tag_data.model_dump(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] != tag.name:
        existing = db.query(Tag).filter(
            Tag.name == update_data["name"],
            Tag.id != tag_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    for key, value in update_data.items():
        setattr(tag, key, value)
    
    db.commit()
    db.refresh(tag)
    
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        item_count=len(tag.items) if tag.items else 0
    )


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted successfully"}
