"""
Tests for the Sales Funnel Workflow

The core of Scrounger is tracking items through a 10-phase sales funnel:
1. INVENTORY - Items owned that may be sold
2. DRAFT - Preparing listings
3. LISTED - Active listings
4. INTEREST - Leads/inquiries received
5. AGREEMENT - Deal made, awaiting payment
6. PAID - Payment received, needs shipping
7. SHIPPED - In transit
8. DELIVERED - Arrived at buyer
9. COMPLETE - Transaction finished
10. DISPUTE - Issue resolution (alternate path)

These tests verify the business logic of moving items through this funnel.
"""
import pytest


class TestInventoryPhase:
    """
    Phase 1: INVENTORY
    Items we own that we may want to sell eventually.
    """

    def test_new_items_start_in_inventory(self, client):
        """Items should default to inventory status when created"""
        response = client.post("/api/items", json={
            "name": "New GPU",
            "cost_basis": 500.00
        })
        assert response.json()["status"] == "inventory"

    def test_inventory_items_can_track_storage_location(self, client):
        """Sellers need to know where items are physically stored"""
        response = client.post("/api/items", json={
            "name": "Server Parts",
            "location": "Garage - Shelf B2"
        })
        assert response.json()["location"] == "Garage - Shelf B2"

    def test_inventory_items_track_acquisition_cost(self, client):
        """Sellers need to track what they paid to calculate profit later"""
        response = client.post("/api/items", json={
            "name": "Bought on eBay",
            "cost_basis": 150.00,
            "acquisition_source": "eBay"
        })
        item = response.json()
        assert item["cost_basis"] == 150.00
        assert item["acquisition_source"] == "eBay"


class TestDraftPhase:
    """
    Phase 2: DRAFT
    Items we've decided to sell and are preparing listings for.
    """

    def test_item_can_move_to_draft_status(self, client, sample_item):
        """Seller decides to sell - moves item to draft"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "draft"
        })
        assert response.json()["status"] == "draft"

    def test_draft_items_can_have_asking_and_min_price(self, client, sample_item):
        """Draft items need pricing information"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "draft",
            "asking_price": 300.00,
            "min_price": 250.00
        })
        item = response.json()
        assert item["asking_price"] == 300.00
        assert item["min_price"] == 250.00

    def test_draft_items_can_store_platform_specific_prices(self, client, sample_item):
        """Different platforms may have different pricing"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "draft",
            "platform_prices": {
                "reddit": 290.00,
                "ebay": 320.00,
                "offerup": 280.00
            }
        })
        prices = response.json()["platform_prices"]
        assert prices["reddit"] == 290.00
        assert prices["ebay"] == 320.00

    def test_draft_items_can_store_generated_posts(self, client, sample_item):
        """AI-generated posts are stored per platform"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "draft_posts": {
                "reddit": "[USA-CA] [H] RTX 3080 [W] PayPal, Local Cash",
                "ebay": "NVIDIA RTX 3080 - Great Condition"
            }
        })
        posts = response.json()["draft_posts"]
        assert "reddit" in posts
        assert "[H]" in posts["reddit"]


class TestListedPhase:
    """
    Phase 3: LISTED
    Items actively listed for sale on one or more platforms.
    """

    def test_moving_to_listed_sets_timestamp(self, client, sample_item):
        """listed_at should be automatically set when status becomes listed"""
        assert sample_item["listed_at"] is None

        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "listed"
        })
        assert response.json()["listed_at"] is not None

    def test_listed_items_can_track_active_listings(self, client, sample_item):
        """Sellers need to track where items are listed and listing URLs"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "listed",
            "active_listings": {
                "reddit": {
                    "url": "https://reddit.com/r/hardwareswap/comments/abc123",
                    "posted_at": "2024-01-15T10:00:00Z",
                    "expires_at": "2024-01-18T10:00:00Z"
                },
                "offerup": {
                    "url": "https://offerup.com/item/12345",
                    "posted_at": "2024-01-15T11:00:00Z"
                }
            }
        })
        listings = response.json()["active_listings"]
        assert "reddit" in listings
        assert "offerup" in listings

    def test_listed_items_track_response_count(self, client, sample_item):
        """Sellers want to know how many responses a listing gets"""
        client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "listed",
            "total_responses": 5
        })

        item = client.get(f"/api/items/{sample_item['id']}").json()
        assert item["total_responses"] == 5


class TestSoldPhase:
    """
    Phase 6-9: SOLD through COMPLETE
    Tracking the sale from payment through delivery.
    """

    def test_moving_to_sold_sets_timestamp(self, client, sample_item):
        """sold_at should be automatically set when status becomes sold"""
        assert sample_item["sold_at"] is None

        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "sold"
        })
        assert response.json()["sold_at"] is not None

    def test_sold_timestamp_not_overwritten_on_subsequent_updates(self, client, sample_item):
        """Once sold_at is set, it shouldn't change"""
        # Mark as sold
        client.patch(f"/api/items/{sample_item['id']}", json={"status": "sold"})
        item1 = client.get(f"/api/items/{sample_item['id']}").json()
        original_sold_at = item1["sold_at"]

        # Update something else
        import time
        time.sleep(0.1)
        client.patch(f"/api/items/{sample_item['id']}", json={
            "notes": "Updated notes"
        })

        item2 = client.get(f"/api/items/{sample_item['id']}").json()
        assert item2["sold_at"] == original_sold_at


class TestPriceHistory:
    """
    Sellers need to track price changes over time to understand
    what pricing strategies work.
    """

    def test_can_store_price_change_history(self, client, sample_item):
        """Price changes should be trackable"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "price_history": [
                {"date": "2024-01-15", "price": 500.00, "reason": "Initial listing"},
                {"date": "2024-01-20", "price": 450.00, "reason": "Price drop - no interest"},
                {"date": "2024-01-25", "price": 400.00, "reason": "Final price"}
            ]
        })

        history = response.json()["price_history"]
        assert len(history) == 3
        assert history[0]["price"] == 500.00
        assert history[2]["reason"] == "Final price"


class TestBundles:
    """
    Sellers often bundle multiple items together for a better deal.
    """

    def test_item_can_be_marked_as_bundle(self, client):
        """Sellers can create bundle listings"""
        response = client.post("/api/items", json={
            "name": "Full PC Build",
            "is_bundle": True,
            "asking_price": 1500.00
        })
        assert response.json()["is_bundle"] is True

    def test_bundle_can_reference_component_items(self, client):
        """Bundles should track which items are included"""
        # Create component items
        gpu = client.post("/api/items", json={"name": "RTX 3080"}).json()
        cpu = client.post("/api/items", json={"name": "Ryzen 5800X"}).json()
        ram = client.post("/api/items", json={"name": "32GB RAM"}).json()

        # Create bundle
        bundle = client.post("/api/items", json={
            "name": "Gaming PC Bundle",
            "is_bundle": True,
            "bundle_item_ids": [gpu["id"], cpu["id"], ram["id"]]
        }).json()

        assert bundle["bundle_item_ids"] == [gpu["id"], cpu["id"], ram["id"]]

    def test_can_filter_for_bundles_only(self, client):
        """Sellers need to see all bundles"""
        client.post("/api/items", json={"name": "Single Item", "is_bundle": False})
        client.post("/api/items", json={"name": "Bundle 1", "is_bundle": True})
        client.post("/api/items", json={"name": "Bundle 2", "is_bundle": True})

        response = client.get("/api/items?is_bundle=true")
        items = response.json()["items"]
        assert len(items) == 2
        assert all(item["is_bundle"] for item in items)


class TestReadyChecklist:
    """
    Before listing, sellers need to complete certain tasks.
    The system tracks these via a checklist.
    """

    def test_can_track_listing_preparation_checklist(self, client, sample_item):
        """Sellers need a checklist before listing"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "ready_checklist": {
                "photos_taken": True,
                "tested_working": True,
                "cleaned": True,
                "box_found": False,
                "accessories_gathered": True
            }
        })

        checklist = response.json()["ready_checklist"]
        assert checklist["photos_taken"] is True
        assert checklist["box_found"] is False


class TestFunnelStatistics:
    """
    Dashboard needs to show items at each funnel stage.
    """

    def test_get_counts_at_each_funnel_stage(self, client):
        """Dashboard shows how many items at each stage"""
        # Create items at different stages
        client.post("/api/items", json={"name": "Inv 1", "status": "inventory"})
        client.post("/api/items", json={"name": "Inv 2", "status": "inventory"})
        client.post("/api/items", json={"name": "Inv 3", "status": "inventory"})
        client.post("/api/items", json={"name": "Draft 1", "status": "draft"})
        client.post("/api/items", json={"name": "Draft 2", "status": "draft"})
        client.post("/api/items", json={"name": "Listed 1", "status": "listed"})
        client.post("/api/items", json={"name": "Sold 1", "status": "sold"})

        response = client.get("/api/items/stats/by-status")
        stats = response.json()

        assert stats["inventory"] == 3
        assert stats["draft"] == 2
        assert stats["listed"] == 1
        assert stats["sold"] == 1
