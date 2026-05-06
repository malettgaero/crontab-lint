"""Output formatters for crontab-lint results."""

import json
from typing import List

from .validator import ValidationResult

_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def _colorize(text: str, color: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def format_result(result: ValidationResult, *, color: bool = True, next_runs: List = None) -> str:
    """Format a ValidationResult as a human-readable string.

    Optionally includes upcoming run times if `next_runs` is provided.
    """
    lines = []
    status = _colorize("VALID", "green") if result.valid else _colorize("INVALID", "red")
    expr = _colorize(result.expression, "cyan") if color else result.expression
    lines.append(f"{status}  {expr}")

    if result.human_readable:
        label = _colorize("Schedule:", "bold") if color else "Schedule:"
        lines.append(f"  {label} {result.human_readable}")

    for warning in result.warnings:
        tag = _colorize("WARN", "yellow") if color else "WARN"
        lines.append(f"  [{tag}] {warning}")

    for error in result.errors:
        tag = _colorize("ERR", "red") if color else "ERR"
        lines.append(f"  [{tag}] {error}")

    if next_runs:
        label = _colorize("Next runs:", "bold") if color else "Next runs:"
        lines.append(f"  {label}")
        for dt in next_runs:
            lines.append(f"    - {dt.strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(lines)


def format_result_json(result: ValidationResult, *, next_runs: List = None) -> str:
    """Format a ValidationResult as a JSON string."""
    data = {
        "expression": result.expression,
        "valid": result.valid,
        "human_readable": result.human_readable,
        "warnings": result.warnings,
        "errors": result.errors,
    }
    if next_runs is not None:
        data["next_runs"] = [dt.strftime("%Y-%m-%dT%H:%M:00") for dt in next_runs]
    return json.dumps(data, indent=2)
