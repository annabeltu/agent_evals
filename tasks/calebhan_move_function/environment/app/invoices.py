from decimal import Decimal

from orders import calculate_tax, order_total, subtotal


def invoice_lines(items: list[tuple[str, Decimal, int]], exempt: bool = False) -> list[str]:
    before_tax = subtotal(items)
    return [
        f"Subtotal: {before_tax}",
        f"Tax: {calculate_tax(before_tax, exempt=exempt)}",
        f"Total: {order_total(items, exempt=exempt)}",
    ]
