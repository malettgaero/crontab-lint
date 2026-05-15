"""Tests for crontab_lint.profiler."""

import pytest
from crontab_lint.profiler import profile, _count_values, _frequency_label


# --- _count_values ---

def test_wildcard_returns_full_range():
    assert _count_values("*", 0, 59) == 60


def test_single_value_returns_one():
    assert _count_values("5", 0, 59) == 1


def test_range_returns_correct_count():
    assert _count_values("1-5", 0, 59) == 5


def test_step_returns_correct_count():
    assert _count_values("*/15", 0, 59) == 4


def test_list_returns_sum():
    assert _count_values("1,2,3", 0, 59) == 3


# --- _frequency_label ---

def test_every_minute_label():
    assert _frequency_label(1440) == "every-minute"


def test_high_frequency_label():
    assert _frequency_label(48) == "high-frequency"


def test_moderate_label():
    assert _frequency_label(4) == "moderate"


def test_low_frequency_label():
    assert _frequency_label(0.5) == "low-frequency"


def test_rare_label():
    assert _frequency_label(0.01) == "rare"


# --- profile ---

def test_invalid_expression_returns_invalid_result():
    result = profile("not a cron")
    assert result.is_valid is False
    assert result.runs_per_day == 0
    assert result.frequency_label == "invalid"
    assert len(result.warnings) > 0


def test_every_minute_profile():
    result = profile("* * * * *")
    assert result.is_valid is True
    assert result.runs_per_day == 1440
    assert result.frequency_label == "every-minute"
    assert any("every minute" in w.lower() for w in result.warnings)


def test_daily_at_midnight_profile():
    result = profile("0 0 * * *")
    assert result.is_valid is True
    assert result.runs_per_day == 1
    assert result.frequency_label == "moderate"
    assert result.warnings == []


def test_hourly_profile():
    result = profile("0 * * * *")
    assert result.is_valid is True
    assert result.runs_per_day == 24
    assert result.frequency_label == "high-frequency"


def test_weekly_profile():
    result = profile("0 9 * * 1")
    assert result.is_valid is True
    assert result.runs_per_day == 1
    assert result.runs_per_week < 7


def test_bool_true_for_valid():
    result = profile("0 0 * * *")
    assert bool(result) is True


def test_bool_false_for_invalid():
    result = profile("bad expr")
    assert bool(result) is False


def test_every_five_minutes_runs_per_hour():
    result = profile("*/5 * * * *")
    assert result.runs_per_hour == 12
    assert result.runs_per_day == 288


def test_monthly_profile():
    result = profile("0 6 1 * *")
    assert result.is_valid is True
    assert result.runs_per_month < 2
