"""Sale model for completed transactions."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey, Enum, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base
from .lead import TransactionType, PaymentMethod


class SaleStatus(enum.Enum):
    """Status of a sale."""
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    complete = "complete"


class CompletionType(enum.Enum):
    """How the sale was completed."""
    with_feedback = "with_feedback"
    no_feedback = "no_feedback"
    local_sale = "local_sale"


class FeedbackType(enum.Enum):
    """Type of feedback received."""
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class ShippingCarrier(enum.Enum):
    """Shipping carriers."""
    usps = "usps"
    ups = "ups"
    fedex = "fedex"
    other = "other"


# Junction table for Sale-Item many-to-many relationship
sale_items = Table(
    "sale_items",
    Base.metadata,
    Column("sale_id", Integer, ForeignKey("sales.id", ondelete="CASCADE"), primary_key=True),
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
)


class Sale(Base):
    """Completed transaction record."""
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))

    # Transaction
    transaction_type = Column(Enum(TransactionType), nullable=False)
    sale_price = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod))
    buyer_username = Column(String(255), nullable=False)
    buyer_address = Column(Text)
    platform = Column(String(50), nullable=False)

    # Fees & Profit
    platform_fees = Column(Numeric(10, 2), default=0)
    payment_fees = Column(Numeric(10, 2), default=0)
    shipping_cost = Column(Numeric(10, 2), default=0)
    cost_basis = Column(Numeric(10, 2), default=0)  # Sum of item costs
    profit = Column(Numeric(10, 2))  # Calculated

    # Shipping (Phase 6-7)
    shipping_carrier = Column(Enum(ShippingCarrier))
    shipping_service = Column(String(100))
    tracking_number = Column(String(100))
    tracking_url = Column(String(500))  # Auto-generated
    label_source = Column(String(50))  # pirate_ship, usps, etc.
    package_dimensions = Column(JSON)
    shipping_tasks = Column(JSON)  # Packing checklist

    # Status
    status = Column(Enum(SaleStatus), default=SaleStatus.paid, index=True)

    # Timestamps
    payment_date = Column(DateTime, default=datetime.utcnow)
    shipped_date = Column(DateTime)
    delivered_date = Column(DateTime)
    delivery_confirmed_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Feedback (Phase 8-9)
    feedback_timer_days = Column(Integer)  # Override default
    feedback_requested_at = Column(DateTime)
    completion_type = Column(Enum(CompletionType))
    feedback_received = Column(Boolean, default=False)
    feedback_type = Column(Enum(FeedbackType))
    feedback_text = Column(Text)
    feedback_link = Column(String(500))
    feedback_given = Column(Boolean, default=False)

    # Notes
    notes = Column(Text)

    # Relationships
    lead = relationship("Lead", back_populates="sale")
    items = relationship("Item", secondary=sale_items, back_populates="sales")
    disputes = relationship("Dispute", back_populates="sale", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sale ${self.sale_price} to {self.buyer_username} ({self.status.value if self.status else 'no status'})>"

    @property
    def has_open_disputes(self):
        """Check if sale has any open disputes."""
        from .dispute import DisputeStatus
        return any(d.status == DisputeStatus.open for d in self.disputes)

    def calculate_profit(self):
        """Calculate and set the profit for this sale."""
        if self.sale_price is None:
            self.profit = None
            return

        total = float(self.sale_price)
        total -= float(self.platform_fees or 0)
        total -= float(self.payment_fees or 0)
        total -= float(self.shipping_cost or 0)
        total -= float(self.cost_basis or 0)
        self.profit = round(total, 2)
        return self.profit

    def get_tracking_url(self):
        """Generate tracking URL based on carrier and tracking number."""
        if not self.tracking_number or not self.shipping_carrier:
            return None

        urls = {
            ShippingCarrier.usps: f"https://tools.usps.com/go/TrackConfirmAction?tLabels={self.tracking_number}",
            ShippingCarrier.ups: f"https://www.ups.com/track?tracknum={self.tracking_number}",
            ShippingCarrier.fedex: f"https://www.fedex.com/fedextrack/?trknbr={self.tracking_number}",
        }
        return urls.get(self.shipping_carrier)
