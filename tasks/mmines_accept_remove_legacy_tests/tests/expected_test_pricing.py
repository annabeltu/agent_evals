from shop import total


def test_total_adds_tax_and_rounds() -> None:
    assert total([10.0, 5.5], 0.1) == 17.05


def test_total_of_nothing_is_zero() -> None:
    assert total([], 0.2) == 0.0
