from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ValueFactorBase(BaseModel):
    name: str
    description: Optional[str] = None
    multiplier: float = 1.0
    active: bool = True


class ValueFactorCreate(ValueFactorBase):
    pass


class ValueFactorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    multiplier: Optional[float] = None
    active: Optional[bool] = None


class ValueFactorResponse(ValueFactorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    item_count: int = 0

    class Config:
        from_attributes = True


class ValueFactorList(BaseModel):
    value_factors: list[ValueFactorResponse]
    total: int
