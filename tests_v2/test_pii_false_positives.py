"""False positive regression tests."""

from privysha import process, sanitize
from privysha.security.pii_detector import PIIDetector


def test_order_number_not_flagged_as_phone():
    types = PIIDetector().detect_pii_types("Order #12345-6789 shipped today")
    assert "phone" not in types


def test_version_string_not_flagged_as_phone():
    types = PIIDetector().detect_pii_types("Upgrade to v1.2.3.4 release")
    assert "phone" not in types


def test_sql_in_documentation_context_not_blocked():
    text = "Documentation: use SELECT name FROM users WHERE id = 1 as an example."
    out = process(text, mode="balanced")
    assert isinstance(out, str)
    assert len(out) > 0


def test_teaching_example_com_still_allowed():
    out = sanitize("Use test@example.com in your docs.")
    assert "test@example.com" in out
