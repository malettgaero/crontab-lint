"""Annotator module: attach inline comments/labels to crontab fields."""

from dataclasses import dataclass
from typing import List

from .parser import parse, ParsedCron
from .humanizer import humanize


@dataclass
class AnnotatedField:
    name: str
    raw: str
    description: str


@dataclass
class AnnotatedCron:
    expression: str
    fields: List[AnnotatedField]
    summary: str
    valid: bool


_FIELD_LABELS = {
    "minute": "minute (0-59)",
    "hour": "hour (0-23)",
    "day_of_month": "day of month (1-31)",
    "month": "month (1-12)",
    "day_of_week": "day of week (0-6, Sun=0)",
}

_FIELD_ORDER = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def _describe_field_value(name: str, value: str) -> str:
    """Return a short inline description for a single field's raw value."""
    if value == "*":
        return f"every {name.replace('_', ' ')}"
    if "/" in value:
        base, step = value.split("/", 1)
        base_str = "any" if base == "*" else f"starting at {base}"
        return f"every {step} ({base_str})"
    if "-" in value:
        lo, hi = value.split("-", 1)
        return f"from {lo} to {hi}"
    if "," in value:
        parts = value.split(",")
        return "one of: " + ", ".join(parts)
    return f"at {value}"


def annotate(expression: str) -> AnnotatedCron:
    """Parse a crontab expression and return an annotated breakdown."""
    from .validator import validate

    result = validate(expression)
    if not result:
        return AnnotatedCron(
            expression=expression,
            fields=[],
            summary="Invalid expression: " + "; ".join(result.errors),
            valid=False,
        )

    parsed: ParsedCron = parse(expression)
    raw_fields = {
        "minute": parsed.minute,
        "hour": parsed.hour,
        "day_of_month": parsed.day_of_month,
        "month": parsed.month,
        "day_of_week": parsed.day_of_week,
    }

    annotated_fields = [
        AnnotatedField(
            name=name,
            raw=raw_fields[name],
            description=_describe_field_value(name, raw_fields[name]),
        )
        for name in _FIELD_ORDER
    ]

    return AnnotatedCron(
        expression=expression,
        fields=annotated_fields,
        summary=humanize(expression),
        valid=True,
    )


def format_annotation(annotated: AnnotatedCron) -> str:
    """Render an AnnotatedCron as a human-readable multi-line string."""
    lines = [f"Expression : {annotated.expression}"]
    if not annotated.valid:
        lines.append(f"Status     : INVALID — {annotated.summary}")
        return "\n".join(lines)

    lines.append(f"Summary    : {annotated.summary}")
    lines.append("Fields     :")
    for field in annotated.fields:
        label = _FIELD_LABELS.get(field.name, field.name)
        lines.append(f"  {field.raw:<12} # {label} — {field.description}")
    return "\n".join(lines)
