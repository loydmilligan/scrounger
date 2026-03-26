from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import Item
from ..schemas import ItemCreate, ItemUpdate, ItemResponse, ItemList

router = APIRouter()


@router.get("", response_model=ItemList)
def list_items(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "updated_at",
    sort_dir: str = "desc",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Item)

    if status:
        query = query.filter(Item.status == status)
    if platform:
        query = query.filter(Item.platforms.contains([platform]))
    if search:
        query = query.filter(
            (Item.name.ilike(f"%{search}%")) |
            (Item.description.ilike(f"%{search}%"))
        )

    # Sort
    sort_column = getattr(Item, sort_by, Item.updated_at)
    if sort_dir == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    # Add computed fields
    result_items = []
    for item in items:
        item_dict = {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "category": item.category,
            "condition": item.condition,
            "asking_price": item.asking_price,
            "min_price": item.min_price,
            "cost_basis": item.cost_basis,
            "status": item.status,
            "platforms": item.platforms or [],
            "images": item.images or [],
            "notes": item.notes,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "listed_at": item.listed_at,
            "sold_at": item.sold_at,
            "lead_count": len(item.leads) if item.leads else 0,
            "has_sale": item.sale is not None
        }
        result_items.append(ItemResponse(**item_dict))

    return ItemList(items=result_items, total=total)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        category=item.category,
        condition=item.condition,
        asking_price=item.asking_price,
        min_price=item.min_price,
        cost_basis=item.cost_basis,
        status=item.status,
        platforms=item.platforms or [],
        images=item.images or [],
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at,
        listed_at=item.listed_at,
        sold_at=item.sold_at,
        lead_count=len(item.leads) if item.leads else 0,
        has_sale=item.sale is not None
    )


@router.post("", response_model=ItemResponse)
def create_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    item = Item(**item_data.model_dump())
    if item.status == "listed" and not item.listed_at:
        item.listed_at = datetime.utcnow()
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        category=item.category,
        condition=item.condition,
        asking_price=item.asking_price,
        min_price=item.min_price,
        cost_basis=item.cost_basis,
        status=item.status,
        platforms=item.platforms or [],
        images=item.images or [],
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at,
        listed_at=item.listed_at,
        sold_at=item.sold_at,
        lead_count=0,
        has_sale=False
    )


@router.patch("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_data: ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_data.model_dump(exclude_unset=True)

    # Auto-set listed_at when status changes to listed
    if update_data.get("status") == "listed" and item.status != "listed":
        update_data["listed_at"] = datetime.utcnow()

    # Auto-set sold_at when status changes to sold
    if update_data.get("status") == "sold" and item.status != "sold":
        update_data["sold_at"] = datetime.utcnow()

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        category=item.category,
        condition=item.condition,
        asking_price=item.asking_price,
        min_price=item.min_price,
        cost_basis=item.cost_basis,
        status=item.status,
        platforms=item.platforms or [],
        images=item.images or [],
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at,
        listed_at=item.listed_at,
        sold_at=item.sold_at,
        lead_count=len(item.leads) if item.leads else 0,
        has_sale=item.sale is not None
    )


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}
