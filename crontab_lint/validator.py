"""Validation logic for crontab expressions with detailed error reporting."""

from dataclasses import dataclass, field
from typing import List, Optional
from .parser import parse, ParsedCron


@dataclass
class ValidationResult:
    """Result of validating a crontab expression."""

    expression: str
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    parsed: Optional[ParsedCron] = None

    def __bool__(self) -> bool:
        return self.is_valid


def _check_unreachable_schedule(parsed: ParsedCron) -> List[str]:
    """Detect potentially unreachable or suspicious schedule combinations."""
    warnings = []

    # Warn if day-of-month and day-of-week are both restricted
    dom = parsed.day_of_month
    dow = parsed.day_of_week
    if dom != "*" and dow != "*":
        warnings.append(
            "Both day-of-month and day-of-week are restricted; "
            "cron uses OR logic between them, which may be unintentional."
        )

    # Warn on very high frequency (every minute)
    if all(
        getattr(parsed, f) == "*"
        for f in ("minute", "hour", "day_of_month", "month", "day_of_week")
    ):
        warnings.append("Schedule runs every minute — ensure this is intentional.")

    # Warn if step on minute field is 1 (redundant)
    if "/1" in parsed.minute:
        warnings.append(
            f"Step value of 1 in minute field '{parsed.minute}' is redundant."
        )

    return warnings


def validate(expression: str) -> ValidationResult:
    """Validate a crontab expression and return a detailed result."""
    expression = expression.strip()

    if not expression:
        return ValidationResult(
            expression=expression,
            is_valid=False,
            errors=["Expression is empty."],
        )

    try:
        parsed = parse(expression)
    except ValueError as exc:
        return ValidationResult(
            expression=expression,
            is_valid=False,
            errors=[str(exc)],
        )

    warnings = _check_unreachable_schedule(parsed)

    return ValidationResult(
        expression=expression,
        is_valid=True,
        warnings=warnings,
        parsed=parsed,
    )
