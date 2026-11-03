import pricing
from pricing import rate


def summary(amount):
    return f"{rate} -> {pricing.apply(amount)}"


def bump():
    pricing.rate = 0.3
