"""CLI entry point for profiling crontab expressions."""

import argparse
import json
import sys

from .profiler import profile


def build_profile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-profile",
        description="Profile crontab expressions for execution frequency.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPRESSION",
        help="One or more crontab expressions to profile.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    return parser


def _result_to_dict(result) -> dict:
    return {
        "expression": result.expression,
        "valid": result.is_valid,
        "runs_per_hour": result.runs_per_hour,
        "runs_per_day": result.runs_per_day,
        "runs_per_week": result.runs_per_week,
        "runs_per_month": result.runs_per_month,
        "frequency_label": result.frequency_label,
        "warnings": result.warnings,
    }


def main(argv=None) -> int:
    parser = build_profile_parser()
    args = parser.parse_args(argv)

    results = [profile(expr) for expr in args.expressions]
    any_invalid = any(not r.is_valid for r in results)

    if args.json:
        payload = [_result_to_dict(r) for r in results]
        print(json.dumps(payload, indent=2))
        return 1 if any_invalid else 0

    for r in results:
        print(f"Expression : {r.expression}")
        if not r.is_valid:
            print("  Status   : INVALID")
            for w in r.warnings:
                print(f"  Warning  : {w}")
        else:
            print(f"  Status   : valid")
            print(f"  Frequency: {r.frequency_label}")
            print(f"  Per hour : {r.runs_per_hour}")
            print(f"  Per day  : {r.runs_per_day}")
            print(f"  Per week : {r.runs_per_week}")
            print(f"  Per month: {r.runs_per_month}")
            for w in r.warnings:
                print(f"  Warning  : {w}")
        print()

    return 1 if any_invalid else 0


if __name__ == "__main__":
    sys.exit(main())
