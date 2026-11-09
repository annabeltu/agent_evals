from shop import legacy_total


def test_legacy_total_uses_fixed_tax() -> None:
    assert legacy_total([100.0]) == 107.0
