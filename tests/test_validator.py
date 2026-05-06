"""Tests for crontab_lint.validator."""

import pytest
from crontab_lint.validator import validate, ValidationResult


def test_valid_simple_expression():
    result = validate("0 12 * * *")
    assert result.is_valid is True
    assert result.errors == []
    assert result.parsed is not None


def test_invalid_expression_too_few_fields():
    result = validate("0 12 * *")
    assert result.is_valid is False
    assert len(result.errors) == 1


def test_invalid_empty_expression():
    result = validate("")
    assert result.is_valid is False
    assert "empty" in result.errors[0].lower()


def test_invalid_out_of_range_hour():
    result = validate("0 25 * * *")
    assert result.is_valid is False


def test_bool_truthy_for_valid():
    result = validate("*/5 * * * *")
    assert bool(result) is True


def test_bool_falsy_for_invalid():
    result = validate("bad expression here")
    assert bool(result) is False


def test_warning_both_dom_and_dow():
    result = validate("0 12 15 * 1")
    assert result.is_valid is True
    assert any("OR" in w for w in result.warnings)


def test_warning_every_minute():
    result = validate("* * * * *")
    assert result.is_valid is True
    assert any("every minute" in w.lower() for w in result.warnings)


def test_warning_redundant_step_one():
    result = validate("*/1 * * * *")
    assert result.is_valid is True
    assert any("redundant" in w.lower() for w in result.warnings)


def test_no_warnings_for_normal_schedule():
    result = validate("30 9 * * 1-5")
    assert result.is_valid is True
    assert result.warnings == []


def test_whitespace_stripped():
    result = validate("  0 0 * * *  ")
    assert result.is_valid is True


def test_validation_result_dataclass_defaults():
    r = ValidationResult(expression="x", is_valid=False)
    assert r.errors == []
    assert r.warnings == []
    assert r.parsed is None
