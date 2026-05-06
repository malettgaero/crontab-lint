"""Tests for crontab_lint.recommender."""

import pytest
from crontab_lint.recommender import recommend, _suggest_field_fix, _closest_common_schedule


def test_valid_every_minute_warns():
    recs = recommend("* * * * *")
    assert any("every minute" in r.lower() for r in recs)


def test_common_schedule_daily_suggests_alias():
    recs = recommend("0 0 * * *")
    assert any("@daily" in r or "@midnight" in r for r in recs)


def test_common_schedule_hourly_suggests_alias():
    recs = recommend("0 * * * *")
    assert any("@hourly" in r for r in recs)


def test_common_schedule_weekly_suggests_alias():
    recs = recommend("0 0 * * 0")
    assert any("@weekly" in r for r in recs)


def test_common_schedule_yearly_suggests_alias():
    recs = recommend("0 0 1 1 *")
    assert any("@yearly" in r for r in recs)


def test_too_few_fields_reported():
    recs = recommend("* * *")
    assert any("3 field" in r for r in recs)


def test_too_many_fields_reported():
    recs = recommend("* * * * * *")
    assert any("6 field" in r for r in recs)


def test_hour_overflow_suggests_fix():
    recs = recommend("0 24 * * *")
    assert any("24" in r and "23" in r for r in recs)


def test_minute_overflow_suggests_fix():
    recs = recommend("60 * * * *")
    assert any("60" in r and "59" in r for r in recs)


def test_month_overflow_suggests_fix():
    recs = recommend("0 0 1 13 *")
    assert any("13" in r and "12" in r for r in recs)


def test_no_recommendations_for_clean_specific_expression():
    recs = recommend("30 6 * * 1")
    # No alias match, no overflow, not every-minute -> empty list
    assert recs == []


def test_suggest_field_fix_over_max():
    assert _suggest_field_fix("25", 0, 23) == "23"


def test_suggest_field_fix_under_min():
    assert _suggest_field_fix("0", 1, 31) == "1"


def test_suggest_field_fix_valid_returns_none():
    assert _suggest_field_fix("12", 0, 23) is None


def test_closest_common_schedule_no_match():
    assert _closest_common_schedule("30 6 * * 1") is None


def test_closest_common_schedule_monthly():
    result = _closest_common_schedule("0 0 1 * *")
    assert result == "@monthly"
