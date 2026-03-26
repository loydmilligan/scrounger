"""
Seed script for Scrounger database.

Usage:
    docker compose exec backend python -m src.scripts.seed

Or directly:
    cd backend && python -m src.scripts.seed
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database import SessionLocal, init_db
from src.models.setting import UserSetting


def seed_user_settings(db):
    """Seed default user settings."""
    defaults = [
        ("user_state", "TX"),
        ("user_zip", "78701"),
        ("feedback_timer_days", "3"),
        ("chaser_timer_days", "14"),
    ]

    for key, value in defaults:
        existing = db.query(UserSetting).filter(UserSetting.key == key).first()
        if not existing:
            setting = UserSetting(key=key, value=value)
            db.add(setting)
            print(f"  Added setting: {key} = {value}")
        else:
            print(f"  Setting exists: {key}")

    db.commit()


def seed_categories(db):
    """Seed default categories (when Category model exists)."""
    # Will be implemented when Category model is added
    categories = [
        ("electronics", "Electronics", "General electronics"),
        ("homelab", "Homelab", "Servers, networking, infrastructure"),
        ("gpu", "Graphics Cards", "GPUs and video cards"),
        ("cpu", "Processors", "CPUs"),
        ("ram", "Memory", "RAM modules"),
        ("storage", "Storage", "SSDs, HDDs, NVMe drives"),
        ("3d_printing", "3D Printing", "Printers, filament, parts"),
        ("beauty", "Beauty", "Beauty products and tools"),
        ("tools", "Tools", "Hand tools, power tools"),
        ("other", "Other", "Miscellaneous items"),
    ]

    # Check if Category model exists
    try:
        from src.models.category import Category

        for name, display_name, description in categories:
            existing = db.query(Category).filter(Category.name == name).first()
            if not existing:
                category = Category(
                    name=name,
                    display_name=display_name,
                    description=description,
                    sort_order=categories.index((name, display_name, description))
                )
                db.add(category)
                print(f"  Added category: {display_name}")
            else:
                print(f"  Category exists: {display_name}")

        db.commit()
    except ImportError:
        print("  Category model not yet implemented, skipping...")


def seed_marketplaces(db):
    """Seed default marketplaces (when Marketplace model exists)."""
    marketplaces = [
        {
            "name": "reddit_hardwareswap",
            "display_name": "r/hardwareswap",
            "platform_type": "reddit",
            "fee_percentage": 0,
            "bump_interval_hours": 72,
            "feedback_timer_days": 2,
        },
        {
            "name": "reddit_homelabsales",
            "display_name": "r/homelabsales",
            "platform_type": "reddit",
            "fee_percentage": 0,
            "bump_interval_hours": 72,
            "feedback_timer_days": 2,
        },
        {
            "name": "ebay",
            "display_name": "eBay",
            "platform_type": "ebay",
            "fee_percentage": 13.25,
            "feedback_timer_days": 5,
        },
        {
            "name": "offerup",
            "display_name": "OfferUp",
            "platform_type": "offerup",
            "fee_percentage": 12.9,
            "feedback_timer_days": 3,
        },
        {
            "name": "craigslist",
            "display_name": "Craigslist",
            "platform_type": "craigslist",
            "fee_percentage": 0,
            "bump_interval_hours": 48,
        },
        {
            "name": "swappa",
            "display_name": "Swappa",
            "platform_type": "swappa",
            "fee_percentage": 3,
            "feedback_timer_days": 3,
        },
        {
            "name": "facebook",
            "display_name": "Facebook Marketplace",
            "platform_type": "facebook",
            "fee_percentage": 5,
        },
    ]

    # Check if Marketplace model exists
    try:
        from src.models.marketplace import Marketplace

        for mp_data in marketplaces:
            existing = db.query(Marketplace).filter(Marketplace.name == mp_data["name"]).first()
            if not existing:
                marketplace = Marketplace(**mp_data)
                db.add(marketplace)
                print(f"  Added marketplace: {mp_data['display_name']}")
            else:
                print(f"  Marketplace exists: {mp_data['display_name']}")

        db.commit()
    except ImportError:
        print("  Marketplace model not yet implemented, skipping...")


def seed_value_factors(db):
    """Seed example value factors (when ValueFactor model exists)."""
    value_factors = [
        {
            "name": "Tariff Premium",
            "description": "Import tariffs affecting supply and pricing",
            "multiplier": 1.0,
            "active": False,
        },
        {
            "name": "Supply Shortage",
            "description": "Limited supply driving up prices",
            "multiplier": 1.0,
            "active": False,
        },
        {
            "name": "Seasonal Demand",
            "description": "Holiday or seasonal demand increase",
            "multiplier": 1.0,
            "active": False,
        },
    ]

    # Check if ValueFactor model exists
    try:
        from src.models.value_factor import ValueFactor

        for vf_data in value_factors:
            existing = db.query(ValueFactor).filter(ValueFactor.name == vf_data["name"]).first()
            if not existing:
                vf = ValueFactor(**vf_data)
                db.add(vf)
                print(f"  Added value factor: {vf_data['name']}")
            else:
                print(f"  Value factor exists: {vf_data['name']}")

        db.commit()
    except ImportError:
        print("  ValueFactor model not yet implemented, skipping...")


def main():
    """Run all seed functions."""
    print("=" * 50)
    print("Scrounger Database Seeding")
    print("=" * 50)

    # Initialize database (create tables if needed)
    print("\n1. Initializing database...")
    init_db()
    print("   Done.")

    # Get database session
    db = SessionLocal()

    try:
        print("\n2. Seeding user settings...")
        seed_user_settings(db)

        print("\n3. Seeding categories...")
        seed_categories(db)

        print("\n4. Seeding marketplaces...")
        seed_marketplaces(db)

        print("\n5. Seeding value factors...")
        seed_value_factors(db)

        print("\n" + "=" * 50)
        print("Seeding complete!")
        print("=" * 50)

    except Exception as e:
        print(f"\nError during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
