"""Tests for crontab_lint.comparator module."""

import pytest
from crontab_lint.comparator import compare, format_comparison


def test_identical_expressions_are_equivalent():
    result = compare("0 9 * * 1", "0 9 * * 1")
    assert result.are_equivalent is True
    assert result.differences == []


def test_different_minute_fields_not_equivalent():
    result = compare("0 9 * * 1", "30 9 * * 1")
    assert result.are_equivalent is False
    assert any("minute" in d for d in result.differences)


def test_different_hour_fields_not_equivalent():
    result = compare("0 8 * * *", "0 10 * * *")
    assert result.are_equivalent is False
    assert any("hour" in d for d in result.differences)


def test_both_valid_sets_valid_flags():
    result = compare("* * * * *", "0 0 * * *")
    assert result.valid_a is True
    assert result.valid_b is True


def test_invalid_expression_a_sets_flag():
    result = compare("99 * * * *", "0 0 * * *")
    assert result.valid_a is False
    assert result.are_equivalent is False


def test_invalid_expression_b_sets_flag():
    result = compare("0 0 * * *", "* * * * * * extra")
    assert result.valid_b is False
    assert result.are_equivalent is False


def test_human_readable_set_for_valid():
    result = compare("0 0 * * *", "0 12 * * *")
    assert result.human_a is not None
    assert result.human_b is not None


def test_human_readable_none_for_invalid():
    result = compare("99 * * * *", "0 0 * * *")
    assert result.human_a is None
    assert result.human_b is not None


def test_multiple_field_differences_all_reported():
    result = compare("0 9 1 * *", "30 18 15 * *")
    assert result.are_equivalent is False
    diff_text = " ".join(result.differences)
    assert "minute" in diff_text
    assert "hour" in diff_text
    assert "day_of_month" in diff_text


def test_format_comparison_equivalent():
    result = compare("* * * * *", "* * * * *")
    output = format_comparison(result)
    assert "equivalent" in output.lower()
    assert "A:" in output
    assert "B:" in output


def test_format_comparison_different_contains_diffs():
    result = compare("0 9 * * *", "0 18 * * *")
    output = format_comparison(result)
    assert "differ" in output.lower()
    assert "hour" in output


def test_format_comparison_includes_schedule_descriptions():
    result = compare("0 0 * * *", "0 12 * * *")
    output = format_comparison(result)
    assert "A schedule:" in output
    assert "B schedule:" in output


def test_wildcard_vs_specific_not_equivalent():
    result = compare("* * * * *", "0 0 * * *")
    assert result.are_equivalent is False
