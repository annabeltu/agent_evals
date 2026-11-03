"""Check the replacement and preservation of the rest of the README."""

from pathlib import Path

EXPECTED_README = b"""# A simple project

This is a simple project.

## Features

- A simple thing.
- The smallest of things.
- Small things are simple.

## Usage

Read this README before getting started on this simple project.
"""


def test_readme_has_only_the_requested_replacements() -> None:
    readme = Path("/app/README.md")
    assert readme.is_file(), "Keep the README at /app/README.md"
    assert readme.read_bytes() == EXPECTED_README
