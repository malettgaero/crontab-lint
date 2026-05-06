"""Tests for crontab_lint.cli."""

import json
import pytest
from crontab_lint.cli import main, build_parser


def test_valid_expression_exits_zero():
    rc = main(["0 12 * * *"])
    assert rc == 0


def test_invalid_expression_exits_nonzero():
    rc = main(["bad expr"])
    assert rc == 1


def test_multiple_valid_exits_zero():
    rc = main(["0 12 * * *", "*/5 * * * *"])
    assert rc == 0


def test_any_invalid_exits_nonzero():
    rc = main(["0 12 * * *", "bad"])
    assert rc == 1


def test_json_output_single(capsys):
    rc = main(["--json", "0 12 * * *"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["valid"] is True
    assert data["expression"] == "0 12 * * *"
    assert rc == 0


def test_json_output_multiple(capsys):
    rc = main(["--json", "0 12 * * *", "*/5 * * * *"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert len(data) == 2


def test_json_invalid_expression(capsys):
    rc = main(["--json", "not valid"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["valid"] is False
    assert len(data["errors"]) > 0
    assert rc == 1


def test_no_color_flag(capsys):
    rc = main(["--no-color", "0 12 * * *"])
    captured = capsys.readouterr()
    assert "\033[" not in captured.out
    assert rc == 0


def test_build_parser_prog_name():
    p = build_parser()
    assert p.prog == "crontab-lint"
