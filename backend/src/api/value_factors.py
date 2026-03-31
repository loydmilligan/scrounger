from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import ValueFactor
from ..schemas import ValueFactorCreate, ValueFactorUpdate, ValueFactorResponse, ValueFactorList

router = APIRouter()


@router.get("", response_model=ValueFactorList)
def list_value_factors(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all value factors, optionally filtered."""
    query = db.query(ValueFactor).order_by(ValueFactor.name)
    
    if active_only:
        query = query.filter(ValueFactor.active == True)
    
    total = query.count()
    value_factors = query.offset(skip).limit(limit).all()
    
    # Add item count to each value factor
    result_factors = []
    for vf in value_factors:
        vf_dict = {
            "id": vf.id,
            "name": vf.name,
            "description": vf.description,
            "multiplier": float(vf.multiplier),
            "active": vf.active,
            "created_at": vf.created_at,
            "updated_at": vf.updated_at,
            "item_count": len(vf.items) if vf.items else 0
        }
        result_factors.append(ValueFactorResponse(**vf_dict))
    
    return ValueFactorList(value_factors=result_factors, total=total)


@router.get("/{value_factor_id}", response_model=ValueFactorResponse)
def get_value_factor(value_factor_id: int, db: Session = Depends(get_db)):
    """Get a specific value factor by ID."""
    vf = db.query(ValueFactor).filter(ValueFactor.id == value_factor_id).first()
    if not vf:
        raise HTTPException(status_code=404, detail="Value factor not found")
    
    return ValueFactorResponse(
        id=vf.id,
        name=vf.name,
        description=vf.description,
        multiplier=float(vf.multiplier),
        active=vf.active,
        created_at=vf.created_at,
        updated_at=vf.updated_at,
        item_count=len(vf.items) if vf.items else 0
    )


@router.post("", response_model=ValueFactorResponse)
def create_value_factor(value_factor_data: ValueFactorCreate, db: Session = Depends(get_db)):
    """Create a new value factor."""
    # Check if name already exists
    existing = db.query(ValueFactor).filter(ValueFactor.name == value_factor_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Value factor with this name already exists")
    
    vf = ValueFactor(**value_factor_data.model_dump())
    db.add(vf)
    db.commit()
    db.refresh(vf)
    
    return ValueFactorResponse(
        id=vf.id,
        name=vf.name,
        description=vf.description,
        multiplier=float(vf.multiplier),
        active=vf.active,
        created_at=vf.created_at,
        updated_at=vf.updated_at,
        item_count=0
    )


@router.patch("/{value_factor_id}", response_model=ValueFactorResponse)
def update_value_factor(
    value_factor_id: int, 
    value_factor_data: ValueFactorUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing value factor."""
    vf = db.query(ValueFactor).filter(ValueFactor.id == value_factor_id).first()
    if not vf:
        raise HTTPException(status_code=404, detail="Value factor not found")
    
    update_data = value_factor_data.model_dump(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] != vf.name:
        existing = db.query(ValueFactor).filter(
            ValueFactor.name == update_data["name"],
            ValueFactor.id != value_factor_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Value factor with this name already exists")
    
    for key, value in update_data.items():
        setattr(vf, key, value)
    
    db.commit()
    db.refresh(vf)
    
    return ValueFactorResponse(
        id=vf.id,
        name=vf.name,
        description=vf.description,
        multiplier=float(vf.multiplier),
        active=vf.active,
        created_at=vf.created_at,
        updated_at=vf.updated_at,
        item_count=len(vf.items) if vf.items else 0
    )


@router.delete("/{value_factor_id}")
def delete_value_factor(value_factor_id: int, db: Session = Depends(get_db)):
    """Delete a value factor."""
    vf = db.query(ValueFactor).filter(ValueFactor.id == value_factor_id).first()
    if not vf:
        raise HTTPException(status_code=404, detail="Value factor not found")
    
    db.delete(vf)
    db.commit()
    return {"message": "Value factor deleted successfully"}
