"""Lead Message models for conversation tracking."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class MessageDirection(enum.Enum):
    """Direction of the message."""
    incoming = "incoming"
    outgoing = "outgoing"


class ReviewStatus(enum.Enum):
    """Review status for incoming messages."""
    needs_review = "needs_review"
    responded = "responded"
    ignored = "ignored"
    snoozed = "snoozed"


class AttachmentPurpose(enum.Enum):
    """Purpose of message attachments."""
    additional_photos = "additional_photos"
    performance_screenshot = "performance_screenshot"
    timestamp_photo = "timestamp_photo"
    shipping_estimate = "shipping_estimate"
    other = "other"


class LeadMessage(Base):
    """Individual messages in a lead conversation."""
    __tablename__ = "lead_messages"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)

    # Message Content
    direction = Column(Enum(MessageDirection), nullable=False)
    message_text = Column(Text, nullable=False)
    platform = Column(String(50))

    # Review Status
    review_status = Column(Enum(ReviewStatus), default=ReviewStatus.needs_review, index=True)
    reviewed_at = Column(DateTime)

    # Response Details (if responded)
    response_details = Column(JSON)  # Response metadata

    # Ignore/Snooze Details
    ignore_reason = Column(String(255))
    ignore_notes = Column(Text)
    snooze_reason = Column(String(255))
    snooze_until = Column(DateTime)

    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="messages")
    attachments = relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LeadMessage {self.direction.value} for lead {self.lead_id}>"


class MessageAttachment(Base):
    """Attachments sent with responses."""
    __tablename__ = "message_attachments"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("lead_messages.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    purpose = Column(Enum(AttachmentPurpose))
    caption = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    message = relationship("LeadMessage", back_populates="attachments")

    def __repr__(self):
        return f"<MessageAttachment {self.purpose.value if self.purpose else 'other'} for message {self.message_id}>"
