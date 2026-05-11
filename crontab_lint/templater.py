"""Crontab expression template library with named common schedules."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CronTemplate:
    name: str
    expression: str
    description: str
    tags: List[str] = field(default_factory=list)


_TEMPLATES: Dict[str, CronTemplate] = {
    "every_minute": CronTemplate(
        name="every_minute",
        expression="* * * * *",
        description="Runs every minute",
        tags=["frequent", "debug"],
    ),
    "every_5_minutes": CronTemplate(
        name="every_5_minutes",
        expression="*/5 * * * *",
        description="Runs every 5 minutes",
        tags=["frequent"],
    ),
    "hourly": CronTemplate(
        name="hourly",
        expression="0 * * * *",
        description="Runs at the top of every hour",
        tags=["common"],
    ),
    "daily_midnight": CronTemplate(
        name="daily_midnight",
        expression="0 0 * * *",
        description="Runs once a day at midnight",
        tags=["common", "daily"],
    ),
    "daily_noon": CronTemplate(
        name="daily_noon",
        expression="0 12 * * *",
        description="Runs once a day at noon",
        tags=["common", "daily"],
    ),
    "weekly_sunday": CronTemplate(
        name="weekly_sunday",
        expression="0 0 * * 0",
        description="Runs every Sunday at midnight",
        tags=["common", "weekly"],
    ),
    "monthly_first": CronTemplate(
        name="monthly_first",
        expression="0 0 1 * *",
        description="Runs on the first day of every month at midnight",
        tags=["common", "monthly"],
    ),
    "yearly": CronTemplate(
        name="yearly",
        expression="0 0 1 1 *",
        description="Runs once a year on January 1st at midnight",
        tags=["rare", "yearly"],
    ),
    "weekdays_morning": CronTemplate(
        name="weekdays_morning",
        expression="0 9 * * 1-5",
        description="Runs at 9 AM on weekdays",
        tags=["business", "daily"],
    ),
    "weekends_midnight": CronTemplate(
        name="weekends_midnight",
        expression="0 0 * * 6,0",
        description="Runs at midnight on weekends",
        tags=["weekly"],
    ),
}


def list_templates(tag: Optional[str] = None) -> List[CronTemplate]:
    """Return all templates, optionally filtered by tag."""
    templates = list(_TEMPLATES.values())
    if tag:
        templates = [t for t in templates if tag in t.tags]
    return templates


def get_template(name: str) -> Optional[CronTemplate]:
    """Retrieve a template by name, or None if not found."""
    return _TEMPLATES.get(name)


def search_templates(query: str) -> List[CronTemplate]:
    """Search templates by name or description (case-insensitive)."""
    query_lower = query.lower()
    return [
        t for t in _TEMPLATES.values()
        if query_lower in t.name.lower() or query_lower in t.description.lower()
    ]
