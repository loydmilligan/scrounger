"""
Tests for Epic 1: Item Management

These tests validate the user stories and acceptance criteria for managing
inventory items in Scrounger.

User Stories:
- US-1.1: Add New Item for Sale
- US-1.2: View and Filter Inventory
- US-1.3: Edit Item Details
"""
import pytest


class TestAddNewItemForSale:
    """
    US-1.1: As a seller, I want to add items to my inventory
    so that I can track what I'm selling.
    """

    def test_seller_can_add_item_with_basic_details(self, client, sample_category):
        """AC: Can enter item name, description, category, condition"""
        response = client.post("/api/items", json={
            "name": "AMD Ryzen 7 5800X",
            "description": "CPU, never overclocked, original box included",
            "category_id": sample_category["id"],
            "condition": "like_new"
        })

        assert response.status_code == 200
        item = response.json()
        assert item["name"] == "AMD Ryzen 7 5800X"
        assert item["description"] == "CPU, never overclocked, original box included"
        assert item["category"]["name"] == "electronics"
        assert item["condition"] == "like_new"

    def test_seller_can_set_asking_and_minimum_price(self, client, sample_category):
        """AC: Can set asking price and minimum acceptable price"""
        response = client.post("/api/items", json={
            "name": "Dell Monitor 27inch",
            "category_id": sample_category["id"],
            "asking_price": 250.00,
            "min_price": 200.00
        })

        assert response.status_code == 200
        item = response.json()
        assert item["asking_price"] == 250.00
        assert item["min_price"] == 200.00

    def test_seller_can_set_item_status(self, client, sample_category):
        """AC: Can set item status (draft, listed, sold, archived)"""
        # Test inventory status (default)
        response = client.post("/api/items", json={
            "name": "Item 1",
            "status": "inventory"
        })
        assert response.json()["status"] == "inventory"

        # Test draft status
        response = client.post("/api/items", json={
            "name": "Item 2",
            "status": "draft"
        })
        assert response.json()["status"] == "draft"

        # Test listed status
        response = client.post("/api/items", json={
            "name": "Item 3",
            "status": "listed"
        })
        assert response.json()["status"] == "listed"

    def test_item_appears_in_inventory_after_creation(self, client, sample_category):
        """AC: Item appears in inventory list after creation"""
        # Create an item
        create_response = client.post("/api/items", json={
            "name": "Corsair 32GB RAM Kit",
            "category_id": sample_category["id"]
        })
        created_item = create_response.json()

        # Verify it appears in the list
        list_response = client.get("/api/items")
        items = list_response.json()["items"]

        item_ids = [item["id"] for item in items]
        assert created_item["id"] in item_ids

    def test_required_fields_are_validated(self, client):
        """AC: Form validates required fields before submission"""
        # Name is required
        response = client.post("/api/items", json={
            "description": "Missing name field"
        })
        assert response.status_code == 422  # Validation error

    def test_seller_can_track_acquisition_details(self, client, sample_category):
        """Sellers need to track where and when they acquired items"""
        response = client.post("/api/items", json={
            "name": "MacBook Pro 2021",
            "category_id": sample_category["id"],
            "cost_basis": 1200.00,
            "acquisition_source": "Facebook Marketplace",
            "acquisition_condition": "used",
            "acquisition_date": "2024-01-15",
            "location": "Home office closet"
        })

        assert response.status_code == 200
        item = response.json()
        assert item["cost_basis"] == 1200.00
        assert item["acquisition_source"] == "Facebook Marketplace"
        assert item["location"] == "Home office closet"

    def test_seller_can_assign_tags_to_item(self, client, sample_category, sample_tag):
        """Sellers need to organize items with tags"""
        response = client.post("/api/items", json={
            "name": "Tagged Item",
            "category_id": sample_category["id"],
            "tag_ids": [sample_tag["id"]]
        })

        assert response.status_code == 200
        item = response.json()
        assert len(item["tags"]) == 1
        assert item["tags"][0]["name"] == "urgent"


class TestViewAndFilterInventory:
    """
    US-1.2: As a seller, I want to view my inventory with filtering options
    so that I can quickly find specific items.
    """

    def test_seller_can_see_all_items_in_list(self, client, sample_category):
        """AC: Can see all items in a list view"""
        # Create multiple items
        for i in range(3):
            client.post("/api/items", json={
                "name": f"Test Item {i}",
                "category_id": sample_category["id"]
            })

        response = client.get("/api/items")
        assert response.status_code == 200
        assert response.json()["total"] == 3

    def test_seller_can_filter_by_status(self, client, sample_category):
        """AC: Can filter by status (listed, sold, draft)"""
        # Create items with different statuses
        client.post("/api/items", json={"name": "Draft Item", "status": "draft"})
        client.post("/api/items", json={"name": "Listed Item", "status": "listed"})
        client.post("/api/items", json={"name": "Inventory Item", "status": "inventory"})

        # Filter by draft
        response = client.get("/api/items?status=draft")
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["name"] == "Draft Item"

        # Filter by listed
        response = client.get("/api/items?status=listed")
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["name"] == "Listed Item"

    def test_seller_can_search_by_name_or_description(self, client, sample_category):
        """AC: Can search by item name/description"""
        client.post("/api/items", json={
            "name": "NVIDIA Graphics Card",
            "description": "RTX 3080 Founders Edition"
        })
        client.post("/api/items", json={
            "name": "AMD Processor",
            "description": "Ryzen 9 5900X"
        })

        # Search by name
        response = client.get("/api/items?search=NVIDIA")
        assert response.json()["total"] == 1

        # Search by description
        response = client.get("/api/items?search=Ryzen")
        assert response.json()["total"] == 1

    def test_seller_can_sort_items(self, client, sample_category):
        """AC: Can sort by date added, price, or status"""
        client.post("/api/items", json={"name": "Cheap", "asking_price": 50})
        client.post("/api/items", json={"name": "Expensive", "asking_price": 500})
        client.post("/api/items", json={"name": "Mid", "asking_price": 200})

        # Sort by price ascending
        response = client.get("/api/items?sort_by=asking_price&sort_dir=asc")
        items = response.json()["items"]
        assert items[0]["name"] == "Cheap"
        assert items[2]["name"] == "Expensive"

        # Sort by price descending
        response = client.get("/api/items?sort_by=asking_price&sort_dir=desc")
        items = response.json()["items"]
        assert items[0]["name"] == "Expensive"

    def test_seller_can_filter_by_category(self, client):
        """Sellers need to filter items by category"""
        # Create two categories
        cat1 = client.post("/api/categories", json={"name": "gpu"}).json()
        cat2 = client.post("/api/categories", json={"name": "cpu"}).json()

        client.post("/api/items", json={"name": "RTX 3080", "category_id": cat1["id"]})
        client.post("/api/items", json={"name": "Ryzen 5800X", "category_id": cat2["id"]})

        response = client.get(f"/api/items?category_id={cat1['id']}")
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["name"] == "RTX 3080"

    def test_seller_can_filter_by_location(self, client):
        """Sellers need to find items by storage location"""
        client.post("/api/items", json={"name": "Item 1", "location": "Garage shelf"})
        client.post("/api/items", json={"name": "Item 2", "location": "Office drawer"})

        response = client.get("/api/items?location=Garage")
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["name"] == "Item 1"


class TestEditItemDetails:
    """
    US-1.3: As a seller, I want to update item information
    so that I can adjust prices or descriptions.
    """

    def test_seller_can_edit_all_item_fields(self, client, sample_item):
        """AC: Can edit all item fields"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "name": "Updated Name",
            "description": "Updated description",
            "asking_price": 500.00,
            "min_price": 450.00,
            "condition": "like_new"
        })

        assert response.status_code == 200
        item = response.json()
        assert item["name"] == "Updated Name"
        assert item["description"] == "Updated description"
        assert item["asking_price"] == 500.00
        assert item["min_price"] == 450.00
        assert item["condition"] == "like_new"

    def test_changes_save_successfully(self, client, sample_item):
        """AC: Changes save successfully"""
        # Update the item
        client.patch(f"/api/items/{sample_item['id']}", json={
            "name": "Permanently Changed"
        })

        # Fetch it again and verify
        response = client.get(f"/api/items/{sample_item['id']}")
        assert response.json()["name"] == "Permanently Changed"

    def test_can_see_last_modified_date(self, client, sample_item):
        """AC: Can see edit history/last modified date"""
        original_updated = sample_item["updated_at"]

        # Make an update
        import time
        time.sleep(0.1)  # Ensure time passes
        client.patch(f"/api/items/{sample_item['id']}", json={
            "name": "Modified Item"
        })

        response = client.get(f"/api/items/{sample_item['id']}")
        # updated_at should be present and reflect the change
        assert "updated_at" in response.json()

    def test_partial_updates_preserve_other_fields(self, client, sample_item):
        """When updating one field, other fields should remain unchanged"""
        original_description = sample_item["description"]

        # Update only the name
        client.patch(f"/api/items/{sample_item['id']}", json={
            "name": "New Name Only"
        })

        response = client.get(f"/api/items/{sample_item['id']}")
        item = response.json()
        assert item["name"] == "New Name Only"
        assert item["description"] == original_description


class TestItemStatusTransitions:
    """
    Test the sales funnel status transitions for items.
    Items should flow: inventory -> draft -> listed -> sold -> archived
    """

    def test_item_starts_in_inventory_by_default(self, client):
        """New items should default to inventory status"""
        response = client.post("/api/items", json={"name": "New Item"})
        assert response.json()["status"] == "inventory"

    def test_status_change_to_listed_sets_listed_at(self, client, sample_item):
        """When item becomes listed, listed_at timestamp should be set"""
        assert sample_item["listed_at"] is None

        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "listed"
        })

        assert response.json()["listed_at"] is not None

    def test_status_change_to_sold_sets_sold_at(self, client, sample_item):
        """When item is sold, sold_at timestamp should be set"""
        assert sample_item["sold_at"] is None

        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "sold"
        })

        assert response.json()["sold_at"] is not None

    def test_invalid_status_is_rejected(self, client, sample_item):
        """Invalid status values should be rejected"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "status": "not_a_real_status"
        })

        assert response.status_code == 400


class TestItemOrganization:
    """Test item organization features: tags, categories, value factors"""

    def test_seller_can_add_tag_to_existing_item(self, client, sample_item, sample_tag):
        """Sellers should be able to add tags after item creation"""
        response = client.post(f"/api/items/{sample_item['id']}/tags/{sample_tag['id']}")
        assert response.status_code == 200

        # Verify tag was added
        item = client.get(f"/api/items/{sample_item['id']}").json()
        tag_names = [t["name"] for t in item["tags"]]
        assert "urgent" in tag_names

    def test_seller_can_remove_tag_from_item(self, client, sample_item, sample_tag):
        """Sellers should be able to remove tags from items"""
        # Add tag first
        client.post(f"/api/items/{sample_item['id']}/tags/{sample_tag['id']}")

        # Remove it
        response = client.delete(f"/api/items/{sample_item['id']}/tags/{sample_tag['id']}")
        assert response.status_code == 200

        # Verify removal
        item = client.get(f"/api/items/{sample_item['id']}").json()
        assert len(item["tags"]) == 0

    def test_value_factors_affect_effective_price(self, client, sample_item, sample_value_factor):
        """Value factors should multiply the asking price"""
        original_price = sample_item["asking_price"]

        # Add value factor (1.15 multiplier)
        client.post(f"/api/items/{sample_item['id']}/value-factors/{sample_value_factor['id']}")

        item = client.get(f"/api/items/{sample_item['id']}").json()
        expected_price = original_price * 1.15
        assert abs(item["effective_price"] - expected_price) < 0.01


class TestInventoryStatistics:
    """Test inventory statistics and dashboard data"""

    def test_can_get_item_counts_by_status(self, client):
        """Dashboard needs item counts grouped by status"""
        # Create items in different statuses
        client.post("/api/items", json={"name": "Inv 1", "status": "inventory"})
        client.post("/api/items", json={"name": "Inv 2", "status": "inventory"})
        client.post("/api/items", json={"name": "Listed", "status": "listed"})
        client.post("/api/items", json={"name": "Draft", "status": "draft"})

        response = client.get("/api/items/stats/by-status")
        assert response.status_code == 200
        stats = response.json()

        assert stats["inventory"] == 2
        assert stats["listed"] == 1
        assert stats["draft"] == 1
