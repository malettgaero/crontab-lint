"""Next-run time explainer for crontab expressions."""

from datetime import datetime, timedelta
from typing import List

from .parser import ParsedCron, parse


def _field_matches(value: int, field: str, min_val: int, max_val: int) -> bool:
    """Check if a value matches a crontab field expression."""
    if field == "*":
        return True
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" else (int(base.split("-")[1]) if "-" in base else start)
            if start <= value <= end and (value - start) % step == 0:
                return True
        elif "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= value <= int(hi):
                return True
        else:
            if int(part) == value:
                return True
    return False


def next_runs(expression: str, count: int = 5, after: datetime = None) -> List[datetime]:
    """Return the next `count` run times for the given cron expression."""
    parsed = parse(expression)
    if parsed is None:
        return []

    start = (after or datetime.now()).replace(second=0, microsecond=0)
    current = start + timedelta(minutes=1)
    results: List[datetime] = []

    max_iterations = 366 * 24 * 60 * 2  # safety limit: ~2 years
    iterations = 0

    while len(results) < count and iterations < max_iterations:
        iterations += 1
        if (
            _field_matches(current.minute, parsed.minute, 0, 59)
            and _field_matches(current.hour, parsed.hour, 0, 23)
            and _field_matches(current.day, parsed.day_of_month, 1, 31)
            and _field_matches(current.month, parsed.month, 1, 12)
            and _field_matches(current.weekday(), parsed.day_of_week, 0, 6)
        ):
            results.append(current)
        current += timedelta(minutes=1)

    return results
