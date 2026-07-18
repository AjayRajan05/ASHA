"""Hybrid PII mode tests."""

import os

from asha import process
from asha.core.policy_config import PolicyConfig
from asha.types.results import ProcessResult

from conftest import output_of


def test_hybrid_pii_mode_masks_email():
    """Hybrid mode must mask PII regardless of ML availability.

    When ASHA_DISABLE_ML=1, it falls back to rule-based detection.
    Either way, PII must be masked.
    """
    result = process(
        "Contact john@company.com",
        policy=PolicyConfig(pii_mode="hybrid"),
    )
    assert isinstance(result, ProcessResult)
    out = output_of(result)
    # PII must be masked regardless of ML availability
    assert "john@company.com" not in out
    assert result.degraded is False


def test_hybrid_pii_mode_masks_ssn():
    """Hybrid mode must mask SSN."""
    result = process(
        "My SSN is 123-45-6789",
        policy=PolicyConfig(pii_mode="hybrid"),
    )
    assert isinstance(result, ProcessResult)
    assert "123-45-6789" not in output_of(result)


def test_hybrid_pii_mode_returns_security_info():
    """Hybrid mode must return security info with detected PII types."""
    result = process(
        "Email alice@corp.com and SSN 987-65-4321",
        policy=PolicyConfig(pii_mode="hybrid"),
    )
    assert isinstance(result, ProcessResult)
    assert result.security is not None
    assert len(result.security.pii_detected) > 0
