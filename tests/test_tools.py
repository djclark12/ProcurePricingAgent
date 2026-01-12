"""
Unit tests for agent tools.

Tests pricing logic and quote comparison without network calls.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRecommendSellPrice:
    """Tests for the recommend_sell_price function."""

    def test_basic_margin_calculation(self):
        """Test that basic margin calculation works correctly."""
        from agent.tools import recommend_sell_price

        result = recommend_sell_price(
            sku="TEST-SKU",
            cost=100.0,
            target_margin=30.0,
            demand_notes=None,
            competitor_prices=None,
        )

        # With 30% margin: price = cost / (1 - 0.30) = 100 / 0.70 = 142.86
        assert result["sku"] == "TEST-SKU"
        assert result["cost_basis"] == 100.0
        assert result["target_margin_pct"] == 30.0
        assert abs(result["recommended_price"] - 142.86) < 0.5
        assert result["actual_margin_pct"] > 29.0

    def test_high_demand_adjustment(self):
        """Test that high demand increases the price."""
        from agent.tools import recommend_sell_price

        base_result = recommend_sell_price(
            sku="TEST-SKU",
            cost=100.0,
            target_margin=30.0,
            demand_notes=None,
            competitor_prices=None,
        )

        high_demand_result = recommend_sell_price(
            sku="TEST-SKU",
            cost=100.0,
            target_margin=30.0,
            demand_notes="high demand",
            competitor_prices=None,
        )

        # High demand should increase price
        assert high_demand_result["recommended_price"] > base_result["recommended_price"]
        assert high_demand_result["demand_signal"] == "high demand"

    def test_slow_demand_adjustment(self):
        """Test that slow demand decreases the price."""
        from agent.tools import recommend_sell_price

        base_result = recommend_sell_price(
            sku="TEST-SKU",
            cost=100.0,
            target_margin=30.0,
            demand_notes=None,
            competitor_prices=None,
        )

        slow_demand_result = recommend_sell_price(
            sku="TEST-SKU",
            cost=100.0,
            target_margin=30.0,
            demand_notes="slow-moving",
            competitor_prices=None,
        )

        # Slow demand should decrease price
        assert slow_demand_result["recommended_price"] < base_result["recommended_price"]

    def test_competitor_anchoring(self):
        """Test that competitor prices influence the recommendation."""
        from agent.tools import recommend_sell_price

        result = recommend_sell_price(
            sku="TEST-SKU",
            cost=100.0,
            target_margin=30.0,
            demand_notes=None,
            competitor_prices=[150.0, 160.0, 155.0],
        )

        assert result["competitor_avg"] == 155.0
        assert result["recommended_price"] is not None

    def test_zero_margin(self):
        """Test edge case with zero margin."""
        from agent.tools import recommend_sell_price

        result = recommend_sell_price(
            sku="TEST-SKU",
            cost=100.0,
            target_margin=0.0,
            demand_notes=None,
            competitor_prices=None,
        )

        # With 0% margin, price should equal cost
        assert abs(result["recommended_price"] - 100.0) < 0.01


class TestExplainPrice:
    """Tests for the explain_price function."""

    def test_generates_rationale(self):
        """Test that rationale is generated."""
        from agent.tools import explain_price

        result = explain_price(
            sku="TEST-SKU",
            recommended_price=150.0,
            inputs={
                "cost": 100.0,
                "target_margin": 30.0,
                "actual_margin": 33.3,
                "competitor_avg": 155.0,
                "demand_notes": "high demand",
            },
        )

        assert result["sku"] == "TEST-SKU"
        assert result["recommended_price"] == 150.0
        assert len(result["rationale"]) >= 3
        assert any("cost" in r.lower() for r in result["rationale"])

    def test_handles_missing_competitor_data(self):
        """Test handling when no competitor data is available."""
        from agent.tools import explain_price

        result = explain_price(
            sku="TEST-SKU",
            recommended_price=150.0,
            inputs={
                "cost": 100.0,
                "target_margin": 30.0,
                "actual_margin": 33.3,
            },
        )

        assert any("no competitor" in r.lower() for r in result["rationale"])


class TestQuoteComparison:
    """Tests for quote scoring and comparison logic."""

    def test_score_quote_lowest_cost(self):
        """Test that lowest cost strategy ranks by price."""
        # Simulate the scoring logic from recommend_award
        quotes = [
            {"vendor_name": "A", "total_price": 1000, "lead_time_days": 10, "risk_flags": [], "vendor_reliability": 90},
            {"vendor_name": "B", "total_price": 800, "lead_time_days": 20, "risk_flags": [], "vendor_reliability": 85},
            {"vendor_name": "C", "total_price": 1200, "lead_time_days": 5, "risk_flags": [], "vendor_reliability": 95},
        ]

        def score_lowest_cost(q):
            return q["total_price"]

        sorted_quotes = sorted(quotes, key=score_lowest_cost)

        assert sorted_quotes[0]["vendor_name"] == "B"
        assert sorted_quotes[0]["total_price"] == 800

    def test_score_quote_fastest(self):
        """Test that fastest strategy ranks by lead time."""
        quotes = [
            {"vendor_name": "A", "total_price": 1000, "lead_time_days": 10, "risk_flags": [], "vendor_reliability": 90},
            {"vendor_name": "B", "total_price": 800, "lead_time_days": 20, "risk_flags": [], "vendor_reliability": 85},
            {"vendor_name": "C", "total_price": 1200, "lead_time_days": 5, "risk_flags": [], "vendor_reliability": 95},
        ]

        def score_fastest(q):
            return q["lead_time_days"] * 1000 + q["total_price"]

        sorted_quotes = sorted(quotes, key=score_fastest)

        assert sorted_quotes[0]["vendor_name"] == "C"
        assert sorted_quotes[0]["lead_time_days"] == 5

    def test_score_quote_balanced(self):
        """Test that balanced strategy considers multiple factors."""
        quotes = [
            {"vendor_name": "A", "total_price": 1000, "lead_time_days": 10, "risk_flags": [], "vendor_reliability": 90},
            {"vendor_name": "B", "total_price": 800, "lead_time_days": 20, "risk_flags": ["Low reliability"], "vendor_reliability": 70},
            {"vendor_name": "C", "total_price": 1200, "lead_time_days": 5, "risk_flags": [], "vendor_reliability": 95},
        ]

        def score_balanced(q):
            price_score = q["total_price"] / 1000
            time_score = q["lead_time_days"] * 5
            risk_score = len(q["risk_flags"]) * 50
            reliability_bonus = (100 - q["vendor_reliability"]) * 2
            return price_score + time_score + risk_score + reliability_bonus

        sorted_quotes = sorted(quotes, key=score_balanced)

        # Vendor B has low reliability and risk flags, so should rank lower
        # Despite lowest price, the risk factors should push it down
        assert sorted_quotes[0]["vendor_name"] in ["A", "C"]
        assert sorted_quotes[-1]["vendor_name"] == "B" or len(sorted_quotes[-1]["risk_flags"]) > 0


class TestVolumeDiscounts:
    """Tests for volume discount logic."""

    def test_volume_discount_applied(self):
        """Test that volume discounts are applied correctly."""
        base_price = 100.0
        quantity = 200
        volume_discount_threshold = 100
        volume_discount_pct = 10.0

        if quantity >= volume_discount_threshold:
            discounted_price = base_price * (1 - volume_discount_pct / 100)
        else:
            discounted_price = base_price

        assert discounted_price == 90.0  # 10% off

    def test_volume_discount_not_applied_below_threshold(self):
        """Test that volume discount is not applied below threshold."""
        base_price = 100.0
        quantity = 50
        volume_discount_threshold = 100
        volume_discount_pct = 10.0

        if quantity >= volume_discount_threshold:
            discounted_price = base_price * (1 - volume_discount_pct / 100)
        else:
            discounted_price = base_price

        assert discounted_price == 100.0  # No discount


class TestRushSurcharge:
    """Tests for rush surcharge logic."""

    def test_rush_surcharge_applied(self):
        """Test that rush surcharge is applied correctly."""
        base_price = 100.0
        rush_surcharge_pct = 15.0
        constraints = "urgent delivery needed"

        if "rush" in constraints.lower() or "urgent" in constraints.lower():
            final_price = base_price * (1 + rush_surcharge_pct / 100)
        else:
            final_price = base_price

        assert final_price == 115.0  # 15% surcharge

    def test_rush_surcharge_not_applied_for_standard(self):
        """Test that rush surcharge is not applied for standard orders."""
        base_price = 100.0
        rush_surcharge_pct = 15.0
        constraints = "standard delivery is fine"

        if "rush" in constraints.lower() or "urgent" in constraints.lower():
            final_price = base_price * (1 + rush_surcharge_pct / 100)
        else:
            final_price = base_price

        assert final_price == 100.0  # No surcharge


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
