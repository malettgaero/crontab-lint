"""CLI helpers for exporting batch analysis results."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .exporter import export_csv, export_markdown
from .summarizer import summarize_batch


def build_export_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the export sub-command."""
    parser = argparse.ArgumentParser(
        prog="crontab-lint-export",
        description="Export batch crontab analysis results to CSV or Markdown.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPRESSION",
        help="One or more crontab expressions to analyse.",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "markdown"],
        default="csv",
        dest="output_format",
        help="Output format (default: csv).",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    """Entry point for the export CLI."""
    parser = build_export_parser()
    args = parser.parse_args(argv)

    batch = summarize_batch(args.expressions)
    summaries = batch.summaries

    if args.output_format == "csv":
        content = export_csv(summaries)
    else:
        content = export_markdown(summaries)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(content)
        except OSError as exc:
            print(f"Error writing to {args.output}: {exc}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(content)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
