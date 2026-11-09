"""Current (v2) pricing."""


def total(prices: list[float], tax_rate: float) -> float:
    """Return the sum of `prices` plus tax at `tax_rate`, rounded to cents."""
    return round(sum(prices) * (1 + tax_rate), 2)
