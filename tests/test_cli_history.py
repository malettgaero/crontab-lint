"""Tests for crontab_lint.cli_history."""

import json

import pytest

from crontab_lint.cli_history import main
from crontab_lint.history import HistoryEntry, History, save_history


@pytest.fixture()
def history_file(tmp_path):
    path = str(tmp_path / "hist.json")
    h = History()
    h.entries = [
        HistoryEntry(expression="* * * * *", valid=True, human_readable="Every minute", errors=[]),
        HistoryEntry(expression="0 * * * *", valid=True, human_readable="Every hour", errors=[]),
        HistoryEntry(expression="bad expr", valid=False, human_readable=None, errors=["Too few fields"]),
    ]
    save_history(h, path)
    return path


def test_no_command_exits_zero(history_file):
    assert main(["--path", history_file]) == 0


def test_show_command_exits_zero(history_file, capsys):
    rc = main(["--path", history_file, "show"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "* * * * *" in out


def test_show_valid_only(history_file, capsys):
    main(["--path", history_file, "show", "--valid"])
    out = capsys.readouterr().out
    assert "bad expr" not in out
    assert "Every minute" in out


def test_show_invalid_only(history_file, capsys):
    main(["--path", history_file, "show", "--invalid"])
    out = capsys.readouterr().out
    assert "bad expr" in out
    assert "Every minute" not in out


def test_show_json_output(history_file, capsys):
    main(["--path", history_file, "show", "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[-1]["expression"] == "bad expr"


def test_show_last_n(history_file, capsys):
    main(["--path", history_file, "show", "-n", "1"])
    out = capsys.readouterr().out
    assert "bad expr" in out
    assert "Every minute" not in out


def test_clear_command(history_file, capsys):
    rc = main(["--path", history_file, "clear"])
    assert rc == 0
    assert "cleared" in capsys.readouterr().out.lower()
    from crontab_lint.history import load_history
    h = load_history(history_file)
    assert h.entries == []


def test_stats_command(history_file, capsys):
    main(["--path", history_file, "stats"])
    out = capsys.readouterr().out
    assert "Total" in out
    assert "Valid" in out
    assert "Pass rate" in out


def test_stats_pass_rate_value(history_file, capsys):
    main(["--path", history_file, "stats"])
    out = capsys.readouterr().out
    # 2 valid out of 3 total = 66.7%
    assert "66.7%" in out
