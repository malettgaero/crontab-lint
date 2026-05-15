"""CLI interface for tagging crontab expressions with semantic labels."""

import argparse
import json
import sys
from crontab_lint.tagger import tag


def build_tag_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-tag",
        description="Tag crontab expressions with semantic labels.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPRESSION",
        help="One or more crontab expressions to tag.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON.",
    )
    parser.add_argument(
        "--filter-tag",
        metavar="TAG",
        dest="filter_tag",
        default=None,
        help="Only show expressions that have this tag.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_tag_parser()
    args = parser.parse_args(argv)

    results = [tag(expr) for expr in args.expressions]

    if args.filter_tag:
        results = [r for r in results if r.has_tag(args.filter_tag)]

    if args.json_output:
        output = [
            {
                "expression": r.expression,
                "valid": r.valid,
                "tags": r.tags,
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
        return 0 if all(r.valid for r in results) else 1

    exit_code = 0
    for r in results:
        status = "OK" if r.valid else "INVALID"
        tags_str = ", ".join(r.tags) if r.tags else "(none)"
        print(f"[{status}] {r.expression}")
        if r.valid:
            print(f"  Tags: {tags_str}")
        else:
            print("  Could not tag: expression is invalid.")
        if not r.valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
