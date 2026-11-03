from decimal import ROUND_HALF_UP, Decimal

TAX_RATE = Decimal("0.0725")
CENTS = Decimal("0.01")


def to_money(value: Decimal | int | str) -> Decimal:
    return Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)


def apply_discount(subtotal: Decimal, percent: int) -> Decimal:
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return to_money(subtotal * (100 - percent) / 100)
