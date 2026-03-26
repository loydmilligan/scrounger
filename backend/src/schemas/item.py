from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = "good"
    asking_price: Optional[float] = None
    min_price: Optional[float] = None
    cost_basis: Optional[float] = None
    status: Optional[str] = "draft"
    platforms: Optional[List[str]] = []
    images: Optional[List[str]] = []
    notes: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    asking_price: Optional[float] = None
    min_price: Optional[float] = None
    cost_basis: Optional[float] = None
    status: Optional[str] = None
    platforms: Optional[List[str]] = None
    images: Optional[List[str]] = None
    notes: Optional[str] = None
    listed_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    listed_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None
    lead_count: Optional[int] = 0
    has_sale: Optional[bool] = False

    class Config:
        from_attributes = True


class ItemList(BaseModel):
    items: List[ItemResponse]
    total: int
