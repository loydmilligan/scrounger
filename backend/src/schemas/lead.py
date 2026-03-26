from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LeadBase(BaseModel):
    username: str
    platform: Optional[str] = "reddit"
    contact_method: Optional[str] = None
    contact_info: Optional[str] = None
    status: Optional[str] = "new"
    offered_price: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None


class LeadCreate(LeadBase):
    item_id: int  # Primary item
    item_ids: Optional[List[int]] = None  # Additional items (for multi-item leads)


class LeadUpdate(BaseModel):
    username: Optional[str] = None
    platform: Optional[str] = None
    contact_method: Optional[str] = None
    contact_info: Optional[str] = None
    status: Optional[str] = None
    offered_price: Optional[str] = None
    notes: Optional[str] = None
    last_contact_at: Optional[datetime] = None


class LeadResponse(LeadBase):
    id: int
    item_id: int
    created_at: datetime
    updated_at: datetime
    last_contact_at: Optional[datetime] = None
    item_name: Optional[str] = None

    class Config:
        from_attributes = True


class LeadList(BaseModel):
    leads: List[LeadResponse]
    total: int


class RedditImport(BaseModel):
    url: str
    item_id: int
