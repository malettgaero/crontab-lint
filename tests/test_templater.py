"""Tests for crontab_lint.templater module."""

import pytest
from crontab_lint.templater import (
    CronTemplate,
    list_templates,
    get_template,
    search_templates,
)


def test_list_templates_returns_all():
    templates = list_templates()
    assert len(templates) >= 8
    assert all(isinstance(t, CronTemplate) for t in templates)


def test_list_templates_filter_by_tag_common():
    templates = list_templates(tag="common")
    assert len(templates) > 0
    assert all("common" in t.tags for t in templates)


def test_list_templates_filter_by_tag_daily():
    templates = list_templates(tag="daily")
    assert len(templates) > 0
    assert all("daily" in t.tags for t in templates)


def test_list_templates_unknown_tag_returns_empty():
    templates = list_templates(tag="nonexistent_tag_xyz")
    assert templates == []


def test_get_template_existing():
    template = get_template("hourly")
    assert template is not None
    assert template.name == "hourly"
    assert template.expression == "0 * * * *"


def test_get_template_daily_midnight():
    template = get_template("daily_midnight")
    assert template is not None
    assert template.expression == "0 0 * * *"
    assert "daily" in template.tags


def test_get_template_nonexistent_returns_none():
    template = get_template("does_not_exist")
    assert template is None


def test_get_template_every_minute():
    template = get_template("every_minute")
    assert template is not None
    assert template.expression == "* * * * *"


def test_search_templates_by_name():
    results = search_templates("weekly")
    assert len(results) > 0
    assert all("weekly" in r.name.lower() or "weekly" in r.description.lower() for r in results)


def test_search_templates_by_description():
    results = search_templates("midnight")
    assert len(results) > 0
    assert all("midnight" in r.description.lower() for r in results)


def test_search_templates_case_insensitive():
    results_lower = search_templates("hourly")
    results_upper = search_templates("HOURLY")
    assert len(results_lower) == len(results_upper)


def test_search_templates_no_match():
    results = search_templates("zzznomatch999")
    assert results == []


def test_template_has_required_fields():
    template = get_template("yearly")
    assert template.name
    assert template.expression
    assert template.description
    assert isinstance(template.tags, list)


def test_weekdays_morning_expression():
    template = get_template("weekdays_morning")
    assert template is not None
    assert template.expression == "0 9 * * 1-5"
    assert "business" in template.tags
