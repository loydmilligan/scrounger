from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryList

router = APIRouter()


@router.get("", response_model=CategoryList)
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all categories, optionally filtered."""
    query = db.query(Category).order_by(Category.sort_order, Category.name)
    
    total = query.count()
    categories = query.offset(skip).limit(limit).all()
    
    # Add item count to each category
    result_categories = []
    for category in categories:
        cat_dict = {
            "id": category.id,
            "name": category.name,
            "display_name": category.display_name,
            "description": category.description,
            "icon": category.icon,
            "sort_order": category.sort_order,
            "created_at": category.created_at,
            "item_count": len(category.items) if category.items else 0
        }
        result_categories.append(CategoryResponse(**cat_dict))
    
    return CategoryList(categories=result_categories, total=total)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        display_name=category.display_name,
        description=category.description,
        icon=category.icon,
        sort_order=category.sort_order,
        created_at=category.created_at,
        item_count=len(category.items) if category.items else 0
    )


@router.post("", response_model=CategoryResponse)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    # Check if name already exists
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        display_name=category.display_name,
        description=category.description,
        icon=category.icon,
        sort_order=category.sort_order,
        created_at=category.created_at,
        item_count=0
    )


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    """Update an existing category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_data.model_dump(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] != category.name:
        existing = db.query(Category).filter(
            Category.name == update_data["name"],
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    for key, value in update_data.items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        display_name=category.display_name,
        description=category.description,
        icon=category.icon,
        sort_order=category.sort_order,
        created_at=category.created_at,
        item_count=len(category.items) if category.items else 0
    )


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has items
    if category.items and len(category.items) > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category with {len(category.items)} item(s). Please reassign or delete items first."
        )
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}
