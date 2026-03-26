"""Item model - the core inventory entity."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey, Enum, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base
from .tag import item_tags
from .value_factor import item_value_factors


class ItemStatus(enum.Enum):
    """Status of an item in the sales pipeline."""
    inventory = "inventory"
    draft = "draft"
    listed = "listed"
    sold = "sold"
    archived = "archived"


class ItemCondition(enum.Enum):
    """Current condition of the item."""
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"
    poor = "poor"


class AcquisitionCondition(enum.Enum):
    """Condition when item was acquired."""
    new = "new"
    used = "used"


class Item(Base):
    """Core inventory item - the heart of the system."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    condition = Column(Enum(ItemCondition))

    # Acquisition (Phase 1)
    cost_basis = Column(Numeric(10, 2))  # What we paid
    location = Column(String(255))  # Where stored
    acquisition_source = Column(String(255))  # Amazon, eBay, etc.
    acquisition_condition = Column(Enum(AcquisitionCondition))
    acquisition_date = Column(Date)

    # Pricing (Phase 2)
    asking_price = Column(Numeric(10, 2))  # Base asking price
    min_price = Column(Numeric(10, 2))  # Lowest acceptable
    platform_prices = Column(JSON)  # Per-platform pricing

    # Listing (Phase 3)
    status = Column(Enum(ItemStatus), default=ItemStatus.inventory, index=True)
    is_bundle = Column(Boolean, default=False)
    bundle_item_ids = Column(JSON)  # IDs if this is a bundle
    draft_posts = Column(JSON)  # Generated posts per platform
    ready_checklist = Column(JSON)  # Listing prep checklist
    active_listings = Column(JSON)  # URLs, expiry per platform
    price_history = Column(JSON)  # Price change log

    # Stats
    total_views = Column(Integer, default=0)
    total_responses = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    listed_at = Column(DateTime)
    sold_at = Column(DateTime)

    # Notes
    notes = Column(Text)

    # Relationships
    category = relationship("Category", back_populates="items")
    images = relationship("ItemImage", back_populates="item", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=item_tags, back_populates="items")
    value_factors = relationship("ValueFactor", secondary=item_value_factors, back_populates="items")
    leads = relationship("Lead", secondary="lead_items", back_populates="items")
    sales = relationship("Sale", secondary="sale_items", back_populates="items")

    def __repr__(self):
        return f"<Item {self.name} ({self.status.value if self.status else 'no status'})>"

    @property
    def effective_price(self):
        """Calculate price with value factors applied."""
        if not self.asking_price:
            return None
        price = float(self.asking_price)
        for vf in self.value_factors:
            if vf.active:
                price *= float(vf.multiplier)
        return round(price, 2)
