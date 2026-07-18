"""Tests for v0.4 typed results and API semantics.

Validates the exact shape and contracts of ProcessResult, SanitizeResult,
OptimizeResult, and AgentResult.
"""

import asyncio

import pytest

from asha import process, sanitize, optimize
from asha.integrations import wrap_llm
from asha.types import (
    AgentResult,
    OptimizeResult,
    ProcessResult,
    SanitizeResult,
)
from asha.exceptions import ASHAWrapError
from asha.utils.dropin import optimize_async, process_async, sanitize_async


# ---------------------------------------------------------------------------
# ProcessResult shape and semantics
# ---------------------------------------------------------------------------


def test_process_returns_process_result_with_correct_fields():
    result = process("Contact john@example.com for help")
    assert isinstance(result, ProcessResult)
    assert "john@example.com" not in result.output
    assert result.original == "Contact john@example.com for help"
    assert str(result) == result.output
    assert result.degraded is False
    assert result.degraded_reason is None
    assert result.security is not None
    assert result.metrics is not None


def test_process_result_to_dict_keys():
    result = process("Hello world")
    d = result.to_dict()
    assert "optimized" in d
    assert "original" in d
    assert "degraded" in d
    assert "privacy_applied" in d
    assert "token_reduction" in d


# ---------------------------------------------------------------------------
# SanitizeResult shape and semantics
# ---------------------------------------------------------------------------


def test_sanitize_returns_sanitize_result_with_correct_fields():
    result = sanitize("Contact john@example.com for analysis")
    assert isinstance(result, SanitizeResult)
    assert "john@example.com" not in result.output
    assert result.original == "Contact john@example.com for analysis"
    assert str(result) == result.output
    assert result.degraded is False
    assert result.security is not None
    assert len(result.security.pii_detected) > 0


def test_sanitize_result_to_dict_keys():
    result = sanitize("Email user@test.com")
    d = result.to_dict()
    assert "sanitized" in d
    assert "original" in d
    assert "is_safe" in d
    assert "pii_detected" in d
    assert "threats" in d
    assert "masked_entities" in d


# ---------------------------------------------------------------------------
# OptimizeResult shape and semantics
# ---------------------------------------------------------------------------


def test_optimize_returns_optimize_result():
    prompt = "Hey bro can you please analyze this dataset for anomalies?"
    result = optimize(prompt)
    assert isinstance(result, OptimizeResult)
    assert result.original == prompt
    assert result.degraded is False


def test_optimize_does_not_strip_pii():
    """optimize() is tokens-only — email must survive."""
    prompt = "Contact john@example.com for help"
    result = optimize(prompt)
    assert isinstance(result, OptimizeResult)
    assert "john@example.com" in result.output


def test_optimize_result_to_dict_keys():
    result = optimize("Summarize data")
    d = result.to_dict()
    assert "optimized" in d
    assert "original" in d
    assert "degraded" in d
    assert "token_reduction" in d
    assert "metrics" in d


# ---------------------------------------------------------------------------
# mode="off" semantics
# ---------------------------------------------------------------------------


def test_process_mode_off_preserves_pii_exactly():
    prompt = "Contact john@example.com for help"
    result = process(prompt, mode="off")
    assert result.output == prompt


# ---------------------------------------------------------------------------
# Observable failure / degradation
# ---------------------------------------------------------------------------


def test_sanitize_observable_failure(monkeypatch):
    def boom(*_a, **_k):
        raise RuntimeError("detector down")

    monkeypatch.setattr(
        "asha.core.engines.run_security_only",
        boom,
    )
    result = sanitize("test@example.com")
    assert isinstance(result, SanitizeResult)
    assert result.degraded is True
    assert result.safe is False


def test_process_balanced_failure_masks_pii_in_fallback(monkeypatch):
    def boom(*_a, **_k):
        raise RuntimeError("security down")

    monkeypatch.setattr(
        "asha.runtime.processor.run_security",
        boom,
    )
    result = process("Email john@example.com now", mode="balanced")
    assert isinstance(result, ProcessResult)
    assert "john@example.com" not in result.output
    assert result.degraded is True


# ---------------------------------------------------------------------------
# Async variants
# ---------------------------------------------------------------------------


def test_process_async_returns_process_result():
    result = asyncio.run(process_async("hello world", mode="balanced"))
    assert isinstance(result, ProcessResult)
    assert result.output is not None


def test_sanitize_async_returns_sanitize_result():
    result = asyncio.run(sanitize_async("hello@example.com"))
    assert isinstance(result, SanitizeResult)
    assert "hello@example.com" not in result.output


def test_optimize_async_returns_optimize_result():
    result = asyncio.run(optimize_async("hello world please summarize"))
    assert isinstance(result, OptimizeResult)
    assert result.output is not None


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


def test_agent_trace_returns_agent_result():
    from asha import Agent

    agent = Agent(model="mock", privacy=True)
    out = agent.run("hello", trace=True)
    assert isinstance(out, AgentResult)
    assert out.trace is not None
    assert out.response is not None


# ---------------------------------------------------------------------------
# wrap_llm error handling
# ---------------------------------------------------------------------------


def test_wrap_llm_invalid_raises():
    class BadClient:
        pass

    with pytest.raises(ValueError):
        wrap_llm(BadClient())
