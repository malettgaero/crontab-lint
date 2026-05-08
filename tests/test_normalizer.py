"""Tests for crontab_lint.normalizer module."""

import pytest
from crontab_lint.normalizer import normalize, expand_alias


def test_expand_alias_daily():
    assert expand_alias("@daily") == "0 0 * * *"


def test_expand_alias_hourly():
    assert expand_alias("@hourly") == "0 * * * *"


def test_expand_alias_weekly():
    assert expand_alias("@weekly") == "0 0 * * 0"


def test_expand_alias_monthly():
    assert expand_alias("@monthly") == "0 0 1 * *"


def test_expand_alias_yearly():
    assert expand_alias("@yearly") == "0 0 1 1 *"


def test_expand_alias_annually_same_as_yearly():
    assert expand_alias("@annually") == expand_alias("@yearly")


def test_expand_alias_midnight_same_as_daily():
    assert expand_alias("@midnight") == expand_alias("@daily")


def test_expand_alias_unknown_passthrough():
    assert expand_alias("0 12 * * *") == "0 12 * * *"


def test_normalize_simple_expression():
    assert normalize("0 0 * * *") == "@daily"


def test_normalize_every_minute():
    assert normalize("* * * * *") == "@every_minute"


def test_normalize_hourly():
    assert normalize("0 * * * *") == "@hourly"


def test_normalize_weekly():
    assert normalize("0 0 * * 0") == "@weekly"


def test_normalize_monthly():
    assert normalize("0 0 1 * *") == "@monthly"


def test_normalize_yearly():
    assert normalize("0 0 1 1 *") == "@yearly"


def test_normalize_alias_input_daily():
    assert normalize("@daily") == "@daily"


def test_normalize_alias_input_hourly():
    assert normalize("@hourly") == "@hourly"


def test_normalize_leading_zeros_removed():
    result = normalize("05 09 * * *")
    assert result == "5 9 * * *"


def test_normalize_step_value():
    result = normalize("*/5 * * * *")
    assert result == "*/5 * * * *"


def test_normalize_range_value():
    result = normalize("0 9-17 * * *")
    assert result == "0 9-17 * * *"


def test_normalize_invalid_expression_returns_none():
    assert normalize("invalid") is None


def test_normalize_too_few_fields_returns_none():
    assert normalize("* * *") is None


def test_normalize_out_of_range_returns_none():
    assert normalize("0 25 * * *") is None


def test_normalize_list_values():
    result = normalize("0 9,12,17 * * *")
    assert result == "0 9,12,17 * * *"
