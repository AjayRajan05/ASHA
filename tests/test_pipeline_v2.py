"""Tests for PromptProcessor orchestration (security + compile + optimize)."""

import pytest
from privysha import process
from privysha.compat.legacy_results import to_legacy_pipeline_dict
from privysha.runtime.processor import PromptProcessor
from privysha.types.results import ProcessResult


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


def test_processor_routing_metadata():
    """Legacy routing_decision placeholder is attached for compat consumers."""
    result = process("Simple greeting", include_legacy_detail=True)
    legacy = to_legacy_pipeline_dict(result)
    assert "routing_decision" in legacy
    assert legacy["routing_decision"]["selected_model"] == "default"


def test_processor_trace():
    """Trace output when trace=True."""
    processor = PromptProcessor()
    result = processor.run("Hello world", trace=True)
    assert result.trace is not None
    assert "stages" in result.trace
    assert len(result.trace["stages"]) > 0
