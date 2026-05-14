"""Group and cluster crontab expressions by schedule similarity."""

from dataclasses import dataclass, field
from typing import Dict, List

from crontab_lint.parser import parse
from crontab_lint.normalizer import normalize


@dataclass
class ExpressionGroup:
    """A cluster of crontab expressions sharing the same normalized form."""

    canonical: str
    members: List[str] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.members)


@dataclass
class GroupResult:
    """Result of grouping a batch of crontab expressions."""

    groups: List[ExpressionGroup] = field(default_factory=list)
    invalid: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(g.size for g in self.groups) + len(self.invalid)

    @property
    def unique_schedules(self) -> int:
        return len(self.groups)


def group(expressions: List[str]) -> GroupResult:
    """Group expressions by their normalized canonical form.

    Expressions that are syntactically invalid are collected separately.
    Aliases and equivalent forms are collapsed into the same group.
    """
    buckets: Dict[str, ExpressionGroup] = {}
    invalid: List[str] = []

    for expr in expressions:
        parsed = parse(expr)
        if not parsed:
            invalid.append(expr)
            continue

        canonical = normalize(expr)
        if canonical not in buckets:
            buckets[canonical] = ExpressionGroup(canonical=canonical)
        buckets[canonical].members.append(expr)

    groups = sorted(buckets.values(), key=lambda g: (-g.size, g.canonical))
    return GroupResult(groups=groups, invalid=invalid)


def format_groups(result: GroupResult) -> str:
    """Return a human-readable summary of grouped expressions."""
    lines: List[str] = []

    lines.append(f"Unique schedules : {result.unique_schedules}")
    lines.append(f"Total expressions: {result.total}")
    lines.append(f"Invalid          : {len(result.invalid)}")

    if result.groups:
        lines.append("")
        lines.append("Groups:")
        for grp in result.groups:
            lines.append(f"  [{grp.size}] {grp.canonical}")
            for member in grp.members:
                marker = "    =" if member == grp.canonical else "    ~"
                lines.append(f"{marker} {member}")

    if result.invalid:
        lines.append("")
        lines.append("Invalid expressions:")
        for expr in result.invalid:
            lines.append(f"  ! {expr}")

    return "\n".join(lines)
