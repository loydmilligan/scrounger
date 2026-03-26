from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import csv
import io
from icalendar import Calendar, Event, Todo
from dateutil import tz

from ..database import get_db
from ..models import Item, Lead, Sale

router = APIRouter()


@router.get("/items/csv")
def export_items_csv(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export items to CSV."""
    query = db.query(Item)
    if status:
        query = query.filter(Item.status == status)

    items = query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Name", "Description", "Category", "Condition",
        "Asking Price", "Min Price", "Cost Basis", "Status",
        "Platforms", "Notes", "Created At", "Listed At", "Sold At"
    ])

    for item in items:
        writer.writerow([
            item.id,
            item.name,
            item.description or "",
            item.category or "",
            item.condition or "",
            item.asking_price or "",
            item.min_price or "",
            item.cost_basis or "",
            item.status,
            ",".join(item.platforms or []),
            item.notes or "",
            item.created_at.isoformat() if item.created_at else "",
            item.listed_at.isoformat() if item.listed_at else "",
            item.sold_at.isoformat() if item.sold_at else ""
        ])

    output.seek(0)
    filename = f"scrounger_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/leads/csv")
def export_leads_csv(
    item_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export leads to CSV."""
    query = db.query(Lead)
    if item_id:
        query = query.filter(Lead.item_id == item_id)
    if status:
        query = query.filter(Lead.status == status)

    leads = query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Item ID", "Item Name", "Username", "Platform",
        "Contact Method", "Contact Info", "Status", "Offered Price",
        "Notes", "Source", "Created At", "Last Contact At"
    ])

    for lead in leads:
        item = db.query(Item).filter(Item.id == lead.item_id).first()
        writer.writerow([
            lead.id,
            lead.item_id,
            item.name if item else "",
            lead.username,
            lead.platform or "",
            lead.contact_method or "",
            lead.contact_info or "",
            lead.status,
            lead.offered_price or "",
            lead.notes or "",
            lead.source or "",
            lead.created_at.isoformat() if lead.created_at else "",
            lead.last_contact_at.isoformat() if lead.last_contact_at else ""
        ])

    output.seek(0)
    filename = f"scrounger_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/sales/csv")
def export_sales_csv(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Export sales to CSV."""
    query = db.query(Sale)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)

    sales = query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Item ID", "Item Name", "Sale Price", "Platform",
        "Buyer Username", "Shipping Cost", "Shipping Carrier",
        "Tracking Number", "Platform Fees", "Payment Fees",
        "Profit", "Sale Date", "Shipped Date", "Delivered Date", "Notes"
    ])

    for sale in sales:
        item = db.query(Item).filter(Item.id == sale.item_id).first()
        writer.writerow([
            sale.id,
            sale.item_id,
            item.name if item else "",
            sale.sale_price,
            sale.platform or "",
            sale.buyer_username or "",
            sale.shipping_cost or 0,
            sale.shipping_carrier or "",
            sale.tracking_number or "",
            sale.platform_fees or 0,
            sale.payment_fees or 0,
            sale.profit or "",
            sale.sale_date.isoformat() if sale.sale_date else "",
            sale.shipped_date.isoformat() if sale.shipped_date else "",
            sale.delivered_date.isoformat() if sale.delivered_date else "",
            sale.notes or ""
        ])

    output.seek(0)
    filename = f"scrounger_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/items/csv")
async def import_items_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import items from CSV."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))

    created = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            item = Item(
                name=row.get('Name', row.get('name', '')),
                description=row.get('Description', row.get('description', '')),
                category=row.get('Category', row.get('category', '')),
                condition=row.get('Condition', row.get('condition', 'good')),
                asking_price=float(row.get('Asking Price', row.get('asking_price', 0)) or 0) or None,
                min_price=float(row.get('Min Price', row.get('min_price', 0)) or 0) or None,
                cost_basis=float(row.get('Cost Basis', row.get('cost_basis', 0)) or 0) or None,
                status=row.get('Status', row.get('status', 'draft')),
                platforms=row.get('Platforms', row.get('platforms', '')).split(',') if row.get('Platforms', row.get('platforms', '')) else [],
                notes=row.get('Notes', row.get('notes', ''))
            )
            db.add(item)
            created += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    db.commit()

    return {
        "success": True,
        "created": created,
        "errors": errors
    }


@router.get("/calendar/leads.ics")
def export_leads_calendar(
    days_ahead: int = 7,
    db: Session = Depends(get_db)
):
    """Export leads as calendar events for follow-up reminders."""
    # Get leads that need follow-up (new or negotiating)
    leads = db.query(Lead).filter(
        Lead.status.in_(["new", "contacted", "negotiating"])
    ).all()

    cal = Calendar()
    cal.add('prodid', '-//Scrounger//Sales Tracker//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')

    for lead in leads:
        item = db.query(Item).filter(Item.id == lead.item_id).first()

        # Create follow-up event
        event = Event()
        event.add('summary', f"Follow up: {lead.username} - {item.name if item else 'Unknown'}")
        event.add('description', f"""
Lead: {lead.username}
Item: {item.name if item else 'Unknown'}
Platform: {lead.platform}
Status: {lead.status}
Offered: {lead.offered_price or 'Not specified'}
Notes: {lead.notes or 'None'}
""")

        # Set event for tomorrow or based on last contact
        if lead.last_contact_at:
            event_date = lead.last_contact_at + timedelta(days=2)
        else:
            event_date = datetime.now() + timedelta(days=1)

        event.add('dtstart', event_date.date())
        event.add('dtend', event_date.date())
        event.add('uid', f"scrounger-lead-{lead.id}@localhost")

        cal.add_component(event)

    output = cal.to_ical()
    filename = f"scrounger_leads_{datetime.now().strftime('%Y%m%d')}.ics"

    return StreamingResponse(
        iter([output]),
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/tasks/leads.ics")
def export_leads_tasks(db: Session = Depends(get_db)):
    """Export leads as TODO items for Google Tasks."""
    leads = db.query(Lead).filter(
        Lead.status.in_(["new", "contacted", "negotiating"])
    ).all()

    cal = Calendar()
    cal.add('prodid', '-//Scrounger//Sales Tracker//EN')
    cal.add('version', '2.0')

    for lead in leads:
        item = db.query(Item).filter(Item.id == lead.item_id).first()

        todo = Todo()
        todo.add('summary', f"Contact {lead.username} about {item.name if item else 'item'}")
        todo.add('description', f"""
Platform: {lead.platform}
Status: {lead.status}
Offered: {lead.offered_price or 'Not specified'}
Notes: {lead.notes or 'None'}
""")

        # Due date
        if lead.last_contact_at:
            due_date = lead.last_contact_at + timedelta(days=2)
        else:
            due_date = datetime.now() + timedelta(days=1)

        todo.add('due', due_date)
        todo.add('uid', f"scrounger-todo-{lead.id}@localhost")

        # Priority based on status
        if lead.status == "negotiating":
            todo.add('priority', 1)
        elif lead.status == "contacted":
            todo.add('priority', 5)
        else:
            todo.add('priority', 9)

        cal.add_component(todo)

    output = cal.to_ical()
    filename = f"scrounger_tasks_{datetime.now().strftime('%Y%m%d')}.ics"

    return StreamingResponse(
        iter([output]),
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/template/items.csv")
def get_items_template():
    """Get a template CSV for importing items."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Name", "Description", "Category", "Condition",
        "Asking Price", "Min Price", "Cost Basis", "Status",
        "Platforms", "Notes"
    ])

    writer.writerow([
        "Example GPU", "NVIDIA RTX 3080 10GB", "Graphics Card", "good",
        "500", "450", "700", "draft",
        "reddit,ebay", "Original box included"
    ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scrounger_items_template.csv"}
    )
