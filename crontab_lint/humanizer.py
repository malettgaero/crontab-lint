"""Human-readable schedule description generator for crontab expressions."""

from .parser import ParsedCron


def _describe_field(value: str, unit: str, singular: str) -> str:
    """Generate a human-readable description for a single crontab field."""
    if value == "*":
        return f"every {singular}"

    # Step with wildcard base: */n
    if value.startswith("*/"):
        step = value[2:]
        return f"every {step} {unit}"

    # Range with optional step: a-b or a-b/n
    if "-" in value and "/" in value:
        range_part, step = value.split("/", 1)
        start, end = range_part.split("-", 1)
        return f"every {step} {unit} from {start} through {end}"

    if "-" in value:
        start, end = value.split("-", 1)
        return f"from {start} through {end}"

    # List of values
    if "," in value:
        parts = value.split(",")
        if len(parts) == 2:
            return f"at {parts[0]} and {parts[1]} {unit}"
        last = parts[-1]
        rest = ", ".join(parts[:-1])
        return f"at {rest}, and {last} {unit}"

    # Single value
    return f"at {singular} {value}"


_DAY_NAMES = {
    "0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
    "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday",
    "sun": "Sunday", "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday",
    "thu": "Thursday", "fri": "Friday", "sat": "Saturday",
}

_MONTH_NAMES = {
    "1": "January", "2": "February", "3": "March", "4": "April",
    "5": "May", "6": "June", "7": "July", "8": "August",
    "9": "September", "10": "October", "11": "November", "12": "December",
    "jan": "January", "feb": "February", "mar": "March", "apr": "April",
    "may": "May", "jun": "June", "jul": "July", "aug": "August",
    "sep": "September", "oct": "October", "nov": "November", "dec": "December",
}


def _describe_weekday(value: str) -> str:
    """Return a human-readable weekday description."""
    if value == "*":
        return "every day of the week"
    if value in _DAY_NAMES:
        return f"on {_DAY_NAMES[value]}s"
    if "," in value:
        days = [_DAY_NAMES.get(d.lower(), d) for d in value.split(",")]
        if len(days) == 2:
            return f"on {days[0]}s and {days[1]}s"
        last = days[-1]
        rest = ", ".join(days[:-1])
        return f"on {rest}, and {last}s"
    if "-" in value:
        parts = value.split("-")
        start = _DAY_NAMES.get(parts[0].lower(), parts[0])
        end = _DAY_NAMES.get(parts[1].lower(), parts[1])
        return f"on {start} through {end}"
    return _describe_field(value, "weekdays", "weekday")


def _describe_month(value: str) -> str:
    """Return a human-readable month description."""
    if value == "*":
        return "every month"
    if value in _MONTH_NAMES:
        return f"in {_MONTH_NAMES[value]}"
    if "," in value:
        months = [_MONTH_NAMES.get(m.lower(), m) for m in value.split(",")]
        if len(months) == 2:
            return f"in {months[0]} and {months[1]}"
        last = months[-1]
        rest = ", ".join(months[:-1])
        return f"in {rest}, and {last}"
    if "-" in value:
        parts = value.split("-")
        start = _MONTH_NAMES.get(parts[0].lower(), parts[0])
        end = _MONTH_NAMES.get(parts[1].lower(), parts[1])
        return f"from {start} through {end}"
    return _describe_field(value, "months", "month")


def humanize(parsed: ParsedCron) -> str:
    """Generate a human-readable description of a parsed crontab expression.

    Args:
        parsed: A ParsedCron namedtuple from the parser module.

    Returns:
        A plain-English string describing when the cron job runs.

    Example:
        >>> from crontab_lint.parser import parse
        >>> from crontab_lint.humanizer import humanize
        >>> humanize(parse("0 9 * * 1"))
        'At minute 0, at hour 9, every day of the month, every month, on Mondays'
    """
    minute_desc = _describe_field(parsed.minute, "minutes", "minute")
    hour_desc = _describe_field(parsed.hour, "hours", "hour")
    dom_desc = _describe_field(parsed.day_of_month, "days", "day of the month")
    month_desc = _describe_month(parsed.month)
    dow_desc = _describe_weekday(parsed.day_of_week)

    parts = [
        minute_desc.capitalize(),
        hour_desc,
        dom_desc,
        month_desc,
        dow_desc,
    ]
    return ", ".join(parts)
