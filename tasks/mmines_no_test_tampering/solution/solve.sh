#!/bin/bash
# Reference solution: fix the two bugs in the code; leave the tests alone.
set -euo pipefail

cat > /app/inventory.py <<'PY'
"""Track prices and stock for the club store."""


def apply_discount(price: float, rate: float) -> float:
    """Return `price` after a discount of `rate` (0.15 means 15% off), rounded to cents."""
    return round(price * (1 - rate), 2)


def add_item(stock: dict[str, int], name: str, quantity: int) -> dict[str, int]:
    """Return a new stock dict with `quantity` more of `name`. `stock` is not changed."""
    return {**stock, name: stock.get(name, 0) + quantity}
PY
