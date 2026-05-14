"""Tests for crontab_lint.merger module."""

import pytest
from crontab_lint.merger import merge, MergeResult, _deduplicate, _build_merged_description


def test_merge_all_valid_returns_all_in_valid_list():
    result = merge(["* * * * *", "0 12 * * *"])
    assert "* * * * *" in result.valid_expressions
    assert "0 12 * * *" in result.valid_expressions
    assert result.invalid_expressions == []


def test_merge_invalid_expression_excluded():
    result = merge(["* * * * *", "99 99 99 99 99"])
    assert "* * * * *" in result.valid_expressions
    assert "99 99 99 99 99" in result.invalid_expressions


def test_merge_all_invalid_returns_empty_valid_list():
    result = merge(["99 99 99 99 99", "abc def"])
    assert result.valid_expressions == []
    assert len(result.invalid_expressions) == 2


def test_merge_result_total_count():
    result = merge(["* * * * *", "0 6 * * *", "0 12 * * *"])
    assert result.total == 3


def test_merge_result_valid_count():
    result = merge(["* * * * *", "0 6 * * *"])
    assert result.valid_count == 2


def test_merge_warning_for_invalid_expressions():
    result = merge(["99 99 99 99 99"])
    assert any("excluded" in w for w in result.warnings)


def test_merge_deduplicate_removes_duplicates():
    result = merge(["* * * * *", "* * * * *", "0 12 * * *"], deduplicate=True)
    assert result.total == 2


def test_merge_no_deduplicate_keeps_duplicates():
    result = merge(["* * * * *", "* * * * *"], deduplicate=False)
    assert result.total == 2


def test_merge_single_expression_description_not_combined():
    result = merge(["0 12 * * *"])
    assert "Combined schedule" not in result.merged_description


def test_merge_multiple_valid_description_is_combined():
    result = merge(["0 6 * * *", "0 18 * * *"])
    assert "Combined schedule" in result.merged_description


def test_merge_empty_list_returns_empty_result():
    result = merge([])
    assert result.total == 0
    assert result.valid_expressions == []
    assert result.invalid_expressions == []


def test_merge_empty_list_description_fallback():
    result = merge([])
    assert "No valid" in result.merged_description


def test_deduplicate_preserves_order():
    exprs = ["0 12 * * *", "* * * * *", "0 12 * * *"]
    result = _deduplicate(exprs)
    assert result == ["0 12 * * *", "* * * * *"]


def test_deduplicate_handles_extra_whitespace():
    exprs = ["0  12  *  *  *", "0 12 * * *"]
    result = _deduplicate(exprs)
    assert len(result) == 1


def test_build_merged_description_empty():
    desc = _build_merged_description([])
    assert "No valid" in desc


def test_merge_result_is_dataclass_instance():
    result = merge(["* * * * *"])
    assert isinstance(result, MergeResult)
