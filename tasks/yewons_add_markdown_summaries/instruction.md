# Add Markdown summaries

Add a short `## Summary` section immediately below the existing title in each
of these guides: `/app/docs/setup.md`, `/app/docs/verification.md`, and
`/app/docs/results.md`.

Each summary must have exactly two unordered Markdown bullets, with one command
per bullet in the order it appears in the guide. Explain what each command does
in your own words and include the complete command in inline backticks:

- `setup.md`: `uv sync --locked` and `make test`.
- `verification.md`: `make oracle` and `make baseline`.
- `results.md`: `uv run harbor view jobs` and `make clean`.

Leave a blank line before and after the summary heading and between the summary
and the existing content. Preserve the existing titles and all existing guide
content exactly. Do not edit or create other files.
