"""False positive regression tests.

Ensures that common non-PII patterns are NOT incorrectly flagged.
"""

from asha import process, sanitize
from asha.core.security.pii_detector import PIIDetector
from asha.types.results import ProcessResult, SanitizeResult

from conftest import output_of


# ---------------------------------------------------------------------------
# Phone-like patterns that are NOT phone numbers
# ---------------------------------------------------------------------------


def test_order_number_not_flagged_as_phone():
    types = PIIDetector().detect_pii_types("Order #12345-6789 shipped today")
    assert "phone" not in types


def test_version_string_not_flagged_as_phone():
    types = PIIDetector().detect_pii_types("Upgrade to v1.2.3.4 release")
    assert "phone" not in types


def test_zip_code_not_flagged_as_phone():
    types = PIIDetector().detect_pii_types("Ship to zip code 90210")
    assert "phone" not in types


# ---------------------------------------------------------------------------
# Non-threatening SQL in documentation context
# ---------------------------------------------------------------------------


def test_sql_in_documentation_context_not_blocked():
    text = "Documentation: use SELECT name FROM users WHERE id = 1 as an example."
    result = process(text, mode="balanced")
    assert isinstance(result, ProcessResult)
    assert len(output_of(result)) > 0


# ---------------------------------------------------------------------------
# Example/placeholder emails in teaching context
# ---------------------------------------------------------------------------


def test_teaching_example_com_preserved():
    """example.com emails in teaching context should be preserved."""
    result = sanitize("Use test@example.com in your docs.")
    assert isinstance(result, SanitizeResult)
    # example.com is a reserved domain for documentation - should be preserved
    assert "test@example.com" in result.output


# ---------------------------------------------------------------------------
# Non-PII numeric patterns
# ---------------------------------------------------------------------------


def test_year_not_flagged_as_pii():
    types = PIIDetector().detect_pii_types("The year 2024 was productive")
    assert "ssn" not in types
    assert "phone" not in types
    assert "credit_card" not in types


def test_hex_color_not_flagged_as_pii():
    types = PIIDetector().detect_pii_types("Use color #FF5733 for the header")
    assert "credit_card" not in types
    assert "ssn" not in types


def test_uuid_not_flagged_as_pii():
    types = PIIDetector().detect_pii_types(
        "Request ID: 550e8400-e29b-41d4-a716-446655440000"
    )
    assert "ssn" not in types
    assert "phone" not in types


def test_ip_address_not_flagged_as_phone():
    types = PIIDetector().detect_pii_types("Server at 192.168.1.100")
    assert "phone" not in types


# ---------------------------------------------------------------------------
# Safe prompts should not be flagged
# ---------------------------------------------------------------------------


def test_plain_question_no_pii_detected():
    types = PIIDetector().detect_pii_types("What is machine learning?")
    assert len(types) == 0


def test_technical_prompt_no_false_positives():
    types = PIIDetector().detect_pii_types(
        "Implement a REST API with OAuth 2.0 authentication"
    )
    assert "api_key" not in types
    assert "email" not in types
