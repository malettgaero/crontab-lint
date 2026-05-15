"""Calendar view: render which hours/days a cron expression fires in a compact grid."""

from typing import List, Optional
from crontab_lint.parser import parse
from crontab_lint.explainer import _field_matches

DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _expand_field(field: str, min_val: int, max_val: int) -> List[int]:
    """Return list of integers matched by a cron field string."""
    result = []
    for v in range(min_val, max_val + 1):
        if _field_matches(field, v, min_val, max_val):
            result.append(v)
    return result


def hour_grid(expression: str) -> Optional[List[List[bool]]]:
    """Return a 7-row x 24-col boolean grid: grid[weekday][hour] is True if the
    expression fires during that weekday/hour combination.

    Returns None when the expression is invalid.
    """
    parsed = parse(expression)
    if parsed is None:
        return None

    active_hours = _expand_field(parsed.hour, 0, 23)
    # cron weekday: 0=Sunday ... 6=Saturday; we map to Mon-Sun (0-6) for display
    # cron 0 and 7 both mean Sunday
    active_cron_days = _expand_field(parsed.day_of_week, 0, 6)
    # convert cron day (0=Sun) to display day (0=Mon)
    active_display_days = set()
    for d in active_cron_days:
        display = (d - 1) % 7  # Sun(0)->6, Mon(1)->0, ..., Sat(6)->5
        active_display_days.add(display)

    grid = []
    for display_day in range(7):
        row = [display_day in active_display_days and h in active_hours for h in range(24)]
        grid.append(row)
    return grid


def format_calendar(expression: str) -> str:
    """Render a compact ASCII calendar grid for the expression.

    Returns an error message string when the expression is invalid.
    """
    grid = hour_grid(expression)
    if grid is None:
        return f"Invalid expression: {expression!r}"

    hour_header = "     " + "".join(f"{h:02d}" for h in range(24))
    separator = "     " + "-" * 48
    lines = [hour_header, separator]
    for day_idx, row in enumerate(grid):
        cells = "".join("##" if active else ".." for active in row)
        lines.append(f"{DAYS_OF_WEEK[day_idx]}  {cells}")
    lines.append("")
    lines.append(f"Expression : {expression}")
    lines.append(f"Active cells: {sum(cell for row in grid for cell in row)} / 168")
    return "\n".join(lines)
