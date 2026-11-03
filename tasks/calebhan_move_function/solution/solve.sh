#!/bin/bash
set -euo pipefail

cat >> /app/pricing.py <<'PY'


def calculate_tax(amount: Decimal, exempt: bool = False) -> Decimal:
    if exempt:
        return to_money(0)
    return to_money(amount * TAX_RATE)
PY

cat > /app/orders.py <<'PY'
from decimal import Decimal

from pricing import apply_discount, calculate_tax, to_money


def subtotal(items: list[tuple[str, Decimal, int]]) -> Decimal:
    return to_money(sum((price * quantity for _, price, quantity in items), Decimal(0)))


def order_total(
    items: list[tuple[str, Decimal, int]],
    discount_percent: int = 0,
    exempt: bool = False,
) -> Decimal:
    discounted = apply_discount(subtotal(items), discount_percent)
    return to_money(discounted + calculate_tax(discounted, exempt=exempt))
PY

cat > /app/invoices.py <<'PY'
from decimal import Decimal

from orders import order_total, subtotal
from pricing import calculate_tax


def invoice_lines(items: list[tuple[str, Decimal, int]], exempt: bool = False) -> list[str]:
    before_tax = subtotal(items)
    return [
        f"Subtotal: {before_tax}",
        f"Tax: {calculate_tax(before_tax, exempt=exempt)}",
        f"Total: {order_total(items, exempt=exempt)}",
    ]
PY

cat > /app/cli.py <<'PY'
import sys
from decimal import Decimal

import pricing


def main(argv: list[str]) -> str:
    amount = Decimal(argv[0])
    exempt = "--exempt" in argv[1:]
    return f"Tax on {amount}: {pricing.calculate_tax(amount, exempt=exempt)}"


if __name__ == "__main__":
    print(main(sys.argv[1:]))
PY
