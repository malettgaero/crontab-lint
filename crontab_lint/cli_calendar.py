"""CLI entry point for the calendar view feature."""

import argparse
import json
import sys
from crontab_lint.calendar_view import format_calendar, hour_grid


def build_calendar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-calendar",
        description="Render a weekly hour/day grid for one or more cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPRESSION",
        help="Cron expression(s) to visualise.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw grid data as JSON instead of ASCII art.",
    )
    return parser


def _grid_to_json(expression: str) -> dict:
    grid = hour_grid(expression)
    if grid is None:
        return {"expression": expression, "valid": False, "grid": None}
    active_count = sum(cell for row in grid for cell in row)
    return {
        "expression": expression,
        "valid": True,
        "active_cells": active_count,
        "total_cells": 168,
        "grid": grid,
    }


def main(argv=None) -> int:
    parser = build_calendar_parser()
    args = parser.parse_args(argv)

    exit_code = 0

    if args.json:
        results = [_grid_to_json(expr) for expr in args.expressions]
        print(json.dumps(results, indent=2))
        if any(not r["valid"] for r in results):
            exit_code = 1
    else:
        for expr in args.expressions:
            output = format_calendar(expr)
            print(output)
            print()
            if output.startswith("Invalid"):
                exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
