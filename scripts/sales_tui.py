#!/usr/bin/env python3
import os
import math
from dotenv import load_dotenv
import requests

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time

SHEET_NINJA_ENDPOINT = os.getenv("SHEET_NINJA_ENDPOINT_URL")
SHEET_NINJA_API_KEY = os.getenv("SHEET_NINJA_API_KEY")

DAYS_3_YEARS = 1095
MIN_VALUE_PCT = 0.20

def calculate_current_value(retail_price, date_purchase):
    if not retail_price or not date_purchase:
        return retail_price if retail_price else 0
    
    try:
        date_purchase = int(date_purchase)
        purchase_dt = datetime(1899, 12, 30) + timedelta(days=date_purchase)
        days_owned = (datetime.now() - purchase_dt).days
        
        if days_owned <= 0:
            return retail_price
        
        if days_owned >= DAYS_3_YEARS:
            return round(retail_price * MIN_VALUE_PCT, 2)
        
        log_decay = math.log(1 + days_owned) / math.log(1 + DAYS_3_YEARS)
        current_pct = MIN_VALUE_PCT + (1 - MIN_VALUE_PCT) * (1 - log_decay)
        
        return round(retail_price * current_pct, 2)
    except:
        return retail_price if retail_price else 0

def get_deadline_info(item, now):
    status = item.get("status", "").upper()
    
    if status == "PAID":
        date_paid = item.get("datePaid")
        if date_paid:
            paid_dt = datetime(1899, 12, 30) + timedelta(days=int(date_paid))
            deadline = paid_dt + timedelta(days=5)
            return deadline, "Ship"
    
    elif status == "SHIPPED":
        date_paid = item.get("datePaid")
        if date_paid:
            paid_dt = datetime(1899, 12, 30) + timedelta(days=int(date_paid))
            deadline = paid_dt + timedelta(days=5)
            return deadline, "Deliver"
    
    elif status == "DELIVERED":
        date_delivered = item.get("dateDelivered")
        if date_delivered:
            delivered_dt = datetime(1899, 12, 30) + timedelta(days=int(date_delivered))
            deadline = delivered_dt + timedelta(days=3)
            return deadline, "Confirm"
    
    return None, None

def get_urgency_color(deadline, now):
    if not deadline:
        return "green"
    
    days_left = (deadline - now).days
    
    if days_left <= 0:
        return "red"
    elif days_left <= 1:
        return "bright red"
    elif days_left <= 3:
        return "yellow"
    else:
        return "green"

def fetch_sales():
    headers = {"Authorization": f"Bearer {SHEET_NINJA_API_KEY}"}
    response = requests.get(SHEET_NINJA_ENDPOINT, headers=headers)
    response.raise_for_status()
    return response.json()["data"]

def update_current_values(items):
    headers = {"Authorization": f"Bearer {SHEET_NINJA_API_KEY}"}
    
    for item in items:
        current_value = calculate_current_value(
            item.get("retailPrice"), 
            item.get("datePurchase")
        )
        
        if current_value != item.get("currentValue"):
            requests.patch(
                f"{SHEET_NINJA_ENDPOINT}/{item['id']}",
                headers=headers,
                json={"currentValue": current_value}
            )
            item["currentValue"] = current_value

STATUS_ORDER = ["AGREEMENT", "PAID", "PRINTED", "PACKAGED", "SHIPPED", "DELIVERED", "CONFIRMED", "COMPLETE"]

def map_status_to_bucket(status):
    s = status.upper() if status else "INVENTORY"
    mapping = {
        "AGREED": "AGREEMENT",
        "AGREEMENT": "AGREEMENT",
        "PAID": "PAID",
        "PRINTED": "PRINTED",
        "PRINTED SHIPPING LABEL": "PRINTED",
        "LABEL PRINTED": "PRINTED",
        "PACKAGED": "PACKAGED",
        "PACKED": "PACKAGED",
        "SHIPPED": "SHIPPED",
        "DELIVERED": "DELIVERED",
        "CONFIRMED": "CONFIRMED",
        "COMPLETE": "COMPLETE",
        "ARCHIVED": "COMPLETE",
        "INVENTORY": "AGREEMENT",
        "DRAFT": "AGREEMENT",
        "LISTED": "AGREEMENT",
        "INTEREST": "AGREEMENT",
        "DISPUTE": "COMPLETE",
    }
    return mapping.get(s, "AGREEMENT")

def group_by_status(items):
    buckets = {s: [] for s in STATUS_ORDER}
    
    for item in items:
        bucket = map_status_to_bucket(item.get("status", ""))
        buckets[bucket].append(item)
    
    return buckets

def render_card(item, now):
    name = item.get("itemName", "Unknown")[:25]
    sale_price = item.get("salePrice", 0)
    current_value = item.get("currentValue", 0)
    marketplace = item.get("marketplace", "")
    
    deadline, deadline_action = get_deadline_info(item, now)
    urgency = get_urgency_color(deadline, now)
    
    lines = []
    lines.append(f"[bold {urgency}]{name}[/bold {urgency}]")
    lines.append(f"[bold]${sale_price}[/bold] | Val: ${current_value}")
    if marketplace:
        lines.append(f"[dim]{marketplace}[/dim]")
    if deadline:
        days_left = (deadline - now).days
        if days_left >= 0:
            lines.append(f"[bold {urgency}]{deadline_action}: {days_left}d[/bold {urgency}]")
        else:
            lines.append(f"[bold red]OVERDUE![/bold red]")
    
    text = Text("\n".join(lines))
    return Panel(text, border_style=urgency, padding=(1, 1), width=28)

def main(once=False):
    console = Console(force_terminal=True)
    now = datetime.now()
    
    while True:
        try:
            now = datetime.now()
            items = fetch_sales()
            update_current_values(items)
            
            buckets = group_by_status(items)
            
            console.clear()
            
            console.print(f"[bold cyan reverse]  SCRQUINGER SALES FUNNEL  [/bold cyan reverse]  [dim]{now.strftime('%H:%M:%S')}[/dim]")
            console.print()
            
            console.print("[bold magenta]" + "═" * 100 + "[/bold magenta]")
            console.print()
            
            for status in STATUS_ORDER:
                items = buckets[status]
                count = len(items)
                console.print(f"[bold magenta reverse] {status} ({count}) [/bold magenta reverse]")
                if items:
                    for item in items:
                        console.print(render_card(item, now))
                else:
                    console.print("[dim]  -- empty --[/dim]")
                console.print()
            
            if once:
                break
            time.sleep(30)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if once:
                break
            time.sleep(10)

if __name__ == "__main__":
    import sys
    once = "--once" in sys.argv
    main(once=once)
