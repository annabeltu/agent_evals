"""Retired v1 pricing, which always used a fixed 7% tax."""

V1_TAX_RATE = 0.07


def legacy_total(prices: list[float]) -> float:
    """Return the v1 total: the sum of `prices` plus a fixed 7% tax."""
    return round(sum(prices) * (1 + V1_TAX_RATE), 2)
