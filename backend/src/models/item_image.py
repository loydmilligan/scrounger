"""Item Image model for photos and attachments."""

import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class ImageType(enum.Enum):
    """Types of item images."""
    physical = "physical"       # Photos of item
    specs = "specs"             # Specification screenshots
    performance = "performance" # Benchmark results
    receipt = "receipt"         # Purchase receipts
    other = "other"


class ItemImage(Base):
    """Images attached to items with type classification."""
    __tablename__ = "item_images"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)  # Path or URL
    image_type = Column(Enum(ImageType), default=ImageType.physical)
    caption = Column(String(255))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    item = relationship("Item", back_populates="images")

    def __repr__(self):
        return f"<ItemImage {self.image_type.value} for item {self.item_id}>"
