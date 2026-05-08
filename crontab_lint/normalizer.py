"""Normalize crontab expressions to a canonical form."""

from typing import Optional
from crontab_lint.parser import parse, ParsedCron

# Canonical alias mappings (expression -> alias)
_ALIAS_MAP = {
    "0 0 * * *": "@daily",
    "0 0 * * 0": "@weekly",
    "0 0 1 * *": "@monthly",
    "0 0 1 1 *": "@yearly",
    "* * * * *": "@every_minute",
    "0 * * * *": "@hourly",
}

_ALIAS_EXPAND = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


def expand_alias(expression: str) -> str:
    """Expand a @-style alias to a standard 5-field expression."""
    stripped = expression.strip()
    return _ALIAS_EXPAND.get(stripped, stripped)


def _normalize_field(field: str) -> str:
    """Normalize a single cron field to its simplest form."""
    if field == "*":
        return field
    # Remove leading zeros from numbers
    parts = field.split(",")
    normalized_parts = []
    for part in parts:
        if "/" in part:
            base, step = part.split("/", 1)
            step = str(int(step))
            if base == "*":
                normalized_parts.append(f"*/{step}")
            elif "-" in base:
                start, end = base.split("-", 1)
                normalized_parts.append(f"{int(start)}-{int(end)}/{step}")
            else:
                normalized_parts.append(f"{int(base)}/{step}")
        elif "-" in part:
            start, end = part.split("-", 1)
            normalized_parts.append(f"{int(start)}-{int(end)}")
        else:
            normalized_parts.append(str(int(part)))
    return ",".join(normalized_parts)


def normalize(expression: str) -> Optional[str]:
    """Normalize a crontab expression to canonical form.

    Returns the canonical string, or None if the expression is invalid.
    Attempts to replace known patterns with @-aliases.
    """
    expanded = expand_alias(expression)
    parsed = parse(expanded)
    if not parsed:
        return None

    fields = [
        _normalize_field(parsed.minute),
        _normalize_field(parsed.hour),
        _normalize_field(parsed.day_of_month),
        _normalize_field(parsed.month),
        _normalize_field(parsed.day_of_week),
    ]
    canonical = " ".join(fields)
    return _ALIAS_MAP.get(canonical, canonical)
