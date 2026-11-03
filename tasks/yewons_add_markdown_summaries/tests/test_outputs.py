"""Pytest checks for Markdown summaries inside the task sandbox."""

import re
from pathlib import Path

import pytest

APP = Path("/app")
ORIGINALS = Path(__file__).with_name("original_docs")
COMMANDS = {
    "setup.md": ("uv sync --locked", "make test"),
    "verification.md": ("make oracle", "make baseline"),
    "results.md": ("uv run harbor view jobs", "make clean"),
}


@pytest.fixture(params=COMMANDS)
def guide(request):
    filename = request.param
    path = APP / "docs" / filename
    assert path.is_file() and not path.is_symlink(), f"{filename} must be a regular file"
    original = (ORIGINALS / filename).read_text()
    title, separator, body = original.partition("\n")
    text = path.read_text()
    assert text.startswith(title + separator), f"{filename}: the title changed"
    assert text.endswith(body), f"{filename}: existing guide content changed"
    section = text[len(title + separator) : -len(body)]
    return filename, section


def test_summary_heading_and_spacing(guide):
    filename, section = guide
    assert re.match(r"\n(?:[ \t]*\n)*## Summary\n[ \t]*\n", section), (
        f"{filename}: add a level-two Summary heading below the title, with blank lines"
    )
    assert section.endswith("\n"), f"{filename}: separate the summary from existing content"


def test_summary_has_two_bullets_covering_the_commands(guide):
    filename, section = guide
    lines = [line for line in section.splitlines() if line.strip()]
    assert lines and lines[0] == "## Summary"
    bullets = []
    for line in lines[1:]:
        if re.match(r"[-*+] +\S", line):
            bullets.append(line.lstrip("-*+ "))
        else:
            assert bullets and line[0].isspace(), f"{filename}: expected a Markdown bullet"
            bullets[-1] += " " + line.strip()
    assert len(bullets) == 2, f"{filename}: expected exactly two bullets"
    for bullet, command in zip(bullets, COMMANDS[filename], strict=True):
        assert re.findall(r"`([^`]+)`", bullet) == [command], (
            f"{filename}: each bullet must include its complete command in inline backticks"
        )
        explanation = bullet.replace(f"`{command}`", "").strip(" .:;!-")
        assert re.search(r"[A-Za-z]", explanation), (
            f"{filename}: explain the command rather than listing only the command"
        )


def test_only_requested_files_exist():
    entries = {path.relative_to(APP).as_posix() for path in APP.rglob("*")}
    assert entries == {"docs", *(f"docs/{filename}" for filename in COMMANDS)}
