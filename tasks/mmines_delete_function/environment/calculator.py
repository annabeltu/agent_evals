def _round(value):
    return round(value, 2)


def _square(value):
    return value * value


def hypotenuse(a, b):
    return _round((_square(a) + _square(b)) ** 0.5)


def average(numbers):
    return _round(sum(numbers) / len(numbers))
