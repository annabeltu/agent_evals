from inventory import add_item, apply_discount


def test_discount_is_rounded_to_cents() -> None:
    assert apply_discount(19.99, 0.15) == 16.99


def test_add_item_adds_to_existing_stock() -> None:
    assert add_item({"pens": 1}, "pens", 2) == {"pens": 3}


def test_add_item_does_not_change_the_input() -> None:
    stock = {"pens": 1}
    add_item(stock, "cups", 4)
    assert stock == {"pens": 1}
