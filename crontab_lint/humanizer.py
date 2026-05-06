"""Human-readable descriptions for crontab expressions."""

from .parser import ParsedCron

_WEEKDAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]

_MONTH_NAMES = [
    "", "January", "February", "March", "April",
    "May", "June", "July", "August", "September",
    "October", "November", "December"
]


def _describe_weekday(value: str) -> str:
    """Return a human-readable weekday name or range."""
    if value == "*":
        return "every day of the week"
    if "-" in value:
        start, end = value.split("-", 1)
        return f"{_WEEKDAY_NAMES[int(start)]} through {_WEEKDAY_NAMES[int(end)]}"
    if "," in value:
        parts = [_WEEKDAY_NAMES[int(v)] for v in value.split(",")]
        return ", ".join(parts)
    return _WEEKDAY_NAMES[int(value)]


def _describe_month(value: str) -> str:
    """Return a human-readable month name or range."""
    if value == "*":
        return "every month"
    if "-" in value:
        start, end = value.split("-", 1)
        return f"{_MONTH_NAMES[int(start)]} through {_MONTH_NAMES[int(end)]}"
    if "," in value:
        parts = [_MONTH_NAMES[int(v)] for v in value.split(",")]
        return ", ".join(parts)
    return _MONTH_NAMES[int(value)]


def _describe_field(value: str, unit: str, singular: str) -> str:
    """Return a human-readable description for a generic cron field."""
    if value == "*":
        return f"every {singular}"
    if value.startswith("*/"):
        step = value[2:]
        return f"every {step} {unit}"
    if "-" in value and "/" in value:
        range_part, step = value.split("/", 1)
        start, end = range_part.split("-", 1)
        return f"every {step} {unit} from {start} through {end}"
    if "-" in value:
        start, end = value.split("-", 1)
        return f"{start} through {end}"
    if "," in value:
        parts = value.split(",")
        return f"at {unit} " + ", ".join(parts)
    return f"at {singular} {value}"


def humanize(parsed: ParsedCron) -> str:
    """Convert a ParsedCron into a human-readable schedule description."""
    minute = parsed.minute
    hour = parsed.hour
    dom = parsed.day_of_month
    month = parsed.month
    dow = parsed.day_of_week

    parts = []

    # Time description
    if minute == "*" and hour == "*":
        parts.append("every minute")
    elif minute.startswith("*/") and hour == "*":
        step = minute[2:]
        parts.append(f"every {step} minute(s)")
    elif minute == "0" and hour != "*":
        hour_desc = _describe_field(hour, "hours", "hour")
        parts.append(f"at the top of {hour_desc}")
    else:
        min_desc = _describe_field(minute, "minutes", "minute")
        hour_desc = _describe_field(hour, "hours", "hour")
        parts.append(f"{min_desc} past {hour_desc}")

    # Day of month
    if dom != "*":
        parts.append(f"on day {dom} of the month")

    # Month
    if month != "*":
        parts.append(f"in {_describe_month(month)}")

    # Day of week
    if dow != "*":
        parts.append(f"on {_describe_weekday(dow)}")

    return ", ".join(parts)
