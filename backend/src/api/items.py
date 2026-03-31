from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import Item, ItemStatus, Tag, ValueFactor, Category
from ..schemas.item import (
    ItemCreate, ItemUpdate, ItemResponse, ItemList,
    ItemImageNested, TagNested, ValueFactorNested, CategoryNested
)

router = APIRouter()


def _item_to_response(item: Item) -> ItemResponse:
    """Convert Item model to response schema."""
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        category_id=item.category_id,
        category=CategoryNested(
            id=item.category.id,
            name=item.category.name,
            display_name=item.category.display_name
        ) if item.category else None,
        condition=item.condition.value if item.condition else None,
        cost_basis=float(item.cost_basis) if item.cost_basis else None,
        location=item.location,
        acquisition_source=item.acquisition_source,
        acquisition_condition=item.acquisition_condition.value if item.acquisition_condition else None,
        acquisition_date=item.acquisition_date,
        asking_price=float(item.asking_price) if item.asking_price else None,
        min_price=float(item.min_price) if item.min_price else None,
        platform_prices=item.platform_prices,
        effective_price=item.effective_price,
        status=item.status.value if item.status else None,
        is_bundle=item.is_bundle,
        bundle_item_ids=item.bundle_item_ids,
        draft_posts=item.draft_posts,
        ready_checklist=item.ready_checklist,
        active_listings=item.active_listings,
        price_history=item.price_history,
        total_views=item.total_views or 0,
        total_responses=item.total_responses or 0,
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at,
        listed_at=item.listed_at,
        sold_at=item.sold_at,
        images=[
            ItemImageNested(
                id=img.id,
                url=img.url,
                image_type=img.image_type.value if img.image_type else "physical",
                caption=img.caption,
                sort_order=img.sort_order
            ) for img in (item.images or [])
        ],
        tags=[
            TagNested(id=tag.id, name=tag.name, color=tag.color)
            for tag in (item.tags or [])
        ],
        value_factors=[
            ValueFactorNested(
                id=vf.id,
                name=vf.name,
                multiplier=float(vf.multiplier)
            ) for vf in (item.value_factors or [])
        ],
        lead_count=len(item.leads) if item.leads else 0,
        sale_count=len(item.sales) if item.sales else 0
    )


@router.get("", response_model=ItemList)
def list_items(
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    search: Optional[str] = None,
    location: Optional[str] = None,
    is_bundle: Optional[bool] = None,
    sort_by: str = "updated_at",
    sort_dir: str = "desc",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List items with various filters."""
    query = db.query(Item).options(
        joinedload(Item.category),
        joinedload(Item.images),
        joinedload(Item.tags),
        joinedload(Item.value_factors)
    )

    if status:
        try:
            status_enum = ItemStatus(status)
            query = query.filter(Item.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Allowed: {[s.value for s in ItemStatus]}"
            )

    if category_id:
        query = query.filter(Item.category_id == category_id)

    if tag_id:
        query = query.filter(Item.tags.any(Tag.id == tag_id))

    if location:
        query = query.filter(Item.location.ilike(f"%{location}%"))

    if is_bundle is not None:
        query = query.filter(Item.is_bundle == is_bundle)

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

    return ItemList(
        items=[_item_to_response(item) for item in items],
        total=total
    )


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID."""
    item = db.query(Item).options(
        joinedload(Item.category),
        joinedload(Item.images),
        joinedload(Item.tags),
        joinedload(Item.value_factors),
        joinedload(Item.leads),
        joinedload(Item.sales)
    ).filter(Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return _item_to_response(item)


@router.post("", response_model=ItemResponse)
def create_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item."""
    data = item_data.model_dump(exclude={"tag_ids", "value_factor_ids"})

    # Convert string enums to enum types
    if data.get("status"):
        try:
            data["status"] = ItemStatus(data["status"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Allowed: {[s.value for s in ItemStatus]}"
            )

    if data.get("condition"):
        from ..models import ItemCondition
        try:
            data["condition"] = ItemCondition(data["condition"])
        except ValueError:
            pass  # Allow null

    if data.get("acquisition_condition"):
        from ..models import AcquisitionCondition
        try:
            data["acquisition_condition"] = AcquisitionCondition(data["acquisition_condition"])
        except ValueError:
            pass

    # Validate category exists
    if data.get("category_id"):
        category = db.query(Category).filter(Category.id == data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

    item = Item(**data)

    # Handle status timestamps
    if item.status == ItemStatus.listed and not item.listed_at:
        item.listed_at = datetime.utcnow()

    # Add tags
    if item_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(item_data.tag_ids)).all()
        item.tags = tags

    # Add value factors
    if item_data.value_factor_ids:
        vfs = db.query(ValueFactor).filter(ValueFactor.id.in_(item_data.value_factor_ids)).all()
        item.value_factors = vfs

    db.add(item)
    db.commit()
    db.refresh(item)

    return _item_to_response(item)


@router.patch("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_data: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item."""
    item = db.query(Item).options(
        joinedload(Item.category),
        joinedload(Item.images),
        joinedload(Item.tags),
        joinedload(Item.value_factors)
    ).filter(Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_data.model_dump(exclude_unset=True, exclude={"tag_ids", "value_factor_ids"})

    # Handle status enum
    if "status" in update_data and update_data["status"]:
        try:
            new_status = ItemStatus(update_data["status"])
            # Auto-set timestamps on status change
            if new_status == ItemStatus.listed and item.status != ItemStatus.listed:
                update_data["listed_at"] = datetime.utcnow()
            if new_status == ItemStatus.sold and item.status != ItemStatus.sold:
                update_data["sold_at"] = datetime.utcnow()
            update_data["status"] = new_status
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Allowed: {[s.value for s in ItemStatus]}"
            )

    # Handle condition enum
    if "condition" in update_data and update_data["condition"]:
        from ..models import ItemCondition
        try:
            update_data["condition"] = ItemCondition(update_data["condition"])
        except ValueError:
            pass

    # Handle acquisition_condition enum
    if "acquisition_condition" in update_data and update_data["acquisition_condition"]:
        from ..models import AcquisitionCondition
        try:
            update_data["acquisition_condition"] = AcquisitionCondition(update_data["acquisition_condition"])
        except ValueError:
            pass

    # Validate category if being updated
    if "category_id" in update_data and update_data["category_id"]:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

    # Apply scalar updates
    for key, value in update_data.items():
        setattr(item, key, value)

    # Update tags if provided
    if item_data.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(item_data.tag_ids)).all()
        item.tags = tags

    # Update value factors if provided
    if item_data.value_factor_ids is not None:
        vfs = db.query(ValueFactor).filter(ValueFactor.id.in_(item_data.value_factor_ids)).all()
        item.value_factors = vfs

    db.commit()
    db.refresh(item)

    return _item_to_response(item)


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}


@router.post("/{item_id}/tags/{tag_id}")
def add_tag_to_item(item_id: int, tag_id: int, db: Session = Depends(get_db)):
    """Add a tag to an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag not in item.tags:
        item.tags.append(tag)
        db.commit()

    return {"message": "Tag added successfully"}


@router.delete("/{item_id}/tags/{tag_id}")
def remove_tag_from_item(item_id: int, tag_id: int, db: Session = Depends(get_db)):
    """Remove a tag from an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag in item.tags:
        item.tags.remove(tag)
        db.commit()

    return {"message": "Tag removed successfully"}


@router.post("/{item_id}/value-factors/{vf_id}")
def add_value_factor_to_item(item_id: int, vf_id: int, db: Session = Depends(get_db)):
    """Add a value factor to an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    vf = db.query(ValueFactor).filter(ValueFactor.id == vf_id).first()
    if not vf:
        raise HTTPException(status_code=404, detail="Value factor not found")

    if vf not in item.value_factors:
        item.value_factors.append(vf)
        db.commit()

    return {"message": "Value factor added successfully"}


@router.delete("/{item_id}/value-factors/{vf_id}")
def remove_value_factor_from_item(item_id: int, vf_id: int, db: Session = Depends(get_db)):
    """Remove a value factor from an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    vf = db.query(ValueFactor).filter(ValueFactor.id == vf_id).first()
    if not vf:
        raise HTTPException(status_code=404, detail="Value factor not found")

    if vf in item.value_factors:
        item.value_factors.remove(vf)
        db.commit()

    return {"message": "Value factor removed successfully"}


@router.get("/stats/by-status")
def get_items_by_status(db: Session = Depends(get_db)):
    """Get item counts grouped by status (for funnel view)."""
    from sqlalchemy import func

    results = db.query(
        Item.status,
        func.count(Item.id).label("count")
    ).group_by(Item.status).all()

    stats = {status.value: 0 for status in ItemStatus}
    for status, count in results:
        if status:
            stats[status.value] = count

    return stats


@router.get("/stats/by-category")
def get_items_by_category(db: Session = Depends(get_db)):
    """Get item counts grouped by category."""
    from sqlalchemy import func

    results = db.query(
        Category.name,
        func.count(Item.id).label("count")
    ).outerjoin(Item).group_by(Category.id, Category.name).all()

    return {name: count for name, count in results}
