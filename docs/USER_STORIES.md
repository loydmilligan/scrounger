# Scrounger - User Stories & Acceptance Criteria

## App Overview
Scrounger is a sales tracking application for managing secondary/resale items across platforms like Reddit (r/hardwareswap, r/homelabsales), OfferUp, Swappa, and eBay.

---

## Epic 1: Item Management

### US-1.1: Add New Item for Sale
**As a** seller
**I want to** add items to my inventory
**So that** I can track what I'm selling

**Acceptance Criteria:**
- [ ] Can enter item name, description, category, condition
- [ ] Can set asking price and minimum acceptable price
- [ ] Can upload/attach images
- [ ] Can specify which platforms to list on
- [ ] Can set item status (draft, listed, sold, archived)
- [ ] Item appears in inventory list after creation
- [ ] Form validates required fields before submission

### US-1.2: View and Filter Inventory
**As a** seller
**I want to** view my inventory with filtering options
**So that** I can quickly find specific items

**Acceptance Criteria:**
- [ ] Can see all items in a list/grid view
- [ ] Can filter by status (listed, sold, draft)
- [ ] Can filter by platform
- [ ] Can search by item name/description
- [ ] Can sort by date added, price, or status
- [ ] Visual indicators show item status clearly

### US-1.3: Edit Item Details
**As a** seller
**I want to** update item information
**So that** I can adjust prices or descriptions

**Acceptance Criteria:**
- [ ] Can edit all item fields
- [ ] Changes save successfully
- [ ] Can see edit history/last modified date

---

## Epic 2: Lead Management

### US-2.1: Manual Lead Entry
**As a** seller
**I want to** add potential buyers manually
**So that** I can track who's interested

**Acceptance Criteria:**
- [ ] Can enter buyer username/name
- [ ] Can associate lead with specific item(s)
- [ ] Can add contact method (Reddit DM, email, phone)
- [ ] Can set lead status (new, contacted, negotiating, sold, dead)
- [ ] Can add notes about the conversation

### US-2.2: Import Leads from Reddit Post
**As a** seller
**I want to** paste a Reddit post URL and extract interested users
**So that** I can quickly capture leads without manual entry

**Acceptance Criteria:**
- [ ] Can paste Reddit post URL
- [ ] System extracts usernames who commented
- [ ] Leads are associated with the related item
- [ ] Duplicate usernames are handled gracefully
- [ ] Can review and confirm before importing

### US-2.3: Track Lead Status
**As a** seller
**I want to** update lead status through the sales funnel
**So that** I know where each potential sale stands

**Acceptance Criteria:**
- [ ] Visual pipeline/kanban view of leads
- [ ] Can drag leads between status columns
- [ ] Can see lead details on click
- [ ] Shows time since last contact

---

## Epic 3: Sales Tracking

### US-3.1: Record a Sale
**As a** seller
**I want to** record when an item sells
**So that** I can track my sales history

**Acceptance Criteria:**
- [ ] Can mark item as sold
- [ ] Can record final sale price
- [ ] Can associate with a lead/buyer
- [ ] Can record platform sold on
- [ ] Can add shipping cost
- [ ] Calculates profit/loss automatically

### US-3.2: View Sales Dashboard
**As a** seller
**I want to** see sales statistics
**So that** I can understand my performance

**Acceptance Criteria:**
- [ ] Shows total sales amount
- [ ] Shows number of items sold
- [ ] Shows profit/loss summary
- [ ] Shows sales by platform breakdown
- [ ] Date range filtering available

---

## Epic 4: Data Import/Export

### US-4.1: CSV Export
**As a** seller
**I want to** export my data to CSV
**So that** I can use it in spreadsheets

**Acceptance Criteria:**
- [ ] Can export items to CSV
- [ ] Can export leads to CSV
- [ ] Can export sales history to CSV
- [ ] CSV includes all relevant fields
- [ ] Filename includes export date

### US-4.2: CSV Import
**As a** seller
**I want to** import data from CSV
**So that** I can bulk add items or migrate data

**Acceptance Criteria:**
- [ ] Can upload CSV file
- [ ] System validates CSV format
- [ ] Preview data before import
- [ ] Shows import success/error summary
- [ ] Template CSV available for download

### US-4.3: Google Calendar Export
**As a** seller
**I want to** export tasks to Google Calendar
**So that** I can track follow-ups and deadlines

**Acceptance Criteria:**
- [ ] Can export follow-up reminders as .ics file
- [ ] Events include item and lead details
- [ ] Can import .ics into Google Calendar

---

## Epic 5: AI Assistant

### US-5.1: Generate Sale Post
**As a** seller
**I want to** AI generate a listing post
**So that** I can create professional posts quickly

**Acceptance Criteria:**
- [ ] Can request post for specific item
- [ ] AI generates platform-appropriate format (Reddit, eBay, etc.)
- [ ] Includes item details, price, condition
- [ ] Can edit generated post before copying
- [ ] Follows r/hardwareswap format rules

### US-5.2: Price Research
**As a** seller
**I want to** AI find comparable prices
**So that** I can price items competitively

**Acceptance Criteria:**
- [ ] Can ask for price suggestions
- [ ] AI searches for similar items
- [ ] Shows price range and reasoning
- [ ] Can apply suggested price to item

### US-5.3: Shipping Label Help
**As a** seller
**I want to** AI help with shipping
**So that** I can estimate costs and create labels

**Acceptance Criteria:**
- [ ] Can input package dimensions/weight
- [ ] AI suggests shipping options
- [ ] Shows estimated costs by carrier
- [ ] Provides tips for cost savings

---

## Epic 6: Settings

### US-6.1: OpenRouter Configuration
**As a** user
**I want to** configure my OpenRouter API key
**So that** I can use AI features

**Acceptance Criteria:**
- [ ] Can enter/update API key
- [ ] Key is stored securely (not exposed in UI)
- [ ] Can test connection
- [ ] Can select default model
- [ ] Can manage favorite models
- [ ] Shows model capabilities (streaming, reasoning)

---

## Non-Functional Requirements

### NFR-1: Modern UI/UX
- Use color strategically to indicate status and priority
- Clear visual hierarchy guides user attention
- Responsive design works on mobile/tablet
- Dark mode support
- Loading states and feedback for all actions

### NFR-2: Performance
- Page load under 2 seconds
- Smooth animations and transitions
- Efficient data fetching with caching

### NFR-3: Accessibility
- Keyboard navigation support
- Screen reader compatible
- Sufficient color contrast
