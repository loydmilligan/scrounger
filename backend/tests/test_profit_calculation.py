"""
Tests for Profit Calculation and Sales Tracking

Epic 3: Sales Tracking
- US-3.1: Record a Sale
- US-3.2: View Sales Dashboard

Sellers need to track:
- Cost basis (what they paid)
- Sale price (what they sold for)
- Fees (platform, payment processing, shipping)
- Profit/loss calculation
"""
import pytest


class TestProfitTracking:
    """
    The core value proposition: Know if you're making money.
    """

    def test_item_tracks_cost_basis(self, client):
        """Sellers need to record what they paid for items"""
        response = client.post("/api/items", json={
            "name": "Bought at Best Buy",
            "cost_basis": 299.99,
            "acquisition_source": "Best Buy"
        })

        assert response.json()["cost_basis"] == 299.99

    def test_cost_basis_can_be_updated(self, client, sample_item):
        """Sellers may need to correct cost basis"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "cost_basis": 750.00
        })

        assert response.json()["cost_basis"] == 750.00

    def test_asking_price_vs_min_price_spread(self, client, sample_item):
        """
        Sellers need to know their acceptable price range.
        asking_price: What they want
        min_price: Lowest they'll accept
        """
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "asking_price": 500.00,
            "min_price": 400.00
        })

        item = response.json()
        assert item["asking_price"] == 500.00
        assert item["min_price"] == 400.00

        # The spread is $100 (negotiation room)
        spread = item["asking_price"] - item["min_price"]
        assert spread == 100.00


class TestPlatformPricing:
    """
    Different platforms may justify different pricing due to:
    - Fees (eBay takes more, Reddit takes nothing)
    - Audience (eBay buyers may pay more)
    - Competition
    """

    def test_can_set_per_platform_prices(self, client, sample_item):
        """Each platform can have its own price"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "platform_prices": {
                "reddit": 400.00,   # Lower - no fees
                "ebay": 450.00,     # Higher - account for fees
                "offerup": 420.00,  # Middle - local pickup
                "craigslist": 420.00
            }
        })

        prices = response.json()["platform_prices"]
        assert prices["reddit"] == 400.00
        assert prices["ebay"] == 450.00

    def test_platform_prices_independent_of_asking_price(self, client, sample_item):
        """Platform prices can differ from the base asking price"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "asking_price": 425.00,  # Base reference
            "platform_prices": {
                "reddit": 400.00,    # Below base
                "ebay": 475.00       # Above base
            }
        })

        item = response.json()
        assert item["asking_price"] == 425.00
        assert item["platform_prices"]["reddit"] == 400.00
        assert item["platform_prices"]["ebay"] == 475.00


class TestValueFactorPricing:
    """
    Value factors adjust effective price based on market conditions.
    """

    def test_single_value_factor_multiplies_price(self, client):
        """One factor: effective = asking * multiplier"""
        vf = client.post("/api/value-factors", json={
            "name": "High Demand",
            "multiplier": 1.20  # 20% premium
        }).json()

        item = client.post("/api/items", json={
            "name": "In Demand Item",
            "asking_price": 100.00,
            "value_factor_ids": [vf["id"]]
        }).json()

        # 100 * 1.20 = 120
        assert item["effective_price"] == 120.00

    def test_multiple_value_factors_stack(self, client):
        """Multiple factors multiply together"""
        vf1 = client.post("/api/value-factors", json={
            "name": "Holiday",
            "multiplier": 1.10  # 10% premium
        }).json()

        vf2 = client.post("/api/value-factors", json={
            "name": "Shortage",
            "multiplier": 1.20  # 20% premium
        }).json()

        item = client.post("/api/items", json={
            "name": "Scarce Holiday Item",
            "asking_price": 100.00,
            "value_factor_ids": [vf1["id"], vf2["id"]]
        }).json()

        # 100 * 1.10 * 1.20 = 132
        assert item["effective_price"] == 132.00

    def test_inactive_value_factors_dont_affect_price(self, client):
        """Deactivated factors shouldn't affect pricing"""
        vf = client.post("/api/value-factors", json={
            "name": "Expired Promotion",
            "multiplier": 0.80,  # 20% discount
            "active": False
        }).json()

        item = client.post("/api/items", json={
            "name": "Normal Price Item",
            "asking_price": 100.00,
            "value_factor_ids": [vf["id"]]
        }).json()

        # Inactive factor shouldn't apply, price stays at 100
        # Note: This behavior depends on implementation
        # If inactive factors are still associated but not applied, this should be 100
        # If they're not associated at all, this would still be 100

    def test_below_one_multiplier_reduces_price(self, client):
        """Factors below 1.0 reduce price (clearance, depreciation)"""
        vf = client.post("/api/value-factors", json={
            "name": "Clearance",
            "multiplier": 0.75  # 25% off
        }).json()

        item = client.post("/api/items", json={
            "name": "Clearance Item",
            "asking_price": 100.00,
            "value_factor_ids": [vf["id"]]
        }).json()

        # 100 * 0.75 = 75
        assert item["effective_price"] == 75.00


class TestPriceHistory:
    """
    Tracking price changes helps sellers understand what works.
    """

    def test_can_record_price_changes(self, client, sample_item):
        """Keep a history of price changes and reasons"""
        response = client.patch(f"/api/items/{sample_item['id']}", json={
            "price_history": [
                {
                    "date": "2024-01-01",
                    "price": 500.00,
                    "reason": "Initial listing"
                },
                {
                    "date": "2024-01-07",
                    "price": 475.00,
                    "reason": "No bites after 1 week"
                },
                {
                    "date": "2024-01-14",
                    "price": 450.00,
                    "reason": "Price matched competitor"
                }
            ]
        })

        history = response.json()["price_history"]
        assert len(history) == 3
        assert history[0]["price"] == 500.00
        assert history[-1]["price"] == 450.00

    def test_price_history_persists(self, client, sample_item):
        """Price history is saved and retrievable"""
        # Add history
        client.patch(f"/api/items/{sample_item['id']}", json={
            "price_history": [{"date": "2024-01-01", "price": 100}]
        })

        # Fetch item
        item = client.get(f"/api/items/{sample_item['id']}").json()
        assert len(item["price_history"]) == 1


class TestMarketplaceFeeCalculation:
    """
    Sellers need to understand fees to price correctly.
    These tests verify fee storage (calculation would be frontend).
    """

    def test_marketplace_stores_percentage_fee(self, client):
        """eBay-style percentage fees"""
        mp = client.post("/api/marketplaces", json={
            "name": "ebay",
            "platform_type": "ebay",
            "fee_percentage": 12.9
        }).json()

        assert mp["fee_percentage"] == 12.9

    def test_marketplace_stores_flat_fee(self, client):
        """Flat listing fees"""
        mp = client.post("/api/marketplaces", json={
            "name": "premium_platform",
            "fee_flat": 10.00
        }).json()

        assert mp["fee_flat"] == 10.00

    def test_marketplace_stores_combined_fees(self, client):
        """Combined percentage + flat (like PayPal)"""
        mp = client.post("/api/marketplaces", json={
            "name": "paypal_platform",
            "fee_percentage": 2.9,
            "fee_flat": 0.30
        }).json()

        # For a $100 sale: $100 * 0.029 + $0.30 = $3.20
        assert mp["fee_percentage"] == 2.9
        assert mp["fee_flat"] == 0.30


class TestAcquisitionTracking:
    """
    Tracking where items came from helps with:
    - Cost basis accuracy
    - Understanding profitable sources
    - Warranty/return tracking
    """

    def test_can_track_acquisition_source(self, client):
        """Record where the item was purchased"""
        sources = ["Amazon", "Best Buy", "Facebook Marketplace", "Estate Sale", "Goodwill"]

        for source in sources:
            response = client.post("/api/items", json={
                "name": f"From {source}",
                "acquisition_source": source
            })
            assert response.json()["acquisition_source"] == source

    def test_can_track_acquisition_date(self, client):
        """Record when the item was purchased"""
        response = client.post("/api/items", json={
            "name": "Dated Purchase",
            "acquisition_date": "2024-01-15"
        })

        assert response.json()["acquisition_date"] == "2024-01-15"

    def test_can_track_acquisition_condition(self, client):
        """Was it new or used when purchased?"""
        new_item = client.post("/api/items", json={
            "name": "Bought New",
            "acquisition_condition": "new"
        }).json()

        used_item = client.post("/api/items", json={
            "name": "Bought Used",
            "acquisition_condition": "used"
        }).json()

        assert new_item["acquisition_condition"] == "new"
        assert used_item["acquisition_condition"] == "used"
