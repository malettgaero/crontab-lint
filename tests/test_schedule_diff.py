"""Tests for schedule diff functionality."""

from datetime import datetime

import pytest

from crontab_lint.schedule_diff import diff_schedules, format_diff


ANCHOR = datetime(2024, 1, 15, 12, 0)


def test_identical_expressions_all_common():
    diff = diff_schedules("* * * * *", "* * * * *", count=5, after=ANCHOR)
    assert len(diff["common"]) == 5
    assert diff["only_a"] == []
    assert diff["only_b"] == []


def test_different_hours_no_overlap():
    diff = diff_schedules("0 8 * * *", "0 17 * * *", count=5, after=ANCHOR)
    assert diff["common"] == []
    assert len(diff["only_a"]) > 0
    assert len(diff["only_b"]) > 0


def test_partial_overlap():
    # Every 30 min vs every hour on the hour
    diff = diff_schedules("0 * * * *", "*/30 * * * *", count=10, after=ANCHOR)
    # Top-of-hour minutes appear in both
    assert len(diff["common"]) > 0
    # Half-hour marks appear only in B
    assert len(diff["only_b"]) > 0


def test_format_diff_contains_sections():
    diff = diff_schedules("0 8 * * *", "0 17 * * *", count=3, after=ANCHOR)
    output = format_diff(diff)
    assert "Only in A:" in output or "Only in B:" in output


def test_format_diff_shared():
    diff = diff_schedules("* * * * *", "* * * * *", count=3, after=ANCHOR)
    output = format_diff(diff)
    assert "Shared run times:" in output


def test_format_diff_no_shared_message():
    diff = diff_schedules("0 8 * * *", "0 17 * * *", count=3, after=ANCHOR)
    output = format_diff(diff)
    assert "No shared run times" in output


def test_invalid_expression_empty_diff():
    diff = diff_schedules("bad expr", "* * * * *", count=5, after=ANCHOR)
    assert diff["common"] == []
    assert diff["only_a"] == []
