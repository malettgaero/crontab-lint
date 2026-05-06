"""Tests for next-run time explainer."""

from datetime import datetime

import pytest

from crontab_lint.explainer import next_runs, _field_matches


ANCHOR = datetime(2024, 1, 15, 12, 0)  # Monday, Jan 15 2024, noon


def test_every_minute_returns_five_consecutive():
    runs = next_runs("* * * * *", count=5, after=ANCHOR)
    assert len(runs) == 5
    for i, run in enumerate(runs):
        assert run == datetime(2024, 1, 15, 12, i + 1)


def test_specific_hour_and_minute():
    runs = next_runs("30 14 * * *", count=3, after=ANCHOR)
    assert len(runs) == 3
    assert runs[0] == datetime(2024, 1, 15, 14, 30)
    assert runs[1] == datetime(2024, 1, 16, 14, 30)
    assert runs[2] == datetime(2024, 1, 17, 14, 30)


def test_step_expression():
    runs = next_runs("*/15 * * * *", count=4, after=ANCHOR)
    assert runs[0] == datetime(2024, 1, 15, 12, 15)
    assert runs[1] == datetime(2024, 1, 15, 12, 30)
    assert runs[2] == datetime(2024, 1, 15, 12, 45)
    assert runs[3] == datetime(2024, 1, 15, 13, 0)


def test_specific_weekday():
    # 0 = Monday in Python's weekday()
    runs = next_runs("0 9 * * 0", count=2, after=ANCHOR)
    assert runs[0].weekday() == 0
    assert runs[0].hour == 9
    assert runs[0].minute == 0


def test_invalid_expression_returns_empty():
    runs = next_runs("invalid expression", count=5, after=ANCHOR)
    assert runs == []


def test_count_parameter():
    runs = next_runs("* * * * *", count=10, after=ANCHOR)
    assert len(runs) == 10


def test_default_count_is_five():
    runs = next_runs("* * * * *", after=ANCHOR)
    assert len(runs) == 5


def test_field_matches_wildcard():
    assert _field_matches(5, "*", 0, 59) is True


def test_field_matches_exact():
    assert _field_matches(5, "5", 0, 59) is True
    assert _field_matches(6, "5", 0, 59) is False


def test_field_matches_range():
    assert _field_matches(3, "1-5", 0, 59) is True
    assert _field_matches(6, "1-5", 0, 59) is False


def test_field_matches_step():
    assert _field_matches(15, "*/15", 0, 59) is True
    assert _field_matches(14, "*/15", 0, 59) is False


def test_field_matches_list():
    assert _field_matches(3, "1,3,5", 0, 59) is True
    assert _field_matches(4, "1,3,5", 0, 59) is False


def test_runs_are_strictly_after_anchor():
    """All returned run times must be strictly after the anchor timestamp."""
    runs = next_runs("* * * * *", count=5, after=ANCHOR)
    for run in runs:
        assert run > ANCHOR


def test_runs_are_sorted_ascending():
    """Returned run times must be in ascending (chronological) order."""
    runs = next_runs("*/5 * * * *", count=6, after=ANCHOR)
    for i in range(len(runs) - 1):
        assert runs[i] < runs[i + 1]
