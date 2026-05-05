"""Core crontab expression parser and validator."""

import re
from dataclasses import dataclass
from typing import Optional

FIELD_RANGES = {
    "minute":     (0, 59),
    "hour":       (0, 23),
    "day_month":  (1, 31),
    "month":      (1, 12),
    "day_week":   (0, 7),
}

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

WEEKDAY_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}

SPECIAL_STRINGS = {
    "@yearly":   "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly":  "0 0 1 * *",
    "@weekly":   "0 0 * * 0",
    "@daily":    "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly":   "0 * * * *",
}


@dataclass
class ParsedCron:
    raw: str
    minute: str
    hour: str
    day_month: str
    month: str
    day_week: str
    is_valid: bool
    errors: list


def _resolve_aliases(expression: str) -> str:
    lower = expression.strip().lower()
    return SPECIAL_STRINGS.get(lower, expression)


def _normalize_names(value: str, mapping: dict) -> str:
    for name, num in mapping.items():
        value = re.sub(rf"\b{name}\b", str(num), value, flags=re.IGNORECASE)
    return value


def _validate_field(value: str, field: str, min_val: int, max_val: int) -> list:
    errors = []
    if value == "*":
        return errors
    parts = value.split(",")
    for part in parts:
        step_match = re.match(r"^(\*|\d+(?:-\d+)?)(?:/(\d+))?$", part)
        if not step_match:
            errors.append(f"Invalid syntax in {field} field: '{part}'")
            continue
        base, step = step_match.group(1), step_match.group(2)
        if step is not None and int(step) == 0:
            errors.append(f"Step value cannot be zero in {field} field")
        if "-" in base:
            lo, hi = base.split("-", 1)
            if not (min_val <= int(lo) <= max_val):
                errors.append(f"{field} range start {lo} out of bounds [{min_val}-{max_val}]")
            if not (min_val <= int(hi) <= max_val):
                errors.append(f"{field} range end {hi} out of bounds [{min_val}-{max_val}]")
            if int(lo) > int(hi):
                errors.append(f"{field} range start {lo} > end {hi}")
        elif base != "*":
            if not (min_val <= int(base) <= max_val):
                errors.append(f"{field} value {base} out of bounds [{min_val}-{max_val}]")
    return errors


def parse(expression: str) -> ParsedCron:
    expression = _resolve_aliases(expression.strip())
    fields = expression.split()
    errors = []

    if len(fields) != 5:
        return ParsedCron(
            raw=expression, minute="", hour="", day_month="",
            month="", day_week="", is_valid=False,
            errors=[f"Expected 5 fields, got {len(fields)}"]
        )

    minute, hour, day_month, month, day_week = fields
    month = _normalize_names(month, MONTH_NAMES)
    day_week = _normalize_names(day_week, WEEKDAY_NAMES)

    errors += _validate_field(minute,    "minute",    0, 59)
    errors += _validate_field(hour,      "hour",      0, 23)
    errors += _validate_field(day_month, "day_month", 1, 31)
    errors += _validate_field(month,     "month",     1, 12)
    errors += _validate_field(day_week,  "day_week",  0,  7)

    return ParsedCron(
        raw=expression, minute=minute, hour=hour,
        day_month=day_month, month=month, day_week=day_week,
        is_valid=len(errors) == 0, errors=errors
    )
