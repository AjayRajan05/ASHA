"""Additional process() coverage for untested drop-in code paths."""

from __future__ import annotations

from privysha.core.policy_config import PolicyConfig
from privysha.types.results import ProcessResult
from privysha.utils.dropin import process

from conftest import output_of


def test_process_with_trace_and_debug():
    result = process(
        "Contact support@example.com for help.",
        trace=True,
        debug=True,
    )
    assert isinstance(result, ProcessResult)
    assert "support@example.com" not in result.output
    assert result.metrics is not None


def test_process_debug_mode():
    result = process(
        "Analyze dataset with user@company.com",
        debug=True,
    )
    assert isinstance(result, ProcessResult)
    assert result.output


def test_process_preserve_intent_clean_prompt():
    prompt = "What is the capital of France?"
    result = process(prompt, policy=PolicyConfig(preserve_intent=True))
    assert isinstance(result, ProcessResult)
    assert len(result.output) > 0


def test_process_reversible_masking():
    result = process(
        "Email me at alice@example.com",
        policy=PolicyConfig(reversible=True),
    )
    assert isinstance(result, ProcessResult)
    assert "alice@example.com" not in result.output


def test_process_verbose_json_logging():
    result = process(
        "Hello world",
        verbose=True,
        log_output="json",
    )
    assert isinstance(result, ProcessResult)
    assert result.metrics is not None
