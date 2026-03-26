"""Tag model for linking/grouping items."""

from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


# Junction table for Item-Tag many-to-many relationship
item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    """User-defined tags for linking/grouping items."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    color = Column(String(7))  # Hex color "#FF5733"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("Item", secondary=item_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"
