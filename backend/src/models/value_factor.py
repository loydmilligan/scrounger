"""Value Factor model for market condition multipliers."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


# Junction table for Item-ValueFactor many-to-many relationship
item_value_factors = Table(
    "item_value_factors",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
    Column("value_factor_id", Integer, ForeignKey("value_factors.id", ondelete="CASCADE"), primary_key=True),
    Column("applied_at", DateTime, default=datetime.utcnow),
)


class ValueFactor(Base):
    """Market condition multipliers applied to items."""
    __tablename__ = "value_factors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # "Tariff Premium"
    description = Column(Text)  # Why this factor exists
    multiplier = Column(Numeric(4, 2), default=1.0)  # 1.2 = 20% boost
    active = Column(Boolean, default=True)  # Currently applied?
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("Item", secondary=item_value_factors, back_populates="value_factors")

    def __repr__(self):
        return f"<ValueFactor {self.name} x{self.multiplier}>"
