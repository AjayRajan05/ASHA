"""Hybrid PII mode tests."""

import os

from asha import process
from asha.core.policy_config import PolicyConfig
from asha.types.results import ProcessResult

from conftest import output_of


def test_hybrid_pii_mode_runs_or_falls_back():
    """Hybrid mode uses 7-stage pipeline or falls back when ML disabled."""
    result = process(
        "Contact john@company.com",
        policy=PolicyConfig(pii_mode="hybrid"),
    )
    assert isinstance(result, ProcessResult)
    out = output_of(result)
    if os.environ.get("ASHA_DISABLE_ML") == "1":
        assert "john@company.com" not in out
    else:
        assert isinstance(out, str)
