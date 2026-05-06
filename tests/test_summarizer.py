"""Tests for crontab_lint.summarizer module."""

import pytest
from crontab_lint.summarizer import (
    summarize_expression,
    summarize_batch,
    format_batch_summary,
    ExpressionSummary,
    BatchSummary,
)


def test_summarize_valid_expression():
    summary = summarize_expression("0 9 * * 1-5")
    assert summary.valid is True
    assert summary.errors == []
    assert summary.human_readable != "(invalid expression)"
    assert len(summary.next_run_previews) == 3


def test_summarize_invalid_expression():
    summary = summarize_expression("99 9 * * *")
    assert summary.valid is False
    assert len(summary.errors) > 0
    assert summary.human_readable == "(invalid expression)"
    assert summary.next_run_previews == []


def test_summarize_expression_stores_original():
    expr = "*/5 * * * *"
    summary = summarize_expression(expr)
    assert summary.expression == expr


def test_summarize_batch_counts():
    expressions = ["* * * * *", "0 12 * * *", "99 99 * * *"]
    batch = summarize_batch(expressions)
    assert batch.total == 3
    assert batch.valid_count == 2
    assert batch.invalid_count == 1


def test_summarize_batch_pass_rate():
    expressions = ["* * * * *", "0 0 * * *"]
    batch = summarize_batch(expressions)
    assert batch.pass_rate == 100.0


def test_summarize_batch_zero_pass_rate():
    expressions = ["99 * * * *", "* 25 * * *"]
    batch = summarize_batch(expressions)
    assert batch.pass_rate == 0.0


def test_summarize_batch_empty():
    batch = summarize_batch([])
    assert batch.total == 0
    assert batch.valid_count == 0
    assert batch.invalid_count == 0
    assert batch.pass_rate == 0.0


def test_summarize_batch_contains_summaries():
    expressions = ["* * * * *", "0 6 * * *"]
    batch = summarize_batch(expressions)
    assert len(batch.summaries) == 2
    assert all(isinstance(s, ExpressionSummary) for s in batch.summaries)


def test_format_batch_summary_contains_header():
    batch = summarize_batch(["* * * * *"])
    report = format_batch_summary(batch)
    assert "Crontab Batch Summary" in report
    assert "Pass rate" in report


def test_format_batch_summary_shows_ok_and_fail():
    batch = summarize_batch(["* * * * *", "99 * * * *"])
    report = format_batch_summary(batch)
    assert "[OK]" in report
    assert "[FAIL]" in report


def test_format_batch_summary_shows_errors_for_invalid():
    batch = summarize_batch(["99 * * * *"])
    report = format_batch_summary(batch)
    assert "ERROR" in report


def test_format_batch_summary_shows_next_runs_for_valid():
    batch = summarize_batch(["0 9 * * 1"])
    report = format_batch_summary(batch)
    assert "Next runs" in report
