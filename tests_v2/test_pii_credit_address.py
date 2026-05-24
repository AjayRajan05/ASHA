"""PII detection tests for credit cards and addresses."""

from privysha.security.pii_detector import PIIDetector
from privysha.core.pii_pipeline.stages.detection_stage import RegexDetector
from privysha.utils.dropin import sanitize


VALID_VISA = "4111111111111111"
VALID_VISA_SPACED = "4111 1111 1111 1111"
INVALID_LUHN = "4111111111111112"


class TestCreditCardLuhn:
    def test_valid_card_detected(self):
        detector = PIIDetector()
        types = detector.detect_pii_types(f"Pay with {VALID_VISA}")
        assert "credit_card" in types

    def test_invalid_luhn_rejected_by_detector(self):
        detector = PIIDetector()
        types = detector.detect_pii_types(f"ID {INVALID_LUHN}")
        assert "credit_card" not in types

    def test_regex_detector_luhn_filter(self):
        regex = RegexDetector()
        valid = regex.detect(f"Card: {VALID_VISA_SPACED}")
        invalid = regex.detect(f"Ref: {INVALID_LUHN}")
        assert any(e.pii_type == "credit_card" for e in valid)
        assert not any(e.pii_type == "credit_card" for e in invalid)

    def test_sanitize_masks_valid_card(self):
        out = sanitize(f"My card is {VALID_VISA}")
        assert VALID_VISA not in out
        assert "[CREDIT_CARD_HASH]" in out

    def test_sanitize_masks_spaced_card(self):
        out = sanitize(f"Charge {VALID_VISA_SPACED} please")
        assert VALID_VISA not in out.replace(" ", "")


class TestAddressDetection:
    def test_street_suffix_detected(self):
        detector = PIIDetector()
        text = "Office at 500 Main Street, Boston"
        types = detector.detect_pii_types(text)
        assert "address" in types

    def test_sanitize_masks_street_address(self):
        out = sanitize("Ship to 742 Evergreen Street today")
        assert "742 Evergreen Street" not in out
        assert "[ADDRESS_HASH]" in out

    def test_process_masks_full_address(self):
        from privysha import process

        text = "Office at 100 Oak Avenue, Springfield, IL 62701"
        out = process(text, mode="strict")
        assert "Oak Avenue" not in out or "[ADDRESS_HASH]" in out

    def test_address_hash_token_in_output(self):
        out = sanitize("Located at 42 Maple Drive")
        assert "[ADDRESS_HASH]" in out
