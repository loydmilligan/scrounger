# Scrounger Implementation Plan

## Release Strategy

### Alpha (MVP)
**Goal:** Usable system with complete funnel, basic functionality at each phase.

**Target:** Core workflow works end-to-end. Can track items from inventory through sale completion.

### Beta (Full Featured)
**Goal:** Enhanced system with automation, deep integrations, and advanced AI.

**Target:** Streamlined workflow with minimal manual effort. Learning from data.

---

## Alpha vs Beta Feature Split

### Phase 1: INVENTORY

| Feature | Alpha | Beta |
|---------|-------|------|
| Basic item CRUD | ✅ | ✅ |
| Categories (predefined) | ✅ | ✅ |
| Categories (custom) | ❌ | ✅ |
| Tags | ✅ | ✅ |
| Value Factors | ✅ | ✅ |
| Image upload (basic) | ✅ | ✅ |
| Image types (physical, specs, etc.) | ✅ | ✅ |
| Location tracking | ✅ | ✅ |
| Acquisition tracking | ✅ | ✅ |
| AI price check | ✅ | ✅ |
| AI photo analysis | ❌ | ✅ |
| Depreciation warnings | ❌ | ✅ |

### Phase 2: DRAFT

| Feature | Alpha | Beta |
|---------|-------|------|
| Pricing (base, min) | ✅ | ✅ |
| Platform-specific pricing | ✅ | ✅ |
| Fee calculator | ✅ | ✅ |
| Ready-to-list checklist | ✅ | ✅ |
| Bundle creation | ✅ | ✅ |
| Draft post storage | ✅ | ✅ |
| AI post generation | ✅ | ✅ |
| AI title generation | ✅ | ✅ |
| Marketplace rules storage | ✅ | ✅ |
| AI prompt templates | ✅ | ✅ |
| Price research (basic) | ✅ | ✅ |
| Price research (with links) | ❌ | ✅ |
| Photo enhancement tips | ❌ | ✅ |
| SEO optimization | ❌ | ✅ |

### Phase 3: LISTED

| Feature | Alpha | Beta |
|---------|-------|------|
| Listing URL storage | ✅ | ✅ |
| Multi-platform listings | ✅ | ✅ |
| Bump reminders | ✅ | ✅ |
| Bump automation | ❌ | ✅ |
| Response tracking | ✅ | ✅ |
| Price history | ✅ | ✅ |
| Price adjustment suggestions | ❌ | ✅ |
| Cross-post scheduling | ❌ | ✅ |
| View tracking (if available) | ❌ | ✅ |
| Global Action List | ✅ | ✅ |
| Action auto-generation | ✅ | ✅ |

### Phase 4: INTEREST

| Feature | Alpha | Beta |
|---------|-------|------|
| Lead tracking | ✅ | ✅ |
| Interest levels | ✅ | ✅ |
| Multi-item leads | ✅ | ✅ |
| Message tracking | ✅ | ✅ |
| Required review actions | ✅ | ✅ |
| Response attachments | ✅ | ✅ |
| Bundle offer builder | ✅ | ✅ |
| Reddit auto-import | ✅ | ✅ |
| AI response suggestions | ✅ (basic) | ✅ (learned) |
| AI scam detection | ❌ | ✅ |
| Response analytics | ❌ | ✅ |
| OfferUp/eBay import | ❌ | ✅ |

### Phase 5: AGREEMENT

| Feature | Alpha | Beta |
|---------|-------|------|
| Shipped vs Local types | ✅ | ✅ |
| Invoice workflow | ✅ | ✅ |
| Meetup planning | ✅ | ✅ |
| Escalating visibility | ✅ | ✅ |
| Follow-up reminders | ✅ | ✅ |
| Safe meetup locations | ✅ | ✅ |
| AI shipping estimation | ✅ | ✅ |
| PayPal invoice generation | ❌ | ✅ |

### Phase 6: PAID

| Feature | Alpha | Beta |
|---------|-------|------|
| Sale record creation | ✅ | ✅ |
| Fee tracking | ✅ | ✅ |
| Profit calculation | ✅ | ✅ |
| Shipping task checklist | ✅ | ✅ |
| Packing list (bundles) | ✅ | ✅ |
| Carrier options | ✅ | ✅ |
| AI shipping recommendations | ✅ | ✅ |
| Label price comparison | ❌ | ✅ |
| Pirate Ship integration | ❌ | ✅ |

### Phase 7: SHIPPED

| Feature | Alpha | Beta |
|---------|-------|------|
| Tracking number storage | ✅ | ✅ |
| Tracking URL generation | ✅ | ✅ |
| Buyer message template | ✅ | ✅ |
| Manual tracking check | ✅ | ✅ |
| Auto tracking updates | ❌ | ✅ |
| Delivery notifications | ❌ | ✅ |

### Phase 8: DELIVERED

| Feature | Alpha | Beta |
|---------|-------|------|
| Delivery confirmation | ✅ | ✅ |
| Feedback timer system | ✅ | ✅ |
| Per-marketplace timers | ✅ | ✅ |
| Feedback request messages | ✅ | ✅ |
| Chaser tasks | ✅ | ✅ |
| Auto-delivery detection | ❌ | ✅ |

### Phase 9: COMPLETE

| Feature | Alpha | Beta |
|---------|-------|------|
| Completion tracking | ✅ | ✅ |
| Feedback tracking | ✅ | ✅ |
| Item archival | ✅ | ✅ |
| Profit summary | ✅ | ✅ |
| Analytics capture | ✅ | ✅ |
| Lessons learned AI | ❌ | ✅ |
| Buyer relationship tracking | ❌ | ✅ |

### Phase 10: DISPUTE

| Feature | Alpha | Beta |
|---------|-------|------|
| Dispute tracking | ✅ | ✅ |
| Resolution workflow | ✅ | ✅ |
| Refund tracking | ✅ | ✅ |
| Communication log | ✅ | ✅ |
| Feedback amendment | ✅ | ✅ |
| AI response templates | ✅ | ✅ |
| Sentiment analysis | ❌ | ✅ |

### Cross-Cutting

| Feature | Alpha | Beta |
|---------|-------|------|
| Dashboard with funnel view | ✅ | ✅ |
| Action list widget | ✅ | ✅ |
| Quick phase transitions | ✅ | ✅ |
| Marketplace configuration | ✅ | ✅ |
| CSV import/export | ✅ | ✅ |
| Mobile responsive | ✅ | ✅ |
| PWA support | ❌ | ✅ |
| Analytics dashboard | ❌ | ✅ |
| Multi-user support | ❌ | ✅ |

---

## Alpha Implementation Tasks

### Phase A1: Database & Models
*Foundation work - no UI changes yet*

- [ ] **A1.1** Create migration for new tables
  - categories, tags, value_factors, item_images, etc.
- [ ] **A1.2** Create new SQLAlchemy models
  - All models from SCHEMA.md
- [ ] **A1.3** Update existing models (Item, Lead, Sale)
  - Add new fields, modify enums
- [ ] **A1.4** Create seed data
  - Categories, default marketplaces, config
- [ ] **A1.5** Test database migrations
  - Ensure existing data preserved

### Phase A2: Core API Updates
*Backend endpoints for new functionality*

- [ ] **A2.1** Category CRUD API
- [ ] **A2.2** Tag CRUD API
- [ ] **A2.3** Value Factor CRUD API
- [ ] **A2.4** Item Image API (upload, list, delete)
- [ ] **A2.5** Update Item API for new fields
- [ ] **A2.6** Marketplace CRUD API
- [ ] **A2.7** Marketplace Rules API
- [ ] **A2.8** Marketplace AI Prompts API
- [ ] **A2.9** Config API

### Phase A3: Lead System Updates
*Multi-item leads and message tracking*

- [ ] **A3.1** Lead-Item junction API
- [ ] **A3.2** LeadMessage CRUD API
- [ ] **A3.3** Message attachment handling
- [ ] **A3.4** Review action workflow
- [ ] **A3.5** Update Reddit webhook for new message model
- [ ] **A3.6** Interest level tracking

### Phase A4: Sale & Shipping Updates
*Complete sale workflow*

- [ ] **A4.1** Update Sale model and API
- [ ] **A4.2** Sale-Item junction for bundles
- [ ] **A4.3** Tracking URL generation
- [ ] **A4.4** Shipping task checklist API
- [ ] **A4.5** Fee and profit calculation

### Phase A5: Feedback & Dispute System
*Post-delivery workflow*

- [ ] **A5.1** Feedback timer system
- [ ] **A5.2** Dispute CRUD API
- [ ] **A5.3** Resolution workflow
- [ ] **A5.4** Generated message templates

### Phase A6: Action System
*Global task management*

- [ ] **A6.1** Action model and CRUD
- [ ] **A6.2** Action generation rules
- [ ] **A6.3** Action priority calculation
- [ ] **A6.4** Action completion/dismissal

### Phase A7: Frontend - Dashboard
*New funnel dashboard*

- [ ] **A7.1** Funnel visualization component
- [ ] **A7.2** Phase count badges
- [ ] **A7.3** Action list widget
- [ ] **A7.4** Quick stats cards
- [ ] **A7.5** Recent activity feed

### Phase A8: Frontend - Item Management
*Updated item forms and views*

- [ ] **A8.1** Category selector
- [ ] **A8.2** Tag manager
- [ ] **A8.3** Value factor assignment
- [ ] **A8.4** Image upload with types
- [ ] **A8.5** Location field
- [ ] **A8.6** Acquisition fields
- [ ] **A8.7** Quick-add form
- [ ] **A8.8** Status filter by phase

### Phase A9: Frontend - Draft & Listing
*Listing preparation workflow*

- [ ] **A9.1** Platform pricing table
- [ ] **A9.2** Ready checklist UI
- [ ] **A9.3** Bundle builder
- [ ] **A9.4** Draft post editor
- [ ] **A9.5** Post generation with marketplace rules
- [ ] **A9.6** Copy to clipboard
- [ ] **A9.7** Listing URL entry
- [ ] **A9.8** Bump reminder display

### Phase A10: Frontend - Leads
*Lead management updates*

- [ ] **A10.1** Lead inbox view
- [ ] **A10.2** Interest level badges
- [ ] **A10.3** Message thread view
- [ ] **A10.4** Review action modal (respond/ignore/snooze)
- [ ] **A10.5** Bundle offer builder
- [ ] **A10.6** Response attachment upload
- [ ] **A10.7** Multi-item lead display

### Phase A11: Frontend - Agreement & Sale
*Deal and payment workflow*

- [ ] **A11.1** Transaction type selector (ship/local)
- [ ] **A11.2** Invoice workflow UI
- [ ] **A11.3** Meetup planner UI
- [ ] **A11.4** Escalation indicators
- [ ] **A11.5** Sale creation flow
- [ ] **A11.6** Packing list display
- [ ] **A11.7** Shipping entry form
- [ ] **A11.8** Fee entry and profit preview

### Phase A12: Frontend - Post-Sale
*Shipping, delivery, feedback*

- [ ] **A12.1** In-transit list
- [ ] **A12.2** Tracking link display
- [ ] **A12.3** Delivery confirmation
- [ ] **A12.4** Feedback timer display
- [ ] **A12.5** Feedback request generator
- [ ] **A12.6** Completion flow
- [ ] **A12.7** Dispute creation
- [ ] **A12.8** Dispute resolution UI

### Phase A13: Frontend - Settings
*Configuration screens*

- [ ] **A13.1** Marketplace management
- [ ] **A13.2** Marketplace rules editor
- [ ] **A13.3** AI prompt templates editor
- [ ] **A13.4** Value factors management
- [ ] **A13.5** Timer configuration
- [ ] **A13.6** Safe meetup locations

### Phase A14: Testing & Polish
*Quality assurance*

- [ ] **A14.1** End-to-end workflow testing
- [ ] **A14.2** Data migration testing
- [ ] **A14.3** Error handling review
- [ ] **A14.4** UI polish and consistency
- [ ] **A14.5** Documentation update

---

## Implementation Order (Recommended)

### Sprint 1: Foundation
- A1.1 - A1.5 (Database)
- A2.1 - A2.4 (Core APIs)
- A7.1 - A7.2 (Dashboard shell)

### Sprint 2: Item Management
- A2.5 (Item API)
- A8.1 - A8.8 (Item UI)
- A7.3 - A7.5 (Dashboard widgets)

### Sprint 3: Marketplace & Listings
- A2.6 - A2.9 (Marketplace APIs)
- A9.1 - A9.8 (Draft/Listing UI)
- A13.1 - A13.3 (Settings)

### Sprint 4: Leads
- A3.1 - A3.6 (Lead APIs)
- A10.1 - A10.7 (Lead UI)

### Sprint 5: Agreement & Sale
- A4.1 - A4.5 (Sale APIs)
- A11.1 - A11.8 (Agreement/Sale UI)

### Sprint 6: Post-Sale
- A5.1 - A5.4 (Feedback/Dispute APIs)
- A12.1 - A12.8 (Post-sale UI)

### Sprint 7: Actions & Polish
- A6.1 - A6.4 (Action system)
- A13.4 - A13.6 (Remaining settings)
- A14.1 - A14.5 (Testing)

---

## Beta Features (Future)

### Automation
- [ ] Carrier tracking API integration
- [ ] Auto-delivery detection
- [ ] Auto-bump where allowed
- [ ] PayPal invoice API

### AI Enhancements
- [ ] Response effectiveness learning
- [ ] Price research with real links
- [ ] Scam detection
- [ ] Photo analysis
- [ ] Sentiment analysis

### Platform Integrations
- [ ] OfferUp link parsing
- [ ] eBay API integration
- [ ] Swappa integration

### Advanced Features
- [ ] Analytics dashboard
- [ ] Multi-user support
- [ ] PWA/mobile app
- [ ] Label generation (Pirate Ship)

---

## Getting Started

To begin Alpha development:

1. **Review PLANNING.md** - Full phase specifications
2. **Review SCHEMA.md** - Database schema
3. **Start with Sprint 1** - Foundation work
4. **Test incrementally** - Each sprint should be usable

---

*Document created: 2026-03-26*
*Status: Ready for implementation*
