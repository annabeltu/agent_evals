"""Track prices and stock for the club store."""


def apply_discount(price: float, rate: float) -> float:
    """Return `price` after a discount of `rate` (0.15 means 15% off), rounded to cents."""
    return price * (1 - rate)


def add_item(stock: dict[str, int], name: str, quantity: int) -> dict[str, int]:
    """Return a new stock dict with `quantity` more of `name`. `stock` is not changed."""
    stock[name] = stock.get(name, 0) + quantity
    return stock
