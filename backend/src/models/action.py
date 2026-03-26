"""Action model for global task/action list."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from datetime import datetime

from ..database import Base


class ActionType(enum.Enum):
    """Types of actions in the system."""
    respond_to_inquiry = "respond_to_inquiry"
    bump_listing = "bump_listing"
    update_listing = "update_listing"
    follow_up_lead = "follow_up_lead"
    ship_item = "ship_item"
    add_tracking = "add_tracking"
    confirm_delivery = "confirm_delivery"
    request_feedback = "request_feedback"
    review_price = "review_price"
    take_photos = "take_photos"
    complete_checklist = "complete_checklist"
    send_chaser = "send_chaser"
    resolve_dispute = "resolve_dispute"
    manual = "manual"


class ActionPriority(enum.Enum):
    """Priority levels for actions."""
    urgent = "urgent"
    high = "high"
    normal = "normal"
    low = "low"


class SourceType(enum.Enum):
    """Source types for actions."""
    item = "item"
    lead = "lead"
    sale = "sale"
    listing = "listing"
    dispute = "dispute"


class Action(Base):
    """Global task/action list entry."""
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)

    # Action Info
    action_type = Column(Enum(ActionType), nullable=False)
    priority = Column(Enum(ActionPriority), default=ActionPriority.normal, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Source Reference (polymorphic)
    source_type = Column(Enum(SourceType))
    source_id = Column(Integer)  # FK to source table (not enforced for flexibility)

    # Timing
    due_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, index=True)
    dismissed_at = Column(DateTime)

    # Metadata
    auto_generated = Column(Boolean, default=True)
    generated_message = Column(Text)  # Pre-generated message
    generated_instructions = Column(Text)  # How to complete

    def __repr__(self):
        status = "completed" if self.completed_at else "pending"
        return f"<Action {self.action_type.value} ({status})>"

    @property
    def is_completed(self):
        return self.completed_at is not None

    @property
    def is_dismissed(self):
        return self.dismissed_at is not None

    @property
    def is_open(self):
        return not self.is_completed and not self.is_dismissed

    @property
    def is_overdue(self):
        if self.due_at and self.is_open:
            return datetime.utcnow() > self.due_at
        return False
