"""CLI entry point for the annotate sub-command."""

import argparse
import json
import sys
from typing import List

from .annotator import annotate, format_annotation


def build_annotate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-annotate",
        description="Display an annotated breakdown of a crontab expression.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPRESSION",
        help="One or more crontab expressions to annotate.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON.",
    )
    return parser


def _annotated_to_dict(annotated) -> dict:
    return {
        "expression": annotated.expression,
        "valid": annotated.valid,
        "summary": annotated.summary,
        "fields": [
            {
                "name": f.name,
                "raw": f.raw,
                "description": f.description,
            }
            for f in annotated.fields
        ],
    }


def main(argv: List[str] = None) -> int:
    parser = build_annotate_parser()
    args = parser.parse_args(argv)

    results = [annotate(expr) for expr in args.expressions]
    all_valid = all(r.valid for r in results)

    if args.json_output:
        payload = (
            _annotated_to_dict(results[0])
            if len(results) == 1
            else [_annotated_to_dict(r) for r in results]
        )
        print(json.dumps(payload, indent=2))
    else:
        for i, result in enumerate(results):
            if i > 0:
                print()
            print(format_annotation(result))

    return 0 if all_valid else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
