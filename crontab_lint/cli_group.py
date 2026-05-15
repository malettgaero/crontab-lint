"""CLI entry point for grouping crontab expressions."""

import argparse
import json
import sys
from typing import List

from crontab_lint.grouper import group, format_groups


def build_group_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-group",
        description="Group crontab expressions by equivalent schedule.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expressions to group (or read from --file).",
    )
    parser.add_argument(
        "--file",
        "-f",
        metavar="PATH",
        help="Read expressions from a file, one per line.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    return parser


def _load_from_file(path: str) -> List[str]:
    """Read non-empty, stripped lines from *path* and return them as a list."""
    with open(path) as fh:
        return [line.strip() for line in fh if line.strip()]


def _build_json_payload(result) -> dict:
    """Convert a GroupResult into a JSON-serialisable dictionary."""
    return {
        "unique_schedules": result.unique_schedules,
        "total": result.total,
        "invalid_count": len(result.invalid),
        "groups": [
            {"canonical": g.canonical, "members": g.members, "size": g.size}
            for g in result.groups
        ],
        "invalid": result.invalid,
    }


def main(argv=None) -> int:
    parser = build_group_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions)

    if args.file:
        try:
            expressions.extend(_load_from_file(args.file))
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help()
        return 0

    result = group(expressions)

    if args.json:
        print(json.dumps(_build_json_payload(result), indent=2))
    else:
        print(format_groups(result))

    return 1 if result.invalid else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
