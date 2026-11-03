# Add input validation

The `add(a, b)` function in `/app/calculator.py` adds its arguments without
validating them. Update it to enforce the following behavior:

- Accept integers and floats in either argument, including mixed numeric types,
  negative values, zero, and fractions. Return their sum.
- Raise `TypeError` if either argument is a boolean or any type other than an
  integer or float. Do not convert invalid inputs into numbers.
- Keep the function name `add` and parameter names `a` and `b` unchanged, so
  positional and keyword calls continue to work.

No particular exception message is required.
