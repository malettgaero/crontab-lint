"""Tests for crontab_lint.calendar_view."""

import pytest
from crontab_lint.calendar_view import hour_grid, format_calendar, DAYS_OF_WEEK


def test_invalid_expression_returns_none():
    assert hour_grid("not a cron") is None


def test_grid_shape_is_7_rows_24_cols():
    grid = hour_grid("* * * * *")
    assert grid is not None
    assert len(grid) == 7
    assert all(len(row) == 24 for row in grid)


def test_every_minute_all_cells_true():
    grid = hour_grid("* * * * *")
    assert all(cell for row in grid for cell in row)


def test_specific_hour_only_that_column_true():
    # fires every minute of hour 9, every day
    grid = hour_grid("* 9 * * *")
    for row in grid:
        for h, cell in enumerate(row):
            if h == 9:
                assert cell, f"Expected True at hour 9"
            else:
                assert not cell, f"Expected False at hour {h}"


def test_specific_weekday_only_that_row_true():
    # cron weekday 1 = Monday => display row 0
    grid = hour_grid("* * * * 1")
    for day_idx, row in enumerate(grid):
        if day_idx == 0:  # Monday
            assert all(row), "Monday row should be all True"
        else:
            assert not any(row), f"{DAYS_OF_WEEK[day_idx]} row should be all False"


def test_step_hours_fires_every_six_hours():
    grid = hour_grid("0 */6 * * *")
    expected_hours = {0, 6, 12, 18}
    for row in grid:
        for h, cell in enumerate(row):
            assert cell == (h in expected_hours), f"Mismatch at hour {h}"


def test_active_cell_count_matches_format_output():
    grid = hour_grid("0 0 * * *")
    active = sum(cell for row in grid for cell in row)
    output = format_calendar("0 0 * * *")
    assert f"Active cells: {active} / 168" in output


def test_format_calendar_invalid_expression_returns_error_string():
    result = format_calendar("bad expr")
    assert "Invalid expression" in result


def test_format_calendar_contains_day_labels():
    result = format_calendar("* * * * *")
    for day in DAYS_OF_WEEK:
        assert day in result


def test_format_calendar_contains_expression():
    expr = "30 8 * * 1-5"
    result = format_calendar(expr)
    assert expr in result


def test_sunday_cron_zero_maps_to_last_display_row():
    # cron weekday 0 = Sunday => display row 6
    grid = hour_grid("* * * * 0")
    for day_idx, row in enumerate(grid):
        if day_idx == 6:  # Sunday
            assert all(row)
        else:
            assert not any(row)
