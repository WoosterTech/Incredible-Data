import pytest

from incredible_data.helpers.functions import (
    create_media_name,
    truncate_string,
)


@pytest.fixture
def dummy_field_file():
    class DummyFieldFile:
        def __init__(self, name: str):
            self.name: str = name

    return DummyFieldFile("path/to/file.txt")


def test_truncate_string():
    s = "This is a long string that needs to be truncated to fit within a certain length."
    assert truncate_string(s, 19) == "This is a long..."
    assert truncate_string(s, 100) == s
    assert truncate_string("short", 10) == "short"


def test_create_media_name(dummy_field_file):
    assert create_media_name(dummy_field_file) == "file"
