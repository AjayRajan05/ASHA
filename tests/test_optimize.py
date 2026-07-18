"""Tests for optimize() API - tokens-only in v0.4.

optimize() must NEVER run security stages. It only does MSDPC token compression.
PII in input will remain in output — that's by design.
"""

from asha import optimize
from asha.types.results import OptimizeResult


def test_optimize_returns_optimize_result():
    result = optimize("Summarize quarterly sales trends.")
    assert isinstance(result, OptimizeResult)
    assert len(result.output) > 0


def test_optimize_preserves_original_field():
    prompt = "Summarize quarterly sales trends."
    result = optimize(prompt)
    assert result.original == prompt


def test_optimize_trust_input_bypasses_compression():
    prompt = "Contact john@company.com unchanged"
    result = optimize(prompt, trust_input=True)
    assert isinstance(result, OptimizeResult)
    assert result.output == prompt
    assert result.degraded is False
    assert result.metrics is not None
    assert result.metrics.tokens_saved == 0
    assert result.metrics.token_reduction_pct == 0.0


def test_optimize_does_not_mask_pii():
    """optimize() is tokens-only — PII must survive untouched."""
    email = "secret@company.com"
    result = optimize(f"Contact {email} for help")
    assert isinstance(result, OptimizeResult)
    assert email in result.output


def test_optimize_token_budget_reduces_long_prompt():
    long_prompt = "word " * 500
    result = optimize(long_prompt, token_budget=50)
    assert isinstance(result, OptimizeResult)
    assert result.metrics is not None
    assert result.metrics.tokens_saved >= 0
    assert result.metrics.token_reduction_pct >= 0.0
    assert len(result.output) > 0
    # Output should be shorter than input for a very long prompt with tight budget
    assert len(result.output) <= len(long_prompt)


def test_optimize_empty_prompt():
    result = optimize("")
    assert isinstance(result, OptimizeResult)
    assert result.output == ""


def test_optimize_metrics_have_valid_ranges():
    result = optimize("Please analyze this dataset and produce a comprehensive report.")
    assert isinstance(result, OptimizeResult)
    assert result.metrics is not None
    assert result.metrics.tokens_saved >= 0
    assert 0.0 <= result.metrics.token_reduction_pct <= 100.0
    assert result.metrics.processing_time_ms >= 0.0


def test_optimize_short_prompt_not_degraded():
    result = optimize("Hello")
    assert isinstance(result, OptimizeResult)
    assert result.degraded is False
    assert result.degraded_reason is None


def test_optimize_preserves_ssn_since_no_security():
    """SSN must survive since optimize() has no security stage."""
    ssn = "123-45-6789"
    result = optimize(f"My SSN is {ssn}")
    assert ssn in result.output
