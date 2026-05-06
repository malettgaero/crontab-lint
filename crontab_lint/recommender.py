"""Suggests corrections or alternatives for invalid or unusual crontab expressions."""

from typing import List, Optional
from crontab_lint.parser import parse

# Common named schedules and their cron equivalents
COMMON_SCHEDULES = {
    "@yearly": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@midnight": "0 0 * * *",
}

SUGGESTIONS_MAP = {
    # Patterns that look like mistakes and their likely intent
    "60": "59",  # seconds overflow into minutes
    "24": "23",  # hour overflow
    "32": "31",  # day overflow
    "13": "12",  # month overflow
    "7": "0",   # weekday 7 -> 0 (Sunday)
}


def _suggest_field_fix(field: str, min_val: int, max_val: int) -> Optional[str]:
    """Return a corrected field value if a simple fix is possible."""
    if field.isdigit():
        val = int(field)
        if val > max_val:
            return str(max_val)
        if val < min_val:
            return str(min_val)
    return None


def _closest_common_schedule(expression: str) -> Optional[str]:
    """Return the closest named schedule alias if the expression matches one."""
    for alias, pattern in COMMON_SCHEDULES.items():
        if expression.strip() == pattern:
            return alias
    return None


def recommend(expression: str) -> List[str]:
    """Analyze an expression and return a list of human-readable recommendations."""
    recommendations: List[str] = []

    alias = _closest_common_schedule(expression)
    if alias:
        recommendations.append(f"This expression can be written as the alias '{alias}'.")

    parsed = parse(expression)
    if parsed is None:
        parts = expression.strip().split()
        if len(parts) != 5:
            recommendations.append(
                f"Expression has {len(parts)} field(s); expected exactly 5 "
                "(minute hour day month weekday)."
            )
            return recommendations

        field_meta = [
            ("minute", 0, 59),
            ("hour", 0, 23),
            ("day", 1, 31),
            ("month", 1, 12),
            ("weekday", 0, 6),
        ]
        for i, (name, lo, hi) in enumerate(field_meta):
            fix = _suggest_field_fix(parts[i], lo, hi)
            if fix:
                recommendations.append(
                    f"Field '{name}' has value '{parts[i]}'; valid range is {lo}-{hi}. "
                    f"Did you mean '{fix}'?"
                )
        if not recommendations:
            recommendations.append(
                "Expression could not be parsed. Check for unsupported syntax or typos."
            )
    else:
        if parsed.minute == "*" and parsed.hour == "*":
            recommendations.append(
                "Schedule runs every minute. Consider using a less frequent interval "
                "if this is unintentional."
            )

    return recommendations
