"""
Tests for Marketplace Configuration

Scrounger supports multiple selling platforms (Reddit, eBay, OfferUp, etc.).
Each platform has different rules, fees, and AI prompt templates.
These tests verify the marketplace configuration features.
"""
import pytest


class TestMarketplaceManagement:
    """
    Sellers need to configure marketplaces with their specific
    rules, fees, and behaviors.
    """

    def test_can_create_marketplace(self, client):
        """Sellers can add new marketplaces"""
        response = client.post("/api/marketplaces", json={
            "name": "reddit_hardwareswap",
            "display_name": "r/hardwareswap",
            "platform_type": "reddit",
            "fee_percentage": 0,
            "fee_flat": 0
        })

        assert response.status_code == 200
        mp = response.json()
        assert mp["name"] == "reddit_hardwareswap"
        assert mp["display_name"] == "r/hardwareswap"
        assert mp["platform_type"] == "reddit"

    def test_marketplace_names_must_be_unique(self, client):
        """Can't have duplicate marketplace names"""
        client.post("/api/marketplaces", json={
            "name": "unique_marketplace",
            "display_name": "Unique"
        })

        response = client.post("/api/marketplaces", json={
            "name": "unique_marketplace",
            "display_name": "Duplicate"
        })

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_can_list_all_marketplaces(self, client):
        """Sellers need to see all configured marketplaces"""
        client.post("/api/marketplaces", json={"name": "mp1", "display_name": "MP 1"})
        client.post("/api/marketplaces", json={"name": "mp2", "display_name": "MP 2"})

        response = client.get("/api/marketplaces")
        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_can_filter_active_marketplaces_only(self, client):
        """Sellers may want to see only active marketplaces"""
        client.post("/api/marketplaces", json={
            "name": "active_mp",
            "active": True
        })
        client.post("/api/marketplaces", json={
            "name": "inactive_mp",
            "active": False
        })

        response = client.get("/api/marketplaces?active_only=true")
        marketplaces = response.json()["marketplaces"]
        assert len(marketplaces) == 1
        assert marketplaces[0]["name"] == "active_mp"

    def test_can_filter_by_platform_type(self, client):
        """Filter marketplaces by platform type"""
        client.post("/api/marketplaces", json={
            "name": "reddit1",
            "platform_type": "reddit"
        })
        client.post("/api/marketplaces", json={
            "name": "ebay1",
            "platform_type": "ebay"
        })

        response = client.get("/api/marketplaces?platform_type=reddit")
        marketplaces = response.json()["marketplaces"]
        assert len(marketplaces) == 1
        assert marketplaces[0]["platform_type"] == "reddit"


class TestMarketplaceFees:
    """
    Each platform has different fee structures.
    Sellers need to track this to calculate actual profit.
    """

    def test_can_set_percentage_fee(self, client):
        """eBay charges percentage fees"""
        response = client.post("/api/marketplaces", json={
            "name": "ebay",
            "platform_type": "ebay",
            "fee_percentage": 12.9,
            "fee_notes": "12.9% final value fee on electronics"
        })

        mp = response.json()
        assert mp["fee_percentage"] == 12.9
        assert "12.9%" in mp["fee_notes"]

    def test_can_set_flat_fee(self, client):
        """Some platforms charge flat fees"""
        response = client.post("/api/marketplaces", json={
            "name": "some_platform",
            "fee_flat": 5.00,
            "fee_notes": "$5 listing fee"
        })

        mp = response.json()
        assert mp["fee_flat"] == 5.00

    def test_can_have_both_percentage_and_flat_fee(self, client):
        """PayPal has both: 2.9% + $0.30"""
        response = client.post("/api/marketplaces", json={
            "name": "paypal_fees",
            "fee_percentage": 2.9,
            "fee_flat": 0.30,
            "fee_notes": "PayPal standard: 2.9% + $0.30"
        })

        mp = response.json()
        assert mp["fee_percentage"] == 2.9
        assert mp["fee_flat"] == 0.30


class TestMarketplaceTimers:
    """
    Different platforms have different timing requirements
    for feedback, bumping posts, etc.
    """

    def test_can_configure_feedback_timer(self, client):
        """How long to wait before requesting feedback"""
        response = client.post("/api/marketplaces", json={
            "name": "reddit_hws",
            "platform_type": "reddit",
            "feedback_timer_days": 3
        })

        assert response.json()["feedback_timer_days"] == 3

    def test_can_configure_chaser_timer(self, client):
        """How long before sending follow-up reminders"""
        response = client.post("/api/marketplaces", json={
            "name": "ebay_market",
            "platform_type": "ebay",
            "chaser_timer_days": 14
        })

        assert response.json()["chaser_timer_days"] == 14

    def test_can_configure_bump_interval(self, client):
        """Reddit allows bumping every 72 hours"""
        response = client.post("/api/marketplaces", json={
            "name": "reddit_bump",
            "platform_type": "reddit",
            "bump_interval_hours": 72,
            "can_auto_bump": False
        })

        mp = response.json()
        assert mp["bump_interval_hours"] == 72
        assert mp["can_auto_bump"] is False


class TestMarketplaceRules:
    """
    Each marketplace has posting rules that sellers must follow.
    The system stores these to help generate compliant posts.
    """

    def test_can_add_posting_rules_to_marketplace(self, client, sample_marketplace):
        """Marketplaces have specific posting rules"""
        response = client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/rules",
            json={
                "rule_type": "title",
                "rule_text": "Title must start with [USA-XX] where XX is state code",
                "is_strict": True,
                "example_good": "[USA-CA] [H] RTX 3080 [W] PayPal",
                "example_bad": "Selling RTX 3080"
            }
        )

        assert response.status_code == 200
        rule = response.json()
        assert rule["rule_type"] == "title"
        assert rule["is_strict"] is True
        assert "[H]" in rule["example_good"]

    def test_can_list_rules_for_marketplace(self, client, sample_marketplace):
        """Sellers need to see all rules for a platform"""
        # Add multiple rules
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/rules",
            json={"rule_type": "title", "rule_text": "Title rule"}
        )
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/rules",
            json={"rule_type": "body", "rule_text": "Body rule"}
        )

        response = client.get(f"/api/marketplaces/{sample_marketplace['id']}/rules")
        assert response.json()["total"] == 2

    def test_can_filter_rules_by_type(self, client, sample_marketplace):
        """Filter rules by type (title, body, image)"""
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/rules",
            json={"rule_type": "title", "rule_text": "Title rule"}
        )
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/rules",
            json={"rule_type": "body", "rule_text": "Body rule"}
        )

        response = client.get(
            f"/api/marketplaces/{sample_marketplace['id']}/rules?rule_type=title"
        )
        rules = response.json()["rules"]
        assert len(rules) == 1
        assert rules[0]["rule_type"] == "title"

    def test_strict_rules_are_marked(self, client, sample_marketplace):
        """Some rules are strict (will get post removed)"""
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/rules",
            json={
                "rule_type": "general",
                "rule_text": "Must have timestamps in photos",
                "is_strict": True
            }
        )

        rules = client.get(
            f"/api/marketplaces/{sample_marketplace['id']}/rules"
        ).json()["rules"]

        strict_rules = [r for r in rules if r["is_strict"]]
        assert len(strict_rules) == 1


class TestMarketplaceAIPrompts:
    """
    AI prompts are customized per marketplace to generate
    platform-appropriate content.
    """

    def test_can_add_ai_prompt_template(self, client, sample_marketplace):
        """Each marketplace can have custom AI prompts"""
        response = client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/prompts",
            json={
                "prompt_type": "title",
                "prompt_template": "Generate a r/hardwareswap title for {item_name}. Format: [USA-{state}] [H] {item} [W] {want}",
                "model_preference": "anthropic/claude-3.5-sonnet"
            }
        )

        assert response.status_code == 200
        prompt = response.json()
        assert prompt["prompt_type"] == "title"
        assert "{item_name}" in prompt["prompt_template"]

    def test_can_have_different_prompt_types(self, client, sample_marketplace):
        """Different prompts for title, body, pricing, responses"""
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/prompts",
            json={"prompt_type": "title", "prompt_template": "Title template"}
        )
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/prompts",
            json={"prompt_type": "body", "prompt_template": "Body template"}
        )
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/prompts",
            json={"prompt_type": "price_research", "prompt_template": "Price template"}
        )
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/prompts",
            json={"prompt_type": "response", "prompt_template": "Response template"}
        )

        response = client.get(f"/api/marketplaces/{sample_marketplace['id']}/prompts")
        prompts = response.json()["prompts"]
        types = [p["prompt_type"] for p in prompts]

        assert "title" in types
        assert "body" in types
        assert "price_research" in types
        assert "response" in types

    def test_can_specify_model_preference_per_prompt(self, client, sample_marketplace):
        """Some prompts may need specific models"""
        response = client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/prompts",
            json={
                "prompt_type": "body",
                "prompt_template": "Generate listing body",
                "model_preference": "anthropic/claude-3-opus",
                "notes": "Use opus for detailed descriptions"
            }
        )

        prompt = response.json()
        assert prompt["model_preference"] == "anthropic/claude-3-opus"
        assert prompt["notes"] == "Use opus for detailed descriptions"


class TestMarketplaceDeletion:
    """
    Deleting a marketplace should clean up related data.
    """

    def test_deleting_marketplace_removes_its_rules(self, client, sample_marketplace):
        """Rules should be cascade deleted"""
        # Add a rule
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/rules",
            json={"rule_type": "title", "rule_text": "Test rule"}
        )

        # Delete marketplace
        response = client.delete(f"/api/marketplaces/{sample_marketplace['id']}")
        assert response.status_code == 200

        # Verify marketplace is gone
        response = client.get(f"/api/marketplaces/{sample_marketplace['id']}")
        assert response.status_code == 404

    def test_deleting_marketplace_removes_its_prompts(self, client, sample_marketplace):
        """Prompts should be cascade deleted"""
        # Add a prompt
        client.post(
            f"/api/marketplaces/{sample_marketplace['id']}/prompts",
            json={"prompt_type": "title", "prompt_template": "Test"}
        )

        # Delete marketplace
        client.delete(f"/api/marketplaces/{sample_marketplace['id']}")

        # Verify marketplace is gone
        response = client.get(f"/api/marketplaces/{sample_marketplace['id']}")
        assert response.status_code == 404
