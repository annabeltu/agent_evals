#!/bin/bash
set -euo pipefail

python - <<'PY'
from pathlib import Path

summaries = {
    "setup.md": [
        "Install the locked project dependencies with `uv sync --locked`.",
        "Run the host pytest suite with `make test` without Docker or credentials.",
    ],
    "verification.md": [
        "Run `make oracle` in Docker to check that reference solutions earn reward 1.",
        "Run `make baseline` to check that unchanged starters earn reward 0.",
    ],
    "results.md": [
        "Inspect saved results and logs with `uv run harbor view jobs`.",
        "Save needed results before `make clean` removes generated output and caches.",
    ],
}

for filename, bullets in summaries.items():
    path = Path("/app/docs") / filename
    title, separator, body = path.read_text().partition("\n")
    summary = "\n## Summary\n\n" + "\n".join(f"- {bullet}" for bullet in bullets) + "\n"
    path.write_text(title + separator + summary + body)
PY
