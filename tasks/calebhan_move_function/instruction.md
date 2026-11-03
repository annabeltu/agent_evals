# Move `calculate_tax` into the pricing module

The modules in `/app` (`pricing.py`, `orders.py`, `invoices.py`, and `cli.py`)
make up a small order-pricing app. `calculate_tax` is defined in
`/app/orders.py`, but it belongs with the other pricing helpers.

Move `calculate_tax` from `/app/orders.py` to `/app/pricing.py`:

- Define it in `pricing.py` with the same name, signature, and body. Remove its
  definition from `orders.py`, so it is defined only in `pricing.py`.
- Update every use of the function in `/app` to get it from `pricing`. No
  module may import or access `calculate_tax` through `orders`, whether with
  `from orders import calculate_tax` or `orders.calculate_tax`. `orders.py` may
  import it from `pricing` for its own use.
- `pricing.py` must not import `orders`, `invoices`, or `cli`.
- Every module must still import cleanly, and the app's behavior, including
  `python /app/cli.py <amount> [--exempt]`, must stay the same.
