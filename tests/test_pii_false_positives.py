"""False positive regression tests."""

from privysha import process, sanitize
from privysha.core.security.pii_detector import PIIDetector
from privysha.types.results import ProcessResult, SanitizeResult

from conftest import output_of


def test_order_number_not_flagged_as_phone():
    types = PIIDetector().detect_pii_types("Order #12345-6789 shipped today")
    assert "phone" not in types


def test_version_string_not_flagged_as_phone():
    types = PIIDetector().detect_pii_types("Upgrade to v1.2.3.4 release")
    assert "phone" not in types


def test_sql_in_documentation_context_not_blocked():
    text = "Documentation: use SELECT name FROM users WHERE id = 1 as an example."
    result = process(text, mode="balanced")
    assert isinstance(result, ProcessResult)
    assert len(output_of(result)) > 0


def test_teaching_example_com_still_allowed():
    result = sanitize("Use test@example.com in your docs.")
    assert isinstance(result, SanitizeResult)
    assert "test@example.com" in result.output
