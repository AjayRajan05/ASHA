"""Edge-case tests for drop-in API reliability."""

import json

import pytest

from privysha.types.results import ProcessResult, SanitizeResult
from privysha.utils.dropin import process, sanitize, optimize

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


def test_structured_json_mostly_unchanged():
    payload = {
        "task": "classify",
        "labels": ["positive", "negative"],
        "text": "Great product!",
    }
    prompt = json.dumps(payload, indent=2)
    result = process(prompt, mode="off")
    out = output_of(result)
    parsed = json.loads(out)
    assert parsed["task"] == "classify"
    assert parsed["labels"] == ["positive", "negative"]


def test_safe_prompt_no_pii_minimal_change():
    prompt = "Explain the difference between supervised and unsupervised learning."
    result = process(prompt, mode="lite")
    out = output_of(result)
    # Core instruction should survive optimization
    assert "supervised" in out.lower() or "unsupervised" in out.lower()


def test_credit_card_valid_detected_and_masked():
    prompt = f"My card is {VALID_CARD}"
    result = sanitize(prompt)
    out = output_of(result)
    assert VALID_CARD not in out.replace("-", "").replace(" ", "")
    assert "[CREDIT_CARD_HASH]" in out


def test_credit_card_invalid_luhn_not_masked():
    """Random digit sequences failing Luhn should not be treated as cards."""
    from privysha.core.security.pii_detector import PIIDetector

    prompt = f"Reference number {INVALID_CARD}"
    detector = PIIDetector()
    assert "credit_card" not in detector.detect_pii_types(prompt)
    assert not detector._is_valid_credit_card(INVALID_CARD)


def test_address_type_detected_by_detector():
    """Address detection is available on PIIDetector; masking is not required yet."""
    from privysha.core.security.pii_detector import PIIDetector

    detector = PIIDetector()
    types = detector.detect_pii_types("Ship to 742 Evergreen Street, Springfield")
    assert "address" in types
