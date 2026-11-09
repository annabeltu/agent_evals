Fix the indentation errors in `/app/report.py`.

Change only leading spaces or tabs on existing lines. Preserve every line's
remaining text, line order, function names, signatures, and docstring. The file
must import successfully. Use indentation to restore the following behavior:

- `summarize_numbers(numbers)` accepts a list of integers and returns a dictionary
  with `positive`, `negative`, and `zero` counts plus `total`, the sum of all
  numbers. An empty list returns zero for all four fields. Process every number.
- `describe_numbers(numbers)` returns `No numbers` for an empty list. Otherwise,
  return `positive=P, negative=N, zero=Z, total=T` using those summary values.

For example, `[3, -2, 0, 3]` has counts 2, 1, 1 and total 4.
