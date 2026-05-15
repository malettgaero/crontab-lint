"""Tests for crontab_lint.tagger module."""

import pytest
from crontab_lint.tagger import tag, TagResult


def test_every_minute_tagged_correctly():
    result = tag("* * * * *")
    assert result.valid
    assert result.has_tag("every-minute")


def test_invalid_expression_returns_invalid():
    result = tag("invalid")
    assert not result.valid
    assert result.tags == []


def test_hourly_alias_tagged():
    result = tag("@hourly")
    assert result.valid
    assert result.has_tag("alias")
    assert result.has_tag("hourly")


def test_daily_alias_tagged():
    result = tag("@daily")
    assert result.valid
    assert result.has_tag("alias")
    assert result.has_tag("daily")


def test_weekly_alias_tagged():
    result = tag("@weekly")
    assert result.valid
    assert result.has_tag("alias")
    assert result.has_tag("weekly")


def test_monthly_alias_tagged():
    result = tag("@monthly")
    assert result.valid
    assert result.has_tag("alias")
    assert result.has_tag("monthly")


def test_yearly_alias_tagged():
    result = tag("@yearly")
    assert result.valid
    assert result.has_tag("alias")
    assert result.has_tag("yearly")


def test_top_of_hour_tagged():
    result = tag("0 9 * * *")
    assert result.valid
    assert result.has_tag("top-of-hour")


def test_interval_tagged_for_step_minute():
    result = tag("*/15 * * * *")
    assert result.valid
    assert result.has_tag("interval")


def test_interval_tagged_for_step_hour():
    result = tag("0 */6 * * *")
    assert result.valid
    assert result.has_tag("interval")


def test_monthly_schedule_tagged():
    result = tag("0 0 1 * *")
    assert result.valid
    assert result.has_tag("monthly")


def test_yearly_schedule_tagged():
    result = tag("0 0 1 1 *")
    assert result.valid
    assert result.has_tag("yearly")


def test_weekly_schedule_tagged():
    result = tag("0 9 * * 1")
    assert result.valid
    assert result.has_tag("weekly")


def test_multi_value_tagged():
    result = tag("0 9,17 * * *")
    assert result.valid
    assert result.has_tag("multi-value")


def test_range_tagged():
    result = tag("0 9-17 * * *")
    assert result.valid
    assert result.has_tag("range")


def test_has_tag_false_for_missing_tag():
    result = tag("0 9 * * *")
    assert not result.has_tag("every-minute")


def test_expression_stored_on_result():
    expr = "30 8 * * 1-5"
    result = tag(expr)
    assert result.expression == expr
