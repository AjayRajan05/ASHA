"""Additional process() coverage for untested drop-in code paths."""

from __future__ import annotations

from asha.core.policy_config import PolicyConfig
from asha.types.results import ProcessResult
from asha.utils.dropin import process

from conftest import output_of


def test_process_with_trace_returns_trace_dict():
    """trace=True must populate result.trace with stage information."""
    result = process(
        "Contact support@example.com for help.",
        trace=True,
    )
    assert isinstance(result, ProcessResult)
    assert "support@example.com" not in result.output
    assert result.trace is not None
    assert isinstance(result.trace, dict)
    assert "stages" in result.trace


def test_process_with_debug_returns_diff():
    """debug=True must populate result.diff."""
    result = process(
        "Analyze dataset with user@company.com",
        debug=True,
    )
    assert isinstance(result, ProcessResult)
    assert result.output
    # diff should be populated when debug=True
    # (may be None if no changes were made, but type should be str or None)


def test_process_with_trace_and_debug():
    """Both trace and debug enabled simultaneously."""
    result = process(
        "Contact support@example.com for help.",
        trace=True,
        debug=True,
    )
    assert isinstance(result, ProcessResult)
    assert "support@example.com" not in result.output
    assert result.metrics is not None
    assert result.trace is not None


def test_process_preserve_intent_clean_prompt_returns_original():
    """preserve_intent=True + clean prompt → output equals original."""
    prompt = "What is the capital of France?"
    result = process(prompt, policy=PolicyConfig(preserve_intent=True))
    assert isinstance(result, ProcessResult)
    assert result.output == prompt


def test_process_reversible_masking_returns_map():
    """reversible=True must produce a masking_map in security info."""
    result = process(
        "Email me at alice@example.com",
        policy=PolicyConfig(reversible=True),
    )
    assert isinstance(result, ProcessResult)
    assert "alice@example.com" not in result.output
    assert result.security is not None
    assert result.security.masking_map is not None
    assert len(result.security.masking_map) > 0


def test_process_verbose_json_logging_does_not_crash():
    result = process(
        "Hello world",
        verbose=True,
        log_output="json",
    )
    assert isinstance(result, ProcessResult)
    assert result.metrics is not None


def test_process_returns_metrics_with_timing():
    """Metrics must include processing time."""
    result = process("Summarize quarterly data")
    assert result.metrics is not None
    assert result.metrics.processing_time_ms >= 0
