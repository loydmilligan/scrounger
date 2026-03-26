# Models package - exports all models for easy importing

# Core models
from .item import Item, ItemStatus, ItemCondition, AcquisitionCondition
from .lead import Lead, InterestLevel, LeadStatus, TransactionType, PaymentMethod
from .sale import Sale, SaleStatus, CompletionType, FeedbackType, ShippingCarrier, sale_items

# Organization models
from .category import Category
from .tag import Tag, item_tags
from .value_factor import ValueFactor, item_value_factors

# Image models
from .item_image import ItemImage, ImageType

# Message models
from .lead_message import LeadMessage, MessageAttachment, MessageDirection, ReviewStatus, AttachmentPurpose

# Marketplace models
from .marketplace import Marketplace, MarketplaceRule, MarketplaceAIPrompt, PlatformType, RuleType, PromptType

# Action system
from .action import Action, ActionType, ActionPriority, SourceType

# Dispute model
from .dispute import Dispute, DisputeType, DisputeStatus

# Settings/config
from .setting import UserSetting, AIModel

# Reddit integration
from .reddit_message import RedditMessage

# Junction tables
from .lead_item import lead_items

__all__ = [
    # Core models
    "Item", "ItemStatus", "ItemCondition", "AcquisitionCondition",
    "Lead", "InterestLevel", "LeadStatus", "TransactionType", "PaymentMethod",
    "Sale", "SaleStatus", "CompletionType", "FeedbackType", "ShippingCarrier", "sale_items",

    # Organization
    "Category",
    "Tag", "item_tags",
    "ValueFactor", "item_value_factors",

    # Images
    "ItemImage", "ImageType",

    # Messages
    "LeadMessage", "MessageAttachment", "MessageDirection", "ReviewStatus", "AttachmentPurpose",

    # Marketplace
    "Marketplace", "MarketplaceRule", "MarketplaceAIPrompt", "PlatformType", "RuleType", "PromptType",

    # Actions
    "Action", "ActionType", "ActionPriority", "SourceType",

    # Disputes
    "Dispute", "DisputeType", "DisputeStatus",

    # Settings
    "UserSetting", "AIModel",

    # Reddit
    "RedditMessage",

    # Junction tables
    "lead_items",
]
