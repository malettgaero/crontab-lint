"""Tests for crontab_lint.exporter module."""

import csv
import io

import pytest

from crontab_lint.exporter import export_csv, export_markdown
from crontab_lint.summarizer import summarize_expression


@pytest.fixture()
def valid_summary():
    return summarize_expression("0 9 * * 1")


@pytest.fixture()
def invalid_summary():
    return summarize_expression("99 9 * * 1")


def test_export_csv_headers(valid_summary):
    result = export_csv([valid_summary])
    reader = csv.DictReader(io.StringIO(result))
    assert reader.fieldnames == ["expression", "valid", "human_readable", "errors"]


def test_export_csv_valid_row(valid_summary):
    result = export_csv([valid_summary])
    rows = list(csv.DictReader(io.StringIO(result)))
    assert len(rows) == 1
    assert rows[0]["expression"] == "0 9 * * 1"
    assert rows[0]["valid"] == "True"
    assert rows[0]["errors"] == ""


def test_export_csv_invalid_row(invalid_summary):
    result = export_csv([invalid_summary])
    rows = list(csv.DictReader(io.StringIO(result)))
    assert rows[0]["valid"] == "False"
    assert rows[0]["errors"] != ""


def test_export_csv_multiple_rows(valid_summary, invalid_summary):
    result = export_csv([valid_summary, invalid_summary])
    rows = list(csv.DictReader(io.StringIO(result)))
    assert len(rows) == 2


def test_export_csv_empty():
    result = export_csv([])
    rows = list(csv.DictReader(io.StringIO(result)))
    assert rows == []


def test_export_markdown_contains_header(valid_summary):
    result = export_markdown([valid_summary])
    assert "| Expression | Valid | Human Readable | Errors |" in result


def test_export_markdown_valid_row(valid_summary):
    result = export_markdown([valid_summary])
    assert "`0 9 * * 1`" in result
    assert "✅" in result


def test_export_markdown_invalid_row(invalid_summary):
    result = export_markdown([invalid_summary])
    assert "❌" in result


def test_export_markdown_separator_row(valid_summary):
    result = export_markdown([valid_summary])
    assert "| --- | --- | --- | --- |" in result


def test_export_markdown_ends_with_newline(valid_summary):
    result = export_markdown([valid_summary])
    assert result.endswith("\n")


def test_export_markdown_empty():
    result = export_markdown([])
    lines = result.strip().splitlines()
    # Only header + separator, no data rows
    assert len(lines) == 2
