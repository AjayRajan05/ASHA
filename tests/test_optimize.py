"""Tests for optimize() API - tokens-only in v0.4."""

from asha import optimize
from asha.types.results import OptimizeResult


def test_optimize_returns_optimize_result():
    result = optimize("Summarize quarterly sales trends.")
    assert isinstance(result, OptimizeResult)
    assert len(result.output) > 0


def test_optimize_trust_input_bypasses_compression():
    prompt = "Contact john@company.com unchanged"
    result = optimize(prompt, trust_input=True)
    assert isinstance(result, OptimizeResult)
    assert result.output == prompt


def test_optimize_tokens_only_may_keep_pii():
    """optimize() does not run security - email may remain."""
    result = optimize("Contact secret@company.com for help")
    assert isinstance(result, OptimizeResult)
    # tokens-only path; PII masking is not guaranteed
    assert result.output


def test_optimize_token_budget():
    long_prompt = "word " * 500
    result = optimize(long_prompt, token_budget=50)
    assert isinstance(result, OptimizeResult)
    assert result.metrics is not None
    assert result.output


def test_optimize_empty_prompt():
    result = optimize("")
    assert isinstance(result, OptimizeResult)
    assert result.output == ""
