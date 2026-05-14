"""Tests for crontab_lint.grouper."""

import pytest

from crontab_lint.grouper import group, format_groups, ExpressionGroup, GroupResult


VALID_EVERY_MINUTE = "* * * * *"
VALID_DAILY = "0 0 * * *"
VALID_HOURLY = "0 * * * *"
INVALID = "99 * * * *"


def test_single_valid_expression_creates_one_group():
    result = group([VALID_EVERY_MINUTE])
    assert len(result.groups) == 1
    assert result.groups[0].size == 1


def test_invalid_expression_goes_to_invalid_list():
    result = group([INVALID])
    assert len(result.groups) == 0
    assert INVALID in result.invalid


def test_empty_input_returns_empty_result():
    result = group([])
    assert result.total == 0
    assert result.unique_schedules == 0
    assert result.invalid == []


def test_two_distinct_schedules_form_two_groups():
    result = group([VALID_EVERY_MINUTE, VALID_DAILY])
    assert result.unique_schedules == 2


def test_duplicate_identical_expressions_share_one_group():
    result = group([VALID_DAILY, VALID_DAILY])
    assert result.unique_schedules == 1
    assert result.groups[0].size == 2


def test_alias_and_expanded_form_share_one_group():
    # @daily expands to 0 0 * * * via normalize
    result = group(["@daily", VALID_DAILY])
    assert result.unique_schedules == 1


def test_total_counts_valid_and_invalid():
    result = group([VALID_EVERY_MINUTE, INVALID])
    assert result.total == 2


def test_valid_count_excludes_invalid():
    result = group([VALID_EVERY_MINUTE, VALID_DAILY, INVALID])
    total_valid = sum(g.size for g in result.groups)
    assert total_valid == 2


def test_groups_sorted_by_size_descending():
    result = group([VALID_DAILY, VALID_EVERY_MINUTE, VALID_EVERY_MINUTE])
    assert result.groups[0].size >= result.groups[1].size


def test_expression_group_size_property():
    grp = ExpressionGroup(canonical="* * * * *", members=["* * * * *", "* * * * *"])
    assert grp.size == 2


def test_group_result_unique_schedules_property():
    result = GroupResult(
        groups=[
            ExpressionGroup(canonical="* * * * *", members=["* * * * *"]),
            ExpressionGroup(canonical="0 0 * * *", members=["0 0 * * *"]),
        ]
    )
    assert result.unique_schedules == 2


def test_format_groups_contains_canonical():
    result = group([VALID_DAILY])
    output = format_groups(result)
    assert "0 0 * * *" in output


def test_format_groups_shows_invalid_section():
    result = group([INVALID])
    output = format_groups(result)
    assert "Invalid" in output
    assert INVALID in output


def test_format_groups_shows_unique_count():
    result = group([VALID_DAILY, VALID_HOURLY])
    output = format_groups(result)
    assert "2" in output


def test_mixed_batch_all_sections_present():
    result = group([VALID_DAILY, VALID_DAILY, INVALID])
    output = format_groups(result)
    assert "Groups" in output
    assert "Invalid" in output
