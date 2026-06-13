"""
Regex-based PII Detector - High precision pattern matching
"""

import re
from typing import List, Dict
from ...stages.base_stage import PIIEntity
from .....security.patterns import compile_pii_patterns, is_example_email


class RegexDetector:
    """
    Regex-based PII detector with high precision pattern matching.

    This detector uses carefully crafted regular expressions to identify
    PII patterns with very high precision and low false positive rate.
    """

    def __init__(self) -> None:
        """Initialize regex detector with comprehensive pattern library."""
        self.patterns = self._compile_patterns()
        self.confidence_weights = self._get_confidence_weights()

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile all regex patterns for efficient matching."""
        return compile_pii_patterns()

    def _get_confidence_weights(self) -> Dict[str, float]:
        """Get confidence weights for different PII types."""
        return {
            "email": 0.95,
            "phone": 0.90,
            "ssn": 0.95,
            "credit_card": 0.90,
            "ip_address": 0.85,
            "url": 0.80,
            "zip_code": 0.75,
            "date_of_birth": 0.70,
            "address": 0.65,
            "name": 0.60,
            "api_key": 0.95,
            "jwt_token": 0.95,
            "bearer_token": 0.90,
        }

    def detect(self, text: str) -> List[PIIEntity]:
        """
        Detect PII entities using regex patterns.

        Args:
            text: Input text to analyze

        Returns:
            List of detected PII entities
        """
        entities = []

        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(text)

                for match in matches:
                    # Additional validation for certain types
                    if not self._validate_match(pii_type, match.group()):
                        continue

                    entity = PIIEntity(
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        pii_type=pii_type,
                        confidence=self.confidence_weights.get(pii_type, 0.8),
                        context=self._get_context(
                            text, match.start(), match.end()),
                        metadata={
                            "detector": "regex",
                            "pattern": pattern.pattern,
                            "validation_passed": True,
                        },
                    )
                    entities.append(entity)

        return entities

    def _validate_match(self, pii_type: str, match_text: str) -> bool:
        """Additional validation for certain PII types."""
        if pii_type == "email":
            return self._validate_email(match_text)
        elif pii_type == "credit_card":
            return self._validate_credit_card(match_text)
        elif pii_type == "ip_address":
            return self._validate_ip_address(match_text)
        elif pii_type == "phone":
            return self._validate_phone(match_text)

        return True

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if is_example_email(email):
            return False
        # Basic email validation
        if "@" not in email or "." not in email:
            return False

        local, domain = email.split("@", 1)

        # Check local part
        if len(local) < 1 or len(local) > 64:
            return False

        # Check domain part
        if len(domain) < 4 or len(domain) > 253:
            return False

        # Check for valid domain structure
        if "." not in domain:
            return False

        domain_parts = domain.split(".")
        if len(domain_parts) < 2:
            return False

        # Check TLD
        tld = domain_parts[-1]
        if len(tld) < 2:
            return False

        return True

    def _validate_credit_card(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm."""
        # Remove non-digits
        digits = re.sub(r"\D", "", card_number)

        # Check length
        if len(digits) not in [13, 14, 15, 16]:
            return False

        # Luhn algorithm
        total = 0
        reverse_digits = digits[::-1]

        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:  # Every second digit
                n *= 2
                if n > 9:
                    n -= 9
            total += n

        return total % 10 == 0

    def _validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format."""
        parts = ip.split(".")

        if len(parts) != 4:
            return False

        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            except ValueError:
                return False

        return True

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        # Remove non-digits
        digits = re.sub(r"\D", "", phone)

        # Check for valid length (10 or 11 digits with country code)
        if len(digits) not in [10, 11]:
            return False

        # Check for reasonable area code (first 3 digits)
        if len(digits) >= 10:
            area_code = digits[-10:-7] if len(digits) == 11 else digits[:3]
            # Area codes shouldn't start with 0 or 1
            if area_code.startswith(("0", "1")):
                return False

        return True

    def _get_context(
        self, text: str, start: int, end: int, window_size: int = 50
    ) -> str:
        """Get context around a match."""
        context_start = max(0, start - window_size)
        context_end = min(len(text), end + window_size)
        return text[context_start:context_end]

    def get_pattern_count(self) -> Dict[str, int]:
        """Get count of patterns by type."""
        return {pii_type: len(patterns) for pii_type, patterns in self.patterns.items()}

    def add_custom_pattern(
        self, pii_type: str, pattern: str, confidence: float = 0.8
    ) -> None:
        """Add a custom regex pattern."""
        if pii_type not in self.patterns:
            self.patterns[pii_type] = []

        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        self.patterns[pii_type].append(compiled_pattern)
        self.confidence_weights[pii_type] = confidence
