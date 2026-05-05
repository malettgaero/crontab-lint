"""Tests for the crontab expression parser."""

import pytest
from crontab_lint.parser import parse


# --- Valid expressions ---

def test_simple_valid_expression():
    result = parse("0 12 * * *")
    assert result.is_valid
    assert result.errors == []
    assert result.minute == "0"
    assert result.hour == "12"


def test_wildcard_all_fields():
    result = parse("* * * * *")
    assert result.is_valid


def test_step_values():
    result = parse("*/5 */2 * * *")
    assert result.is_valid


def test_range_values():
    result = parse("0-30 9-17 * * 1-5")
    assert result.is_valid


def test_list_values():
    result = parse("0,15,30,45 * * * *")
    assert result.is_valid


def test_month_name_aliases():
    result = parse("0 0 1 jan *")
    assert result.is_valid
    assert result.month == "1"


def test_weekday_name_aliases():
    result = parse("0 9 * * mon")
    assert result.is_valid
    assert result.day_week == "1"


# --- Special strings ---

def test_at_yearly():
    result = parse("@yearly")
    assert result.is_valid
    assert result.minute == "0"
    assert result.month == "1"


def test_at_hourly():
    result = parse("@hourly")
    assert result.is_valid
    assert result.minute == "0"
    assert result.hour == "*"


def test_at_midnight_alias():
    result = parse("@midnight")
    assert result.is_valid


# --- Invalid expressions ---

def test_wrong_field_count_too_few():
    result = parse("0 12 * *")
    assert not result.is_valid
    assert any("5 fields" in e for e in result.errors)


def test_wrong_field_count_too_many():
    result = parse("0 12 * * * *")
    assert not result.is_valid


def test_minute_out_of_range():
    result = parse("60 * * * *")
    assert not result.is_valid
    assert any("minute" in e for e in result.errors)


def test_hour_out_of_range():
    result = parse("* 24 * * *")
    assert not result.is_valid
    assert any("hour" in e for e in result.errors)


def test_month_out_of_range():
    result = parse("* * * 13 *")
    assert not result.is_valid


def test_zero_step_invalid():
    result = parse("*/0 * * * *")
    assert not result.is_valid
    assert any("zero" in e for e in result.errors)


def test_invalid_range_start_greater_than_end():
    result = parse("30-10 * * * *")
    assert not result.is_valid
    assert any(">" in e for e in result.errors)


def test_garbage_input():
    result = parse("not a cron expression at all")
    assert not result.is_valid
