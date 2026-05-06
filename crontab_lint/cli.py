"""Command-line interface for crontab-lint."""

import argparse
import json
import sys

from .validator import validate
from .formatter import format_result, format_result_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Static analyzer and syntax checker for crontab expressions.",
    )
    p.add_argument(
        "expression",
        nargs="+",
        help="One or more crontab expressions to validate (quote each one).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output results as JSON.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output.",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    results = [validate(expr) for expr in args.expression]
    all_valid = all(r.is_valid for r in results)

    if args.json:
        payload = (
            format_result_json(results[0])
            if len(results) == 1
            else [format_result_json(r) for r in results]
        )
        print(json.dumps(payload, indent=2))
    else:
        use_color = not args.no_color and sys.stdout.isatty()
        for i, result in enumerate(results):
            if i > 0:
                print()
            print(format_result(result, use_color=use_color))

    return 0 if all_valid else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
