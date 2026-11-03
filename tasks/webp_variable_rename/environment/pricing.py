rate = 0.2
rate_cap = 100


def apply(amount):
    # rate applies before the cap
    return min(amount * rate, rate_cap)


def describe():
    rate = "standard"
    return "rate: " + rate
