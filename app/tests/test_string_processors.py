import pytest

from app.string_processors import clean_url_strings


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "test&Test",
            "test-test",
        ),
        (
            "test-test",
            "test-test",
        ),
        (
            "test test",
            "test-test",
        ),
        (
            "test1",
            "test1",
        ),
        (
            "Test%",
            "test",
        ),
    ],
)
def test_clean_url_strings(value: str, expected: str) -> None:
    assert clean_url_strings(string=value) == expected
