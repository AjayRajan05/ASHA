"""Comprehensive smoke tests for PrivySHA package readiness."""

from pathlib import Path

import pytest

from privysha import Agent, process
from privysha.core.hybrid_pii import HybridPIIDetector
from privysha.core.security.security_layer import ThreatType
from privysha.types import AgentResult, ProcessResult


REQUIRED_FILES = [
    "src/privysha/__init__.py",
    "src/privysha/runtime/agent.py",
    "src/privysha/runtime/processor.py",
    "src/privysha/runtime/resolve.py",
    "src/privysha/core/engines.py",
    "src/privysha/compat/legacy_results.py",
    "src/privysha/runtime/adapters/factory.py",
    "src/privysha/runtime/adapters/mock_adapter.py",
    "src/privysha/utils/dropin.py",
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
