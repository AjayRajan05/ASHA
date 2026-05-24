"""Phone number PII detection and masking tests."""

from privysha import process, sanitize
from privysha.core.pii_pipeline.stages.detection_stage import RegexDetector
from privysha.security.pii_detector import PIIDetector


def test_phone_dash_format_detected_and_masked():
    out = sanitize("Call 555-123-4567 for support")
    assert "555-123-4567" not in out
    assert "[PHONE_HASH]" in out


def test_phone_dash_format_detected_by_regex():
    entities = RegexDetector().detect("Call 555-123-4567 for support")
    assert any(e.pii_type == "phone" for e in entities)


def test_phone_international_detected_by_regex():
    entities = RegexDetector().detect("International +1-555-123-4567")
    assert any(e.pii_type == "phone" for e in entities)


def test_process_masks_phone_dash_format():
    out = process("Contact 555-987-6543 today", mode="strict")
    assert "555-987-6543" not in out


def test_optimize_strict_masks_phone():
    from privysha import optimize

    out = optimize(
        "My number is 555-111-2222",
        privacy_mode="strict",
        return_metrics=True,
    )
    assert "555-111-2222" not in out["optimized"]


def test_phone_not_confused_with_order_number():
    types = PIIDetector().detect_pii_types("Order #12345-6789 shipped")
    assert "phone" not in types
