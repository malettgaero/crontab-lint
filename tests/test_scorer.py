"""Tests for crontab_lint.scorer."""

import pytest
from crontab_lint.scorer import score, ScoreResult


def test_invalid_expression_returns_zero_score():
    result = score("not a cron")
    assert result.score == 0
    assert result.grade == "F"
    assert not result.is_valid
    assert not result


def test_invalid_expression_has_penalty_message():
    result = score("* * * * * *")  # six fields — invalid
    assert not result.is_valid
    assert any("Invalid" in p for p in result.penalties)


def test_every_minute_scores_high():
    result = score("* * * * *")
    assert result.is_valid
    assert result.score >= 90
    assert result.grade == "A"


def test_alias_daily_scores_high():
    result = score("@daily")
    assert result.is_valid
    assert result.score >= 90


def test_specific_time_daily_scores_well():
    # Only minute and hour constrained
    result = score("30 6 * * *")
    assert result.is_valid
    assert result.score >= 75


def test_highly_specific_schedule_penalised():
    # minute, hour, dom, month all constrained
    result = score("0 9 15 6 *")
    assert result.is_valid
    assert result.score < 90
    assert any("specific" in p.lower() for p in result.penalties)


def test_comma_list_penalised():
    result = score("0,30 * * * *")
    assert result.is_valid
    assert any("comma" in p.lower() for p in result.penalties)
    assert result.score < 100


def test_multiple_comma_lists_penalised_more():
    single = score("0,30 * * * *")
    multi = score("0,30 6,12 * * *")
    assert multi.score < single.score


def test_range_with_step_penalised():
    result = score("0-30/5 * * * *")
    assert result.is_valid
    assert any("range and step" in p.lower() for p in result.penalties)


def test_both_dom_and_dow_set_penalised():
    result = score("0 9 15 * 1")
    assert result.is_valid
    assert any("day-of-month" in p.lower() for p in result.penalties)


def test_score_result_bool_true_for_valid():
    result = score("* * * * *")
    assert bool(result) is True


def test_score_result_bool_false_for_invalid():
    result = score("bad expression")
    assert bool(result) is False


def test_grade_a_for_score_90_plus():
    result = score("* * * * *")
    assert result.grade == "A"


def test_score_is_capped_at_100():
    result = score("@hourly")
    assert result.score <= 100


def test_score_is_non_negative():
    # Even heavily penalised valid expressions should not go below 0
    result = score("0,30 6,12 1-15/2 1,6 1,3")
    assert result.score >= 0
