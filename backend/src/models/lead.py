"""Lead model for tracking potential buyers."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class InterestLevel(enum.Enum):
    """Interest level of the lead."""
    hot = "hot"
    warm = "warm"
    cold = "cold"
    tire_kicker = "tire_kicker"
    unknown = "unknown"


class LeadStatus(enum.Enum):
    """Status of the lead in the sales process."""
    new = "new"
    in_progress = "in_progress"
    waiting_on_buyer = "waiting_on_buyer"
    waiting_on_me = "waiting_on_me"
    agreed = "agreed"
    snoozed = "snoozed"
    dead = "dead"


class TransactionType(enum.Enum):
    """Type of transaction."""
    shipped = "shipped"
    local = "local"


class PaymentMethod(enum.Enum):
    """Payment methods accepted."""
    paypal_gs = "paypal_gs"
    paypal_ff = "paypal_ff"
    venmo = "venmo"
    zelle = "zelle"
    cash = "cash"
    crypto = "crypto"
    other = "other"


class Lead(Base):
    """Represents a potential buyer's interest."""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Contact Info
    username = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # reddit, offerup, etc.
    contact_method = Column(String(50))  # dm, email, phone
    contact_info = Column(String(255))  # Actual email/phone

    # Interest Assessment
    interest_level = Column(Enum(InterestLevel), default=InterestLevel.unknown)
    is_bundle_inquiry = Column(Boolean, default=False)
    source_listing_url = Column(String(500))  # Which listing they came from

    # Status
    status = Column(Enum(LeadStatus), default=LeadStatus.new, index=True)

    # Offer tracking
    offered_price = Column(String(50))  # What they offered (can be text like "asking" or "$150")

    # Agreement Details (Phase 5)
    transaction_type = Column(Enum(TransactionType))
    agreed_price = Column(Numeric(10, 2))
    payment_method = Column(Enum(PaymentMethod))
    agreed_at = Column(DateTime)
    agreement_details = Column(JSON)  # Invoice/meetup details

    # Snooze
    snooze_reason = Column(String(255))
    snooze_until = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact_at = Column(DateTime)

    # Notes
    notes = Column(Text)

    # Relationships
    items = relationship("Item", secondary="lead_items", back_populates="leads")
    messages = relationship("LeadMessage", back_populates="lead", cascade="all, delete-orphan")
    sale = relationship("Sale", back_populates="lead", uselist=False)

    def __repr__(self):
        return f"<Lead {self.username} on {self.platform} ({self.status.value if self.status else 'no status'})>"

    @property
    def has_unreviewed_messages(self):
        """Check if lead has messages needing review."""
        from .lead_message import ReviewStatus
        return any(m.review_status == ReviewStatus.needs_review for m in self.messages)

    @property
    def message_count(self):
        """Get total message count."""
        return len(self.messages) if self.messages else 0
