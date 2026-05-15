"""Profile crontab expressions to estimate execution frequency and resource impact."""

from dataclasses import dataclass, field
from typing import List

from .parser import parse


@dataclass
class ProfileResult:
    expression: str
    is_valid: bool
    runs_per_hour: float
    runs_per_day: float
    runs_per_week: float
    runs_per_month: float
    frequency_label: str
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid


def _count_values(field_str: str, min_val: int, max_val: int) -> int:
    """Count how many distinct values a cron field matches within its range."""
    total = max_val - min_val + 1
    if field_str == "*":
        return total
    count = 0
    for part in field_str.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            lo = min_val if base == "*" else int(base.split("-")[0])
            hi = max_val if "-" not in base or base == "*" else int(base.split("-")[1])
            count += len(range(lo, hi + 1, step))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            count += int(hi) - int(lo) + 1
        else:
            count += 1
    return min(count, total)


def _frequency_label(runs_per_day: float) -> str:
    if runs_per_day >= 1440:
        return "every-minute"
    if runs_per_day >= 24:
        return "high-frequency"
    if runs_per_day >= 1:
        return "moderate"
    if runs_per_day >= 1 / 7:
        return "low-frequency"
    return "rare"


def profile(expression: str) -> ProfileResult:
    """Profile a crontab expression and return frequency statistics."""
    parsed = parse(expression)
    if parsed is None:
        return ProfileResult(
            expression=expression,
            is_valid=False,
            runs_per_hour=0,
            runs_per_day=0,
            runs_per_week=0,
            runs_per_month=0,
            frequency_label="invalid",
            warnings=["Expression could not be parsed."],
        )

    minutes = _count_values(parsed.minute, 0, 59)
    hours = _count_values(parsed.hour, 0, 23)
    dom = _count_values(parsed.dom, 1, 31)
    months = _count_values(parsed.month, 1, 12)
    dow = _count_values(parsed.dow, 0, 6)

    # Approximate: treat dom and dow as independent filters over a month
    dom_factor = dom / 31
    dow_factor = dow / 7
    day_factor = min(dom_factor + dow_factor, 1.0)

    runs_per_hour = minutes
    runs_per_day = minutes * hours
    runs_per_week = runs_per_day * 7 * dow_factor
    runs_per_month = minutes * hours * 31 * day_factor * (months / 12)

    warnings = []
    if runs_per_day >= 1440:
        warnings.append("Schedule runs every minute — consider reducing frequency.")
    elif runs_per_day > 288:
        warnings.append("High execution frequency detected (>288 runs/day).")

    return ProfileResult(
        expression=expression,
        is_valid=True,
        runs_per_hour=round(runs_per_hour, 2),
        runs_per_day=round(runs_per_day, 2),
        runs_per_week=round(runs_per_week, 2),
        runs_per_month=round(runs_per_month, 2),
        frequency_label=_frequency_label(runs_per_day),
        warnings=warnings,
    )
