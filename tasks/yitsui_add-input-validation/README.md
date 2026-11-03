# local/yitsui_add-input-validation

Charlotte's task #1: add input validation to a Python calculator function.
The starter already adds numbers correctly but accepts invalid types such as
booleans, strings, and lists. The agent must reject invalid arguments with
`TypeError` while preserving valid numeric inputs and keyword calls.

Created with Harbor's `task init` command, using `tasks/krisj_fix_add` as the
reference for the Docker environment, oracle script, and pytest verifier.

From the repository root, with Docker running:

```sh
make oracle TASKS=yitsui_add-input-validation
make baseline TASKS=yitsui_add-input-validation
```

The oracle should score **1**; the unchanged starter should score **0** because
it accepts invalid inputs. Inspect results with `uv run --locked harbor view jobs`.
