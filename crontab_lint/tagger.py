"""Tag crontab expressions with semantic labels based on their schedule patterns."""

from dataclasses import dataclass, field
from typing import List
from crontab_lint.validator import validate
from crontab_lint.parser import parse


@dataclass
class TagResult:
    expression: str
    tags: List[str] = field(default_factory=list)
    valid: bool = True

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


def _infer_tags(expression: str) -> List[str]:
    """Infer semantic tags from a valid cron expression."""
    tags = []

    aliases = {
        "@yearly": "yearly",
        "@annually": "yearly",
        "@monthly": "monthly",
        "@weekly": "weekly",
        "@daily": "daily",
        "@midnight": "daily",
        "@hourly": "hourly",
        "@reboot": "reboot",
    }
    if expression.strip() in aliases:
        tags.append(aliases[expression.strip()])
        tags.append("alias")
        return tags

    parsed = parse(expression)
    minute, hour, dom, month, dow = (
        parsed.minute,
        parsed.hour,
        parsed.dom,
        parsed.month,
        parsed.dow,
    )

    if minute == "*" and hour == "*" and dom == "*" and month == "*" and dow == "*":
        tags.append("every-minute")
    elif dom == "*" and month == "*" and dow == "*":
        if hour == "*":
            tags.append("sub-hourly")
        else:
            tags.append("intra-day")
    elif dom == "*" and month == "*" and dow != "*":
        tags.append("weekly")
    elif dom != "*" and month == "*" and dow == "*":
        tags.append("monthly")
    elif month != "*":
        tags.append("yearly")

    if minute == "0" and hour != "*":
        tags.append("top-of-hour")

    if "*/" in minute or "*/" in hour:
        tags.append("interval")

    if "," in minute or "," in hour or "," in dom or "," in dow:
        tags.append("multi-value")

    if "-" in minute or "-" in hour or "-" in dom or "-" in dow or "-" in month:
        tags.append("range")

    return tags


def tag(expression: str) -> TagResult:
    """Tag a crontab expression with semantic labels."""
    result = validate(expression)
    if not result:
        return TagResult(expression=expression, tags=[], valid=False)

    tags = _infer_tags(expression)
    return TagResult(expression=expression, tags=tags, valid=True)
