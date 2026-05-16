"""Generate a frequency heatmap showing how often a cron expression fires
per hour across each day of the week."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .calendar_view import _expand_field
from .validator import validate

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
HOURS = list(range(24))


@dataclass
class HeatmapResult:
    """Result of a heatmap computation."""

    valid: bool
    expression: str
    # grid[day][hour] = number of minutes that fire in that slot (0-60)
    grid: list[list[int]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def max_value(self) -> int:
        if not self.grid:
            return 0
        return max(cell for row in self.grid for cell in row)


def _expand_minutes(expr: str) -> list[int]:
    """Return the list of minutes (0-59) that match the minute field."""
    return _expand_field(expr, 0, 59)


def build_heatmap(expression: str) -> HeatmapResult:
    """Build a 7x24 heatmap grid for *expression*.

    Each cell contains the number of minutes (within that hour) on which the
    cron job fires.  A value of 0 means the job never fires in that slot.
    """
    result = validate(expression)
    if not result:
        return HeatmapResult(
            valid=False,
            expression=expression,
            errors=result.errors,
        )

    # Resolve alias so we always have 5 fields
    from .normalizer import expand_alias, _normalize_field  # noqa: PLC0415

    normalized = expand_alias(expression.strip())
    parts = normalized.split()
    minute_field, hour_field, _dom, _month, dow_field = parts

    active_hours = set(_expand_field(hour_field, 0, 23))
    active_dow = set(_expand_field(dow_field, 0, 6))
    minute_count = len(_expand_minutes(minute_field))

    grid: list[list[int]] = []
    for day in range(7):
        row: list[int] = []
        for hour in range(24):
            if day in active_dow and hour in active_hours:
                row.append(minute_count)
            else:
                row.append(0)
        grid.append(row)

    return HeatmapResult(valid=True, expression=expression, grid=grid)


def format_heatmap(result: HeatmapResult, *, color: bool = True) -> str:
    """Render *result* as a compact ASCII heatmap table."""
    if not result.valid:
        return "Invalid expression: " + "; ".join(result.errors)

    max_val = result.max_value or 1
    shades = " ░▒▓█"

    header = "     " + "".join(f"{h:2}" for h in HOURS)
    lines = [header]
    for day_idx, day_name in enumerate(DAYS):
        row_cells = []
        for hour in range(24):
            val = result.grid[day_idx][hour]
            bucket = int((val / max_val) * (len(shades) - 1))
            ch = shades[bucket]
            row_cells.append(ch * 2)
        lines.append(f"{day_name}  " + "".join(row_cells))

    lines.append(f"\nScale: 0={shades[0]*2} .. {max_val} fires/hr={shades[-1]*2}")
    return "\n".join(lines)
