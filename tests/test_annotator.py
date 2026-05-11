"""Tests for crontab_lint.annotator."""

import pytest
from crontab_lint.annotator import annotate, format_annotation, AnnotatedCron


def test_valid_expression_returns_valid_flag():
    result = annotate("0 9 * * 1")
    assert result.valid is True


def test_invalid_expression_returns_invalid_flag():
    result = annotate("bad expression")
    assert result.valid is False


def test_invalid_expression_has_no_fields():
    result = annotate("60 * * * *")
    assert result.fields == []


def test_five_fields_returned_for_valid_expression():
    result = annotate("*/5 * * * *")
    assert len(result.fields) == 5


def test_field_names_in_order():
    result = annotate("0 6 * * *")
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day_of_month", "month", "day_of_week"]


def test_wildcard_field_description():
    result = annotate("* * * * *")
    minute_field = result.fields[0]
    assert "every" in minute_field.description


def test_step_field_description():
    result = annotate("*/15 * * * *")
    minute_field = result.fields[0]
    assert "15" in minute_field.description
    assert "every" in minute_field.description


def test_range_field_description():
    result = annotate("0 9-17 * * *")
    hour_field = result.fields[1]
    assert "from" in hour_field.description
    assert "9" in hour_field.description
    assert "17" in hour_field.description


def test_list_field_description():
    result = annotate("0 0 * * 1,3,5")
    dow_field = result.fields[4]
    assert "one of" in dow_field.description


def test_specific_value_description():
    result = annotate("30 8 * * *")
    minute_field = result.fields[0]
    assert "30" in minute_field.description
    hour_field = result.fields[1]
    assert "8" in hour_field.description


def test_summary_is_non_empty_for_valid():
    result = annotate("0 0 * * *")
    assert result.summary
    assert len(result.summary) > 0


def test_expression_stored_on_result():
    expr = "0 12 * * 5"
    result = annotate(expr)
    assert result.expression == expr


def test_format_annotation_valid_contains_expression():
    result = annotate("0 9 * * 1")
    output = format_annotation(result)
    assert "0 9 * * 1" in output


def test_format_annotation_valid_contains_summary():
    result = annotate("0 9 * * 1")
    output = format_annotation(result)
    assert "Summary" in output


def test_format_annotation_valid_lists_all_fields():
    result = annotate("*/5 * * * *")
    output = format_annotation(result)
    assert "minute" in output
    assert "hour" in output
    assert "day of month" in output


def test_format_annotation_invalid_shows_invalid_status():
    result = annotate("not a cron")
    output = format_annotation(result)
    assert "INVALID" in output


def test_format_annotation_invalid_no_fields_section():
    result = annotate("99 99 99 99 99")
    output = format_annotation(result)
    assert "Fields" not in output
