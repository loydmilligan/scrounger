# Scrounger Planning Document

## Project Overview

**Scrounger** is a personal sales management system for tracking items through the complete secondary market sales lifecycle - from acquisition through listing, negotiation, sale, shipping, delivery, and transaction completion.

**Target User:** Individual sellers managing inventory across multiple marketplaces (Reddit, OfferUp, eBay, Craigslist, Swappa, etc.)

**Core Value Proposition:** Single source of truth for all sales activity with AI assistance at every step.

---

## Project Phases

### Alpha Release (MVP)
The minimum viable product that provides core functionality for managing the sales funnel.

**Goal:** Usable system that tracks items through all phases with basic functionality at each step.

**Scope:**
- Complete sales funnel with all 9 phases
- Basic fields and transitions for each phase
- Funnel dashboard view
- Quick phase transitions
- Existing AI features (post generation, price check, shipping help)
- Reddit integration (existing)

### Beta Release (Full Featured)
Enhanced version with expanded platform support, automation, and advanced AI assistance.

**Goal:** Comprehensive system with deep marketplace integrations and intelligent automation.

**Scope:**
- Additional marketplace integrations (eBay, OfferUp, Swappa link parsing)
- Carrier API integration for auto-tracking
- AI response generation for leads
- Platform-specific post templates
- Advanced analytics and reporting
- Feedback loop automation
- [Additional features TBD]

---

## Sales Funnel Phases

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1.INVENTORY │───▶│  2. DRAFT   │───▶│  3. LISTED  │
│   (own it)  │    │ (preparing) │    │  (for sale) │
└─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│5. AGREEMENT │◀───│ 4. INTEREST │◀───│   (leads)   │
│   (deal)    │    │  (inquiry)  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │
       ├─── [LOCAL SALE] ──────────────────────┐
       ▼                                       │
┌─────────────┐    ┌─────────────┐    ┌────────▼────┐
│   6. PAID   │───▶│  7. SHIPPED │───▶│8. DELIVERED │
│  (payment)  │    │ (in transit)│    │  (arrived)  │
└─────────────┘    └─────────────┘    └─────────────┘
                                             │
                         ┌───────────────────┤
                         │                   │
                         ▼                   ▼
                  ┌─────────────┐     ┌─────────────┐
                  │ 10. DISPUTE │◀────│ 9. COMPLETE │
                  │  (resolve)  │────▶│  (done ✓)   │
                  └─────────────┘     └─────────────┘
```

**10 Phases Total:**
1. INVENTORY - Items we own
2. DRAFT - Preparing to list
3. LISTED - Active listings
4. INTEREST - Leads/inquiries
5. AGREEMENT - Deal made, awaiting payment
6. PAID - Payment received, need to ship
7. SHIPPED - In transit
8. DELIVERED - Arrived, awaiting feedback
9. COMPLETE - Done (success)
10. DISPUTE - Issue resolution (if needed)

---

## Phase Definitions

### Phase 1: INVENTORY ✅ REVIEWED

**Description:** Items we own that we may sell in the future. Not actively listed.

**When to use:**
- Just acquired something that might be sold later
- Have existing inventory not ready to list
- Storing items for future sale
- Tracking items that may appreciate or depreciate over time

**Alpha Requirements:**

| Field | Type | Required | Highlight if Missing | Notes |
|-------|------|----------|---------------------|-------|
| name | string | ✅ Yes | - | Item name/model |
| category | enum | ✅ Yes | - | See categories below |
| condition | enum | ✅ Yes | - | new, like_new, good, fair, poor |
| cost_basis | decimal | ✅ Yes | - | What we paid / starting value |
| location | string | No | - | Where stored in home/space |
| acquisition_source | string | No | - | Amazon, eBay, local, gift, etc. |
| acquisition_condition | enum | No | - | new, used (condition when acquired) |
| acquisition_date | date | No | - | When we got it |
| description | text | No | ⚠️ Yes | Full description |
| images | array | No | ⚠️ Yes | Photos (see image types below) |
| tags | array | No | - | User-defined tags to link items |
| value_factors | array | No | - | Applied value factor tags |
| notes | text | No | - | Any notes |
| created_at | datetime | Auto | - | When added to system |
| updated_at | datetime | Auto | - | Last modified |

**Image Types:**
Images should be categorized by purpose:
- `physical` - Photos of the actual item, condition
- `specs` - Screenshots of specifications
- `performance` - Benchmark results, test outputs
- `receipt` - Purchase receipts, invoices
- `other` - Anything else

**Categories (Alpha):**
| Category | Description |
|----------|-------------|
| electronics | General electronics |
| homelab | Servers, networking, infrastructure |
| gpu | Graphics cards |
| cpu | Processors |
| ram | Memory modules |
| storage | SSDs, HDDs, NVMe |
| 3d_printing | Printers, filament, parts |
| beauty | Beauty products, tools |
| tools | Hand tools, power tools |
| other | Catch-all |

*Note: Categories are extensible - can add more as needed*

**Value Factors System:**

Value Factors are market condition multipliers that can be applied to items and adjusted globally.

| Field | Type | Notes |
|-------|------|-------|
| name | string | e.g., "Tariff Premium", "Shortage" |
| description | text | Why this factor exists |
| multiplier | decimal | e.g., 1.2 = 20% value boost, 1.0 = neutral |
| active | boolean | Whether currently applied |
| created_at | datetime | When created |
| updated_at | datetime | Last adjusted |

**Example Value Factors:**
- "Tariff Premium" (1.2) - Applied to RAM, NVMe due to import tariffs
- "GPU Shortage" (1.3) - Applied to GPUs during supply constraints
- "Seasonal Demand" (1.15) - Applied to items with holiday demand

**Value Factor CRUD Screen:**
- List all value factors with current multiplier
- Create new factors
- Edit multiplier (e.g., tariffs removed → change 1.2 to 1.0)
- Toggle active/inactive
- See which items have each factor applied

**Calculated Fields:**
- `adjusted_value` = cost_basis × (product of all active value_factor multipliers)

**Date-Sensitive Considerations:**
- Items can age even when not used (batteries, consumables)
- Acquisition date helps track how long we've held something
- Condition may need periodic review for aging items
- [Beta: Condition degradation warnings based on item type]

**AI Help (Alpha):**
- Price check for estimating current market value

**AI Help (Beta):**
- Photo analysis for condition assessment
- Auto-categorization from images/description
- Depreciation/appreciation suggestions
- [TBD]

**Transitions:**
- → DRAFT: When ready to prepare for sale

**UI Notes:**
- Quick-add form with just required fields (name, category, condition, cost_basis)
- Expansion panel for optional fields
- Visual indicator for items missing images/description
- Filter/group by category, location, tags
- Sort by acquisition date, value, condition

---

### Phase 2: DRAFT ✅ REVIEWED

**Description:** Items we've decided to sell and are preparing listings for.

**When to use:**
- Taking photos for listing
- Writing descriptions
- Researching pricing
- Generating platform-specific posts
- Creating bundles from multiple inventory items
- Preparing to post

**Alpha Requirements:**

| Field | Type | Required | Highlight if Missing | Notes |
|-------|------|----------|---------------------|-------|
| (all from INVENTORY) | | | | |
| base_asking_price | decimal | ✅ Yes | - | Base target sale price |
| min_price | decimal | No | - | Lowest acceptable |
| target_platforms | array | ✅ Yes | - | Where planning to list |
| platform_prices | json | No | - | Per-platform pricing (see below) |
| draft_posts | json | No | ⚠️ Yes | Generated posts per platform |
| ready_checklist | json | No | - | Completion status (see below) |
| bundle_item_ids | array | No | - | If bundle, which items included |
| is_bundle | boolean | No | - | Flag for bundle listings |

**Platform-Specific Pricing:**

Each platform can have adjusted pricing to account for fees:

```json
{
  "reddit": {
    "price": 100.00,
    "fees": 0,
    "net": 100.00,
    "notes": "No fees, PayPal G&S buyer covers"
  },
  "offerup": {
    "price": 115.00,
    "fees": 12.99,
    "net": 102.01,
    "notes": "OfferUp takes ~12.9%"
  },
  "ebay": {
    "price": 125.00,
    "fees": 16.25,
    "net": 108.75,
    "notes": "eBay ~13% + PayPal"
  }
}
```

**Ready-to-List Checklist:**

```json
{
  "photos_taken": { "done": true, "required": true },
  "description_written": { "done": true, "required": true },
  "price_researched": { "done": true, "required": true },
  "title_generated": { "done": false, "required": true },
  "post_generated": { "done": false, "required": true },
  "rules_reviewed": { "done": false, "required": false }
}
```

**Draft Posts Storage:**

```json
{
  "reddit_hardwareswap": {
    "title": "[USA-TX] [H] RTX 3080 FE [W] PayPal, Local Cash",
    "body": "Timestamp: [link]\n\nSelling RTX 3080 Founders Edition...",
    "generated_at": "2026-03-26T10:00:00Z",
    "reviewed": true,
    "edited": false
  },
  "offerup": {
    "title": "NVIDIA RTX 3080 Graphics Card",
    "body": "Excellent condition RTX 3080...",
    "generated_at": "2026-03-26T10:00:00Z",
    "reviewed": false,
    "edited": false
  }
}
```

**Bundling:**

When creating a bundle from multiple inventory items:
- Set `is_bundle = true`
- Set `bundle_item_ids = [item1_id, item2_id, ...]`
- Individual items remain in INVENTORY status
- Bundle gets its own pricing, images, description
- When bundle sells, all included items move to SOLD

---

## Marketplace Configuration System (NEW)

Each marketplace needs stored configuration for rules and AI generation.

**Marketplace Model:**

| Field | Type | Notes |
|-------|------|-------|
| id | int | Primary key |
| name | string | Internal name (reddit_hardwareswap) |
| display_name | string | "r/hardwareswap" |
| platform_type | enum | reddit, ebay, offerup, craigslist, swappa, facebook, other |
| active | boolean | Whether we're using this marketplace |
| fee_percentage | decimal | Platform fee % (e.g., 12.9 for OfferUp) |
| fee_flat | decimal | Flat fee if any |
| fee_notes | text | Fee explanation |

**Marketplace Rules:**

| Field | Type | Notes |
|-------|------|-------|
| marketplace_id | FK | Link to marketplace |
| rule_type | enum | title, body, image, general |
| rule_text | text | The actual rule |
| is_strict | boolean | Will they delist for violation? |
| example_good | text | Example of compliant post |
| example_bad | text | Example of violation |

**Marketplace AI Prompts:**

| Field | Type | Notes |
|-------|------|-------|
| marketplace_id | FK | Link to marketplace |
| prompt_type | enum | title, body, price_research |
| prompt_template | text | The AI prompt with {placeholders} |
| model_preference | string | Which model works best |
| notes | text | Any notes about this prompt |

**Example Marketplace Rules (r/hardwareswap):**

```
TITLE RULES:
- Format: [COUNTRY-STATE] [H] Item [W] Payment
- Example: [USA-TX] [H] RTX 3080 FE [W] PayPal, Local Cash
- State must be 2-letter abbreviation
- [H] = Have, [W] = Want
- No prices in title
- No emojis

BODY RULES:
- Must include timestamp photo (handwritten username + date)
- Timestamp must be within 7 days
- Must list price for each item
- Must specify shipping included or not
- Cannot link to other selling platforms
```

**AI Prompt Template Example:**

```
You are generating a title for r/hardwareswap.

STRICT FORMAT: [USA-{state}] [H] {item_name} [W] {payment_methods}

RULES:
- State must be 2-letter code
- No prices in title
- No emojis
- Keep concise

Item: {item.name}
Condition: {item.condition}
Location: {user.state}
Payment: PayPal, Local Cash

Generate ONLY the title, nothing else.
```

---

**AI Help (Alpha):**
- Price check with specific links to recent sales (existing, enhance)
- Post generation per platform using marketplace rules
- Title generation per platform format
- Fee-adjusted pricing calculator

**AI Help (Beta):**
- Photo enhancement suggestions
- SEO-optimized descriptions
- Competitor analysis
- Best time to post suggestions
- [TBD]

**Price Research Enhancement:**

AI should provide:
- Links to actual recent sales (with dates)
- Price ranges observed
- Platform-specific pricing suggestions
- Condition-adjusted estimates
- Warning if data is older than X days

Example output:
```
Recent Sales Found:
1. r/hardwareswap - $450 (3 days ago) - [link]
2. eBay sold listing - $475 (5 days ago) - [link]
3. r/hardwareswap - $425 (7 days ago) - [link]

Suggested Pricing:
- Quick sale: $420-440
- Fair price: $450-470
- Patient seller: $480-500

Platform Adjustments:
- Reddit: $450 (no fees)
- eBay: $510 (after 13% fees = $444 net)
- OfferUp: $520 (after 12.9% fees = $453 net)
```

**Transitions:**
- → LISTED: When posted on at least one platform
- → INVENTORY: If deciding not to sell yet

**UI Notes:**
- Platform selector with fee preview
- One-click "Generate All Posts" button
- Side-by-side post preview per platform
- Checklist progress indicator
- Bundle builder interface
- "Copy to Clipboard" for each platform post

---

### Phase 3: LISTED ✅ REVIEWED

**Description:** Items actively listed for sale on one or more platforms.

**When to use:**
- Post is live on Reddit/OfferUp/etc.
- Monitoring for responses
- Managing multiple active listings
- Bumping/refreshing posts
- Adjusting prices based on response

**Alpha Requirements:**

| Field | Type | Required | Notes |
|-------|------|----------|---------------------|
| (all from DRAFT) | | | |
| listed_at | datetime | Auto | When first listed |
| active_listings | json | Yes | Per-platform listing data (see below) |
| price_history | json | No | Track price changes over time |
| total_views | integer | No | Aggregate views if trackable |
| total_responses | integer | No | Count of all inquiries |

**Active Listings Structure:**

```json
{
  "reddit_hardwareswap": {
    "url": "https://reddit.com/r/hardwareswap/comments/abc123",
    "posted_at": "2026-03-26T10:00:00Z",
    "expires_at": "2026-03-29T10:00:00Z",
    "can_bump_at": "2026-03-29T10:00:00Z",
    "last_bumped": null,
    "bump_count": 0,
    "current_price": 450.00,
    "views": null,
    "responses": 3,
    "status": "active"
  },
  "offerup": {
    "url": "https://offerup.com/item/detail/123456",
    "posted_at": "2026-03-26T10:30:00Z",
    "expires_at": null,
    "can_bump_at": "2026-03-27T10:30:00Z",
    "last_bumped": "2026-03-27T12:00:00Z",
    "bump_count": 1,
    "current_price": 520.00,
    "views": 45,
    "responses": 1,
    "status": "active"
  }
}
```

**Price History Tracking:**

```json
{
  "changes": [
    {
      "date": "2026-03-26T10:00:00Z",
      "old_price": null,
      "new_price": 450.00,
      "reason": "initial_listing",
      "platform": "all"
    },
    {
      "date": "2026-03-30T14:00:00Z",
      "old_price": 450.00,
      "new_price": 425.00,
      "reason": "no_interest_4_days",
      "platform": "reddit_hardwareswap"
    }
  ]
}
```

**Cross-Posting Options:**

1. **Simultaneous** - List on all platforms at once
2. **Staggered** - List on primary platform first, others later
3. **Platform-specific timing** - Some platforms better at certain times

UI should support both workflows with scheduling capability.

**Response Tracking:**

Each listing tracks responses (inquiries that haven't become formal leads yet):

```json
{
  "responses": [
    {
      "id": "resp_001",
      "platform": "reddit_hardwareswap",
      "username": "u/buyer123",
      "message": "PM'd",
      "received_at": "2026-03-26T14:30:00Z",
      "replied": false,
      "reply_due": "2026-03-26T18:30:00Z",
      "converted_to_lead": false
    }
  ]
}
```

**Bundle Management (LISTED phase):**

When items are bundled:
- Show bundle composition in listing view
- When part of bundle sells separately:
  - Alert to update bundle listing
  - Suggest new bundle price
  - Option to auto-adjust or manual
- Track which bundles contain which items
- Prevent double-selling (item in multiple bundles)

**Bump/Refresh System:**

| Platform | Bump Rules | Can Automate? |
|----------|------------|---------------|
| r/hardwareswap | Repost after 72h | Manual only |
| r/homelabsales | Repost after 72h | Manual only |
| OfferUp | Bump daily | [Research needed] |
| eBay | Relist when ended | [Research needed] |
| Craigslist | Renew every 48h | [Research needed] |

**Alpha:** Reminders when bump is available
**Beta:** Automated bumping where platform allows

---

## Global Action List System (NEW)

A central task/action system that aggregates actionable items from all phases.

**Action Model:**

| Field | Type | Notes |
|-------|------|-------|
| id | int | Primary key |
| action_type | enum | See types below |
| priority | enum | urgent, high, normal, low |
| title | string | Short description |
| description | text | Details |
| source_type | enum | item, lead, sale, listing |
| source_id | int | FK to source record |
| due_at | datetime | When action is due |
| created_at | datetime | When action was created |
| completed_at | datetime | When marked done |
| dismissed_at | datetime | If dismissed without completing |
| auto_generated | boolean | System-created vs manual |

**Action Types:**

| Type | Source | Example |
|------|--------|---------|
| `respond_to_inquiry` | Lead | "Reply to u/buyer123 about RTX 3080" |
| `bump_listing` | Listing | "Bump r/hardwareswap post (72h passed)" |
| `update_listing` | Listing | "Update bundle price - GPU sold separately" |
| `follow_up_lead` | Lead | "Follow up with u/buyer456 - no response 2 days" |
| `ship_item` | Sale | "Ship RTX 3080 to buyer - paid yesterday" |
| `add_tracking` | Sale | "Add tracking number for order #123" |
| `confirm_delivery` | Sale | "Check delivery status - should have arrived" |
| `request_feedback` | Sale | "Request feedback from u/buyer789" |
| `review_price` | Item | "Review pricing - listed 7 days, no interest" |
| `take_photos` | Item | "Add photos to RTX 3080 (missing)" |
| `complete_checklist` | Item | "Finish listing prep - 3/5 items done" |
| `manual` | Any | User-created tasks |

**Action Generation Rules:**

```
IF lead.status = "new" AND lead.created_at > 4 hours ago
  → CREATE action "respond_to_inquiry" priority=urgent

IF listing.can_bump_at < NOW
  → CREATE action "bump_listing" priority=normal

IF listing.responses > 0 AND any response.replied = false AND response.received_at > 4 hours
  → CREATE action "respond_to_inquiry" priority=high

IF item.status = "listed" AND item.listed_at > 7 days AND item.total_responses = 0
  → CREATE action "review_price" priority=normal

IF sale.status = "paid" AND sale.shipped_date IS NULL AND sale.sale_date > 24 hours
  → CREATE action "ship_item" priority=urgent
```

**Dashboard Widget:**

```
┌─────────────────────────────────────────────────┐
│  ACTION ITEMS                          View All │
├─────────────────────────────────────────────────┤
│ 🔴 URGENT (2)                                   │
│   • Reply to u/buyer123 - RTX 3080    (4h ago) │
│   • Ship to u/buyer456 - paid yesterday        │
├─────────────────────────────────────────────────┤
│ 🟡 HIGH (3)                                     │
│   • Bump r/hardwareswap post          (ready)  │
│   • Follow up with u/buyer789         (2 days) │
│   • Update bundle price - item sold            │
├─────────────────────────────────────────────────┤
│ 🟢 NORMAL (5)                                   │
│   • Review pricing on 3 items (7+ days)        │
│   • Add photos to 2 items                      │
└─────────────────────────────────────────────────┘
```

**Response Learning (Beta):**

Track which responses lead to sales:
- Store response messages
- Track conversion rate by response type
- AI learns what response styles work
- Suggest responses based on successful patterns

```json
{
  "response_analytics": {
    "total_responses_sent": 150,
    "converted_to_sale": 45,
    "conversion_rate": 0.30,
    "avg_response_time_minutes": 47,
    "best_performing_templates": [
      { "template_id": "quick_specs", "conversion": 0.42 },
      { "template_id": "friendly_offer", "conversion": 0.38 }
    ]
  }
}
```

---

**AI Help (Alpha):**
- Regenerate/update post content
- Price adjustment suggestions
- Response suggestions (basic)
- Action prioritization

**AI Help (Beta):**
- Automated bump scheduling
- Dynamic pricing based on market
- Response templates learned from success
- Optimal posting time suggestions
- Competitor monitoring
- "Why isn't this selling?" analysis

**Transitions:**
- → INTEREST: When a response becomes a formal lead
- → DRAFT: If delisting temporarily (take down posts)
- → INVENTORY: If removing from sale entirely
- → SOLD: If sold outside system (direct, local, etc.)

**UI Notes:**
- **Listings Dashboard**: All active listings with status indicators
- **Response inbox**: All inquiries awaiting reply
- **Bump calendar**: Visual schedule of when bumps available/due
- **Price adjustment panel**: Quick price changes with history
- **Bundle manager**: See bundle composition, adjust when parts sell

---

### Phase 4: INTEREST ✅ REVIEWED

**Description:** Someone has expressed interest in buying. All incoming contacts are leads - we track interest level since many are low-intent.

**When to use:**
- Received DM/comment/email about item
- Any inquiry, even casual "PM'd" or "interested"
- Negotiating price
- Answering questions

**Key Concept:** Every contact is a lead. We track "interest level" to distinguish serious buyers from tire-kickers, but we keep records of all.

**Alpha Requirements:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| lead.username | string | Yes | Buyer identifier |
| lead.platform | enum | Yes | Where they contacted us |
| lead.interest_level | enum | No | See levels below (default: unknown) |
| lead.status | enum | Yes | See statuses below |
| lead.item_ids | array | Yes | Item(s) they're interested in |
| lead.is_bundle_inquiry | boolean | No | Are they asking about multiple items as bundle? |
| lead.source_listing_url | string | No | Which listing they came from |
| lead.created_at | datetime | Auto | When lead was created |
| lead.updated_at | datetime | Auto | Last activity |

**Interest Levels:**

| Level | Description | Example |
|-------|-------------|---------|
| `hot` | Ready to buy, asking for PayPal | "I'll take it, send PayPal" |
| `warm` | Engaged, asking questions | "Is this still available? What's the lowest?" |
| `cold` | Low engagement, generic | "PM'd", "Interested" |
| `tire_kicker` | Unlikely to buy | Lowball offers, endless questions, no commitment |
| `unknown` | Not yet assessed | Default for new leads |

**Lead Statuses:**

| Status | Description |
|--------|-------------|
| `new` | Just received, not reviewed |
| `in_progress` | Actively conversing |
| `waiting_on_buyer` | Ball is in their court |
| `waiting_on_me` | I need to respond |
| `agreed` | → Moves to Phase 5 |
| `snoozed` | Temporarily paused (with reason) |
| `dead` | Not proceeding (with reason) |

---

## Lead Message System (NEW)

All incoming messages are tracked with required review actions.

**LeadMessage Model:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | Auto | Primary key |
| lead_id | FK | Yes | Parent lead |
| direction | enum | Yes | `incoming` or `outgoing` |
| message_text | text | Yes | The actual message |
| platform | enum | Yes | Where message was sent |
| received_at | datetime | Yes | When received/sent |
| review_status | enum | Yes | See below |
| reviewed_at | datetime | No | When reviewed |

**Review Statuses:**

| Status | Required Fields | Description |
|--------|-----------------|-------------|
| `needs_review` | - | Default for incoming messages |
| `responded` | response_details | I replied to this |
| `ignored` | ignore_reason | Intentionally not responding |
| `snoozed` | snooze_reason, snooze_until | Will address later |

**Response Details (when status = responded):**

```json
{
  "response_type": "answer_question",  // or: made_offer, sent_info, sent_photos, declined, counter_offer
  "response_summary": "Sent additional photos and confirmed price includes shipping",
  "offer_made": {
    "is_bundle": true,
    "bundle_total": 250.00,
    "items": [
      { "item_id": 123, "item_name": "RTX 3080", "price": 200.00 },
      { "item_id": 124, "item_name": "Power cables", "price": 50.00 }
    ],
    "shipping_included": true,
    "payment_method": "PayPal G&S"
  },
  "attachments": [
    { "type": "image", "purpose": "additional_photos", "url": "/uploads/img1.jpg" },
    { "type": "image", "purpose": "performance_screenshot", "url": "/uploads/bench.png" }
  ],
  "responded_at": "2026-03-26T15:30:00Z"
}
```

**Bundle Offer Handling:**

When making an offer for multiple items:
- `bundle_total` is **required** (the one price they need to pay)
- `items` array is **optional** (breakdown of individual prices)
- If items provided, they should sum to bundle_total
- UI shows bundle total prominently, item breakdown as expandable detail

**Ignore/Snooze Details:**

```json
{
  "ignore_reason": "lowball_offer",  // or: spam, scam_attempt, out_of_stock, other
  "ignore_notes": "Offered $50 for $450 item, not worth engaging"
}

{
  "snooze_reason": "waiting_for_restock",  // or: busy_now, need_to_check_something, other
  "snooze_notes": "Said they'd get back to me after payday",
  "snooze_until": "2026-03-30T00:00:00Z"
}
```

**Response Attachments:**

When responding, can attach:
- `additional_photos` - More pictures of item
- `performance_screenshot` - Benchmarks, specs
- `timestamp_photo` - Fresh timestamp
- `shipping_estimate` - Screenshot of shipping calc
- `other` - Any other relevant image

---

**Lead Sources (Alpha):**

| Source | Auto-Ingest | Notes |
|--------|-------------|-------|
| Reddit email (n8n) | ✅ Yes | Chat requests, post replies |
| Reddit post comments | ✅ Yes | Via post URL import |
| OfferUp | Manual | Copy/paste or screenshot |
| Craigslist | Manual | Copy/paste |
| Direct message | Manual | Any platform |

**Lead Sources (Beta):**

| Source | Auto-Ingest | Notes |
|--------|-------------|-------|
| OfferUp notifications | [Research] | Email or API? |
| eBay messages | [Research] | API access? |
| Facebook Marketplace | [Research] | Messenger integration? |

---

**AI Help (Alpha):**
- Response suggestions based on message content
- Interest level assessment from message tone
- Scam detection (common red flags)
- Quick reply templates

**AI Help (Beta):**
- Response effectiveness learning
- Negotiation coaching
- Buyer history lookup (Reddit flair, etc.)
- Optimal response timing
- "Should I engage?" recommendations for low-interest leads

**Transitions:**
- → AGREEMENT: When price/terms agreed
- → DEAD: If buyer ghosts, declines, or is ignored
- → SNOOZED: Temporarily paused (can return to INTEREST)

**UI Notes:**
- **Lead Inbox**: All leads with unreviewed messages highlighted
- **Conversation View**: Full thread with buyer
- **Quick Actions**: Respond, Snooze, Ignore (with required details)
- **Offer Builder**: UI for constructing bundle offers
- **Attachment Upload**: Easy image attachment for responses
- **Interest Level Badges**: Visual indicators (🔥 hot, 🌡️ warm, ❄️ cold, 👀 tire-kicker)

---

### Phase 5: AGREEMENT ✅ REVIEWED

**Description:** Buyer and seller have agreed on price and terms. Waiting for payment or meetup.

**When to use:**
- Price agreed
- Payment method agreed
- Waiting for buyer to pay (shipped) OR planning meetup (local)

**Key Concept:** Two transaction types with different workflows:
1. **Shipped Sale** - Send invoice, wait for payment, then ship
2. **Local Sale** - Plan meetup, exchange item for cash/payment

**Note:** Items remain listed on other platforms until payment received.

**Alpha Requirements:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| lead.status | enum | Yes | = "agreed" |
| lead.transaction_type | enum | Yes | `shipped` or `local` |
| lead.agreed_price | decimal | Yes | Final agreed price |
| lead.agreed_at | datetime | Auto | When agreement reached |
| lead.payment_method | enum | Yes | See methods below |
| lead.agreement_details | json | No | See structure below |

**Payment Methods:**

| Method | Transaction Type | Notes |
|--------|------------------|-------|
| `paypal_gs` | Shipped | PayPal Goods & Services (required for Reddit) |
| `paypal_ff` | Either | PayPal Friends & Family |
| `venmo` | Either | Venmo transfer |
| `zelle` | Either | Zelle transfer |
| `cash` | Local | Cash at meetup |
| `crypto` | Either | BTC, ETH, etc. |
| `other` | Either | Specify in notes |

**Agreement Details Structure:**

For **shipped sales**:
```json
{
  "transaction_type": "shipped",
  "agreed_price": 450.00,
  "shipping_included": true,
  "payment_method": "paypal_gs",
  "invoice": {
    "status": "not_sent",  // not_sent, sent, paid
    "sent_at": null,
    "paypal_email": "buyer@email.com",
    "invoice_id": null,
    "invoice_link": null
  },
  "buyer_address": null,  // Collected from PayPal after payment
  "notes": "Includes original box"
}
```

For **local sales**:
```json
{
  "transaction_type": "local",
  "agreed_price": 400.00,
  "payment_method": "cash",
  "meetup": {
    "status": "planning",  // planning, scheduled, completed, cancelled
    "proposed_locations": ["Starbucks on Main St", "Police station parking lot"],
    "confirmed_location": null,
    "confirmed_datetime": null,
    "buyer_contact": "555-123-4567",
    "notes": "Buyer prefers evening"
  }
}
```

---

## Invoice Workflow (Shipped Sales)

**Invoice Status Flow:**
```
not_sent → sent → paid → (Phase 6: PAID)
```

**Auto-Generated Actions:**

| Trigger | Action | Priority |
|---------|--------|----------|
| Agreement created (shipped) | "Generate and send invoice" | high |
| Invoice sent, 24h passed | "Follow up on invoice" | normal |
| Invoice sent, 48h passed | "Invoice reminder - 2 days" | high |
| Invoice sent, 72h passed | "Invoice stale - consider moving on" | urgent |

**Escalating Visibility:**

```
0-24h:   🟢 Normal - invoice sent, waiting
24-48h:  🟡 Yellow - gentle reminder suggested
48-72h:  🟠 Orange - stronger follow-up needed
72h+:    🔴 Red - likely dead, decision time
```

**Invoice Task Checklist:**
- [ ] Get buyer's PayPal email
- [ ] Create PayPal invoice with agreed amount
- [ ] Include item description and photos
- [ ] Send invoice
- [ ] Record invoice ID/link in Scrounger
- [ ] Monitor for payment

---

## Meetup Workflow (Local Sales)

**Meetup Status Flow:**
```
planning → scheduled → completed → (Phase 6: PAID)
                    → cancelled → (back to INTEREST or DEAD)
```

**Meetup Planning Fields:**

| Field | Type | Notes |
|-------|------|-------|
| proposed_locations | array | Safe meetup spots |
| confirmed_location | string | Where we're meeting |
| confirmed_datetime | datetime | When we're meeting |
| buyer_contact | string | Phone number or other contact |
| meetup_notes | text | Any special instructions |

**Auto-Generated Actions:**

| Trigger | Action | Priority |
|---------|--------|----------|
| Agreement created (local) | "Schedule meetup time/place" | high |
| Meetup scheduled | "Reminder: meetup tomorrow" | normal (day before) |
| Meetup time passed, not completed | "Mark meetup completed or rescheduled?" | urgent |

**Safe Meetup Locations (Configurable):**
- Police station parking lots
- Bank lobbies
- Coffee shops (Starbucks, etc.)
- Mall food courts
- Other public places

---

## Items During Agreement

**Item Status:** Items stay `listed` until payment received

**Why:** Buyer may ghost, agreement may fall through

**UI Indication:** Items with pending agreements show badge:
```
RTX 3080 [LISTED] ⏳ Pending agreement with u/buyer123
```

**If another buyer inquires:**
- Can still create lead
- System warns: "Item has pending agreement"
- If first deal falls through, second buyer becomes priority

---

**AI Help (Alpha):**
- Shipping cost estimation
- Invoice amount calculation (include fees if needed)
- Meetup location suggestions (based on ZIP codes)
- Follow-up message templates

**AI Help (Beta):**
- PayPal invoice generation (if API available)
- Optimal meetup time suggestions
- Buyer reliability assessment
- "Is this deal going to close?" prediction

**Transitions:**
- → PAID: When payment received (shipped or local)
- → INTEREST: If deal falls through, renegotiating
- → DEAD: If buyer disappears after agreement

**UI Notes:**
- **Agreement Dashboard**: All pending agreements with escalation status
- **Invoice Tracker**: Send, track, escalate invoices
- **Meetup Planner**: Schedule and confirm local sales
- **Timeline View**: Visual escalation (green → yellow → orange → red)
- **Quick Actions**: "Mark as paid", "Send reminder", "Cancel agreement"

---

### Phase 6: PAID ✅ REVIEWED

**Description:** Payment received. For shipped sales: pack and ship. For local sales: instant transition to complete.

**When to use:**
- Payment confirmed in account
- Ready to fulfill order

**Key Concept:** This phase is primarily **task management** for shipping workflow. Local sales pass through instantly.

**Transaction Type Handling:**

| Type | Phase 6 Duration | Notes |
|------|------------------|-------|
| `shipped` | Until dropped at carrier | Full shipping workflow |
| `local` | Instant | Payment = completion, skip to Phase 9 |

---

## Sale Record (Created at Payment)

**Alpha Requirements:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| sale.id | int | Auto | Primary key |
| sale.lead_id | FK | Yes | Link to lead |
| sale.item_ids | array | Yes | Items sold (supports bundles) |
| sale.transaction_type | enum | Yes | `shipped` or `local` |
| sale.sale_price | decimal | Yes | Total amount received |
| sale.payment_method | enum | Yes | paypal_gs, cash, etc. |
| sale.payment_date | datetime | Auto | When payment confirmed |
| sale.buyer_username | string | Yes | Who bought |
| sale.buyer_address | text | No | Shipping address (from PayPal) |
| sale.platform | enum | Yes | Where sold |
| sale.status | enum | Yes | See statuses below |

**Sale Statuses:**

| Status | Description |
|--------|-------------|
| `paid` | Payment received, needs shipping |
| `shipped` | Package sent, in transit |
| `delivered` | Package arrived |
| `complete` | Feedback exchanged, done |

**Fee Tracking (for profit analysis):**

| Field | Type | Notes |
|-------|------|-------|
| sale.platform_fees | decimal | Marketplace fees (eBay, OfferUp %) |
| sale.payment_fees | decimal | PayPal G&S fees (~3.5%) |
| sale.shipping_cost | decimal | Actual shipping paid |
| sale.cost_basis | decimal | Sum of item cost_basis values |
| sale.profit | decimal | Calculated: sale_price - all fees - cost_basis |

**Profit Calculation:**
```
profit = sale_price - platform_fees - payment_fees - shipping_cost - cost_basis
```

---

## Shipping Workflow (Task Management)

**Shipping Task Checklist:**

Auto-generated when sale created (shipped type):

```json
{
  "tasks": [
    { "id": "get_address", "label": "Get buyer address from PayPal", "done": false, "required": true },
    { "id": "pack_items", "label": "Pack item(s)", "done": false, "required": true },
    { "id": "create_label", "label": "Create shipping label", "done": false, "required": true },
    { "id": "drop_off", "label": "Drop off at carrier", "done": false, "required": true }
  ],
  "packing_list": [
    { "item_id": 123, "item_name": "RTX 3080", "packed": false },
    { "item_id": 124, "item_name": "Power cables", "packed": false }
  ]
}
```

**Task Status in Action List:**

| Trigger | Action | Priority |
|---------|--------|----------|
| Payment received | "Pack and ship to u/buyer123" | high |
| 24h since payment | "Ship reminder - paid yesterday" | urgent |
| 48h since payment | "OVERDUE: Ship to u/buyer123" | urgent |

**Packing List:**

For bundle sales, generate packing list:
```
📦 Order for u/buyer123
━━━━━━━━━━━━━━━━━━━━━━
☐ RTX 3080 FE
☐ 2x 8-pin power cables
☐ Original box
━━━━━━━━━━━━━━━━━━━━━━
Ship to:
John Smith
123 Main Street
Austin, TX 78701
```

---

## Shipping Details

**Shipping Fields:**

| Field | Type | Notes |
|-------|------|-------|
| shipping_carrier | enum | usps, ups, fedex, other |
| shipping_service | string | Priority Mail, Ground, etc. |
| shipping_cost | decimal | What we paid for shipping |
| estimated_weight | decimal | In pounds/ounces |
| package_dimensions | json | L x W x H |
| label_source | enum | pirate_ship, usps_direct, ups_store, etc. |

**Carrier Options:**

| Carrier | Common Services | Notes |
|---------|-----------------|-------|
| USPS | Priority Mail, First Class, Ground Advantage | Usually cheapest for small items |
| UPS | Ground, 2-Day, Next Day | Better for heavy items |
| FedEx | Ground, Express | Good tracking |

**Label Sources:**
- Pirate Ship (discounted USPS/UPS)
- USPS.com directly
- UPS Store
- FedEx Office
- Carrier pickup

---

## Local Sale Completion

For local sales, Phase 6 is instant:

1. Meetup happens (Phase 5)
2. Cash/payment exchanged
3. Item handed over
4. Mark as "paid" → automatically mark as "complete"
5. Skip Phases 7 & 8 (no shipping)

**Quick Action:** "Complete local sale" button that:
- Creates sale record
- Marks items as sold
- Skips to Phase 9 (COMPLETE)

---

**AI Help (Alpha):**
- Shipping cost estimation
- Carrier recommendation based on weight/size
- Packing tips for fragile items

**AI Help (Beta):**
- Auto-fill dimensions from item category
- Label price comparison across carriers
- "Print packing slip" generation
- Optimal box size suggestions

**Transitions:**
- → SHIPPED (Phase 7): When dropped at carrier + tracking added
- → COMPLETE (Phase 9): If local sale (instant)

**UI Notes:**
- **To Ship Queue**: All orders awaiting shipment with time indicators
- **Packing Checklist**: Visual checklist for bundle orders
- **Shipping Calculator**: Quick cost estimate
- **Quick Entry**: Add tracking number + carrier → moves to SHIPPED
- **Profit Preview**: Show expected profit after all fees

---

### Phase 7: SHIPPED ✅ REVIEWED

**Description:** Item is in transit to buyer. Tracking available.

**When to use:**
- Package dropped off at carrier
- Tracking number entered

**Key Concept:** Monitoring phase - waiting for delivery. Provide tracking URLs and message templates if buyer asks.

**Alpha Requirements:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| sale.status | enum | Yes | = "shipped" |
| sale.shipped_date | datetime | Yes | When dropped off |
| sale.shipping_carrier | enum | Yes | usps, ups, fedex, other |
| sale.tracking_number | string | Yes | Tracking ID |
| sale.tracking_url | string | Auto | Generated from carrier + number |

**Tracking URL Generation:**

| Carrier | URL Pattern |
|---------|-------------|
| USPS | `https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking}` |
| UPS | `https://www.ups.com/track?tracknum={tracking}` |
| FedEx | `https://www.fedex.com/fedextrack/?trknbr={tracking}` |

**Buyer Message Template:**

If buyer asks for tracking (PayPal usually sends automatically, but just in case):

```
Hi {buyer_username},

Your order has shipped! Here are the details:

Carrier: {carrier}
Tracking Number: {tracking_number}
Track here: {tracking_url}

Estimated delivery: {estimated_delivery or "Check tracking link"}

Let me know when it arrives!
```

**Copy-to-clipboard** button for easy sharing.

---

**AI Help (Alpha):**
- Generate tracking message
- Estimated delivery lookup (manual)

**AI Help (Beta):**
- Auto-tracking status polling
- Delivery estimate from carrier API
- Proactive "your package was delivered" notification

**Transitions:**
- → DELIVERED (Phase 8): When tracking shows delivered (manual confirmation)

**UI Notes:**
- **In Transit List**: All shipped orders with tracking links
- **Quick Check**: Click tracking URL to verify status
- **Copy Tracking Message**: One-click copy for buyer inquiries

---

### Phase 8: DELIVERED ✅ REVIEWED

**Description:** Package arrived. Waiting for buyer confirmation and feedback.

**When to use:**
- Tracking shows delivered
- Manually confirm delivery in Scrounger

**Key Concept:** Timer-based follow-up system. After delivery, wait configurable time before prompting for feedback request.

**Alpha Requirements:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| sale.status | enum | Yes | = "delivered" |
| sale.delivered_date | datetime | Yes | When tracking showed delivered |
| sale.delivery_confirmed_at | datetime | Yes | When I confirmed in Scrounger |
| sale.feedback_timer_days | int | No | Override default timer (if desired) |
| sale.feedback_requested_at | datetime | No | When I sent feedback request |

---

## Feedback Timer System

**Timer Configuration (hierarchical):**

```
1. Per-shipment override (highest priority)
2. Per-marketplace default
3. Master config default (fallback)
```

**Config Example:**

```json
{
  "feedback_timer": {
    "master_default_days": 3,
    "marketplace_defaults": {
      "reddit_hardwareswap": 2,
      "reddit_homelabsales": 2,
      "ebay": 5,
      "offerup": 3
    }
  }
}
```

**Timer Flow:**

```
Delivery Confirmed
       ↓
   Timer Starts
       ↓
   (X days pass)
       ↓
   Task Created: "Request feedback from u/buyer"
       ↓
   [Action: Send feedback request]
       ↓
   Waiting for feedback...
       ↓
   [Feedback received] → COMPLETE
   [No feedback after Y more days] → COMPLETE (no feedback) + chaser task
```

---

## Feedback Request Task

When timer expires, auto-create action:

**Action Details:**
- Title: "Request feedback from u/{buyer_username}"
- Priority: normal
- Description: Generated message + instructions

**Generated Message:**

```
Hi {buyer_username},

Hope the {item_name} arrived safely! If everything looks good,
I'd really appreciate if you could leave feedback on my
{platform} post.

Here's the link: {original_listing_url}

Thanks for the smooth transaction!
```

**Instructions (especially helpful for old transactions):**

```
📬 How to send:
Platform: {platform}
Send to: u/{buyer_username}
Method: {contact_method - DM, Reddit chat, etc.}

Original listing: {listing_url}
Sale date: {sale_date}
Item: {item_name}
```

---

## Marking Complete

**Options when reviewing delivered item:**

1. **"Feedback Received"** → Mark type (positive/neutral or negative)
   - Positive/Neutral → Phase 9: COMPLETE
   - Negative → Phase 10: DISPUTE

2. **"Complete Without Feedback"** → Phase 9: COMPLETE (no_feedback)
   - Creates chaser task for 2 weeks later (configurable)
   - Chaser is just a reminder, doesn't change status

3. **"Issue Reported"** → Phase 10: DISPUTE

**Chaser Task (after complete without feedback):**

```json
{
  "chaser_timer": {
    "master_default_days": 14,
    "marketplace_defaults": {
      "reddit_hardwareswap": 14,
      "ebay": 21
    }
  }
}
```

**Chaser Message:**

```
Hey {buyer_username},

Just following up on the {item_name} - hope you're enjoying it!

If you have a moment, feedback would be greatly appreciated.

{feedback_link}

Thanks!
```

**Note:** Chaser is one-time, optional reminder. Doesn't change status.

---

## Updating Feedback Later

If buyer leaves feedback after marked "complete without feedback":
- Can update sale to "complete with feedback"
- Select feedback type (positive/neutral or negative)
- If negative → triggers DISPUTE flow

---

**AI Help (Alpha):**
- Generate feedback request message
- Generate chaser message

**AI Help (Beta):**
- Optimal timing for feedback requests
- Success rate tracking for different message styles

**Transitions:**
- → COMPLETE (Phase 9): Feedback received (positive/neutral) or complete without feedback
- → DISPUTE (Phase 10): Negative feedback or issue reported

**UI Notes:**
- **Awaiting Feedback List**: All delivered items with timer status
- **Timer Indicators**: Visual countdown (3 days left, due today, overdue)
- **Quick Actions**: "Feedback received", "Complete without feedback", "Issue"
- **Message Generator**: Copy-ready feedback request

---

### Phase 9: COMPLETE ✅ REVIEWED

**Description:** Transaction successfully completed. Item archived.

**When to use:**
- Positive/neutral feedback received, OR
- Closed without feedback (chaser scheduled), OR
- Local sale completed

**Key Concept:** Terminal state for successful transactions. Items marked as sold/archived.

**Alpha Requirements:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| sale.status | enum | Yes | = "complete" |
| sale.completed_at | datetime | Auto | When marked complete |
| sale.completion_type | enum | Yes | See types below |
| item.status | enum | Yes | = "sold" (then archived) |

**Completion Types:**

| Type | Description | Chaser Task? |
|------|-------------|--------------|
| `with_feedback` | Positive/neutral feedback received | No |
| `no_feedback` | Closed without feedback | Yes (2 weeks) |
| `local_sale` | In-person transaction | No |

**Feedback Tracking:**

| Field | Type | Notes |
|-------|------|-------|
| sale.feedback_received | boolean | Did buyer leave feedback? |
| sale.feedback_type | enum | positive, neutral, negative |
| sale.feedback_text | text | What they said (if captured) |
| sale.feedback_link | string | Link to feedback (if applicable) |
| sale.feedback_given | boolean | Did I leave feedback for buyer? |

**Item Status Updates:**

When sale completes:
1. Item status → `sold`
2. Item `sold_at` → timestamp
3. Item remains in database for history/analytics
4. Optional: Archive after X days (configurable)

**For Bundles:**

When bundle sale completes:
- All items in bundle → `sold`
- Each item linked to same sale record
- Bundle listing → archived

---

## Analytics Data (captured at completion)

For reporting and learning:

```json
{
  "sale_summary": {
    "item_ids": [123, 124],
    "item_names": ["RTX 3080", "Power cables"],
    "total_cost_basis": 350.00,
    "sale_price": 480.00,
    "platform_fees": 0,
    "payment_fees": 16.80,
    "shipping_cost": 15.00,
    "net_profit": 98.20,
    "profit_margin": "28%",
    "days_to_sell": 5,
    "lead_conversion_rate": "1 of 4 leads",
    "platform": "reddit_hardwareswap"
  }
}
```

---

## Updating Completed Sales

Can update a completed sale if:
- Feedback received later (no_feedback → with_feedback)
- Negative feedback received → triggers DISPUTE (Phase 10)
- Error correction needed

---

**AI Help (Alpha):**
- Transaction summary generation
- Profit calculation verification

**AI Help (Beta):**
- "Lessons learned" analysis
- Pricing optimization suggestions for similar items
- Buyer relationship tracking

**Transitions:**
- → DISPUTE (Phase 10): If negative feedback received later
- None otherwise (terminal state)

**UI Notes:**
- **Completed Sales History**: All successful transactions
- **Profit Dashboard**: Revenue, costs, margins
- **Feedback Status**: Quick view of feedback given/received
- **Export**: Transaction data for records/taxes

---

### Phase 10: DISPUTE ✅ REVIEWED

**Description:** Issue reported or negative feedback received. Working to resolve.

**When to use:**
- Buyer reports problem (damaged, not as described, missing)
- Negative feedback received
- Need to ameliorate situation

**Key Concept:** Goal is to turn negative experience into positive (or at least neutral). Track resolution attempts.

**Dispute Entry Points:**

| From | Trigger |
|------|---------|
| Phase 8 (DELIVERED) | Buyer reports issue |
| Phase 9 (COMPLETE) | Negative feedback received |

**Alpha Requirements:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| dispute.id | int | Auto | Primary key |
| dispute.sale_id | FK | Yes | Related sale |
| dispute.type | enum | Yes | See types below |
| dispute.status | enum | Yes | See statuses below |
| dispute.description | text | Yes | What's the issue |
| dispute.created_at | datetime | Auto | When dispute started |
| dispute.resolved_at | datetime | No | When resolved |
| dispute.resolution | text | No | How it was resolved |

**Dispute Types:**

| Type | Description |
|------|-------------|
| `not_as_described` | Item different than listing |
| `damaged_in_shipping` | Arrived broken |
| `missing_items` | Parts missing from bundle |
| `not_received` | Package lost |
| `buyer_remorse` | They changed their mind |
| `negative_feedback` | Received negative without prior complaint |
| `other` | Other issue |

**Dispute Statuses:**

| Status | Description |
|--------|-------------|
| `open` | Issue reported, working on it |
| `waiting_buyer` | Waiting for buyer response |
| `waiting_seller` | I need to take action |
| `resolved_positive` | Fixed, buyer happy |
| `resolved_neutral` | Partially resolved |
| `resolved_negative` | Couldn't fix, remains negative |
| `refunded` | Full or partial refund issued |

---

## Resolution Workflow

**Step 1: Acknowledge**
- Respond promptly to buyer
- Show empathy, don't be defensive
- Ask for details/photos if needed

**Step 2: Assess**
- What went wrong?
- Is it my fault, shipping damage, or buyer issue?
- What's the fair resolution?

**Step 3: Offer Resolution**
- Partial refund
- Full refund + return
- Replacement (if available)
- Other compensation

**Step 4: Execute**
- Process refund if agreed
- Track any returns
- Update dispute status

**Step 5: Follow Up**
- Ask buyer to update/remove negative feedback
- Document outcome

---

## Resolution Actions

| Action | Fields to Track |
|--------|-----------------|
| Partial Refund | amount, method, date |
| Full Refund | amount, method, date, return_required |
| Replacement Sent | tracking_number, date |
| No Action | reason |

**Refund Tracking:**

```json
{
  "refund": {
    "type": "partial",  // partial, full
    "amount": 50.00,
    "method": "paypal",
    "transaction_id": "ABC123",
    "date": "2026-03-28",
    "reason": "Item had minor scratch not shown in photos",
    "return_required": false
  }
}
```

---

## Communication Log

Track all dispute communications:

```json
{
  "communications": [
    {
      "date": "2026-03-27T10:00:00Z",
      "direction": "incoming",
      "message": "Item arrived with cracked corner",
      "attachments": ["photo1.jpg"]
    },
    {
      "date": "2026-03-27T11:00:00Z",
      "direction": "outgoing",
      "message": "So sorry about that! Happy to offer $30 partial refund...",
      "attachments": []
    }
  ]
}
```

---

## Feedback Amendment

If dispute resolved positively:
1. Ask buyer to update feedback (if platform allows)
2. Track whether they did
3. If they update: dispute → resolved_positive

**Request Template:**

```
Hi {buyer_username},

I'm glad we could resolve the issue with the {item_name}.

If you feel the situation was handled fairly, would you mind
updating your feedback? It really helps other buyers trust me.

{feedback_edit_instructions_for_platform}

Thanks for working with me on this!
```

---

**AI Help (Alpha):**
- Response templates for common issues
- Resolution suggestions based on dispute type
- Communication drafts

**AI Help (Beta):**
- Sentiment analysis of buyer messages
- Recommended resolution based on past outcomes
- Risk assessment for future transactions with buyer

**Transitions:**
- → COMPLETE (Phase 9): If resolved (positive/neutral)
- Remains in DISPUTE: If unresolved

**UI Notes:**
- **Active Disputes**: All open issues requiring attention
- **Communication Timeline**: Full conversation thread
- **Resolution Actions**: Refund, replace, etc.
- **Outcome Tracking**: What worked, what didn't
- **Priority Indicators**: Urgent disputes highlighted

---

## Marketplace Support

### Alpha
| Platform | Ingestion | Posting | Notes |
|----------|-----------|---------|-------|
| Reddit | ✅ Email webhook, post parser | Manual | Primary focus |
| OfferUp | Manual | Manual | |
| Craigslist | Manual | Manual | |
| eBay | Manual | Manual | |
| Other | Manual | Manual | Generic support |

### Beta
| Platform | Ingestion | Posting | Notes |
|----------|-----------|---------|-------|
| Reddit | ✅ Enhanced | AI templates | |
| OfferUp | Link parser | AI templates | [Research needed] |
| eBay | Link/API | AI templates | [Research needed] |
| Swappa | Link parser | AI templates | [Research needed] |
| Facebook | Manual | AI templates | [Research needed] |
| Mercari | [TBD] | [TBD] | [Research needed] |

---

## UI Requirements

### Alpha

**Funnel Dashboard**
- Visual representation of items by phase
- Count badges per phase
- Click to filter/view items in that phase
- Items needing action highlighted

**Quick Actions**
- One-click phase transitions
- Smart defaults for required fields
- Bulk operations where sensible

**Phase-Specific Views**
- Each phase has appropriate columns/fields shown
- Relevant actions for that phase
- [TBD: specific layouts]

### Beta
- [TBD: Advanced features]

---

## Database Changes Required

### Alpha

**New: ValueFactor Model:**
```python
class ValueFactor(Base):
    __tablename__ = "value_factors"

    id: Integer, primary_key
    name: String(100), unique, required      # "Tariff Premium"
    description: Text                         # Why this factor exists
    multiplier: Decimal, default 1.0          # 1.2 = 20% boost
    active: Boolean, default True             # Currently applied?
    created_at: DateTime
    updated_at: DateTime
```

**New: ItemValueFactor Junction Table:**
```python
class ItemValueFactor(Base):
    __tablename__ = "item_value_factors"

    item_id: FK → items
    value_factor_id: FK → value_factors
    applied_at: DateTime
```

**New: ItemImage Model:**
```python
class ItemImage(Base):
    __tablename__ = "item_images"

    id: Integer, primary_key
    item_id: FK → items
    url: String(500), required                # Path or URL
    image_type: Enum                          # physical, specs, performance, receipt, other
    caption: String(255)                      # Optional description
    created_at: DateTime
```

**New: Tag Model:**
```python
class Tag(Base):
    __tablename__ = "tags"

    id: Integer, primary_key
    name: String(100), unique, required
    color: String(7)                          # Hex color for UI
    created_at: DateTime
```

**New: ItemTag Junction Table:**
```python
class ItemTag(Base):
    __tablename__ = "item_tags"

    item_id: FK → items
    tag_id: FK → tags
```

**New: Category Model:**
```python
class Category(Base):
    __tablename__ = "categories"

    id: Integer, primary_key
    name: String(100), unique, required       # "homelab"
    display_name: String(100)                 # "Homelab"
    description: Text
    icon: String(50)                          # Icon name for UI
    sort_order: Integer, default 0
```

**Item Model Changes:**
```
MODIFY status: Enum → (inventory, draft, listed, sold, archived)
ADD    category_id: FK → categories (replace string category)
ADD    location: String(255)
ADD    acquisition_source: String(255)
ADD    acquisition_condition: Enum (new, used)
ADD    acquisition_date: Date
REMOVE images: JSON array (replaced by ItemImage relation)
```

**Lead Model Additions:**
```
+ agreed_price: Decimal
+ payment_method: String
[Multi-item support via junction table]
```

**New: LeadItem Junction Table:**
```python
class LeadItem(Base):
    __tablename__ = "lead_items"

    lead_id: FK → leads
    item_id: FK → items
    created_at: DateTime
```

**Sale Model Additions:**
```
+ status: Enum (pending, shipped, delivered, complete)
```

### Beta
- [TBD based on beta feature definitions]

---

## Open Questions / Research Needed

### Platform Integration
- [ ] OfferUp: Can we parse listing URLs? API available?
- [ ] eBay: API access for tracking? Listing import?
- [ ] Swappa: Link parsing possible?
- [ ] Facebook Marketplace: Any automation possible?

### Shipping
- [ ] USPS API: Requirements and costs?
- [ ] UPS API: Requirements and costs?
- [ ] FedEx API: Requirements and costs?
- [ ] Label generation: Integrate with Pirate Ship? ShipStation?

### AI Enhancements
- [ ] Response generation: What context needed?
- [ ] Scam detection: What patterns to look for?
- [ ] Photo analysis: Useful for inventory?

### Other
- [ ] Mobile experience: PWA sufficient or native app?
- [ ] Multi-user: Needed? How to handle?
- [ ] Analytics: What metrics matter most?

---

## Implementation Plan

### Step 1: Finalize Phase Requirements
Go through each phase and confirm:
- All required fields identified
- Transitions defined
- AI help opportunities noted
- Alpha vs Beta scope clear

### Step 2: Database Schema Design
- Design schema changes for Alpha
- Plan migration strategy
- Consider Beta needs in design

### Step 3: Backend Implementation (Alpha)
- Model updates
- API endpoints for phase transitions
- Business logic for workflows

### Step 4: Frontend Implementation (Alpha)
- Funnel dashboard
- Phase-specific views
- Quick action components

### Step 5: Testing & Refinement
- End-to-end workflow testing
- User feedback incorporation
- Bug fixes

### Step 6: Beta Planning
- Prioritize Beta features
- Research open questions
- Design integrations

---

## Next Steps

1. **Review Phase 1 (Inventory)** - Define exactly how we want it to work
2. **Review remaining phases** - Confirm requirements for each
3. **Design database schema** - All Alpha changes
4. **Create implementation tickets** - Break into manageable tasks
5. **Build Alpha** - Iterative development
6. **Test and refine** - Real-world usage

---

*Document created: 2026-03-26*
*Status: DRAFT - Pending phase-by-phase review*
