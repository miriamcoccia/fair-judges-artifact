"""
test_pricing.py
"""

from decimal import Decimal
from tracking.pricing import calculate_cost
from config import ModelPricing


def test_calculate_cost():
    pricing = ModelPricing(
        input_per_million=Decimal("2.5"), output_per_million=Decimal("15.0")
    )
    cost = calculate_cost(pricing, input_tokens=1_000_000, output_tokens=1_000_000)
    assert cost == Decimal("17.5")
