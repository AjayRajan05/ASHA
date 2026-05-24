"""
Stage 2: Multi-Detector Engine - Parallel PII detection
"""

import re
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from .base_stage import BaseStage, StageResult, PIIContext, PIIEntity
from ..components.detectors.regex_detector import RegexDetector


class DetectionStage(BaseStage):
    """
    Multi-Detector Stage - Runs multiple PII detectors in parallel.

    This stage handles:
    - Parallel execution of multiple detectors
    - Regex-based detection
    - Pattern heuristics
    - Dictionary-based detection
    - Contextual rules
    - Entity deduplication
    """

    def __init__(self) -> None:
        super().__init__("detection")

        # Initialize all detectors
        self.regex_detector = RegexDetector()
        self.heuristic_detector = HeuristicDetector()
        self.dictionary_detector = DictionaryDetector()
        self.contextual_detector = ContextualDetector()

        # Detection configuration
        self.detection_config = {
            "enable_regex": True,
            "enable_heuristics": True,
            "enable_dictionary": True,
            "enable_contextual": True,
            "parallel_execution": True,
            "min_confidence": 0.3,
            "overlap_threshold": 0.5,  # For entity deduplication
        }

    def execute(self, context: PIIContext) -> StageResult:
        """
        Execute parallel PII detection.

        Args:
            context: PII pipeline context

        Returns:
            StageResult with detected entities
        """
        text = context.current_text
        config = context.config.get("detection", self.detection_config)

        # Run detectors in parallel
        all_entities = []

        if config.get("parallel_execution", True):
            all_entities = self._run_parallel_detection(text, config)
        else:
            all_entities = self._run_sequential_detection(text, config)

        # Deduplicate entities
        deduplicated_entities = self._deduplicate_entities(
            all_entities, config)

        # Sort entities by position
        deduplicated_entities.sort(key=lambda e: e.start)

        self.add_debug_info(
            context,
            "Multi-detector execution completed",
            {
                "total_entities_detected": len(all_entities),
                "deduplicated_entities": len(deduplicated_entities),
                "detectors_used": self._get_enabled_detectors(config),
            },
        )

        return StageResult(
            success=True,
            stage_name=self.stage_name,
            execution_time_ms=0.0,
            entities=deduplicated_entities,
            metadata={
                "total_entities_detected": len(all_entities),
                "deduplicated_entities": len(deduplicated_entities),
                "detectors_used": self._get_enabled_detectors(config),
                "detection_stats": self._get_detection_stats(
                    all_entities, deduplicated_entities
                ),
            },
        )

    def _run_parallel_detection(
        self, text: str, config: Dict[str, Any]
    ) -> List[PIIEntity]:
        """Run all detectors in parallel"""
        all_entities = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all detection tasks
            futures = {}

            if config.get("enable_regex", True):
                futures["regex"] = executor.submit(
                    self.regex_detector.detect, text)

            if config.get("enable_heuristics", True):
                futures["heuristics"] = executor.submit(
                    self.heuristic_detector.detect, text
                )

            if config.get("enable_dictionary", True):
                futures["dictionary"] = executor.submit(
                    self.dictionary_detector.detect, text
                )

            if config.get("enable_contextual", True):
                futures["contextual"] = executor.submit(
                    self.contextual_detector.detect, text
                )

            # Collect results
            for detector_name, future in futures.items():
                try:
                    # 5 second timeout per detector
                    entities = future.result(timeout=5)
                    all_entities.extend(entities)
                except Exception as e:
                    print(f"[Detection] {detector_name} detector failed: {e}")

        return all_entities

    def _run_sequential_detection(
        self, text: str, config: Dict[str, Any]
    ) -> List[PIIEntity]:
        """Run detectors sequentially"""
        all_entities = []

        if config.get("enable_regex", True):
            try:
                all_entities.extend(self.regex_detector.detect(text))
            except Exception as e:
                print(f"[Detection] Regex detector failed: {e}")

        if config.get("enable_heuristics", True):
            try:
                all_entities.extend(self.heuristic_detector.detect(text))
            except Exception as e:
                print(f"[Detection] Heuristic detector failed: {e}")

        if config.get("enable_dictionary", True):
            try:
                all_entities.extend(self.dictionary_detector.detect(text))
            except Exception as e:
                print(f"[Detection] Dictionary detector failed: {e}")

        if config.get("enable_contextual", True):
            try:
                all_entities.extend(self.contextual_detector.detect(text))
            except Exception as e:
                print(f"[Detection] Contextual detector failed: {e}")

        return all_entities

    def _deduplicate_entities(
        self, entities: List[PIIEntity], config: Dict[str, Any]
    ) -> List[PIIEntity]:
        """Remove overlapping and duplicate entities"""
        if not entities:
            return []

        # Sort by confidence (highest first) then by position
        entities.sort(key=lambda e: (-e.confidence, e.start, e.end))

        deduplicated = []
        overlap_threshold = config.get("overlap_threshold", 0.5)

        for entity in entities:
            # Check for overlaps with existing entities
            is_duplicate = False

            for existing in deduplicated:
                # Check if entities overlap
                if entity.start <= existing.end and entity.end >= existing.start:
                    # Calculate overlap ratio
                    overlap_start = max(entity.start, existing.start)
                    overlap_end = min(entity.end, existing.end)
                    overlap_length = overlap_end - overlap_start + 1

                    entity_length = entity.end - entity.start + 1
                    existing_length = existing.end - existing.start + 1

                    overlap_ratio = overlap_length / \
                        min(entity_length, existing_length)

                    if overlap_ratio > overlap_threshold:
                        # Keep the one with higher confidence
                        if entity.confidence > existing.confidence:
                            deduplicated.remove(existing)
                        else:
                            is_duplicate = True
                        break

            if not is_duplicate:
                deduplicated.append(entity)

        # Sort final result by position
        deduplicated.sort(key=lambda e: e.start)

        return deduplicated

    def _get_enabled_detectors(self, config: Dict[str, Any]) -> List[str]:
        """Get list of enabled detectors"""
        enabled = []

        if config.get("enable_regex", True):
            enabled.append("regex")
        if config.get("enable_heuristics", True):
            enabled.append("heuristics")
        if config.get("enable_dictionary", True):
            enabled.append("dictionary")
        if config.get("enable_contextual", True):
            enabled.append("contextual")

        return enabled

    def _get_detection_stats(
        self, all_entities: List[PIIEntity], deduplicated: List[PIIEntity]
    ) -> Dict[str, Any]:
        """Get detection statistics"""
        stats = {
            "by_type": {},
            "by_confidence": {
                "high": 0,  # > 0.8
                "medium": 0,  # 0.5-0.8
                "low": 0,  # < 0.5
            },
        }

        for entity in all_entities:
            # Count by type
            pii_type = entity.pii_type
            stats["by_type"][pii_type] = stats["by_type"].get(pii_type, 0) + 1

            # Count by confidence
            if entity.confidence > 0.8:
                stats["by_confidence"]["high"] += 1
            elif entity.confidence > 0.5:
                stats["by_confidence"]["medium"] += 1
            else:
                stats["by_confidence"]["low"] += 1

        stats["deduplication_ratio"] = (
            len(deduplicated) / len(all_entities) if all_entities else 0
        )

        return stats

    def validate_input(self, context: PIIContext) -> bool:
        """Validate input for detection stage"""
        if not context.current_text:
            return False

        if not isinstance(context.current_text, str):
            return False

        return True

    def fallback(self, context: PIIContext) -> StageResult:
        """Fallback detection - regex only"""
        try:
            entities = self.regex_detector.detect(context.current_text)

            self.add_debug_info(
                context,
                "Detection fallback used",
                {
                    "reason": "main_detection_failed",
                    "fallback_type": "regex_only",
                    "entities_found": len(entities),
                },
            )

            return StageResult(
                success=True,
                stage_name=self.stage_name,
                execution_time_ms=0.0,
                entities=entities,
                metadata={
                    "fallback_used": True,
                    "fallback_type": "regex_only",
                    "entities_detected": len(entities),
                },
            )
        except Exception as e:
            return StageResult(
                success=False,
                stage_name=self.stage_name,
                execution_time_ms=0.0,
                error=f"Fallback detection failed: {e}",
            )


# Individual Detector Classes (non-regex)


class HeuristicDetector:
    """Pattern heuristics detector"""

    def __init__(self) -> None:
        self.patterns = {
            "name": [
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # First Last
                r"\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b",  # First M. Last
                r"\bMr\.?\s+[A-Z][a-z]+\b",  # Mr. First
                r"\bMs\.?\s+[A-Z][a-z]+\b",  # Ms. First
                r"\bDr\.?\s+[A-Z][a-z]+\b",  # Dr. First
            ],
            "address": [
                r"\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b",
                r"\d+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b",
            ],
            "zip_code": [r"\b\d{5}\b", r"\b\d{5}-\d{4}\b"],
            "date_of_birth": [
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
                r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
            ],
        }

    def detect(self, text: str) -> List[PIIEntity]:
        """Detect PII using heuristic patterns"""
        entities = []

        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    entity = PIIEntity(
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        pii_type=pii_type,
                        confidence=0.6,  # Medium confidence for heuristics
                        context=text[max(0, match.start() - 20): match.end() + 20],
                    )
                    entities.append(entity)

        return entities


class DictionaryDetector:
    """Dictionary-based PII detector"""

    def __init__(self) -> None:
        # Common PII indicators and keywords
        self.pii_keywords = {
            "name": ["name", "called", "known as", "my name is", "i am"],
            "email": ["email", "e-mail", "mail", "contact me at", "reach me at"],
            "phone": ["phone", "telephone", "call me", "my number", "contact"],
            "address": ["address", "live at", "located at", "my address"],
            "ssn": ["ssn", "social security", "social security number"],
            "credit_card": [
                "credit card",
                "card number",
                "payment",
                "visa",
                "mastercard",
            ],
        }

        # Common first names (sample)
        self.first_names = {
            "john",
            "mary",
            "james",
            "patricia",
            "robert",
            "jennifer",
            "michael",
            "linda",
            "william",
            "elizabeth",
            "david",
            "barbara",
            "richard",
            "susan",
            "joseph",
            "jessica",
        }

        # Common last names (sample)
        self.last_names = {
            "smith",
            "johnson",
            "williams",
            "brown",
            "jones",
            "garcia",
            "miller",
            "davis",
            "rodriguez",
            "martinez",
            "hernandez",
            "lopez",
            "gonzalez",
            "wilson",
            "anderson",
        }

    def detect(self, text: str) -> List[PIIEntity]:
        """Detect PII using dictionary matching"""
        entities = []
        words = text.split()

        # Check for name patterns
        for i in range(len(words) - 1):
            word1 = words[i].lower().strip(".,!?;:")
            word2 = words[i + 1].lower().strip(".,!?;:")

            # Check if it's a first name + last name pattern
            if word1 in self.first_names and word2 in self.last_names:
                # Find the original text position
                pattern = f"{words[i]} {words[i+1]}"
                match = re.search(re.escape(pattern), text, re.IGNORECASE)

                if match:
                    entity = PIIEntity(
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        pii_type="name",
                        confidence=0.7,
                        context=text[max(0, match.start() - 20): match.end() + 20],
                    )
                    entities.append(entity)

        # Check for PII keywords in context
        for pii_type, keywords in self.pii_keywords.items():
            for keyword in keywords:
                if keyword in text.lower():
                    # Look for potential PII near the keyword
                    keyword_pos = text.lower().find(keyword)
                    if keyword_pos != -1:
                        # Look in a window around the keyword
                        start = max(0, keyword_pos - 50)
                        end = min(len(text), keyword_pos + len(keyword) + 50)
                        window = text[start:end]

                        # Try to find specific patterns in this window
                        if pii_type == "email":
                            email_match = re.search(
                                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                                window,
                            )
                            if email_match:
                                entity = PIIEntity(
                                    text=email_match.group(),
                                    start=start + email_match.start(),
                                    end=start + email_match.end(),
                                    pii_type="email",
                                    confidence=0.8,
                                    context=window,
                                )
                                entities.append(entity)

        return entities


class ContextualDetector:
    """Contextual rules detector"""

    def __init__(self) -> None:
        self.contextual_rules = {
            "email": {
                "indicators": ["my email", "email me", "contact me at", "reach me at"],
                "boosters": ["personal", "private", "confidential"],
                "reducers": ["example", "demo", "test", "sample", "fake"],
            },
            "phone": {
                "indicators": ["my phone", "call me", "my number", "contact me"],
                "boosters": ["personal", "private", "mobile", "cell"],
                "reducers": ["example", "demo", "test", "sample"],
            },
            "name": {
                "indicators": ["my name is", "i am", "call me"],
                "boosters": ["real name", "actual name"],
                "reducers": ["example", "demo", "test", "sample", "placeholder"],
            },
        }

    def detect(self, text: str) -> List[PIIEntity]:
        """Detect PII using contextual rules"""
        entities = []

        for pii_type, rules in self.contextual_rules.items():
            for indicator in rules["indicators"]:
                if indicator in text.lower():
                    # Look for PII patterns near the indicator
                    indicator_pos = text.lower().find(indicator)
                    if indicator_pos != -1:
                        # Search in a window after the indicator
                        start = indicator_pos + len(indicator)
                        end = min(len(text), start + 100)
                        window = text[start:end]

                        # Try to find specific patterns
                        if pii_type == "email":
                            email_match = re.search(
                                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                                window,
                            )
                            if email_match:
                                confidence = 0.8

                                # Apply contextual adjustments
                                for booster in rules["boosters"]:
                                    if booster in window.lower():
                                        confidence += 0.1

                                for reducer in rules["reducers"]:
                                    if reducer in window.lower():
                                        confidence -= 0.2

                                entity = PIIEntity(
                                    text=email_match.group(),
                                    start=start + email_match.start(),
                                    end=start + email_match.end(),
                                    pii_type="email",
                                    confidence=min(1.0, max(0.0, confidence)),
                                    context=window,
                                )
                                entities.append(entity)

        return entities
