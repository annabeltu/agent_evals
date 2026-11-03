"""Check that /app is on a new-feature branch created from main."""

import subprocess

import pytest

REPO = "/app"
BRANCH = "new-feature"


def git(*args):
    result = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


@pytest.fixture
def main_commit():
    return git("rev-parse", "refs/heads/main")


def test_current_branch_is_new_feature():
    assert git("symbolic-ref", "--short", "HEAD") == BRANCH


def test_new_branch_points_at_main(main_commit):
    assert git("rev-parse", f"refs/heads/{BRANCH}") == main_commit


def test_main_was_not_changed(main_commit):
    assert git("rev-list", "--count", main_commit) == "1"


def test_working_tree_is_clean():
    assert git("status", "--porcelain") == ""
