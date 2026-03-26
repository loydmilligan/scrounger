"""Category model for organizing items."""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class Category(Base):
    """Categories for organizing inventory items."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # "homelab"
    display_name = Column(String(100))  # "Homelab"
    description = Column(Text)
    icon = Column(String(50))  # Lucide icon name
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("Item", back_populates="category")

    def __repr__(self):
        return f"<Category {self.display_name or self.name}>"
