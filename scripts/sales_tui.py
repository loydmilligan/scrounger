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
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
import time

SHEET_NINJA_ENDPOINT = os.getenv("SHEET_NINJA_ENDPOINT_URL")
SHEET_NINJA_API_KEY = os.getenv("SHEET_NINJA_API_KEY")

DAYS_3_YEARS = 1095
MIN_VALUE_PCT = 0.20

def excel_date_to_datetime(excel_date):
    if not excel_date:
        return None
    try:
        excel_date = int(excel_date)
        return datetime(1899, 12, 30) + timedelta(days=excel_date)
    except:
        return None

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

def get_status_bucket(status):
    status = status.upper() if status else "INVENTORY"
    buckets = {
        "INVENTORY": 0,
        "DRAFT": 1,
        "LISTED": 2,
        "INTEREST": 3,
        "AGREEMENT": 4,
        "PAID": 5,
        "SHIPPED": 6,
        "DELIVERED": 7,
        "COMPLETE": 8,
        "DISPUTE": 9,
    }
    return buckets.get(status, 0)

def group_by_status(items):
    buckets = {s: [] for s in ["INVENTORY", "DRAFT", "LISTED", "INTEREST", "AGREEMENT", "PAID", "SHIPPED", "DELIVERED", "COMPLETE", "DISPUTE"]}
    
    for item in items:
        status = item.get("status", "INVENTORY").upper()
        if status in buckets:
            buckets[status].append(item)
        else:
            buckets["INVENTORY"].append(item)
    
    return buckets

def render_bucket(title, items, console):
    text = Text()
    
    if not items:
        text.append(f"[dim]-- empty --[/dim]\n")
    else:
        for item in items:
            name = item.get("itemName", "Unknown")[:25]
            price = item.get("salePrice", 0)
            value = item.get("currentValue", 0)
            date_paid = item.get("datePaid", "")
            
            days_ago = ""
            if date_paid:
                try:
                    paid = int(date_paid)
                    days = (datetime.now() - (datetime(1899, 12, 30) + timedelta(days=paid))).days
                    days_ago = f"[dim]({days}d ago)[/dim]"
                except:
                    pass
            
            text.append(f"• {name}\n")
            text.append(f"  $[yellow]{price}[/yellow] | Val: ${value} {days_ago}\n")
    
    return Panel(text, title=f"[bold]{title}[/bold] ({len(items)})", border_style="blue", padding=(0, 1))

def main(once=False):
    from datetime import timedelta
    
    console = Console()
    
    while True:
        try:
            items = fetch_sales()
            update_current_values(items)
            
            buckets = group_by_status(items)
            
            console.clear()
            
            title = Text("Scrounger Sales Funnel", style="bold cyan", justify="center")
            console.print(Panel(title, style="cyan"))
            console.print()
            
            row1 = ["INVENTORY", "DRAFT", "LISTED", "INTEREST", "AGREEMENT"]
            row2 = ["PAID", "SHIPPED", "DELIVERED", "COMPLETE", "DISPUTE"]
            
            console.print("[bold]Active Sales[/bold]")
            for status in row1:
                console.print(render_bucket(status, buckets[status], console), end=" ")
            console.print()
            
            for status in row2:
                console.print(render_bucket(status, buckets[status], console), end=" ")
            console.print()
            
            console.print(f"\n[dim]Updated: {datetime.now().strftime('%H:%M:%S')}[/dim]")
            
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
