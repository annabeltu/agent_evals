"""Check the saved branch listing inside the task sandbox."""

from pathlib import Path


def test_output_lists_every_local_branch_once() -> None:
    output = Path("/app/local-branches.txt")
    assert output.is_file(), "Save the branch names to /app/local-branches.txt"

    branches = output.read_text(encoding="utf-8").splitlines()
    expected = {"main", "branch1", "branch2", "branch3"}
    assert set(branches) == expected, "List only the four local branch names, without markers"
    assert len(branches) == len(expected), "List each local branch exactly once"
