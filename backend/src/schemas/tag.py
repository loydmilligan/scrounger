from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#3B82F6"


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(TagBase):
    id: int
    created_at: datetime
    item_count: int = 0

    class Config:
        from_attributes = True


class TagList(BaseModel):
    tags: list[TagResponse]
    total: int
