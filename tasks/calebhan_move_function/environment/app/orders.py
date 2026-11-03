from decimal import Decimal

from pricing import TAX_RATE, apply_discount, to_money


def calculate_tax(amount: Decimal, exempt: bool = False) -> Decimal:
    if exempt:
        return to_money(0)
    return to_money(amount * TAX_RATE)


def subtotal(items: list[tuple[str, Decimal, int]]) -> Decimal:
    return to_money(sum((price * quantity for _, price, quantity in items), Decimal(0)))


def order_total(
    items: list[tuple[str, Decimal, int]],
    discount_percent: int = 0,
    exempt: bool = False,
) -> Decimal:
    discounted = apply_discount(subtotal(items), discount_percent)
    return to_money(discounted + calculate_tax(discounted, exempt=exempt))
