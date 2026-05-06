"""Command-line interface for crontab-lint."""

import argparse
import json
import sys
from typing import List

from crontab_lint.validator import validate
from crontab_lint.humanizer import humanize
from crontab_lint.formatter import format_result, format_result_json
from crontab_lint.recommender import recommend


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Static analyzer and syntax checker for crontab expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPRESSION",
        help="One or more crontab expressions to check (quote each one).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output results as JSON.",
    )
    parser.add_argument(
        "--recommend",
        action="store_true",
        default=False,
        help="Show recommendations and suggestions for each expression.",
    )
    return parser


def main(argv: List[str] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    all_valid = True
    results = []

    for expr in args.expressions:
        result = validate(expr)
        human = humanize(expr) if result else None
        recs = recommend(expr) if args.recommend else []

        if not result:
            all_valid = False

        if args.json:
            entry = json.loads(format_result_json(expr, result, human))
            if recs:
                entry["recommendations"] = recs
            results.append(entry)
        else:
            print(format_result(expr, result, human))
            if recs:
                for rec in recs:
                    print(f"  → {rec}")

    if args.json:
        print(json.dumps(results, indent=2))

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
