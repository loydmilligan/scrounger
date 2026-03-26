"""Dispute model for issue resolution tracking."""

import enum
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class DisputeType(enum.Enum):
    """Types of disputes."""
    not_as_described = "not_as_described"
    damaged_in_shipping = "damaged_in_shipping"
    missing_items = "missing_items"
    not_received = "not_received"
    buyer_remorse = "buyer_remorse"
    negative_feedback = "negative_feedback"
    other = "other"


class DisputeStatus(enum.Enum):
    """Status of a dispute."""
    open = "open"
    waiting_buyer = "waiting_buyer"
    waiting_seller = "waiting_seller"
    resolved_positive = "resolved_positive"
    resolved_neutral = "resolved_neutral"
    resolved_negative = "resolved_negative"
    refunded = "refunded"


class Dispute(Base):
    """Issue resolution tracking."""
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)

    # Issue Details
    type = Column(Enum(DisputeType), nullable=False)
    status = Column(Enum(DisputeStatus), default=DisputeStatus.open, index=True)
    description = Column(Text, nullable=False)

    # Resolution
    resolution = Column(Text)
    refund_details = Column(JSON)  # Amount, method, etc.
    communications = Column(JSON)  # Message log

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relationships
    sale = relationship("Sale", back_populates="disputes")

    def __repr__(self):
        return f"<Dispute {self.type.value} ({self.status.value})>"

    @property
    def is_resolved(self):
        return self.resolved_at is not None

    @property
    def is_open(self):
        return self.status == DisputeStatus.open
