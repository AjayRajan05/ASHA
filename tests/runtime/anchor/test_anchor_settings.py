"""Tests for ANCHOR runtime settings resolution."""

from __future__ import annotations

from unittest.mock import patch

from asha.runtime.anchor.settings import resolve_interactive, resolve_warn_policy


def test_resolve_interactive_explicit_override() -> None:
    assert resolve_interactive(True) is True
    assert resolve_interactive(False) is False


def test_resolve_interactive_from_env(monkeypatch) -> None:
    monkeypatch.setenv("ASHA_ANCHOR_INTERACTIVE", "1")
    with patch("sys.stdin.isatty", return_value=False):
        assert resolve_interactive() is True


def test_resolve_interactive_from_tty(monkeypatch) -> None:
    monkeypatch.delenv("ASHA_ANCHOR_INTERACTIVE", raising=False)
    with patch("sys.stdin.isatty", return_value=True):
        assert resolve_interactive() is True
    with patch("sys.stdin.isatty", return_value=False):
        assert resolve_interactive() is False


def test_resolve_warn_policy_strict_when_interactive(monkeypatch) -> None:
    monkeypatch.delenv("ASHA_ANCHOR_WARN_POLICY", raising=False)
    assert resolve_warn_policy(interactive=True) == "strict"
    assert resolve_warn_policy(interactive=False) == "permissive"
