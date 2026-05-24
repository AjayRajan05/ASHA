"""Tests for optimize() API."""

from privysha import optimize


def test_optimize_strict_masks_pii():
    result = optimize(
        "Contact secret@company.com for help",
        privacy_mode="strict",
        return_metrics=True,
    )
    assert result["pii_masked"] is True
    assert "secret@company.com" not in result["optimized"]


def test_optimize_off_skips_masking():
    result = optimize(
        "Contact keep@company.com intact",
        privacy_mode="off",
        trust_input=True,
        return_metrics=True,
    )
    assert "keep@company.com" in result["optimized"]
    assert result["pii_masked"] is False


def test_optimize_balanced_returns_string():
    out = optimize("Summarize quarterly sales trends.", privacy_mode="balanced")
    assert isinstance(out, str)
    assert len(out) > 0


def test_optimize_trust_input_bypasses_pipeline():
    prompt = "Contact john@company.com unchanged"
    result = optimize(prompt, trust_input=True, return_metrics=True)
    assert result["optimized"] == prompt
    assert result["pii_masked"] is False


def test_optimize_return_metrics_shape():
    result = optimize("Hello world", return_metrics=True)
    assert "optimized" in result
    assert "original" in result
    assert "token_reduction" in result
    assert "pii_masked" in result
    assert "privacy_mode" in result


def test_optimize_debug_includes_security():
    result = optimize(
        "Email test@company.com",
        debug=True,
        privacy_mode="strict",
    )
    assert "debug" in result
    assert "security_result" in result["debug"]


def test_optimize_token_budget_hard_cap():
    long_prompt = "word " * 500
    out = optimize(long_prompt, token_budget=50, privacy_mode="off")
    assert len(out.split()) <= 50


def test_optimize_empty_prompt():
    assert optimize("") == ""


def test_optimize_pii_masked_flag_when_entities_found():
    result = optimize(
        "SSN 123-45-6789 here",
        privacy_mode="strict",
        return_metrics=True,
    )
    assert result["pii_masked"] is True
