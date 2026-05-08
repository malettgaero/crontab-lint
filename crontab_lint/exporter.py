"""Export crontab analysis results to various formats (CSV, Markdown)."""

from __future__ import annotations

import csv
import io
from typing import Iterable

from .summarizer import ExpressionSummary


def _format_errors(errors: list[str]) -> str:
    """Join a list of error strings into a single semicolon-separated string."""
    return "; ".join(errors)


def export_csv(summaries: Iterable[ExpressionSummary]) -> str:
    """Serialize a collection of ExpressionSummary objects to a CSV string."""
    output = io.StringIO()
    fieldnames = ["expression", "valid", "human_readable", "errors"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for summary in summaries:
        writer.writerow(
            {
                "expression": summary.expression,
                "valid": summary.valid,
                "human_readable": summary.human_readable or "",
                "errors": _format_errors(summary.errors),
            }
        )
    return output.getvalue()


def export_markdown(summaries: Iterable[ExpressionSummary]) -> str:
    """Serialize a collection of ExpressionSummary objects to a Markdown table."""
    rows = list(summaries)
    lines: list[str] = [
        "| Expression | Valid | Human Readable | Errors |",
        "| --- | --- | --- | --- |",
    ]
    for summary in rows:
        expression = f"`{summary.expression}`"
        valid = "✅" if summary.valid else "❌"
        human_readable = summary.human_readable or ""
        errors = _format_errors(summary.errors) if summary.errors else ""
        lines.append(f"| {expression} | {valid} | {human_readable} | {errors} |")
    return "\n".join(lines) + "\n"
