"""Edge-case tests for drop-in API reliability."""

import json

import pytest

from asha.types.results import ProcessResult, SanitizeResult
from asha.utils.dropin import process, sanitize, optimize

from conftest import output_of

# Valid Luhn test card (Visa)
VALID_CARD = "4111111111111111"
VALID_CARD_FORMATTED = "4111-1111-1111-1111"
INVALID_CARD = "79927398710"  # fails Luhn; avoids phone-number substring matches


def test_empty_prompt_string():
    result = process("")
    assert isinstance(result, ProcessResult)
    assert result.output == ""
    assert result.degraded is True


def test_empty_prompt_sanitize():
    result = sanitize("")
    assert isinstance(result, SanitizeResult)
    assert result.output == ""


def test_invalid_prompt_type():
    result = process(None)  # type: ignore[arg-type]
    assert isinstance(result, ProcessResult)
    assert result.degraded is True
    assert result.degraded_reason == "invalid_prompt"


def test_whitespace_only_prompt():
    """Whitespace-only prompts should be processed without crash."""
    result = process("   \n\t  ")
    assert isinstance(result, ProcessResult)
    assert result.output is not None


def test_unicode_multilingual_prompt():
    prompt = "Bonjour! 联系人: zhang@example.com 電話: 555-123-4567"
    result = process(prompt)
    out = output_of(result)
    assert "zhang@example.com" not in out


def test_unicode_emoji_prompt():
    prompt = "Analyze 📊 data for user john@example.com 🚀"
    result = process(prompt)
    assert "john@example.com" not in output_of(result)


def test_large_prompt_does_not_crash():
    prompt = ("Summarize quarterly revenue trends. " * 500) + "Contact: a@b.com"
    result = process(prompt)
    out = output_of(result)
    assert "a@b.com" not in out
    assert len(out) > 0


def test_structured_json_mode_off_preserves_exact():
    """mode=off must preserve JSON byte-for-byte."""
    payload = {
        "task": "classify",
        "labels": ["positive", "negative"],
        "text": "Great product!",
    }
    prompt = json.dumps(payload, indent=2)
    result = process(prompt, mode="off")
    out = output_of(result)
    parsed = json.loads(out)
    assert parsed == payload


def test_safe_prompt_no_pii_balanced_preserves_meaning():
    """Balanced mode may optimize but must preserve core meaning."""
    prompt = "Explain the difference between supervised and unsupervised learning."
    result = process(prompt, mode="balanced")
    out = output_of(result)
    # The output must be non-empty and contain at least one of the key terms
    assert len(out) > 10
    # At minimum, the subject matter should be recognizable
    lower_out = out.lower()
    assert "learn" in lower_out or "supervised" in lower_out or "unsupervised" in lower_out


def test_credit_card_valid_detected_and_masked():
    prompt = f"My card is {VALID_CARD}"
    result = sanitize(prompt)
    out = output_of(result)
    assert VALID_CARD not in out.replace("-", "").replace(" ", "")
    assert "[CREDIT_CARD_HASH]" in out


def test_credit_card_invalid_luhn_not_masked():
    """Random digit sequences failing Luhn should not be treated as cards."""
    from asha.core.security.pii_detector import PIIDetector

    prompt = f"Reference number {INVALID_CARD}"
    detector = PIIDetector()
    assert "credit_card" not in detector.detect_pii_types(prompt)
    assert not detector._is_valid_credit_card(INVALID_CARD)


def test_address_type_detected_by_detector():
    from asha.core.security.pii_detector import PIIDetector

    detector = PIIDetector()
    types = detector.detect_pii_types("Ship to 742 Evergreen Street, Springfield")
    assert "address" in types


def test_single_character_prompt():
    """Single character should not crash."""
    result = process("x")
    assert isinstance(result, ProcessResult)
    assert result.output is not None


def test_newlines_only_prompt():
    result = process("\n\n\n")
    assert isinstance(result, ProcessResult)


def test_very_long_single_word():
    """A single very long word should not crash."""
    word = "a" * 10000
    result = process(word)
    assert isinstance(result, ProcessResult)
    assert result.output is not None
