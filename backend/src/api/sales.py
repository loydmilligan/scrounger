from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..models import Sale, Item, Lead
from ..schemas import SaleCreate, SaleUpdate, SaleResponse, SaleList

router = APIRouter()


def calculate_profit(sale: Sale, item: Item) -> Optional[float]:
    """Calculate profit from a sale."""
    if sale.sale_price is None:
        return None

    cost = item.cost_basis or 0
    shipping = sale.shipping_cost or 0
    platform_fees = sale.platform_fees or 0
    payment_fees = sale.payment_fees or 0

    return sale.sale_price - cost - shipping - platform_fees - payment_fees


@router.get("", response_model=SaleList)
def list_sales(
    platform: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Sale)

    if platform:
        query = query.filter(Sale.platform == platform)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)

    query = query.order_by(Sale.sale_date.desc())

    total = query.count()
    sales = query.offset(skip).limit(limit).all()

    result_sales = []
    total_revenue = 0
    total_profit = 0

    for sale in sales:
        item = db.query(Item).filter(Item.id == sale.item_id).first()
        profit = calculate_profit(sale, item) if item else None

        if sale.sale_price:
            total_revenue += sale.sale_price
        if profit:
            total_profit += profit

        result_sales.append(SaleResponse(
            id=sale.id,
            item_id=sale.item_id,
            lead_id=sale.lead_id,
            sale_price=sale.sale_price,
            platform=sale.platform,
            buyer_username=sale.buyer_username,
            shipping_cost=sale.shipping_cost,
            shipping_carrier=sale.shipping_carrier,
            tracking_number=sale.tracking_number,
            platform_fees=sale.platform_fees,
            payment_fees=sale.payment_fees,
            profit=profit,
            notes=sale.notes,
            sale_date=sale.sale_date,
            shipped_date=sale.shipped_date,
            delivered_date=sale.delivered_date,
            created_at=sale.created_at,
            item_name=item.name if item else None
        ))

    return SaleList(
        sales=result_sales,
        total=total,
        total_revenue=total_revenue,
        total_profit=total_profit
    )


@router.get("/stats")
def get_sales_stats(db: Session = Depends(get_db)):
    """Get sales statistics for dashboard."""
    sales = db.query(Sale).all()

    total_sales = len(sales)
    total_revenue = sum(s.sale_price or 0 for s in sales)

    # Calculate total profit
    total_profit = 0
    for sale in sales:
        item = db.query(Item).filter(Item.id == sale.item_id).first()
        if item:
            profit = calculate_profit(sale, item)
            if profit:
                total_profit += profit

    # Sales by platform
    platform_stats = {}
    for sale in sales:
        platform = sale.platform or "Unknown"
        if platform not in platform_stats:
            platform_stats[platform] = {"count": 0, "revenue": 0}
        platform_stats[platform]["count"] += 1
        platform_stats[platform]["revenue"] += sale.sale_price or 0

    # Items stats
    total_items = db.query(Item).count()
    listed_items = db.query(Item).filter(Item.status == "listed").count()
    draft_items = db.query(Item).filter(Item.status == "draft").count()

    return {
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "average_sale": total_revenue / total_sales if total_sales > 0 else 0,
        "platform_breakdown": platform_stats,
        "items": {
            "total": total_items,
            "listed": listed_items,
            "draft": draft_items,
            "sold": total_sales
        }
    }


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    item = db.query(Item).filter(Item.id == sale.item_id).first()
    profit = calculate_profit(sale, item) if item else None

    return SaleResponse(
        id=sale.id,
        item_id=sale.item_id,
        lead_id=sale.lead_id,
        sale_price=sale.sale_price,
        platform=sale.platform,
        buyer_username=sale.buyer_username,
        shipping_cost=sale.shipping_cost,
        shipping_carrier=sale.shipping_carrier,
        tracking_number=sale.tracking_number,
        platform_fees=sale.platform_fees,
        payment_fees=sale.payment_fees,
        profit=profit,
        notes=sale.notes,
        sale_date=sale.sale_date,
        shipped_date=sale.shipped_date,
        delivered_date=sale.delivered_date,
        created_at=sale.created_at,
        item_name=item.name if item else None
    )


@router.post("", response_model=SaleResponse)
def create_sale(sale_data: SaleCreate, db: Session = Depends(get_db)):
    # Verify item exists and not already sold
    item = db.query(Item).filter(Item.id == sale_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_sale = db.query(Sale).filter(Sale.item_id == sale_data.item_id).first()
    if existing_sale:
        raise HTTPException(status_code=400, detail="Item already has a sale record")

    sale = Sale(**sale_data.model_dump())
    if not sale.sale_date:
        sale.sale_date = datetime.utcnow()

    db.add(sale)

    # Update item status
    item.status = "sold"
    item.sold_at = sale.sale_date

    # Update lead status if provided
    if sale.lead_id:
        lead = db.query(Lead).filter(Lead.id == sale.lead_id).first()
        if lead:
            lead.status = "sold"

    db.commit()
    db.refresh(sale)

    profit = calculate_profit(sale, item)
    sale.profit = profit
    db.commit()

    return SaleResponse(
        id=sale.id,
        item_id=sale.item_id,
        lead_id=sale.lead_id,
        sale_price=sale.sale_price,
        platform=sale.platform,
        buyer_username=sale.buyer_username,
        shipping_cost=sale.shipping_cost,
        shipping_carrier=sale.shipping_carrier,
        tracking_number=sale.tracking_number,
        platform_fees=sale.platform_fees,
        payment_fees=sale.payment_fees,
        profit=profit,
        notes=sale.notes,
        sale_date=sale.sale_date,
        shipped_date=sale.shipped_date,
        delivered_date=sale.delivered_date,
        created_at=sale.created_at,
        item_name=item.name
    )


@router.patch("/{sale_id}", response_model=SaleResponse)
def update_sale(sale_id: int, sale_data: SaleUpdate, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    update_data = sale_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sale, key, value)

    # Recalculate profit
    item = db.query(Item).filter(Item.id == sale.item_id).first()
    if item:
        sale.profit = calculate_profit(sale, item)

    db.commit()
    db.refresh(sale)

    return SaleResponse(
        id=sale.id,
        item_id=sale.item_id,
        lead_id=sale.lead_id,
        sale_price=sale.sale_price,
        platform=sale.platform,
        buyer_username=sale.buyer_username,
        shipping_cost=sale.shipping_cost,
        shipping_carrier=sale.shipping_carrier,
        tracking_number=sale.tracking_number,
        platform_fees=sale.platform_fees,
        payment_fees=sale.payment_fees,
        profit=sale.profit,
        notes=sale.notes,
        sale_date=sale.sale_date,
        shipped_date=sale.shipped_date,
        delivered_date=sale.delivered_date,
        created_at=sale.created_at,
        item_name=item.name if item else None
    )


@router.delete("/{sale_id}")
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Revert item status
    item = db.query(Item).filter(Item.id == sale.item_id).first()
    if item:
        item.status = "listed"
        item.sold_at = None

    db.delete(sale)
    db.commit()
    return {"message": "Sale deleted successfully"}
