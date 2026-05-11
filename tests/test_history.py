"""Tests for crontab_lint.history."""

import json
import os
import tempfile

import pytest

from crontab_lint.history import (
    History,
    HistoryEntry,
    load_history,
    record,
    save_history,
)


@pytest.fixture()
def tmp_path_file(tmp_path):
    return str(tmp_path / "history.json")


def test_empty_history_has_no_entries():
    h = History()
    assert h.entries == []


def test_add_entry():
    h = History()
    entry = HistoryEntry(expression="* * * * *", valid=True, human_readable="Every minute", errors=[])
    h.add(entry)
    assert len(h.entries) == 1
    assert h.entries[0].expression == "* * * * *"


def test_last_returns_correct_slice():
    h = History()
    for i in range(15):
        h.add(HistoryEntry(expression=str(i), valid=True, human_readable=None, errors=[]))
    assert len(h.last(5)) == 5
    assert h.last(5)[-1].expression == "14"


def test_filter_valid():
    h = History()
    h.add(HistoryEntry(expression="* * * * *", valid=True, human_readable=None, errors=[]))
    h.add(HistoryEntry(expression="bad", valid=False, human_readable=None, errors=["err"]))
    assert len(h.filter_valid()) == 1
    assert h.filter_valid()[0].valid is True


def test_filter_invalid():
    h = History()
    h.add(HistoryEntry(expression="* * * * *", valid=True, human_readable=None, errors=[]))
    h.add(HistoryEntry(expression="bad", valid=False, human_readable=None, errors=["err"]))
    assert len(h.filter_invalid()) == 1
    assert h.filter_invalid()[0].valid is False


def test_clear_removes_all_entries():
    h = History()
    h.add(HistoryEntry(expression="* * * * *", valid=True, human_readable=None, errors=[]))
    h.clear()
    assert h.entries == []


def test_save_and_load_roundtrip(tmp_path_file):
    h = History()
    h.add(HistoryEntry(expression="0 * * * *", valid=True, human_readable="Every hour", errors=[]))
    save_history(h, tmp_path_file)
    loaded = load_history(tmp_path_file)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].expression == "0 * * * *"
    assert loaded.entries[0].human_readable == "Every hour"


def test_load_missing_file_returns_empty(tmp_path_file):
    h = load_history(tmp_path_file + ".nonexistent")
    assert h.entries == []


def test_record_appends_entry(tmp_path_file):
    entry = record("* * * * *", valid=True, human_readable="Every minute", path=tmp_path_file)
    assert entry.expression == "* * * * *"
    assert entry.valid is True
    loaded = load_history(tmp_path_file)
    assert len(loaded.entries) == 1


def test_record_multiple_entries(tmp_path_file):
    record("* * * * *", valid=True, path=tmp_path_file)
    record("bad", valid=False, errors=["Too few fields"], path=tmp_path_file)
    loaded = load_history(tmp_path_file)
    assert len(loaded.entries) == 2
    assert loaded.entries[1].valid is False


def test_entry_has_timestamp(tmp_path_file):
    entry = record("* * * * *", valid=True, path=tmp_path_file)
    assert entry.checked_at  # non-empty ISO timestamp
    assert "T" in entry.checked_at  # ISO 8601 format


def test_saved_json_structure(tmp_path_file):
    record("0 0 * * *", valid=True, human_readable="Daily at midnight", path=tmp_path_file)
    with open(tmp_path_file) as fh:
        data = json.load(fh)
    assert "entries" in data
    assert data["entries"][0]["expression"] == "0 0 * * *"
