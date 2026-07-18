"""Comprehensive smoke tests for ASHA package readiness."""

from asha import Agent, process
from asha.core.hybrid_pii import HybridPIIDetector
from asha.core.security.security_layer import ThreatType
from asha.types import AgentResult, ProcessResult


def test_public_api_imports():
    """Core public API imports resolve and are callable."""
    assert callable(Agent)
    assert callable(process)
    assert ThreatType is not None
    assert HybridPIIDetector is not None


def test_dropin_process_masks_email():
    """Drop-in process() masks PII and returns ProcessResult."""
    result = process("Contact john@example.com for help")
    assert isinstance(result, ProcessResult)
    assert "john@example.com" not in result.output
    assert result.original == "Contact john@example.com for help"
    # Must have security info with PII detected
    assert result.security is not None
    assert len(result.security.pii_detected) > 0


def test_dropin_process_returns_metrics():
    """process() always returns metrics."""
    result = process("Summarize quarterly sales data")
    assert isinstance(result, ProcessResult)
    assert result.metrics is not None
    assert result.metrics.processing_time_ms >= 0


def test_dropin_process_str_matches_output():
    """str(result) must equal result.output."""
    result = process("Hello world")
    assert str(result) == result.output


def test_agent_pipeline_with_mock():
    """Agent runs the full pipeline with mock adapter and returns AgentResult."""
    agent = Agent(model="mock", privacy=True, token_budget=1200)
    test_prompt = (
        "Hey bro can you analyze this dataset for anomalies? "
        "Contact me at john@example.com"
    )
    result = agent.run(test_prompt, trace=True)
    assert isinstance(result, AgentResult)
    assert result.response is not None
    assert result.original == test_prompt
    # Trace should be populated when trace=True
    assert result.trace is not None


def test_agent_privacy_masks_pii():
    """Agent with privacy=True must not leak PII in trace output."""
    agent = Agent(model="mock", privacy=True)
    result = agent.run("Email john@corp.com about report", trace=True)
    assert isinstance(result, AgentResult)
    assert "john@corp.com" not in result.output
