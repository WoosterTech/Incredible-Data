import pytest

from incredible_data.helpers import truncate_string


@pytest.fixture()
def long_string():
    return "This is a long string that needs to be truncated to fit within a certain length."  # noqa: E501


@pytest.mark.parametrize(
    ("max_length", "expected"),
    [
        (19, "This is a long..."),
        (20, "This is a long..."),
        (21, "This is a long..."),
        (25, "This is a long string..."),
        (39, "This is a long string that needs to..."),
        (50, "This is a long string that needs to be..."),
        (
            100,
            "This is a long string that needs to be truncated to fit within a certain length.",  # noqa: E501
        ),
    ],
)
def test_truncate_string(max_length: int, expected: str, long_string: str):
    new_string = truncate_string(long_string, max_length)
    assert len(new_string) <= max_length
    assert new_string == expected
