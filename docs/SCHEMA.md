# Scrounger Database Schema

## Overview

This document defines the complete database schema for Scrounger, organized by domain.

**Database:** SQLite (development) / PostgreSQL (production)
**ORM:** SQLAlchemy

---

## Entity Relationship Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Category   │     │     Tag      │     │ ValueFactor  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ 1:many             │ many:many          │ many:many
       ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│                         Item                              │
│  (inventory, draft, listed, sold, archived)              │
└──────────────────────────┬───────────────────────────────┘
       │                   │                    │
       │ 1:many            │ many:many          │ 1:many
       ▼                   ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  ItemImage   │     │   LeadItem   │     │   Listing    │
└──────────────┘     └──────┬───────┘     └──────────────┘
                           │
                           │ many:1
                           ▼
                    ┌──────────────┐
                    │     Lead     │
                    │  (interest)  │
                    └──────┬───────┘
                           │
                           │ 1:many        1:1
                           ▼                │
                    ┌──────────────┐        │
                    │ LeadMessage  │        │
                    └──────────────┘        │
                                           ▼
                                    ┌──────────────┐
                                    │     Sale     │
                                    │ (paid→done)  │
                                    └──────┬───────┘
                                           │
                                           │ 1:many
                                           ▼
                                    ┌──────────────┐
                                    │   Dispute    │
                                    └──────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Marketplace  │────▶│MarketplaceRule│    │    Action    │
└──────────────┘     └──────────────┘     │ (task list)  │
       │                                   └──────────────┘
       │ 1:many
       ▼
┌──────────────┐
│MarketplaceAI │
│   Prompt     │
└──────────────┘
```

---

## Core Models

### Category

Categories for organizing items.

```python
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # "homelab"
    display_name = Column(String(100))                        # "Homelab"
    description = Column(Text)
    icon = Column(String(50))                                 # Lucide icon name
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("Item", back_populates="category")
```

**Seed Data:**
| name | display_name |
|------|--------------|
| electronics | Electronics |
| homelab | Homelab |
| gpu | Graphics Cards |
| cpu | Processors |
| ram | Memory |
| storage | Storage |
| 3d_printing | 3D Printing |
| beauty | Beauty |
| tools | Tools |
| other | Other |

---

### Tag

User-defined tags for linking/grouping items.

```python
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7))  # Hex color "#FF5733"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("Item", secondary="item_tags", back_populates="tags")
```

---

### ValueFactor

Market condition multipliers applied to items.

```python
class ValueFactor(Base):
    __tablename__ = "value_factors"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # "Tariff Premium"
    description = Column(Text)
    multiplier = Column(Numeric(4, 2), default=1.0)          # 1.2 = 20% boost
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("Item", secondary="item_value_factors", back_populates="value_factors")
```

---

### Item

Core inventory item - the heart of the system.

```python
class ItemStatus(enum.Enum):
    inventory = "inventory"
    draft = "draft"
    listed = "listed"
    sold = "sold"
    archived = "archived"

class ItemCondition(enum.Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"
    poor = "poor"

class AcquisitionCondition(enum.Enum):
    new = "new"
    used = "used"

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)

    # Basic Info
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    condition = Column(Enum(ItemCondition))

    # Acquisition (Phase 1)
    cost_basis = Column(Numeric(10, 2))                      # What we paid
    location = Column(String(255))                           # Where stored
    acquisition_source = Column(String(255))                 # Amazon, eBay, etc.
    acquisition_condition = Column(Enum(AcquisitionCondition))
    acquisition_date = Column(Date)

    # Pricing (Phase 2)
    asking_price = Column(Numeric(10, 2))                    # Base asking price
    min_price = Column(Numeric(10, 2))                       # Lowest acceptable
    platform_prices = Column(JSON)                           # Per-platform pricing

    # Listing (Phase 3)
    status = Column(Enum(ItemStatus), default=ItemStatus.inventory, index=True)
    is_bundle = Column(Boolean, default=False)
    bundle_item_ids = Column(JSON)                           # IDs if this is a bundle
    draft_posts = Column(JSON)                               # Generated posts per platform
    ready_checklist = Column(JSON)                           # Listing prep checklist
    active_listings = Column(JSON)                           # URLs, expiry per platform
    price_history = Column(JSON)                             # Price change log

    # Stats
    total_views = Column(Integer, default=0)
    total_responses = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    listed_at = Column(DateTime)
    sold_at = Column(DateTime)

    # Notes
    notes = Column(Text)

    # Relationships
    category = relationship("Category", back_populates="items")
    images = relationship("ItemImage", back_populates="item", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="item_tags", back_populates="items")
    value_factors = relationship("ValueFactor", secondary="item_value_factors", back_populates="items")
    leads = relationship("Lead", secondary="lead_items", back_populates="items")
    sales = relationship("Sale", secondary="sale_items", back_populates="items")
```

---

### ItemImage

Images attached to items with type classification.

```python
class ImageType(enum.Enum):
    physical = "physical"       # Photos of item
    specs = "specs"             # Specification screenshots
    performance = "performance" # Benchmark results
    receipt = "receipt"         # Purchase receipts
    other = "other"

class ItemImage(Base):
    __tablename__ = "item_images"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    url = Column(String(500), nullable=False)    # Path or URL
    image_type = Column(Enum(ImageType), default=ImageType.physical)
    caption = Column(String(255))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    item = relationship("Item", back_populates="images")
```

---

### Junction Tables (Items)

```python
# Item ↔ Tag
item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

# Item ↔ ValueFactor
item_value_factors = Table(
    "item_value_factors",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    Column("value_factor_id", Integer, ForeignKey("value_factors.id"), primary_key=True),
    Column("applied_at", DateTime, default=datetime.utcnow),
)
```

---

## Lead Models

### Lead

Represents a potential buyer's interest.

```python
class InterestLevel(enum.Enum):
    hot = "hot"
    warm = "warm"
    cold = "cold"
    tire_kicker = "tire_kicker"
    unknown = "unknown"

class LeadStatus(enum.Enum):
    new = "new"
    in_progress = "in_progress"
    waiting_on_buyer = "waiting_on_buyer"
    waiting_on_me = "waiting_on_me"
    agreed = "agreed"
    snoozed = "snoozed"
    dead = "dead"

class TransactionType(enum.Enum):
    shipped = "shipped"
    local = "local"

class PaymentMethod(enum.Enum):
    paypal_gs = "paypal_gs"
    paypal_ff = "paypal_ff"
    venmo = "venmo"
    zelle = "zelle"
    cash = "cash"
    crypto = "crypto"
    other = "other"

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)

    # Contact Info
    username = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)            # reddit, offerup, etc.
    contact_method = Column(String(50))                      # dm, email, phone
    contact_info = Column(String(255))                       # Actual email/phone

    # Interest Assessment
    interest_level = Column(Enum(InterestLevel), default=InterestLevel.unknown)
    is_bundle_inquiry = Column(Boolean, default=False)
    source_listing_url = Column(String(500))                 # Which listing they came from

    # Status
    status = Column(Enum(LeadStatus), default=LeadStatus.new, index=True)

    # Agreement Details (Phase 5)
    transaction_type = Column(Enum(TransactionType))
    agreed_price = Column(Numeric(10, 2))
    payment_method = Column(Enum(PaymentMethod))
    agreed_at = Column(DateTime)
    agreement_details = Column(JSON)                         # Invoice/meetup details

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
```

---

### LeadMessage

Individual messages in a lead conversation.

```python
class MessageDirection(enum.Enum):
    incoming = "incoming"
    outgoing = "outgoing"

class ReviewStatus(enum.Enum):
    needs_review = "needs_review"
    responded = "responded"
    ignored = "ignored"
    snoozed = "snoozed"

class LeadMessage(Base):
    __tablename__ = "lead_messages"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    # Message Content
    direction = Column(Enum(MessageDirection), nullable=False)
    message_text = Column(Text, nullable=False)
    platform = Column(String(50))

    # Review Status
    review_status = Column(Enum(ReviewStatus), default=ReviewStatus.needs_review)
    reviewed_at = Column(DateTime)

    # Response Details (if responded)
    response_details = Column(JSON)                          # See Phase 4 spec

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
```

---

### MessageAttachment

Attachments sent with responses.

```python
class AttachmentPurpose(enum.Enum):
    additional_photos = "additional_photos"
    performance_screenshot = "performance_screenshot"
    timestamp_photo = "timestamp_photo"
    shipping_estimate = "shipping_estimate"
    other = "other"

class MessageAttachment(Base):
    __tablename__ = "message_attachments"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("lead_messages.id"), nullable=False)
    url = Column(String(500), nullable=False)
    purpose = Column(Enum(AttachmentPurpose))
    caption = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    message = relationship("LeadMessage", back_populates="attachments")
```

---

### Lead-Item Junction

```python
lead_items = Table(
    "lead_items",
    Base.metadata,
    Column("lead_id", Integer, ForeignKey("leads.id"), primary_key=True),
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)
```

---

## Sale Models

### Sale

Completed transaction record.

```python
class SaleStatus(enum.Enum):
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    complete = "complete"

class CompletionType(enum.Enum):
    with_feedback = "with_feedback"
    no_feedback = "no_feedback"
    local_sale = "local_sale"

class FeedbackType(enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class ShippingCarrier(enum.Enum):
    usps = "usps"
    ups = "ups"
    fedex = "fedex"
    other = "other"

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
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
    cost_basis = Column(Numeric(10, 2), default=0)           # Sum of item costs
    profit = Column(Numeric(10, 2))                          # Calculated

    # Shipping (Phase 6-7)
    shipping_carrier = Column(Enum(ShippingCarrier))
    shipping_service = Column(String(100))
    tracking_number = Column(String(100))
    tracking_url = Column(String(500))                       # Auto-generated
    label_source = Column(String(50))                        # pirate_ship, usps, etc.
    package_dimensions = Column(JSON)
    shipping_tasks = Column(JSON)                            # Packing checklist

    # Status
    status = Column(Enum(SaleStatus), default=SaleStatus.paid, index=True)

    # Timestamps
    payment_date = Column(DateTime, default=datetime.utcnow)
    shipped_date = Column(DateTime)
    delivered_date = Column(DateTime)
    delivery_confirmed_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Feedback (Phase 8-9)
    feedback_timer_days = Column(Integer)                    # Override default
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
    items = relationship("Item", secondary="sale_items", back_populates="sales")
    disputes = relationship("Dispute", back_populates="sale", cascade="all, delete-orphan")
```

---

### Sale-Item Junction

```python
sale_items = Table(
    "sale_items",
    Base.metadata,
    Column("sale_id", Integer, ForeignKey("sales.id"), primary_key=True),
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
)
```

---

### Dispute

Issue resolution tracking.

```python
class DisputeType(enum.Enum):
    not_as_described = "not_as_described"
    damaged_in_shipping = "damaged_in_shipping"
    missing_items = "missing_items"
    not_received = "not_received"
    buyer_remorse = "buyer_remorse"
    negative_feedback = "negative_feedback"
    other = "other"

class DisputeStatus(enum.Enum):
    open = "open"
    waiting_buyer = "waiting_buyer"
    waiting_seller = "waiting_seller"
    resolved_positive = "resolved_positive"
    resolved_neutral = "resolved_neutral"
    resolved_negative = "resolved_negative"
    refunded = "refunded"

class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)

    # Issue Details
    type = Column(Enum(DisputeType), nullable=False)
    status = Column(Enum(DisputeStatus), default=DisputeStatus.open)
    description = Column(Text, nullable=False)

    # Resolution
    resolution = Column(Text)
    refund_details = Column(JSON)                            # Amount, method, etc.
    communications = Column(JSON)                            # Message log

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relationships
    sale = relationship("Sale", back_populates="disputes")
```

---

## Marketplace Models

### Marketplace

Platform configuration.

```python
class PlatformType(enum.Enum):
    reddit = "reddit"
    ebay = "ebay"
    offerup = "offerup"
    craigslist = "craigslist"
    swappa = "swappa"
    facebook = "facebook"
    other = "other"

class Marketplace(Base):
    __tablename__ = "marketplaces"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # "reddit_hardwareswap"
    display_name = Column(String(100))                       # "r/hardwareswap"
    platform_type = Column(Enum(PlatformType))
    active = Column(Boolean, default=True)

    # Fees
    fee_percentage = Column(Numeric(5, 2), default=0)        # e.g., 12.9
    fee_flat = Column(Numeric(10, 2), default=0)
    fee_notes = Column(Text)

    # Timers (default days)
    feedback_timer_days = Column(Integer, default=3)
    chaser_timer_days = Column(Integer, default=14)

    # Bump Rules
    bump_interval_hours = Column(Integer)                    # e.g., 72 for Reddit
    can_auto_bump = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rules = relationship("MarketplaceRule", back_populates="marketplace", cascade="all, delete-orphan")
    ai_prompts = relationship("MarketplaceAIPrompt", back_populates="marketplace", cascade="all, delete-orphan")
```

---

### MarketplaceRule

Posting rules per marketplace.

```python
class RuleType(enum.Enum):
    title = "title"
    body = "body"
    image = "image"
    general = "general"

class MarketplaceRule(Base):
    __tablename__ = "marketplace_rules"

    id = Column(Integer, primary_key=True)
    marketplace_id = Column(Integer, ForeignKey("marketplaces.id"), nullable=False)
    rule_type = Column(Enum(RuleType), nullable=False)
    rule_text = Column(Text, nullable=False)
    is_strict = Column(Boolean, default=False)               # Will they delist?
    example_good = Column(Text)
    example_bad = Column(Text)
    sort_order = Column(Integer, default=0)

    # Relationships
    marketplace = relationship("Marketplace", back_populates="rules")
```

---

### MarketplaceAIPrompt

AI prompt templates per marketplace.

```python
class PromptType(enum.Enum):
    title = "title"
    body = "body"
    price_research = "price_research"
    response = "response"

class MarketplaceAIPrompt(Base):
    __tablename__ = "marketplace_ai_prompts"

    id = Column(Integer, primary_key=True)
    marketplace_id = Column(Integer, ForeignKey("marketplaces.id"), nullable=False)
    prompt_type = Column(Enum(PromptType), nullable=False)
    prompt_template = Column(Text, nullable=False)           # With {placeholders}
    model_preference = Column(String(100))
    notes = Column(Text)

    # Relationships
    marketplace = relationship("Marketplace", back_populates="ai_prompts")
```

---

## Action System

### Action

Global task/action list.

```python
class ActionType(enum.Enum):
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
    urgent = "urgent"
    high = "high"
    normal = "normal"
    low = "low"

class SourceType(enum.Enum):
    item = "item"
    lead = "lead"
    sale = "sale"
    listing = "listing"
    dispute = "dispute"

class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True)

    # Action Info
    action_type = Column(Enum(ActionType), nullable=False)
    priority = Column(Enum(ActionPriority), default=ActionPriority.normal)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Source Reference
    source_type = Column(Enum(SourceType))
    source_id = Column(Integer)                              # FK to source table

    # Timing
    due_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    dismissed_at = Column(DateTime)

    # Metadata
    auto_generated = Column(Boolean, default=True)
    generated_message = Column(Text)                         # Pre-generated message
    generated_instructions = Column(Text)                    # How to complete
```

---

## Configuration

### Config

System configuration (timers, defaults, etc.)

```python
class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Default Config Keys:**
| Key | Default Value | Description |
|-----|---------------|-------------|
| `feedback_timer_days` | 3 | Days after delivery to request feedback |
| `chaser_timer_days` | 14 | Days after no-feedback close to send chaser |
| `user_state` | "TX" | User's state for listings |
| `user_zip` | "78701" | User's ZIP for shipping |
| `safe_meetup_locations` | [...] | List of safe meetup spots |
| `default_payment_methods` | ["paypal_gs", "cash"] | Default payment options |

---

## Migration from Current Schema

### Existing Tables to Modify

1. **items** - Add new fields, modify status enum
2. **leads** - Add new fields, modify status enum
3. **sales** - Add new fields, modify status enum

### New Tables to Create

1. categories
2. tags
3. item_tags
4. value_factors
5. item_value_factors
6. item_images
7. lead_items
8. lead_messages
9. message_attachments
10. sale_items
11. disputes
12. marketplaces
13. marketplace_rules
14. marketplace_ai_prompts
15. actions
16. config

---

## Indexes

```sql
-- Performance indexes
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_category ON items(category_id);
CREATE INDEX idx_items_name ON items(name);

CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_username ON leads(username);
CREATE INDEX idx_leads_created ON leads(created_at);

CREATE INDEX idx_sales_status ON sales(status);
CREATE INDEX idx_sales_platform ON sales(platform);
CREATE INDEX idx_sales_payment_date ON sales(payment_date);

CREATE INDEX idx_actions_priority ON actions(priority);
CREATE INDEX idx_actions_due ON actions(due_at);
CREATE INDEX idx_actions_completed ON actions(completed_at);

CREATE INDEX idx_lead_messages_lead ON lead_messages(lead_id);
CREATE INDEX idx_lead_messages_status ON lead_messages(review_status);
```

---

*Schema Version: 1.0*
*Created: 2026-03-26*
