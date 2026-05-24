"""Hybrid PII mode tests."""

import os

import pytest

from privysha import process


def test_hybrid_pii_mode_runs_or_falls_back():
    """Hybrid mode uses 7-stage pipeline or falls back when ML disabled."""
    result = process(
        "Contact john@company.com",
        pii_mode="hybrid",
        return_metrics=True,
    )
    assert isinstance(result, dict)
    assert "optimized" in result
    if os.environ.get("PRIVYSHA_DISABLE_ML") == "1":
        assert "john@company.com" not in result["optimized"]
    else:
        assert isinstance(result["optimized"], str)
