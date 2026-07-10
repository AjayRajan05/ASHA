"""Comprehensive smoke tests for ASHA package readiness."""

from pathlib import Path

import pytest

from asha import Agent, process
from asha.core.hybrid_pii import HybridPIIDetector
from asha.core.security.security_layer import ThreatType
from asha.types import AgentResult, ProcessResult


REQUIRED_FILES = [
    "src/asha/__init__.py",
    "src/asha/runtime/agent.py",
    "src/asha/runtime/processor.py",
    "src/asha/runtime/resolve.py",
    "src/asha/core/engines.py",
    "src/asha/compat/legacy_results.py",
    "src/asha/runtime/adapters/factory.py",
    "src/asha/runtime/adapters/mock_adapter.py",
    "src/asha/utils/dropin.py",
    "README.md",
    "LICENSE",
    "pyproject.toml",
]


def test_package_structure():
    """Verify the modular package layout exists."""
    missing = [f for f in REQUIRED_FILES if not Path(f).exists()]
    assert not missing, f"Missing files: {missing}"


def test_public_api_imports():
    """Core public API imports resolve."""
    assert Agent is not None
    assert process is not None
    assert ThreatType is not None
    assert HybridPIIDetector is not None


def test_dropin_process():
    """Drop-in process() masks PII and returns ProcessResult."""
    result = process("Contact john@example.com for help")
    assert isinstance(result, ProcessResult)
    assert "john@example.com" not in result.output


def test_agent_pipeline_trace():
    """Agent runs the full pipeline with mock adapter."""
    agent = Agent(model="mock", privacy=True, token_budget=1200)
    test_prompt = (
        "Hey bro can you analyze this dataset for anomalies? "
        "Contact me at john@example.com"
    )
    result = agent.run(test_prompt, trace=True)
    assert isinstance(result, AgentResult)
    assert result.response is not None
