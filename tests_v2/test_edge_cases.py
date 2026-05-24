"""Edge-case tests for drop-in API reliability."""

import json

import pytest

from privysha.utils.dropin import process, sanitize, optimize


# Valid Luhn test card (Visa)
VALID_CARD = "4111111111111111"
VALID_CARD_FORMATTED = "4111-1111-1111-1111"
INVALID_CARD = "79927398710"  # fails Luhn; avoids phone-number substring matches


def test_empty_prompt_string():
    result = process("", return_metrics=True)
    assert result["optimized"] == ""
    assert result["metrics"]["pii_detected"] == []


def test_empty_prompt_sanitize():
    assert sanitize("") == ""


def test_invalid_prompt_type():
    result = process(None, return_metrics=True)  # type: ignore[arg-type]
    assert "error" in result


def test_unicode_multilingual_prompt():
    prompt = "Bonjour! 联系人: zhang@example.com 電話: 555-123-4567"
    result = process(prompt)
    assert isinstance(result, str)
    assert "zhang@example.com" not in result


def test_unicode_emoji_prompt():
    prompt = "Analyze 📊 data for user john@example.com 🚀"
    result = process(prompt)
    assert "john@example.com" not in result


def test_large_prompt_does_not_crash():
    prompt = ("Summarize quarterly revenue trends. " * 500) + "Contact: a@b.com"
    result = process(prompt)
    assert isinstance(result, str)
    assert "a@b.com" not in result
    assert len(result) > 0


def test_structured_json_mostly_unchanged():
    payload = {
        "task": "classify",
        "labels": ["positive", "negative"],
        "text": "Great product!",
    }
    prompt = json.dumps(payload, indent=2)
    result = process(prompt, mode="off", privacy=False)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed["task"] == "classify"
    assert parsed["labels"] == ["positive", "negative"]


def test_safe_prompt_no_pii_minimal_change():
    prompt = "Explain the difference between supervised and unsupervised learning."
    result = process(prompt, mode="lite")
    assert isinstance(result, str)
    # Core instruction should survive optimization
    assert "supervised" in result.lower() or "unsupervised" in result.lower()


def test_credit_card_valid_detected_and_masked():
    prompt = f"My card is {VALID_CARD}"
    result = sanitize(prompt)
    assert VALID_CARD not in result.replace("-", "").replace(" ", "")
    assert "[CREDIT_CARD_HASH]" in result


def test_credit_card_invalid_luhn_not_masked():
    """Random digit sequences failing Luhn should not be treated as cards."""
    from privysha.security.pii_detector import PIIDetector

    prompt = f"Reference number {INVALID_CARD}"
    detector = PIIDetector()
    assert "credit_card" not in detector.detect_pii_types(prompt)
    assert not detector._is_valid_credit_card(INVALID_CARD)


def test_address_type_detected_by_detector():
    """Address detection is available on PIIDetector; masking is not required yet."""
    from privysha.security.pii_detector import PIIDetector

    detector = PIIDetector()
    types = detector.detect_pii_types("Ship to 742 Evergreen Street, Springfield")
    assert "address" in types
