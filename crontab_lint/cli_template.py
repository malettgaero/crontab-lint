"""CLI interface for browsing and using crontab expression templates."""

import argparse
import json
import sys
from crontab_lint.templater import list_templates, get_template, search_templates


def build_template_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-template",
        description="Browse and use crontab expression templates",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available templates")
    list_parser.add_argument(
        "--tag", default=None, help="Filter templates by tag"
    )
    list_parser.add_argument(
        "--json", dest="as_json", action="store_true", help="Output as JSON"
    )

    get_parser = subparsers.add_parser("get", help="Get a template by name")
    get_parser.add_argument("name", help="Template name")
    get_parser.add_argument(
        "--json", dest="as_json", action="store_true", help="Output as JSON"
    )

    search_parser = subparsers.add_parser("search", help="Search templates")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--json", dest="as_json", action="store_true", help="Output as JSON"
    )

    return parser


def _template_to_dict(t) -> dict:
    return {
        "name": t.name,
        "expression": t.expression,
        "description": t.description,
        "tags": t.tags,
    }


def _print_template(t, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(_template_to_dict(t), indent=2))
    else:
        print(f"  {t.name:<22} {t.expression:<18} {t.description}")


def main(argv=None) -> int:
    parser = build_template_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        templates = list_templates(tag=args.tag)
        if not templates:
            print("No templates found.", file=sys.stderr)
            return 1
        if args.as_json:
            print(json.dumps([_template_to_dict(t) for t in templates], indent=2))
        else:
            print(f"{'NAME':<22} {'EXPRESSION':<18} DESCRIPTION")
            print("-" * 70)
            for t in templates:
                _print_template(t)
        return 0

    elif args.command == "get":
        template = get_template(args.name)
        if template is None:
            print(f"Template '{args.name}' not found.", file=sys.stderr)
            return 1
        _print_template(template, as_json=args.as_json)
        return 0

    elif args.command == "search":
        results = search_templates(args.query)
        if not results:
            print(f"No templates matching '{args.query}'.", file=sys.stderr)
            return 1
        if args.as_json:
            print(json.dumps([_template_to_dict(t) for t in results], indent=2))
        else:
            print(f"{'NAME':<22} {'EXPRESSION':<18} DESCRIPTION")
            print("-" * 70)
            for t in results:
                _print_template(t)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
