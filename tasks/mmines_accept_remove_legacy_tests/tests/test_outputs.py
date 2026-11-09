"""Grade the v1 removal: legacy code and tests gone, current pricing untouched."""

import subprocess
import sys
from pathlib import Path

APP = Path("/app")
# A copy of the starting /app/tests/test_pricing.py, which must not change.
EXPECTED_TEST_PRICING = Path(__file__).with_name("expected_test_pricing.py")


def test_legacy_module_and_its_tests_are_deleted() -> None:
    assert not (APP / "shop" / "legacy_pricing.py").exists()
    assert not (APP / "tests" / "test_legacy_pricing.py").exists()


def test_no_code_refers_to_the_v1_api() -> None:
    for path in APP.rglob("*.py"):
        text = path.read_text()
        assert "legacy_pricing" not in text, path
        assert "legacy_total" not in text, path


def test_current_pricing_still_imports_and_works() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import shop; print(shop.total([10.0], 0.5))"],
        cwd=APP,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "15.0"


def test_current_pricing_tests_are_unchanged_and_pass() -> None:
    assert (APP / "tests" / "test_pricing.py").read_text() == EXPECTED_TEST_PRICING.read_text()

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "/app/tests"],
        cwd=APP,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
