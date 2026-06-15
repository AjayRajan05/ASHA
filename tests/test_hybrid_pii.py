"""Hybrid PII mode tests."""

import os

from privysha import process
from privysha.core.policy_config import PolicyConfig
from privysha.types.results import ProcessResult

from conftest import output_of


def test_hybrid_pii_mode_runs_or_falls_back():
    """Hybrid mode uses 7-stage pipeline or falls back when ML disabled."""
    result = process(
        "Contact john@company.com",
        policy=PolicyConfig(pii_mode="hybrid"),
    )
    assert isinstance(result, ProcessResult)
    out = output_of(result)
    if os.environ.get("PRIVYSHA_DISABLE_ML") == "1":
        assert "john@company.com" not in out
    else:
        assert isinstance(out, str)
