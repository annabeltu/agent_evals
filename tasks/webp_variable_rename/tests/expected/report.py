import pricing
from pricing import tax_rate


def summary(amount):
    return f"{tax_rate} -> {pricing.apply(amount)}"


def bump():
    pricing.tax_rate = 0.3
