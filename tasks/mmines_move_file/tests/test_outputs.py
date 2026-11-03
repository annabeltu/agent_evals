"""Pytest checks that solve.sh was moved and run.sh still works."""

import subprocess
from pathlib import Path

OLD_PATH = Path("/app/solution/solve.sh")
NEW_PATH = Path("/app/solution/solving-solutions/solve.sh")


def test_new_file_exists():
    assert NEW_PATH.is_file()


def test_old_file_removed():
    assert not OLD_PATH.exists()


def test_run_script_still_works():
    result = subprocess.run(["bash", "/app/run.sh"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert result.stdout.strip() == "Mi-Kris Jordan"
