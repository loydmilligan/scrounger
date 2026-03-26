# Scrounger Roadmap & Planning Document

## Vision
A comprehensive secondary sales tracking system that manages items through the complete sales funnel - from inventory through listing, negotiation, sale, shipping, delivery, and feedback - across multiple marketplaces.

---

## Supported Platforms

### Current
- Reddit (r/hardwareswap, r/homelabsales)
- OfferUp
- Craigslist (manual)

### Planned
- eBay
- Swappa
- Facebook Marketplace
- Mercari

### Architecture Note
Platform support is extensible via the `platforms` field on Items and `platform` field on Leads/Sales.

---

## Sales Funnel Phases

### Phase 1: INVENTORY
**Status:** `inventory` (NEW - not yet implemented)
**Description:** Items we own that we may want to sell eventually, but are not actively listing.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Store items | Uses `draft` status | Add dedicated `inventory` status |
| Track cost basis | ✅ Exists | - |
| Track condition | ✅ Exists | - |
| Bulk import | ✅ CSV import | - |
| Quick entry | Partial | Quick-add form for rapid entry |

**Required Fields:**
- Name, Category, Condition
- Cost basis (what we paid)
- Quantity (NEW - for multiple identical items)
- Storage location (NEW - where is it physically)
- Acquisition date (NEW - when we got it)
- Notes

---

### Phase 2: DRAFT
**Status:** `draft`
**Description:** Items we've decided to sell and are preparing listings for.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Draft items | ✅ Exists | - |
| Set pricing | ✅ asking_price, min_price | - |
| AI price check | ✅ Exists | - |
| AI post generation | ✅ Exists | Platform templates |
| Images | ✅ Exists | Image upload UI improvement |
| Multi-platform prep | ✅ platforms array | - |

**Required Fields:**
- All from Phase 1, plus:
- Asking price
- Minimum acceptable price
- Target platforms
- Images
- Post content (generated or manual)

---

### Phase 3: LISTED
**Status:** `listed`
**Description:** Items actively listed for sale on one or more platforms.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Mark as listed | ✅ Exists | - |
| Track listed_at | ✅ Exists | - |
| Track where listed | ✅ platforms array | Per-platform listing URLs (NEW) |
| Post expiration | ❌ | Add expiration/refresh dates |
| Bump/refresh reminders | ❌ | Add notification system |

**Required Fields:**
- All from Phase 2, plus:
- Listed date (auto-set)
- Listing URLs per platform (NEW)
- Expiration dates per platform (NEW)

---

### Phase 4: INTEREST (Leads)
**Status:** Item `listed`, Lead `new` → `contacted` → `negotiating`
**Description:** Someone has expressed interest in buying.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Lead tracking | ✅ Exists | - |
| Auto-create from Reddit email | ✅ Via n8n webhook | - |
| Import from Reddit post | ✅ Exists | - |
| Multi-item leads | ❌ | Add lead_items junction table |
| Track conversations | ✅ Via notes | Structured message history |
| AI response generation | ❌ | Add response templates |

**Required Fields:**
- Username, Platform, Contact method
- Offered price
- Conversation history
- Response deadline (NEW - for time-sensitive offers)

---

### Phase 5: AGREEMENT
**Status:** Lead `agreed`
**Description:** Buyer and seller have agreed on terms, waiting for payment.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Mark as agreed | ✅ Exists | - |
| Track agreed price | Partial (offered_price) | Explicit agreed_price field |
| Payment method | ❌ | Add expected payment method |
| Payment deadline | ❌ | Add deadline tracking |
| Invoice generation | ❌ | PayPal/Venmo link generator |

**Required Fields:**
- Agreed price
- Payment method (PayPal, Venmo, Zelle, etc.)
- Payment deadline
- Shipping estimate
- Buyer shipping address (NEW)

---

### Phase 6: PAID
**Status:** Lead `sold`, Sale created with no shipped_date
**Description:** Payment received, item needs to be shipped.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Record sale | ✅ Exists | - |
| Track payment | ✅ sale_price | - |
| Track fees | ✅ platform_fees, payment_fees | - |
| Calculate profit | ✅ Exists | - |
| Shipping estimation | ✅ AI shipping help | - |
| Label generation | ❌ | Integration with shipping APIs |

**Required Fields:**
- Sale price
- Payment date (NEW - distinct from sale_date)
- Payment confirmation (NEW - transaction ID)
- Platform fees
- Payment fees
- Buyer address

---

### Phase 7: SHIPPED
**Status:** Sale with shipped_date, no delivered_date
**Description:** Item has been shipped, in transit.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Record shipping | ✅ shipped_date, carrier | - |
| Tracking number | ✅ Exists | - |
| Track shipping cost | ✅ Exists | - |
| Tracking status | ❌ | Auto-fetch from carrier API |
| Delivery estimate | ❌ | Pull from tracking |

**Required Fields:**
- Carrier
- Tracking number
- Shipping cost
- Shipped date
- Estimated delivery (NEW)

---

### Phase 8: DELIVERED
**Status:** Sale with delivered_date set
**Description:** Item delivered, awaiting feedback completion.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Mark delivered | ✅ delivered_date | - |
| Auto-detect delivery | ❌ | Carrier API integration |
| Buyer confirmation | ❌ | Track buyer acknowledgment |
| Feedback reminder | ❌ | Notification to leave/request feedback |

**Required Fields:**
- Delivered date
- Delivery confirmation
- Buyer satisfaction (NEW)

---

### Phase 9: COMPLETE
**Status:** Sale marked as `complete` (NEW status)
**Description:** Transaction fully complete with feedback exchanged.

| Aspect | Current State | Needed |
|--------|--------------|--------|
| Feedback tracking | ❌ | Add feedback_given, feedback_received fields |
| Archive item | ✅ `archived` status | - |
| Transaction summary | Partial | Full transaction report |

**Required Fields:**
- Feedback given (boolean + link)
- Feedback received (boolean + text)
- Final notes
- Transaction complete date

---

## Current State Summary

### What We Have ✅

1. **Item Management**
   - Full CRUD with draft/listed/sold/archived statuses
   - Pricing (asking, min, cost basis)
   - Multi-platform support
   - Category and condition tracking
   - Image support
   - CSV import/export

2. **Lead Management**
   - Full CRUD with status flow (new → contacted → negotiating → agreed → sold → dead)
   - Reddit email auto-ingestion via n8n
   - Reddit post comment import
   - Contact tracking

3. **Sale Management**
   - Link to items and leads
   - Full shipping tracking (carrier, tracking, dates)
   - Fee tracking (platform, payment)
   - Profit calculation

4. **AI Assistance**
   - Post generation (Reddit-formatted)
   - Price checking
   - Shipping estimation
   - Bundle parsing
   - General chat

5. **Export/Integration**
   - CSV export for items, leads, sales
   - ICS calendar for follow-ups
   - n8n webhook for Reddit emails

### What's Missing ❌

1. **Inventory Phase**
   - Dedicated inventory status
   - Quantity tracking
   - Storage location
   - Acquisition date

2. **Listing Management**
   - Per-platform listing URLs
   - Expiration/refresh tracking
   - Bump reminders

3. **Multi-Item Leads**
   - Junction table for leads → multiple items
   - Bundle deal tracking

4. **Agreement Phase**
   - Explicit agreed price
   - Payment deadline
   - Buyer address storage

5. **Payment Tracking**
   - Payment confirmation
   - Transaction ID storage

6. **Shipping Automation**
   - Carrier API integration (USPS, UPS, FedEx)
   - Auto-tracking updates
   - Label generation

7. **Feedback Loop**
   - Feedback tracking
   - Completion status

8. **UI Improvements**
   - Funnel view showing items by phase
   - Quick phase transitions
   - Dashboard showing items needing action

---

## Goals Checklist

| # | Goal | Status | Notes |
|---|------|--------|-------|
| 1 | Track items through all statuses | 🟡 Partial | Need inventory, shipped, delivered, complete |
| 2 | Easy ingestion via link paste | 🟡 Partial | Reddit posts work, need OfferUp/CL |
| 3 | View all items with funnel state | 🟡 Partial | Need dedicated funnel view |
| 4 | Swift phase transitions | 🟡 Partial | Need quick-action buttons |
| 5 | Inventory tracking | ❌ Missing | Need dedicated inventory phase |
| 6 | AI post generation per platform | 🟡 Partial | Reddit works, need templates for others |
| 7 | Phase-specific help | 🟡 Partial | Need contextual guidance per phase |

---

## Implementation Priority

### P0: Core Funnel (Must Have)
1. Add inventory status and fields
2. Add funnel dashboard view
3. Quick phase transition actions
4. Multi-item lead support

### P1: Automation (High Value)
5. More platform ingestion (OfferUp, eBay links)
6. Carrier tracking API integration
7. Payment confirmation tracking

### P2: Enhancement (Nice to Have)
8. Listing URL and expiration tracking
9. Feedback tracking
10. AI response templates for leads
11. Label generation integration

### P3: Future
12. Mobile app / PWA
13. Analytics and reporting
14. Multi-user support

---

## Next Steps

1. Review this document and confirm priorities
2. Brainstorm each phase in detail
3. Design database schema changes
4. Plan UI changes
5. Implement in priority order

---

*Document created: 2026-03-26*
*Last updated: 2026-03-26*
