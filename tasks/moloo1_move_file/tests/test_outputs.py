"""Check that file.py was moved into /app/new_dir without changes."""

from pathlib import Path

NEW_PATH = Path("/app/new_dir/file.py")
OLD_PATH = Path("/app/file.py")
ORIGINAL_CONTENTS = b'"hi"\n'


def test_file_in_new_directory():
    assert NEW_PATH.is_file()
    assert not NEW_PATH.is_symlink()


def test_file_not_in_original_path():
    assert not OLD_PATH.exists()
    assert not OLD_PATH.is_symlink()


def test_file_contents_same():
    assert NEW_PATH.read_bytes() == ORIGINAL_CONTENTS
