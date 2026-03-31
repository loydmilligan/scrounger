from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ItemImageBase(BaseModel):
    url: str
    image_type: str = "physical"
    caption: Optional[str] = None
    sort_order: int = 0


class ItemImageCreate(ItemImageBase):
    item_id: int


class ItemImageUpdate(BaseModel):
    url: Optional[str] = None
    image_type: Optional[str] = None
    caption: Optional[str] = None
    sort_order: Optional[int] = None


class ItemImageResponse(ItemImageBase):
    id: int
    item_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ItemImageList(BaseModel):
    images: list[ItemImageResponse]
    total: int
