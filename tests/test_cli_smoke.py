"""Smoke tests for CLI entry points (no network required)."""

from __future__ import annotations

from click.testing import CliRunner

from asha.cli.main import cli, examples, quick_test


def test_quick_test_command():
    runner = CliRunner()
    result = runner.invoke(quick_test)
    assert result.exit_code == 0
    assert "tests passed" in result.output.lower() or "PASS" in result.output


def test_quick_test_via_cli_group():
    runner = CliRunner()
    result = runner.invoke(cli, ["quick-test"])
    assert result.exit_code == 0


def test_examples_command_runs():
    runner = CliRunner()
    result = runner.invoke(examples, ["--count", "1"])
    assert result.exit_code == 0
    assert "1." in result.output
