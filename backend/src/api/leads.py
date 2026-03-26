from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import re
import httpx

from ..database import get_db
from ..models import Lead, Item
from ..schemas import LeadCreate, LeadUpdate, LeadResponse, LeadList, RedditImport

router = APIRouter()


@router.get("", response_model=LeadList)
def list_leads(
    item_id: Optional[int] = None,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Lead)

    if item_id:
        query = query.filter(Lead.item_id == item_id)
    if status:
        query = query.filter(Lead.status == status)
    if platform:
        query = query.filter(Lead.platform == platform)

    query = query.order_by(Lead.updated_at.desc())

    total = query.count()
    leads = query.offset(skip).limit(limit).all()

    result_leads = []
    for lead in leads:
        item = db.query(Item).filter(Item.id == lead.item_id).first()
        result_leads.append(LeadResponse(
            id=lead.id,
            item_id=lead.item_id,
            username=lead.username,
            platform=lead.platform,
            contact_method=lead.contact_method,
            contact_info=lead.contact_info,
            status=lead.status,
            offered_price=lead.offered_price,
            notes=lead.notes,
            source=lead.source,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
            last_contact_at=lead.last_contact_at,
            item_name=item.name if item else None
        ))

    return LeadList(leads=result_leads, total=total)


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    item = db.query(Item).filter(Item.id == lead.item_id).first()
    return LeadResponse(
        id=lead.id,
        item_id=lead.item_id,
        username=lead.username,
        platform=lead.platform,
        contact_method=lead.contact_method,
        contact_info=lead.contact_info,
        status=lead.status,
        offered_price=lead.offered_price,
        notes=lead.notes,
        source=lead.source,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        last_contact_at=lead.last_contact_at,
        item_name=item.name if item else None
    )


@router.post("", response_model=LeadResponse)
def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    # Verify item exists
    item = db.query(Item).filter(Item.id == lead_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    lead = Lead(**lead_data.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)

    return LeadResponse(
        id=lead.id,
        item_id=lead.item_id,
        username=lead.username,
        platform=lead.platform,
        contact_method=lead.contact_method,
        contact_info=lead.contact_info,
        status=lead.status,
        offered_price=lead.offered_price,
        notes=lead.notes,
        source=lead.source,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        last_contact_at=lead.last_contact_at,
        item_name=item.name
    )


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, lead_data: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lead, key, value)

    db.commit()
    db.refresh(lead)

    item = db.query(Item).filter(Item.id == lead.item_id).first()
    return LeadResponse(
        id=lead.id,
        item_id=lead.item_id,
        username=lead.username,
        platform=lead.platform,
        contact_method=lead.contact_method,
        contact_info=lead.contact_info,
        status=lead.status,
        offered_price=lead.offered_price,
        notes=lead.notes,
        source=lead.source,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        last_contact_at=lead.last_contact_at,
        item_name=item.name if item else None
    )


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()
    return {"message": "Lead deleted successfully"}


@router.post("/import-reddit")
async def import_from_reddit(data: RedditImport, db: Session = Depends(get_db)):
    """Import leads from a Reddit post URL by extracting commenters."""

    # Verify item exists
    item = db.query(Item).filter(Item.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Parse Reddit URL to get JSON endpoint
    url = data.url.rstrip("/")
    if not url.endswith(".json"):
        url += ".json"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"User-Agent": "Scrounger/1.0"},
                follow_redirects=True,
                timeout=30.0
            )
            response.raise_for_status()
            json_data = response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch Reddit post: {str(e)}")

    # Extract usernames from comments
    usernames = set()

    def extract_authors(data):
        if isinstance(data, dict):
            if "author" in data and data.get("author") not in ["[deleted]", "AutoModerator", None]:
                usernames.add(data["author"])
            for value in data.values():
                extract_authors(value)
        elif isinstance(data, list):
            for item in data:
                extract_authors(item)

    extract_authors(json_data)

    # Get existing leads for this item to avoid duplicates
    existing = db.query(Lead.username).filter(
        Lead.item_id == data.item_id,
        Lead.platform == "reddit"
    ).all()
    existing_usernames = {e.username for e in existing}

    # Create leads for new usernames
    created = 0
    skipped = 0
    for username in usernames:
        if username in existing_usernames:
            skipped += 1
            continue

        lead = Lead(
            item_id=data.item_id,
            username=username,
            platform="reddit",
            contact_method="reddit_dm",
            status="new",
            source=data.url
        )
        db.add(lead)
        created += 1

    db.commit()

    return {
        "success": True,
        "created": created,
        "skipped": skipped,
        "total_found": len(usernames)
    }
