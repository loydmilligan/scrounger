"""
Tests for Item Organization Features

Sellers need to organize their inventory using:
- Categories: Group similar items (Electronics, Clothing, etc.)
- Tags: Flexible labels for any purpose (urgent, bundle-ready, etc.)
- Value Factors: Market conditions that affect pricing
"""
import pytest


class TestCategories:
    """
    Categories help organize inventory by type.
    Each item belongs to one category.
    """

    def test_can_create_category(self, client):
        """Sellers can create categories for their items"""
        response = client.post("/api/categories", json={
            "name": "graphics_cards",
            "display_name": "Graphics Cards",
            "description": "GPUs and video cards"
        })

        assert response.status_code == 200
        cat = response.json()
        assert cat["name"] == "graphics_cards"
        assert cat["display_name"] == "Graphics Cards"

    def test_category_names_must_be_unique(self, client):
        """Can't have duplicate category names"""
        client.post("/api/categories", json={"name": "unique_cat"})

        response = client.post("/api/categories", json={"name": "unique_cat"})
        assert response.status_code == 400

    def test_categories_track_item_count(self, client, sample_category):
        """Categories should show how many items they contain"""
        # Initially empty
        cat = client.get(f"/api/categories/{sample_category['id']}").json()
        assert cat["item_count"] == 0

        # Add items
        client.post("/api/items", json={
            "name": "Item 1",
            "category_id": sample_category["id"]
        })
        client.post("/api/items", json={
            "name": "Item 2",
            "category_id": sample_category["id"]
        })

        cat = client.get(f"/api/categories/{sample_category['id']}").json()
        assert cat["item_count"] == 2

    def test_cannot_delete_category_with_items(self, client, sample_category):
        """Prevent accidental deletion of categories that have items"""
        # Add an item
        client.post("/api/items", json={
            "name": "Item in category",
            "category_id": sample_category["id"]
        })

        # Try to delete
        response = client.delete(f"/api/categories/{sample_category['id']}")
        assert response.status_code == 400
        assert "item(s)" in response.json()["detail"]

    def test_categories_can_have_icons(self, client):
        """Categories can have emoji icons for display"""
        response = client.post("/api/categories", json={
            "name": "computers",
            "display_name": "Computers",
            "icon": "💻"
        })

        assert response.json()["icon"] == "💻"

    def test_categories_can_be_sorted(self, client):
        """Categories have a sort order for display"""
        client.post("/api/categories", json={"name": "z_last", "sort_order": 99})
        client.post("/api/categories", json={"name": "a_first", "sort_order": 1})
        client.post("/api/categories", json={"name": "m_middle", "sort_order": 50})

        response = client.get("/api/categories")
        categories = response.json()["categories"]

        # Should be sorted by sort_order
        assert categories[0]["name"] == "a_first"
        assert categories[1]["name"] == "m_middle"
        assert categories[2]["name"] == "z_last"


class TestTags:
    """
    Tags are flexible labels that can be applied to items.
    Items can have multiple tags.
    """

    def test_can_create_tag(self, client):
        """Sellers can create tags to organize items"""
        response = client.post("/api/tags", json={
            "name": "needs-testing",
            "color": "#FF5733"
        })

        assert response.status_code == 200
        tag = response.json()
        assert tag["name"] == "needs-testing"
        assert tag["color"] == "#FF5733"

    def test_tag_names_must_be_unique(self, client):
        """Can't have duplicate tag names"""
        client.post("/api/tags", json={"name": "duplicate-tag"})

        response = client.post("/api/tags", json={"name": "duplicate-tag"})
        assert response.status_code == 400

    def test_tags_have_default_color(self, client):
        """Tags default to blue if no color specified"""
        response = client.post("/api/tags", json={"name": "no-color"})

        tag = response.json()
        assert tag["color"] is not None

    def test_tags_track_item_count(self, client, sample_tag, sample_category):
        """Tags should show how many items use them"""
        # Create items and add tag
        item1 = client.post("/api/items", json={
            "name": "Item 1",
            "tag_ids": [sample_tag["id"]]
        }).json()
        item2 = client.post("/api/items", json={
            "name": "Item 2",
            "tag_ids": [sample_tag["id"]]
        }).json()

        tag = client.get(f"/api/tags/{sample_tag['id']}").json()
        assert tag["item_count"] == 2

    def test_item_can_have_multiple_tags(self, client):
        """Items can be tagged with multiple tags"""
        tag1 = client.post("/api/tags", json={"name": "urgent"}).json()
        tag2 = client.post("/api/tags", json={"name": "local-only"}).json()
        tag3 = client.post("/api/tags", json={"name": "firm-price"}).json()

        response = client.post("/api/items", json={
            "name": "Multi-tagged Item",
            "tag_ids": [tag1["id"], tag2["id"], tag3["id"]]
        })

        item = response.json()
        assert len(item["tags"]) == 3

    def test_can_delete_tag_even_if_used(self, client, sample_tag):
        """Deleting a tag should work (removes association)"""
        # Add tag to item
        client.post("/api/items", json={
            "name": "Tagged Item",
            "tag_ids": [sample_tag["id"]]
        })

        # Delete tag
        response = client.delete(f"/api/tags/{sample_tag['id']}")
        assert response.status_code == 200


class TestValueFactors:
    """
    Value factors are market conditions that affect item pricing.
    They multiply the base price (e.g., 1.15 for holiday season).
    """

    def test_can_create_value_factor(self, client):
        """Sellers can create value factors to adjust pricing"""
        response = client.post("/api/value-factors", json={
            "name": "Holiday Demand",
            "description": "Increased demand during holiday season",
            "multiplier": 1.20,
            "active": True
        })

        assert response.status_code == 200
        vf = response.json()
        assert vf["name"] == "Holiday Demand"
        assert vf["multiplier"] == 1.20
        assert vf["active"] is True

    def test_value_factor_names_must_be_unique(self, client):
        """Can't have duplicate value factor names"""
        client.post("/api/value-factors", json={
            "name": "duplicate-factor",
            "multiplier": 1.0
        })

        response = client.post("/api/value-factors", json={
            "name": "duplicate-factor",
            "multiplier": 1.5
        })
        assert response.status_code == 400

    def test_can_deactivate_value_factor(self, client, sample_value_factor):
        """Value factors can be turned off without deleting"""
        response = client.patch(
            f"/api/value-factors/{sample_value_factor['id']}",
            json={"active": False}
        )

        assert response.json()["active"] is False

    def test_can_filter_active_value_factors(self, client):
        """Show only active value factors"""
        client.post("/api/value-factors", json={
            "name": "Active Factor",
            "multiplier": 1.1,
            "active": True
        })
        client.post("/api/value-factors", json={
            "name": "Inactive Factor",
            "multiplier": 0.9,
            "active": False
        })

        response = client.get("/api/value-factors?active_only=true")
        factors = response.json()["value_factors"]
        assert len(factors) == 1
        assert factors[0]["name"] == "Active Factor"

    def test_value_factors_track_item_count(self, client, sample_value_factor):
        """Value factors show how many items they affect"""
        # Create items with value factor
        client.post("/api/items", json={
            "name": "Item 1",
            "asking_price": 100,
            "value_factor_ids": [sample_value_factor["id"]]
        })
        client.post("/api/items", json={
            "name": "Item 2",
            "asking_price": 200,
            "value_factor_ids": [sample_value_factor["id"]]
        })

        vf = client.get(f"/api/value-factors/{sample_value_factor['id']}").json()
        assert vf["item_count"] == 2

    def test_item_can_have_multiple_value_factors(self, client):
        """Multiple factors can stack on an item"""
        vf1 = client.post("/api/value-factors", json={
            "name": "Holiday",
            "multiplier": 1.10
        }).json()
        vf2 = client.post("/api/value-factors", json={
            "name": "Shortage",
            "multiplier": 1.15
        }).json()

        response = client.post("/api/items", json={
            "name": "High Demand Item",
            "asking_price": 100,
            "value_factor_ids": [vf1["id"], vf2["id"]]
        })

        item = response.json()
        assert len(item["value_factors"]) == 2

    def test_effective_price_applies_value_factors(self, client, sample_value_factor):
        """
        effective_price = asking_price * multiplier1 * multiplier2 * ...
        """
        # sample_value_factor has multiplier 1.15
        response = client.post("/api/items", json={
            "name": "Priced Item",
            "asking_price": 100.00,
            "value_factor_ids": [sample_value_factor["id"]]
        })

        item = response.json()
        # 100 * 1.15 = 115
        assert item["effective_price"] == 115.00


class TestCombinedOrganization:
    """
    Test how categories, tags, and value factors work together.
    """

    def test_item_can_have_category_tags_and_value_factors(self, client):
        """Items can use all organization features together"""
        category = client.post("/api/categories", json={
            "name": "gpus",
            "display_name": "Graphics Cards"
        }).json()

        tag = client.post("/api/tags", json={
            "name": "high-demand"
        }).json()

        vf = client.post("/api/value-factors", json={
            "name": "GPU Shortage",
            "multiplier": 1.25
        }).json()

        response = client.post("/api/items", json={
            "name": "RTX 4090",
            "category_id": category["id"],
            "asking_price": 1600,
            "tag_ids": [tag["id"]],
            "value_factor_ids": [vf["id"]]
        })

        item = response.json()
        assert item["category"]["name"] == "gpus"
        assert len(item["tags"]) == 1
        assert len(item["value_factors"]) == 1
        assert item["effective_price"] == 2000.00  # 1600 * 1.25

    def test_can_filter_items_by_tag(self, client):
        """Find items with specific tags"""
        urgent = client.post("/api/tags", json={"name": "urgent"}).json()
        lowprio = client.post("/api/tags", json={"name": "low-priority"}).json()

        client.post("/api/items", json={
            "name": "Urgent Item",
            "tag_ids": [urgent["id"]]
        })
        client.post("/api/items", json={
            "name": "Normal Item",
            "tag_ids": [lowprio["id"]]
        })

        response = client.get(f"/api/items?tag_id={urgent['id']}")
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["name"] == "Urgent Item"
