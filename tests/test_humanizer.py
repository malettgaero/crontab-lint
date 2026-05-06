"""Tests for crontab_lint.humanizer module."""

import pytest
from crontab_lint.parser import parse
from crontab_lint.humanizer import humanize, _describe_field, _describe_weekday, _describe_month


def test_every_minute():
    parsed = parse("* * * * *")
    assert humanize(parsed) == "every minute"


def test_every_five_minutes():
    parsed = parse("*/5 * * * *")
    assert humanize(parsed) == "every 5 minute(s)"


def test_top_of_hour():
    parsed = parse("0 * * * *")
    result = humanize(parsed)
    assert "top of" in result


def test_specific_time():
    parsed = parse("30 9 * * *")
    result = humanize(parsed)
    assert "30" in result
    assert "9" in result


def test_specific_day_of_month():
    parsed = parse("0 0 15 * *")
    result = humanize(parsed)
    assert "day 15" in result


def test_specific_month():
    parsed = parse("0 0 1 6 *")
    result = humanize(parsed)
    assert "June" in result


def test_specific_weekday():
    parsed = parse("0 9 * * 1")
    result = humanize(parsed)
    assert "Monday" in result


def test_weekday_range():
    result = _describe_weekday("1-5")
    assert result == "Monday through Friday"


def test_weekday_list():
    result = _describe_weekday("0,6")
    assert "Sunday" in result
    assert "Saturday" in result


def test_weekday_wildcard():
    result = _describe_weekday("*")
    assert result == "every day of the week"


def test_month_range():
    result = _describe_month("3-5")
    assert result == "March through May"


def test_month_list():
    result = _describe_month("1,12")
    assert "January" in result
    assert "December" in result


def test_describe_field_wildcard():
    assert _describe_field("*", "hours", "hour") == "every hour"


def test_describe_field_step():
    result = _describe_field("*/2", "hours", "hour")
    assert "every 2 hours" in result


def test_describe_field_range():
    result = _describe_field("9-17", "hours", "hour")
    assert "9 through 17" in result


def test_full_complex_expression():
    parsed = parse("0 9 * * 1-5")
    result = humanize(parsed)
    assert "Monday" in result
    assert "Friday" in result
