"""Merge multiple crontab expressions into a unified schedule description."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse
from .humanizer import humanize
from .validator import validate


@dataclass
class MergeResult:
    expressions: List[str]
    valid_expressions: List[str]
    invalid_expressions: List[str]
    merged_description: str
    warnings: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.expressions)

    @property
    def valid_count(self) -> int:
        return len(self.valid_expressions)


def _deduplicate(expressions: List[str]) -> List[str]:
    """Return expressions with duplicates removed, preserving order."""
    seen = set()
    result = []
    for expr in expressions:
        normalized = " ".join(expr.strip().split())
        if normalized not in seen:
            seen.add(normalized)
            result.append(expr)
    return result


def _build_merged_description(valid_expressions: List[str]) -> str:
    """Build a human-readable description for a set of valid expressions."""
    if not valid_expressions:
        return "No valid expressions to describe."
    if len(valid_expressions) == 1:
        return humanize(parse(valid_expressions[0]))
    descriptions = []
    for expr in valid_expressions:
        try:
            descriptions.append(humanize(parse(expr)))
        except Exception:
            continue
    if not descriptions:
        return "Unable to describe merged schedule."
    joined = "; ".join(f"({d})" for d in descriptions)
    return f"Combined schedule: {joined}"


def merge(
    expressions: List[str],
    deduplicate: bool = True,
    skip_invalid: bool = True,
) -> MergeResult:
    """Merge a list of crontab expressions into a single MergeResult.

    Args:
        expressions: List of crontab expression strings.
        deduplicate: If True, remove duplicate expressions before merging.
        skip_invalid: If True, invalid expressions are collected but not merged.

    Returns:
        A MergeResult summarising valid/invalid splits and a merged description.
    """
    if deduplicate:
        expressions = _deduplicate(expressions)

    valid_exprs: List[str] = []
    invalid_exprs: List[str] = []
    warnings: List[str] = []

    for expr in expressions:
        result = validate(expr)
        if result:
            valid_exprs.append(expr)
        else:
            invalid_exprs.append(expr)
            if not skip_invalid:
                warnings.append(f"Invalid expression skipped: '{expr}'")

    if invalid_exprs and skip_invalid:
        warnings.append(
            f"{len(invalid_exprs)} invalid expression(s) excluded from merge."
        )

    merged_description = _build_merged_description(valid_exprs)

    return MergeResult(
        expressions=expressions,
        valid_expressions=valid_exprs,
        invalid_expressions=invalid_exprs,
        merged_description=merged_description,
        warnings=warnings,
    )
