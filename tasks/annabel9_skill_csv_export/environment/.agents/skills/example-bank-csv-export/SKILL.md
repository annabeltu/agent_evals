name: example-bank-csv-export
description: Use this skill when implementing transaction CSV exports using Example Bank's specialized CSV format.

# Example Bank CSV export skill

Use this specification when implementing `export_transactions(transactions)`.
The function returns the complete CSV document as a string.

- The first row is the header, with exactly these columns in this order:
  `transaction_id,amount,date`.
- Emit one row per input transaction.
- Sort rows by transaction ID in ascending order before writing them.
- Format each date as `YYYYMMDD` (for example, `2024-03-07` becomes
  `20240307`).
- Format every present amount with exactly two decimal places (for example,
  `12`, `12.5`, and `12.567` become `12.00`, `12.50`, and `12.57`).
- A missing amount (a missing `amount` field or a value of `None`) is written
  as the literal `NA`.
- Use Python's standard-library `csv` module to produce the CSV; do not build
  CSV rows by manually joining strings. The returned document should use
  normal Unix newline characters.
