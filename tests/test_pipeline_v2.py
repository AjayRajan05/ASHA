"""Tests for PromptProcessor orchestration (security + compile + optimize)."""

import pytest
from asha import process
from asha.compat.legacy_results import to_legacy_pipeline_dict
from asha.runtime.processor import PromptProcessor
from asha.types.results import ProcessResult


def test_processor_full_flow():
    """Security + compile + optimize via PromptProcessor."""
    processor = PromptProcessor()
    input_text = (
        "Summarize this: John Doe (john@example.com) is a great developer "
        "with 10 years of experience."
    )

    result = processor.run(input_text, token_budget=1000, mode="balanced")

    assert isinstance(result, ProcessResult)
    assert result.output
    assert "john@example.com" not in result.output
    assert result.original == input_text

    # Verify via legacy dict too
    legacy = to_legacy_pipeline_dict(
        process(input_text, mode="balanced", include_legacy_detail=True)
    )
    assert "john@example.com" not in legacy["prompts"]["sanitized"]


def test_processor_token_optimization():
    """Token budget enforcement via optimize_tokens engine."""
    processor = PromptProcessor()
    long_text = (
        "This is a very long text that should be significantly optimized to fit "
        "into a very small token budget of just ten tokens."
    )

    result = processor.run(long_text, token_budget=10)
    assert isinstance(result, ProcessResult)
    assert result.metrics is not None
    assert result.output
    # Output should be shorter than or equal to input
    assert len(result.output) <= len(long_text) + 50  # some tolerance for mask tokens


def test_processor_routing_metadata():
    """Legacy routing_decision placeholder is attached for compat consumers."""
    result = process("Simple greeting", include_legacy_detail=True)
    legacy = to_legacy_pipeline_dict(result)
    assert "routing_decision" in legacy
    assert legacy["routing_decision"]["selected_model"] == "default"


def test_processor_trace_has_stages():
    """Trace output must contain stage entries when trace=True."""
    processor = PromptProcessor()
    result = processor.run("Hello world", trace=True)
    assert result.trace is not None
    assert "stages" in result.trace
    assert len(result.trace["stages"]) > 0
    # Each stage should have input/output
    for stage in result.trace["stages"]:
        assert "name" in stage or "stage" in stage


def test_processor_mode_off_passthrough():
    """PromptProcessor with mode=off returns input unchanged."""
    processor = PromptProcessor()
    prompt = "Contact admin@corp.com for help"
    result = processor.run(prompt, mode="off")
    assert result.output == prompt


def test_processor_preserves_original():
    """PromptProcessor always stores the original prompt."""
    processor = PromptProcessor()
    prompt = "Email user@test.com about data"
    result = processor.run(prompt, mode="balanced")
    assert result.original == prompt
