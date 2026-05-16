"""Tests for crontab_lint.heatmap."""

import pytest

from crontab_lint.heatmap import build_heatmap, format_heatmap, DAYS, HOURS


def test_invalid_expression_returns_invalid_result():
    result = build_heatmap("not a cron")
    assert not result.valid
    assert result.grid == []
    assert result.errors


def test_grid_shape_is_7_rows_24_cols():
    result = build_heatmap("* * * * *")
    assert result.valid
    assert len(result.grid) == 7
    assert all(len(row) == 24 for row in result.grid)


def test_every_minute_all_cells_60():
    result = build_heatmap("* * * * *")
    for row in result.grid:
        for cell in row:
            assert cell == 60


def test_specific_hour_only_that_column_nonzero():
    result = build_heatmap("0 9 * * *")
    for day_row in result.grid:
        for hour, val in enumerate(day_row):
            if hour == 9:
                assert val > 0
            else:
                assert val == 0


def test_specific_weekday_only_that_row_nonzero():
    # Monday = 1
    result = build_heatmap("0 * * * 1")
    for day_idx, row in enumerate(result.grid):
        if day_idx == 1:
            assert any(v > 0 for v in row)
        else:
            assert all(v == 0 for v in row)


def test_max_value_every_minute():
    result = build_heatmap("* * * * *")
    assert result.max_value == 60


def test_max_value_invalid_is_zero():
    result = build_heatmap("bad")
    assert result.max_value == 0


def test_step_expression_correct_minute_count():
    # */15 fires at 0,15,30,45 => 4 times per hour
    result = build_heatmap("*/15 * * * *")
    for row in result.grid:
        for cell in row:
            assert cell == 4


def test_format_heatmap_contains_day_names():
    result = build_heatmap("0 0 * * *")
    text = format_heatmap(result)
    for day in DAYS:
        assert day in text


def test_format_heatmap_invalid_shows_error():
    result = build_heatmap("bad expression")
    text = format_heatmap(result)
    assert "Invalid" in text


def test_daily_alias_fires_once_per_day():
    result = build_heatmap("@daily")
    assert result.valid
    # @daily = 0 0 * * *  => 1 minute fires at hour 0 each day
    for row in result.grid:
        assert row[0] == 1
        assert all(v == 0 for v in row[1:])


def test_format_heatmap_scale_line_present():
    result = build_heatmap("* * * * *")
    text = format_heatmap(result)
    assert "Scale" in text
