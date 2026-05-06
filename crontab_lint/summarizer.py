"""Summarize and compare multiple crontab expressions as a report."""

from dataclasses import dataclass, field
from typing import List, Dict

from .validator import validate
from .humanizer import humanize
from .explainer import next_runs


@dataclass
class ExpressionSummary:
    expression: str
    valid: bool
    errors: List[str]
    human_readable: str
    next_run_previews: List[str]


@dataclass
class BatchSummary:
    total: int
    valid_count: int
    invalid_count: int
    summaries: List[ExpressionSummary] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.valid_count / self.total * 100, 1)


def summarize_expression(expression: str) -> ExpressionSummary:
    """Produce a summary for a single crontab expression."""
    result = validate(expression)
    valid = bool(result)
    errors = result.errors if not valid else []

    human_readable = humanize(expression) if valid else "(invalid expression)"

    from datetime import datetime
    previews = []
    if valid:
        runs = next_runs(expression, datetime(2024, 1, 1, 0, 0), count=3)
        previews = [dt.strftime("%Y-%m-%d %H:%M") for dt in runs]

    return ExpressionSummary(
        expression=expression,
        valid=valid,
        errors=errors,
        human_readable=human_readable,
        next_run_previews=previews,
    )


def summarize_batch(expressions: List[str]) -> BatchSummary:
    """Produce a batch summary for a list of crontab expressions."""
    summaries = [summarize_expression(expr) for expr in expressions]
    valid_count = sum(1 for s in summaries if s.valid)
    return BatchSummary(
        total=len(expressions),
        valid_count=valid_count,
        invalid_count=len(expressions) - valid_count,
        summaries=summaries,
    )


def format_batch_summary(batch: BatchSummary) -> str:
    """Format a BatchSummary as a human-readable report string."""
    lines = [
        f"Crontab Batch Summary",
        f"=====================",
        f"Total expressions : {batch.total}",
        f"Valid             : {batch.valid_count}",
        f"Invalid           : {batch.invalid_count}",
        f"Pass rate         : {batch.pass_rate}%",
        "",
    ]
    for i, s in enumerate(batch.summaries, start=1):
        status = "OK" if s.valid else "FAIL"
        lines.append(f"[{i}] {s.expression}  [{status}]")
        lines.append(f"    Schedule : {s.human_readable}")
        if s.next_run_previews:
            lines.append(f"    Next runs: {', '.join(s.next_run_previews)}")
        for err in s.errors:
            lines.append(f"    ERROR    : {err}")
        lines.append("")
    return "\n".join(lines)
