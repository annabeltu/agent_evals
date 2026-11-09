Remove the unused imports from `/app/report.py` without changing its behavior.

Remove the unused bindings `os`, `sys`, `defaultdict`, `Path`, and `median`.
Keep the used imports `json`, `math`, `Counter` (from `collections`), and `average`
(the alias of `statistics.mean`). In statements with both used and unused names,
remove only the unused names. You may reorder or regroup import statements.
Do not add imports or move imports into functions. Preserve the module docstring,
function signatures, and all non-import code; formatting changes are allowed.

`summarize_readings(readings)` accepts a list of integers and returns its count,
total, arithmetic mean, the ceiling of that mean, and a JSON string of the counts
of each reading, with sorted keys. Empty input returns count, total, mean, and
ceiling of zero and `counts_json` equal to `{}`. Preserve negative values and
duplicate readings as well as the existing `average` alias.
