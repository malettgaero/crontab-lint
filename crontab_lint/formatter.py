"""Format validation results for CLI and programmatic output."""

from typing import Optional
from .validator import ValidationResult
from .humanizer import humanize


ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_result(result: ValidationResult, use_color: bool = True) -> str:
    """Format a ValidationResult into a human-readable string."""
    lines = []

    expr_label = _colorize("Expression:", ANSI_BOLD, use_color)
    lines.append(f"{expr_label} {result.expression}")

    if result.is_valid:
        status = _colorize("✔ Valid", ANSI_GREEN, use_color)
    else:
        status = _colorize("✘ Invalid", ANSI_RED, use_color)
    lines.append(f"Status:     {status}")

    for error in result.errors:
        prefix = _colorize("  ERROR:", ANSI_RED, use_color)
        lines.append(f"{prefix} {error}")

    for warning in result.warnings:
        prefix = _colorize("  WARN: ", ANSI_YELLOW, use_color)
        lines.append(f"{prefix} {warning}")

    if result.is_valid and result.parsed is not None:
        try:
            description = humanize(result.parsed)
            label = _colorize("Schedule:", ANSI_CYAN, use_color)
            lines.append(f"{label}  {description}")
        except Exception:  # noqa: BLE001
            pass

    return "\n".join(lines)


def format_result_json(result: ValidationResult) -> dict:
    """Format a ValidationResult as a plain dict suitable for JSON output."""
    out: dict = {
        "expression": result.expression,
        "valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "schedule": None,
    }
    if result.is_valid and result.parsed is not None:
        try:
            out["schedule"] = humanize(result.parsed)
        except Exception:  # noqa: BLE001
            pass
    return out
