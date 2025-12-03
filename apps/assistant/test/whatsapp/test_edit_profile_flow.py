from datetime import date

import pytest

from farmwise.whatsapp.flow_handlers.edit_profile import (
    _dob_from_age,
    _parse_age,
    _safe_age_from_dob,
    _split_full_name,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("18", 18),
        (18, 18),
        (18.0, 18),
        (" 45 ", 45),
        ("abc", None),
        (12, None),
        (121, None),
        (None, None),
    ],
)
def test_parse_age(value, expected):
    assert _parse_age(value) == expected


@pytest.mark.parametrize(
    "full_name,fallback_first,fallback_last,expected",
    [
        ("Jane Doe", "First", "Last", ("Jane", "Doe")),
        ("Jane Mary Doe", "First", "Last", ("Jane", "Mary Doe")),
        ("Jane", "First", "Last", ("Jane", "Last")),
        ("", "First", "Last", ("First", "Last")),
        (None, "First", "Last", ("First", "Last")),
    ],
)
def test_split_full_name(full_name, fallback_first, fallback_last, expected):
    assert _split_full_name(full_name, fallback_first, fallback_last) == expected


@pytest.mark.parametrize("age,expected_year", [(13, date.today().year - 13), (None, None)])
def test_dob_from_age(age, expected_year):
    dob = _dob_from_age(age)
    if age is None:
        assert dob is None
    else:
        assert dob is not None
        assert dob.endswith("-07-01")
        assert int(dob.split("-", 1)[0]) == expected_year


@pytest.mark.parametrize(
    "dob_iso,expected",
    [
        ("2000-01-01", str(date.today().year - 2000)),
        (None, ""),
        ("invalid", ""),
    ],
)
def test_safe_age_from_dob(dob_iso, expected):
    result = _safe_age_from_dob(dob_iso)
    if expected:
        assert result == expected
    else:
        assert result == ""
