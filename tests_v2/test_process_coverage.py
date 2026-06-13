"""Additional process() coverage for untested drop-in code paths."""

from __future__ import annotations

from privysha.utils.dropin import process


def test_process_with_stages_and_context():
    result = process(
        "Summarize quarterly revenue trends.",
        use_stages=True,
        context_config={"role": "data analyst"},
        return_metrics=True,
    )
    assert isinstance(result, dict)
    assert "optimized" in result
    assert isinstance(result["optimized"], str)


def test_process_with_trace_and_metrics():
    result = process(
        "Contact support@example.com for help.",
        trace=True,
        return_metrics=True,
        debug=True,
    )
    assert isinstance(result, dict)
    assert "optimized" in result
    assert "metrics" in result
    assert "support@example.com" not in result["optimized"]


def test_process_debug_mode():
    result = process(
        "Analyze dataset with user@company.com",
        debug_mode=True,
        return_metrics=True,
    )
    assert isinstance(result, dict)
    assert "optimized" in result


def test_process_preserve_intent_clean_prompt():
    prompt = "What is the capital of France?"
    result = process(prompt, preserve_intent=True)
    assert isinstance(result, str)
    assert len(result) > 0


def test_process_reversible_masking():
    result = process(
        "Email me at alice@example.com",
        reversible=True,
        return_metrics=True,
    )
    assert isinstance(result, dict)
    assert "alice@example.com" not in result["optimized"]


def test_process_verbose_json_logging():
    result = process(
        "Hello world",
        verbose=True,
        log_output="json",
        return_metrics=True,
    )
    assert isinstance(result, dict)
    assert "metrics" in result
