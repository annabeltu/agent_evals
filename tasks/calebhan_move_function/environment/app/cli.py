import sys
from decimal import Decimal

import orders


def main(argv: list[str]) -> str:
    amount = Decimal(argv[0])
    exempt = "--exempt" in argv[1:]
    return f"Tax on {amount}: {orders.calculate_tax(amount, exempt=exempt)}"


if __name__ == "__main__":
    print(main(sys.argv[1:]))
