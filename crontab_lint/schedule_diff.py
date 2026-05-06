"""Diff two cron expressions and summarize schedule differences."""

from datetime import datetime, timedelta
from typing import Dict, List

from .explainer import next_runs


def diff_schedules(
    expr_a: str,
    expr_b: str,
    count: int = 10,
    after: datetime = None,
) -> Dict:
    """Compare next run times of two cron expressions.

    Returns a dict with:
      - only_a: times only in expression A
      - only_b: times only in expression B
      - common: times shared by both
    """
    after = after or datetime.now().replace(second=0, microsecond=0)
    runs_a = set(next_runs(expr_a, count=count, after=after))
    runs_b = set(next_runs(expr_b, count=count, after=after))

    return {
        "only_a": sorted(runs_a - runs_b),
        "only_b": sorted(runs_b - runs_a),
        "common": sorted(runs_a & runs_b),
    }


def format_diff(diff: Dict) -> str:
    """Return a human-readable string summarizing the schedule diff."""
    lines = []
    fmt = "%Y-%m-%d %H:%M"

    if diff["common"]:
        lines.append("Shared run times:")
        for dt in diff["common"]:
            lines.append(f"  {dt.strftime(fmt)}")
    else:
        lines.append("No shared run times in the compared window.")

    if diff["only_a"]:
        lines.append("Only in A:")
        for dt in diff["only_a"]:
            lines.append(f"  {dt.strftime(fmt)}")

    if diff["only_b"]:
        lines.append("Only in B:")
        for dt in diff["only_b"]:
            lines.append(f"  {dt.strftime(fmt)}")

    return "\n".join(lines)
