"""Hidden checks for the README formatter skill task."""

from pathlib import Path


def test_readme():
    content = Path("/app/README.md").read_text()

    assert content.startswith("# My Python Project\n")
    assert "## Description" in content
    assert "## Installation" in content
    assert "## Usage" in content
    assert "Built with Python 3.12." in content
    assert content.endswith("\n")
    assert not content.endswith("\n\n")
