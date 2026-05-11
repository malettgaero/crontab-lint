"""CLI sub-command for viewing and managing crontab-lint history."""

from __future__ import annotations

import argparse
import json
import sys

from crontab_lint.history import DEFAULT_HISTORY_PATH, load_history


def build_history_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-history",
        description="View and manage crontab-lint validation history.",
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_HISTORY_PATH,
        help="Path to the history file (default: %(default)s).",
    )
    sub = parser.add_subparsers(dest="command")

    show = sub.add_parser("show", help="Display recent history entries.")
    show.add_argument("-n", "--last", type=int, default=10, metavar="N",
                      help="Show the last N entries (default: 10).")
    show.add_argument("--valid", action="store_true", help="Only show valid expressions.")
    show.add_argument("--invalid", action="store_true", help="Only show invalid expressions.")
    show.add_argument("--json", action="store_true", dest="as_json",
                      help="Output as JSON.")

    sub.add_parser("clear", help="Clear all history entries.")
    sub.add_parser("stats", help="Print summary statistics.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_history_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    history = load_history(args.path)

    if args.command == "show":
        if args.valid:
            entries = history.filter_valid()
        elif args.invalid:
            entries = history.filter_invalid()
        else:
            entries = history.last(args.last)

        if args.as_json:
            import dataclasses
            print(json.dumps([dataclasses.asdict(e) for e in entries], indent=2))
        else:
            for e in entries:
                status = "✓" if e.valid else "✗"
                desc = e.human_readable or "(no description)"
                print(f"[{e.checked_at}] {status} {e.expression!r:40s}  {desc}")
                if e.errors:
                    for err in e.errors:
                        print(f"    ↳ {err}")
        return 0

    if args.command == "clear":
        from crontab_lint.history import save_history
        history.clear()
        save_history(history, args.path)
        print("History cleared.")
        return 0

    if args.command == "stats":
        total = len(history.entries)
        valid = len(history.filter_valid())
        invalid = total - valid
        rate = (valid / total * 100) if total else 0.0
        print(f"Total entries : {total}")
        print(f"Valid         : {valid}")
        print(f"Invalid       : {invalid}")
        print(f"Pass rate     : {rate:.1f}%")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
