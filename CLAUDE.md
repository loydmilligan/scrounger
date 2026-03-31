# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Scrounger is a personal sales management system for tracking items through the complete secondary market sales lifecycle. It manages inventory across multiple marketplaces (Reddit, OfferUp, eBay, Craigslist, Swappa) from acquisition through sale completion.

The system implements a 10-phase sales funnel: INVENTORY → DRAFT → LISTED → INTEREST → AGREEMENT → PAID → SHIPPED → DELIVERED → COMPLETE (with DISPUTE as an alternate path).

## Tech Stack

- **Frontend:** React 18 + TypeScript, Vite, TailwindCSS, Radix UI
- **Backend:** FastAPI (Python), SQLAlchemy 2.0, Pydantic 2.x
- **Database:** SQLite (dev), PostgreSQL (prod), Alembic migrations
- **AI:** OpenRouter API (Claude 3.5 Sonnet default, DeepSeek fallback)

## Commands

### Frontend (from `/frontend`)
```bash
npm run dev       # Start dev server
npm run build     # Production build
npm run preview   # Preview production build
```

### Backend (from `/backend`)
```bash
uvicorn src.main:app --reload    # Start dev server with hot reload
alembic upgrade head             # Apply database migrations
alembic downgrade -1             # Rollback last migration
```

## Architecture

### Backend Structure
- `src/models/` - SQLAlchemy models (Item, Lead, Sale, Dispute, Category, Tag, etc.)
- `src/schemas/` - Pydantic request/response validation
- `src/api/` - FastAPI route handlers
- `src/config.py` - Settings loaded from `.env` (database URL, OpenRouter API key)
- `src/database.py` - SQLAlchemy session management, auto-creates tables on startup

### Key Models and Relationships
- **Item** - Core entity, progresses through phases via `status` field
- **Lead** - Buyer inquiries, supports multi-item leads via `lead_items` junction
- **Sale** - Completed transactions, supports bundles via `sale_items` junction
- **Action** - Auto-generated tasks based on workflow triggers
- **Marketplace** - Platform configuration with associated rules and AI prompts

### Frontend Structure
- `src/components/` - Reusable React components
- `src/pages/` - Page-level components
- `src/utils/` - Utility functions and API client

## Database

SQLite database stored at `backend/data/scrounger.db` in development. Models use junction tables for many-to-many relationships: `item_tags`, `item_value_factors`, `lead_items`, `sale_items`.

## External Integrations

- **n8n workflows** (`/n8n`) - Reddit message import automation
- **OpenRouter** - AI-powered post generation, price research, response suggestions
- **Supabase** (`/supabase`) - Production database hosting
