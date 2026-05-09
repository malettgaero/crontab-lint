"""Compare two crontab expressions and describe their differences in human-readable form."""

from dataclasses import dataclass
from typing import Optional

from crontab_lint.parser import parse
from crontab_lint.humanizer import humanize
from crontab_lint.validator import validate


@dataclass
class ComparisonResult:
    expr_a: str
    expr_b: str
    are_equivalent: bool
    human_a: Optional[str]
    human_b: Optional[str]
    differences: list[str]
    valid_a: bool
    valid_b: bool


def _field_names() -> list[str]:
    return ["minute", "hour", "day_of_month", "month", "day_of_week"]


def compare(expr_a: str, expr_b: str) -> ComparisonResult:
    """Compare two crontab expressions and return a structured ComparisonResult."""
    result_a = validate(expr_a)
    result_b = validate(expr_b)

    valid_a = bool(result_a)
    valid_b = bool(result_b)

    human_a = humanize(parse(expr_a)) if valid_a else None
    human_b = humanize(parse(expr_b)) if valid_b else None

    differences: list[str] = []

    if not valid_a:
        differences.append(f"Expression A is invalid: {'; '.join(result_a.errors)}")
    if not valid_b:
        differences.append(f"Expression B is invalid: {'; '.join(result_b.errors)}")

    are_equivalent = False

    if valid_a and valid_b:
        parsed_a = parse(expr_a)
        parsed_b = parse(expr_b)

        fields_a = [
            parsed_a.minute,
            parsed_a.hour,
            parsed_a.day_of_month,
            parsed_a.month,
            parsed_a.day_of_week,
        ]
        fields_b = [
            parsed_b.minute,
            parsed_b.hour,
            parsed_b.day_of_month,
            parsed_b.month,
            parsed_b.day_of_week,
        ]

        field_diffs = []
        for name, fa, fb in zip(_field_names(), fields_a, fields_b):
            if fa != fb:
                field_diffs.append(f"{name}: '{fa}' vs '{fb}'")

        if field_diffs:
            differences.extend(field_diffs)
        else:
            are_equivalent = True

    return ComparisonResult(
        expr_a=expr_a,
        expr_b=expr_b,
        are_equivalent=are_equivalent,
        human_a=human_a,
        human_b=human_b,
        differences=differences,
        valid_a=valid_a,
        valid_b=valid_b,
    )


def format_comparison(result: ComparisonResult) -> str:
    """Render a ComparisonResult as a human-readable string."""
    lines = [
        f"A: {result.expr_a}",
        f"B: {result.expr_b}",
    ]
    if result.human_a:
        lines.append(f"A schedule: {result.human_a}")
    if result.human_b:
        lines.append(f"B schedule: {result.human_b}")

    if result.are_equivalent:
        lines.append("Result: Expressions are equivalent.")
    else:
        lines.append("Result: Expressions differ.")
        for diff in result.differences:
            lines.append(f"  - {diff}")

    return "\n".join(lines)
