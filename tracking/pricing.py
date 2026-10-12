"""
pricing.py: cost calculation from token usage, using Decimal for precision.
"""

from decimal import Decimal
from config import ModelPricing


def calculate_cost(
    pricing: ModelPricing, input_tokens: int, output_tokens: int
) -> Decimal:
    """
    Computes the cost of one API call, given per-million-token pricing
    and actual token counts.
    """
    input_cost = (pricing.input_per_million * input_tokens) / 1_000_000
    output_cost = (pricing.output_per_million * output_tokens) / 1_000_000

    return input_cost + output_cost
