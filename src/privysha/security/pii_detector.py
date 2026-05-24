# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Canonical rule-based PII detector (domain layer)."""

import re
import hashlib
from typing import Dict, List, Tuple
from dataclasses import dataclass

from .patterns import is_example_email


@dataclass
class PIIMatch:
    """Represents a detected PII entity."""

    text: str
    pii_type: str
    start: int
    end: int
    confidence: float


class PIIDetector:
    """Intelligent PII detector with contextual analysis and multiple detection strategies."""

    def __init__(self):
        """Initialize PII detector with default patterns."""
        self.context_keywords = {
            "name": [
                "name",
                "called",
                "contact",
                "hello",
                "dear",
                "mr",
                "mrs",
                "ms",
                "dr",
            ],
            "email": ["email", "mail", "contact", "reach", "send", "@"],
            "phone": ["phone", "call", "tel", "mobile", "cell", "number"],
            "address": [
                "address",
                "street",
                "st",
                "avenue",
                "ave",
                "road",
                "rd",
                "live",
                "located",
            ],
            "ssn": ["ssn", "social security", "identification", "id number"],
            "credit_card": ["card", "credit", "payment", "visa", "mastercard", "amex"],
            "zip_code": ["zip", "postal", "code"],
            "date_of_birth": ["birth", "born", "birthday", "dob", "age"],
            "api_key": ["api key", "secret key", "api_key", "secret", "token", "credential"],
            "jwt_token": ["jwt", "bearer", "authorization", "access token"],
        }

        self.patterns = {
            "email": [
                re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
                re.compile(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                ),
            ],
            "phone": [
                re.compile(r"\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
                re.compile(r"\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b"),
                re.compile(r"\b\d{3}-\d{3}-\d{4}\b"),
            ],
            "ssn": [
                re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
                re.compile(r"\b\d{3}\s\d{2}\s\d{4}\b"),
            ],
            "credit_card": [
                re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
                re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
                re.compile(r"\b\d{16}\b"),
            ],
            "name": [
                re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"),
                re.compile(r"\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b"),
                re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b"),
                re.compile(
                    r"\b(?:John|Mary|James|Robert|Michael|William|David|Richard|Joseph|Thomas|Charles|Christopher|Daniel|Matthew|Anthony|Mark|Donald|Steven|Paul|Andrew|Joshua|Kevin|Brian|George|Edward|Ronald|Timothy|Jason|yesh|raj|ajay|vijay|anand|rahul|priya|anita|sonia|pooja|ravi|amit|sumit|deepak)\b"
                ),
            ],
            "address": [
                re.compile(
                    r"\b\d+\s+[A-Z][a-z]+\s+(St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Ln|Lane|Dr|Drive|Ct|Court|Way|Place|Pl)\b"
                ),
                re.compile(
                    r"\b\d+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Ln|Lane|Dr|Drive|Ct|Court|Way|Place|Pl)\b"
                ),
                re.compile(
                    r"\d+\s+[A-Za-z\s]+,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}"
                ),
            ],
            "zip_code": [
                re.compile(r"\b\d{5}(?:-\d{4})?\b"),
                re.compile(r"\b[A-Z]{1,2}\d{1,2}\s\d[A-Z]{2}\b"),
            ],
            "ip_address": [
                re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
                re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"),
            ],
            "url": [re.compile(r"https?://[^\s]+"), re.compile(r"www\.[^\s]+")],
            "date_of_birth": [
                re.compile(r"\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\b"),
                re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
                re.compile(r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"),
            ],
            "api_key": [
                re.compile(r"\bsk-[a-zA-Z0-9]{20,}\b"),
                re.compile(r"\bsk-proj-[a-zA-Z0-9_-]{20,}\b"),
                re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
                re.compile(
                    r"(?i)(?:api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{16,}"
                ),
            ],
            "jwt_token": [
                re.compile(
                    r"\beyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b"
                ),
            ],
            "bearer_token": [
                re.compile(r"(?i)Bearer\s+[a-zA-Z0-9._\-]{20,}"),
            ],
        }

        self.masks = {
            "email": "[EMAIL_HASH]",
            "phone": "[PHONE_HASH]",
            "ssn": "[SSN_HASH]",
            "credit_card": "[CREDIT_CARD_HASH]",
            "name": "[NAME_HASH]",
            "address": "[ADDRESS_HASH]",
            "zip_code": "[ZIP_HASH]",
            "ip_address": "[IP_HASH]",
            "url": "[URL_HASH]",
            "date_of_birth": "[DOB_HASH]",
            "api_key": "[API_KEY_HASH]",
            "jwt_token": "[JWT_HASH]",
            "bearer_token": "[TOKEN_HASH]",
        }

    def _calculate_context_score(
        self, text: str, pii_type: str, match_start: int, match_end: int
    ) -> float:
        context_window = 50
        start = max(0, match_start - context_window)
        end = min(len(text), match_end + context_window)
        context = text[start:end].lower()

        keywords = self.context_keywords.get(pii_type, [])
        keyword_count = sum(1 for keyword in keywords if keyword in context)

        base_score = 0.5
        context_boost = min(0.5, keyword_count * 0.1)
        return base_score + context_boost

    def _detect_pii_with_context(self, text: str) -> List[PIIMatch]:
        matches = []

        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    if pii_type == "email" and is_example_email(match.group()):
                        continue

                    confidence = self._calculate_context_score(
                        text, pii_type, match.start(), match.end()
                    )

                    if pii_type == "credit_card" and not self._is_valid_credit_card(
                        match.group()
                    ):
                        confidence *= 0.5
                    elif pii_type == "email" and not self._is_valid_email(
                        match.group()
                    ):
                        confidence *= 0.5

                    if pii_type == "ssn" and re.fullmatch(
                        r"\d{3}-\d{2}-\d{4}", match.group().replace(" ", "-")
                    ):
                        confidence = max(confidence, 0.95)

                    if confidence > 0.3:
                        matches.append(
                            PIIMatch(
                                text=match.group(),
                                pii_type=pii_type,
                                start=match.start(),
                                end=match.end(),
                                confidence=confidence,
                            )
                        )

        return self._remove_overlaps(matches)

    def _remove_overlaps(self, matches: List[PIIMatch]) -> List[PIIMatch]:
        if not matches:
            return matches

        matches.sort(key=lambda x: (x.start, -x.confidence))

        filtered = []
        for match in matches:
            overlaps = any(
                not (match.end <= existing.start or match.start >= existing.end)
                for existing in filtered
            )
            if not overlaps:
                filtered.append(match)

        return filtered

    def _is_valid_email(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]

    def _is_valid_credit_card(self, card: str) -> bool:
        digits = re.sub(r"[\s-]", "", card)
        if not digits.isdigit() or len(digits) not in [13, 14, 15, 16, 19]:
            return False

        total = 0
        for i, digit in enumerate(reversed(digits)):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n

        return total % 10 == 0

    def detect_pii_types(self, text: str) -> List[str]:
        matches = self._detect_pii_with_context(text)
        return list(set(match.pii_type for match in matches))

    def mask(self, text: str) -> str:
        matches = self._detect_pii_with_context(text)
        masked_text = text
        matches.sort(key=lambda x: x.start, reverse=True)

        for match in matches:
            mask = self.masks.get(match.pii_type, "[PII_HASH]")
            hash_suffix = hashlib.md5(
                f"{match.text}{match.pii_type}".encode()
            ).hexdigest()[:8]
            masked_value = f"{mask}_{hash_suffix}"
            masked_text = (
                masked_text[: match.start] + masked_value + masked_text[match.end :]
            )

        return masked_text

    def mask_with_details(self, text: str) -> Tuple[str, Dict[str, List[str]]]:
        matches = self._detect_pii_with_context(text)
        masked_text = text
        masked_entities = {}
        matches.sort(key=lambda x: x.start, reverse=True)

        for match in matches:
            mask = self.masks.get(match.pii_type, "[PII_HASH]")
            hash_suffix = hashlib.md5(
                f"{match.text}{match.pii_type}".encode()
            ).hexdigest()[:8]
            masked_value = f"{mask}_{hash_suffix}"

            if match.pii_type not in masked_entities:
                masked_entities[match.pii_type] = []
            masked_entities[match.pii_type].append(match.text)

            masked_text = (
                masked_text[: match.start] + masked_value + masked_text[match.end :]
            )

        return masked_text, masked_entities

    def get_pii_summary(self, text: str) -> Dict[str, int]:
        matches = self._detect_pii_with_context(text)
        summary = {}
        for match in matches:
            summary[match.pii_type] = summary.get(match.pii_type, 0) + 1
        return summary

    def analyze_text(self, text: str) -> Dict:
        matches = self._detect_pii_with_context(text)
        masked_text, entities = self.mask_with_details(text)

        return {
            "original_text": text,
            "masked_text": masked_text,
            "pii_matches": [
                {"text": m.text, "type": m.pii_type, "confidence": m.confidence}
                for m in matches
            ],
            "pii_types": list(set(m.pii_type for m in matches)),
            "pii_count": len(matches),
            "entities_by_type": entities,
            "risk_score": self._calculate_risk_score(matches),
        }

    def _calculate_risk_score(self, matches: List[PIIMatch]) -> float:
        type_weights = {
            "ssn": 0.95,
            "credit_card": 0.95,
            "email": 0.8,
            "phone": 0.7,
            "address": 0.8,
            "name": 0.6,
            "zip_code": 0.5,
            "date_of_birth": 0.7,
            "ip_address": 0.6,
            "url": 0.4,
            "api_key": 0.98,
            "jwt_token": 0.98,
            "bearer_token": 0.95,
        }

        if not matches:
            return 0.0

        weighted_score = sum(
            type_weights.get(m.pii_type, 0.5) * m.confidence for m in matches
        )
        max_possible = sum(type_weights.get(m.pii_type, 0.5) for m in matches)

        return min(1.0, weighted_score / max_possible if max_possible > 0 else 0.0)
