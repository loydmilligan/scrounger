from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SaleBase(BaseModel):
    sale_price: float
    platform: Optional[str] = None
    buyer_username: Optional[str] = None
    shipping_cost: Optional[float] = 0
    shipping_carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    platform_fees: Optional[float] = 0
    payment_fees: Optional[float] = 0
    notes: Optional[str] = None
    sale_date: Optional[datetime] = None


class SaleCreate(SaleBase):
    item_id: int
    lead_id: Optional[int] = None


class SaleUpdate(BaseModel):
    sale_price: Optional[float] = None
    platform: Optional[str] = None
    buyer_username: Optional[str] = None
    shipping_cost: Optional[float] = None
    shipping_carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    platform_fees: Optional[float] = None
    payment_fees: Optional[float] = None
    notes: Optional[str] = None
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None


class SaleResponse(SaleBase):
    id: int
    item_id: int
    lead_id: Optional[int] = None
    profit: Optional[float] = None
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    created_at: datetime
    item_name: Optional[str] = None

    class Config:
        from_attributes = True


class SaleList(BaseModel):
    sales: List[SaleResponse]
    total: int
    total_revenue: float
    total_profit: float
