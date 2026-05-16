"""CLI entry-point for the heatmap subcommand."""

from __future__ import annotations

import argparse
import json
import sys

from .heatmap import build_heatmap, format_heatmap, DAYS, HOURS


def build_heatmap_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-heatmap",
        description="Show a weekly firing-frequency heatmap for a cron expression.",
    )
    parser.add_argument("expression", help="Cron expression (quote it!)")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit JSON instead of ASCII art",
    )
    parser.add_argument(
        "--no-color",
        action="store_false",
        dest="color",
        default=True,
        help="Disable ANSI colour codes",
    )
    return parser


def _result_to_dict(result) -> dict:
    return {
        "expression": result.expression,
        "valid": result.valid,
        "errors": result.errors,
        "days": DAYS,
        "hours": HOURS,
        "grid": result.grid,
        "max_value": result.max_value,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_heatmap_parser()
    args = parser.parse_args(argv)

    result = build_heatmap(args.expression)

    if args.as_json:
        print(json.dumps(_result_to_dict(result), indent=2))
    else:
        print(format_heatmap(result, color=args.color))

    return 0 if result.valid else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
