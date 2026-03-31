from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class ItemImageNested(BaseModel):
    """Nested image response for item listings."""
    id: int
    url: str
    image_type: str
    caption: Optional[str] = None
    sort_order: int = 0

    class Config:
        from_attributes = True


class TagNested(BaseModel):
    """Nested tag response for item listings."""
    id: int
    name: str
    color: Optional[str] = None

    class Config:
        from_attributes = True


class ValueFactorNested(BaseModel):
    """Nested value factor response for item listings."""
    id: int
    name: str
    multiplier: float

    class Config:
        from_attributes = True


class CategoryNested(BaseModel):
    """Nested category response for item listings."""
    id: int
    name: str
    display_name: Optional[str] = None

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    condition: Optional[str] = "good"

    # Acquisition
    cost_basis: Optional[float] = None
    location: Optional[str] = None
    acquisition_source: Optional[str] = None
    acquisition_condition: Optional[str] = None
    acquisition_date: Optional[date] = None

    # Pricing
    asking_price: Optional[float] = None
    min_price: Optional[float] = None
    platform_prices: Optional[Dict[str, float]] = None

    # Listing
    status: Optional[str] = "inventory"
    is_bundle: Optional[bool] = False
    bundle_item_ids: Optional[List[int]] = None
    draft_posts: Optional[Dict[str, str]] = None
    ready_checklist: Optional[Dict[str, bool]] = None
    active_listings: Optional[Dict[str, Any]] = None
    price_history: Optional[List[Dict[str, Any]]] = None

    # Stats
    total_views: Optional[int] = 0
    total_responses: Optional[int] = 0

    notes: Optional[str] = None


class ItemCreate(ItemBase):
    tag_ids: Optional[List[int]] = None
    value_factor_ids: Optional[List[int]] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    condition: Optional[str] = None

    # Acquisition
    cost_basis: Optional[float] = None
    location: Optional[str] = None
    acquisition_source: Optional[str] = None
    acquisition_condition: Optional[str] = None
    acquisition_date: Optional[date] = None

    # Pricing
    asking_price: Optional[float] = None
    min_price: Optional[float] = None
    platform_prices: Optional[Dict[str, float]] = None

    # Listing
    status: Optional[str] = None
    is_bundle: Optional[bool] = None
    bundle_item_ids: Optional[List[int]] = None
    draft_posts: Optional[Dict[str, str]] = None
    ready_checklist: Optional[Dict[str, bool]] = None
    active_listings: Optional[Dict[str, Any]] = None
    price_history: Optional[List[Dict[str, Any]]] = None

    # Stats
    total_views: Optional[int] = None
    total_responses: Optional[int] = None

    notes: Optional[str] = None
    listed_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None

    # Relationship updates
    tag_ids: Optional[List[int]] = None
    value_factor_ids: Optional[List[int]] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[CategoryNested] = None
    condition: Optional[str] = None

    # Acquisition
    cost_basis: Optional[float] = None
    location: Optional[str] = None
    acquisition_source: Optional[str] = None
    acquisition_condition: Optional[str] = None
    acquisition_date: Optional[date] = None

    # Pricing
    asking_price: Optional[float] = None
    min_price: Optional[float] = None
    platform_prices: Optional[Dict[str, float]] = None
    effective_price: Optional[float] = None

    # Listing
    status: Optional[str] = None
    is_bundle: Optional[bool] = False
    bundle_item_ids: Optional[List[int]] = None
    draft_posts: Optional[Dict[str, str]] = None
    ready_checklist: Optional[Dict[str, bool]] = None
    active_listings: Optional[Dict[str, Any]] = None
    price_history: Optional[List[Dict[str, Any]]] = None

    # Stats
    total_views: int = 0
    total_responses: int = 0

    notes: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    listed_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None

    # Relationships
    images: List[ItemImageNested] = []
    tags: List[TagNested] = []
    value_factors: List[ValueFactorNested] = []

    # Computed
    lead_count: int = 0
    sale_count: int = 0

    class Config:
        from_attributes = True


class ItemList(BaseModel):
    items: List[ItemResponse]
    total: int
