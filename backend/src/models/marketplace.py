"""Marketplace models for platform configuration."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class PlatformType(enum.Enum):
    """Platform types for marketplaces."""
    reddit = "reddit"
    ebay = "ebay"
    offerup = "offerup"
    craigslist = "craigslist"
    swappa = "swappa"
    facebook = "facebook"
    other = "other"


class RuleType(enum.Enum):
    """Types of marketplace rules."""
    title = "title"
    body = "body"
    image = "image"
    general = "general"


class PromptType(enum.Enum):
    """Types of AI prompts for marketplaces."""
    title = "title"
    body = "body"
    price_research = "price_research"
    response = "response"


class Marketplace(Base):
    """Platform configuration for selling."""
    __tablename__ = "marketplaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # "reddit_hardwareswap"
    display_name = Column(String(100))  # "r/hardwareswap"
    platform_type = Column(Enum(PlatformType))
    active = Column(Boolean, default=True)

    # Fees
    fee_percentage = Column(Numeric(5, 2), default=0)  # e.g., 12.9
    fee_flat = Column(Numeric(10, 2), default=0)
    fee_notes = Column(Text)

    # Timers (default days)
    feedback_timer_days = Column(Integer, default=3)
    chaser_timer_days = Column(Integer, default=14)

    # Bump Rules
    bump_interval_hours = Column(Integer)  # e.g., 72 for Reddit
    can_auto_bump = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rules = relationship("MarketplaceRule", back_populates="marketplace", cascade="all, delete-orphan")
    ai_prompts = relationship("MarketplaceAIPrompt", back_populates="marketplace", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Marketplace {self.display_name or self.name}>"


class MarketplaceRule(Base):
    """Posting rules per marketplace."""
    __tablename__ = "marketplace_rules"

    id = Column(Integer, primary_key=True, index=True)
    marketplace_id = Column(Integer, ForeignKey("marketplaces.id", ondelete="CASCADE"), nullable=False)
    rule_type = Column(Enum(RuleType), nullable=False)
    rule_text = Column(Text, nullable=False)
    is_strict = Column(Boolean, default=False)  # Will they delist?
    example_good = Column(Text)
    example_bad = Column(Text)
    sort_order = Column(Integer, default=0)

    # Relationships
    marketplace = relationship("Marketplace", back_populates="rules")

    def __repr__(self):
        return f"<MarketplaceRule {self.rule_type.value} for {self.marketplace_id}>"


class MarketplaceAIPrompt(Base):
    """AI prompt templates per marketplace."""
    __tablename__ = "marketplace_ai_prompts"

    id = Column(Integer, primary_key=True, index=True)
    marketplace_id = Column(Integer, ForeignKey("marketplaces.id", ondelete="CASCADE"), nullable=False)
    prompt_type = Column(Enum(PromptType), nullable=False)
    prompt_template = Column(Text, nullable=False)  # With {placeholders}
    model_preference = Column(String(100))
    notes = Column(Text)

    # Relationships
    marketplace = relationship("Marketplace", back_populates="ai_prompts")

    def __repr__(self):
        return f"<MarketplaceAIPrompt {self.prompt_type.value} for {self.marketplace_id}>"
