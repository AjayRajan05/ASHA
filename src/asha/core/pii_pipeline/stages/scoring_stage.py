"""
Stage 3: Confidence Scoring Engine - Calculate and adjust entity confidence scores
"""

import re
import math
from typing import Dict, Any, List, cast
from .base_stage import BaseStage, StageResult, PIIContext, PIIEntity


class ScoringStage(BaseStage):
    """
    Confidence Scoring Stage - Calculates and adjusts confidence scores for detected entities.

    This stage handles:
    - Base confidence calculation
    - Pattern-based confidence adjustment
    - Contextual confidence boosting
    - Confidence normalization
    - Threshold-based filtering
    """

    def __init__(self) -> None:
        super().__init__("scoring")

        # Scoring configuration
        self.scoring_config = {
            "base_confidence_weights": {
                "regex": 0.9,
                "heuristic": 0.6,
                "dictionary": 0.7,
                "contextual": 0.8,
            },
            "context_boosters": {
                "email": {
                    "personal_words": ["my", "personal", "private", "contact"],
                    "context_words": ["email", "mail", "reach", "contact"],
                    "boost_amount": 0.15,
                },
                "phone": {
                    "personal_words": ["my", "personal", "mobile", "cell"],
                    "context_words": ["phone", "call", "number", "contact"],
                    "boost_amount": 0.15,
                },
                "name": {
                    "personal_words": ["my", "name", "called", "known"],
                    "context_words": ["name", "call", "addressed"],
                    "boost_amount": 0.1,
                },
                "address": {
                    "personal_words": ["my", "live", "home", "address"],
                    "context_words": ["address", "live", "located", "street"],
                    "boost_amount": 0.1,
                },
            },
            "confidence_reducers": {
                "example_words": [
                    "example",
                    "demo",
                    "test",
                    "sample",
                    "fake",
                    "placeholder",
                ],
                "reduction_amount": 0.25,
            },
            "thresholds": {
                "high_confidence": 0.85,
                "medium_confidence": 0.6,
                "low_confidence": 0.3,
                "minimum_confidence": 0.2,
            },
        }

    def execute(self, context: PIIContext) -> StageResult:
        """
        Calculate and adjust confidence scores for entities.

        Args:
            context: PII pipeline context

        Returns:
            StageResult with scored entities
        """
        entities = context.entities.copy()
        config = context.config.get("scoring", self.scoring_config)

        if not entities:
            return StageResult(
                success=True,
                stage_name=self.stage_name,
                execution_time_ms=0.0,
                entities=[],
                metadata={"no_entities": True},
            )

        # Step 1: Calculate base confidence scores
        entities = self._calculate_base_confidence(entities, config)

        # Step 2: Apply contextual adjustments
        entities = self._apply_contextual_adjustments(
            entities, context, config)

        # Step 3: Normalize confidence scores
        entities = self._normalize_confidence(entities, config)

        # Step 4: Apply threshold filtering
        entities = self._apply_threshold_filtering(entities, config)

        # Step 5: Sort by confidence and position
        entities.sort(key=lambda e: (-e.confidence, e.start, e.end))

        self.add_debug_info(
            context,
            "Confidence scoring completed",
            {
                "total_entities": len(context.entities),
                "scored_entities": len(entities),
                "filtered_entities": len(context.entities) - len(entities),
                "confidence_distribution": self._get_confidence_distribution(entities),
            },
        )

        return StageResult(
            success=True,
            stage_name=self.stage_name,
            execution_time_ms=0.0,
            entities=entities,
            metadata={
                "total_entities": len(context.entities),
                "scored_entities": len(entities),
                "filtered_entities": len(context.entities) - len(entities),
                "confidence_distribution": self._get_confidence_distribution(entities),
                "scoring_stats": self._get_scoring_stats(entities),
            },
        )

    def _calculate_base_confidence(
        self, entities: List[PIIEntity], config: Dict[str, Any]
    ) -> List[PIIEntity]:
        """Calculate base confidence scores based on detection method"""
        weights = config.get(
            "base_confidence_weights", self.scoring_config["base_confidence_weights"]
        )

        for entity in entities:
            # For high-sensitivity PII that already has high confidence, preserve it
            HIGH_SENSITIVITY_TYPES = {"ssn", "credit_card", "api_key"}
            if entity.pii_type in HIGH_SENSITIVITY_TYPES and entity.confidence >= 0.85:
                entity.metadata["detection_method"] = self._determine_detection_method(entity)
                entity.metadata["base_confidence"] = entity.confidence
                continue

            # Determine detection method from metadata or patterns
            detection_method = self._determine_detection_method(entity)
            base_confidence = weights.get(detection_method, 0.5)

            # Apply pattern-specific adjustments
            pattern_confidence = self._calculate_pattern_confidence(entity)

            # Combine base confidence with pattern confidence
            entity.confidence = (base_confidence + pattern_confidence) / 2

            # Store detection method in metadata
            entity.metadata["detection_method"] = detection_method
            entity.metadata["base_confidence"] = entity.confidence

        return entities

    def _determine_detection_method(self, entity: PIIEntity) -> str:
        """Determine the detection method for an entity"""
        # Check entity metadata first
        if "detection_method" in entity.metadata:
            return cast(str, entity.metadata["detection_method"])

        # Determine based on entity characteristics
        text = entity.text.lower()

        # Regex patterns (high precision)
        if any(char in entity.text for char in ["@", ".", "-", "(", ")"]):
            if "@" in entity.text and "." in entity.text:
                return "regex"  # Email
            elif re.match(r"\d{3}[-.\s]\d{3}[-.\s]\d{4}", entity.text):
                return "regex"  # Phone
            elif re.match(r"\d{3}[-.\s]\d{2}[-.\s]\d{4}", entity.text):
                return "regex"  # SSN
            elif re.match(r"\d{4}[-.\s]\d{4}[-.\s]\d{4}[-.\s]\d{4}", entity.text):
                return "regex"  # Credit card

        # Dictionary-based detection
        if entity.pii_type == "name" and " " in entity.text:
            return "dictionary"

        # Heuristic patterns
        if entity.pii_type in ["address", "zip_code", "date_of_birth"]:
            return "heuristic"

        # Default to contextual
        return "contextual"

    def _calculate_pattern_confidence(self, entity: PIIEntity) -> float:
        """Calculate confidence based on pattern characteristics"""
        confidence = 0.5  # Base pattern confidence
        text = entity.text

        # Email-specific patterns
        if entity.pii_type == "email":
            if "@" in text and "." in text:
                # Check for valid email structure
                local, domain = text.split("@", 1)
                if "." in domain and len(domain.split(".")) >= 2:
                    confidence += 0.2
                if len(local) > 1 and len(domain) > 3:
                    confidence += 0.1

        # Phone-specific patterns
        elif entity.pii_type == "phone":
            if re.match(r"\d{3}[-.\s]\d{3}[-.\s]\d{4}", text):
                confidence += 0.2
            if "(" in text and ")" in text:
                confidence += 0.1

        # Name-specific patterns
        elif entity.pii_type == "name":
            words = text.split()
            if len(words) == 2 and all(word[0].isupper() for word in words):
                confidence += 0.1

        # Address-specific patterns
        elif entity.pii_type == "address":
            if any(
                word in text.lower()
                for word in ["street", "st", "avenue", "ave", "road", "rd"]
            ):
                confidence += 0.1
            if re.match(r"\d+\s+", text):
                confidence += 0.1

        return min(1.0, confidence)

    def _apply_contextual_adjustments(
        self, entities: List[PIIEntity], context: PIIContext, config: Dict[str, Any]
    ) -> List[PIIEntity]:
        """Apply contextual confidence adjustments"""
        boosters = config.get(
            "context_boosters", self.scoring_config["context_boosters"]
        )
        reducers = config.get(
            "confidence_reducers", self.scoring_config["confidence_reducers"]
        )

        full_text = context.current_text.lower()

        for entity in entities:
            original_confidence = entity.confidence

            # Apply contextual boosters
            if entity.pii_type in boosters:
                booster_config = boosters[entity.pii_type]

                # Check for personal words
                for word in booster_config.get("personal_words", []):
                    if word in full_text:
                        entity.confidence += booster_config.get(
                            "boost_amount", 0.1
                        ) / len(booster_config.get("personal_words", []))

                # Check for context words near the entity
                entity_window = self._get_entity_context(
                    entity, context, 50).lower()
                for word in booster_config.get("context_words", []):
                    if word in entity_window:
                        entity.confidence += booster_config.get(
                            "boost_amount", 0.1
                        ) / len(booster_config.get("context_words", []))

            # Apply confidence reducers
            for word in reducers.get("example_words", []):
                if word in full_text:
                    entity.confidence -= reducers.get("reduction_amount", 0.25) / len(
                        reducers.get("example_words", [])
                    )

            # Ensure confidence stays within bounds
            entity.confidence = max(0.0, min(1.0, entity.confidence))

            # Store adjustment information
            entity.metadata["contextual_adjustment"] = (
                entity.confidence - original_confidence
            )

        return entities

    def _get_entity_context(
        self, entity: PIIEntity, context: PIIContext, window_size: int
    ) -> str:
        """Get context window around an entity"""
        start = max(0, entity.start - window_size)
        end = min(len(context.current_text), entity.end + window_size)
        return context.current_text[start:end]

    def _normalize_confidence(
        self, entities: List[PIIEntity], config: Dict[str, Any]
    ) -> List[PIIEntity]:
        """Normalize confidence scores across entities"""
        if not entities:
            return entities

        # Calculate confidence statistics
        confidences = [e.confidence for e in entities]
        mean_confidence = sum(confidences) / len(confidences)

        # Apply sigmoid-like normalization to spread scores
        for entity in entities:
            # Normalize around mean
            normalized = (entity.confidence - mean_confidence) * 2 + 0.5

            # Apply sigmoid function
            sigmoid_normalized = 1 / (1 + math.exp(-10 * (normalized - 0.5)))

            # Blend original and normalized
            entity.confidence = 0.7 * entity.confidence + 0.3 * sigmoid_normalized

            # Ensure bounds
            entity.confidence = max(0.0, min(1.0, entity.confidence))

            entity.metadata["normalized_confidence"] = entity.confidence

        return entities

    def _apply_threshold_filtering(
        self, entities: List[PIIEntity], config: Dict[str, Any]
    ) -> List[PIIEntity]:
        """Apply confidence threshold filtering"""
        thresholds = config.get(
            "thresholds", self.scoring_config["thresholds"])
        min_confidence = thresholds.get("minimum_confidence", 0.2)

        filtered_entities = []
        filtered_count = 0

        for entity in entities:
            from ...security.patterns import is_example_email

            if entity.pii_type == "email" and is_example_email(entity.text):
                filtered_count += 1
                continue

            if entity.confidence >= min_confidence:
                # Add threshold level to metadata
                if entity.confidence >= thresholds.get("high_confidence", 0.85):
                    entity.metadata["confidence_level"] = "high"
                elif entity.confidence >= thresholds.get("medium_confidence", 0.6):
                    entity.metadata["confidence_level"] = "medium"
                else:
                    entity.metadata["confidence_level"] = "low"

                filtered_entities.append(entity)
            else:
                filtered_count += 1

        return filtered_entities

    def _get_confidence_distribution(self, entities: List[PIIEntity]) -> Dict[str, int]:
        """Get confidence score distribution"""
        distribution = {
            "high": 0,  # >= 0.85
            "medium": 0,  # 0.6 - 0.85
            "low": 0,  # 0.3 - 0.6
            "very_low": 0,  # < 0.3
        }

        for entity in entities:
            if entity.confidence >= 0.85:
                distribution["high"] += 1
            elif entity.confidence >= 0.6:
                distribution["medium"] += 1
            elif entity.confidence >= 0.3:
                distribution["low"] += 1
            else:
                distribution["very_low"] += 1

        return distribution

    def _get_scoring_stats(self, entities: List[PIIEntity]) -> Dict[str, Any]:
        """Get scoring statistics"""
        if not entities:
            return {}

        confidences = [e.confidence for e in entities]

        return {
            "average_confidence": sum(confidences) / len(confidences),
            "max_confidence": max(confidences),
            "min_confidence": min(confidences),
            "confidence_std": self._calculate_std(confidences),
            "entities_by_type": self._count_entities_by_type(entities),
        }

    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _count_entities_by_type(self, entities: List[PIIEntity]) -> Dict[str, int]:
        """Count entities by type"""
        counts: Dict[str, int] = {}
        for entity in entities:
            counts[entity.pii_type] = counts.get(entity.pii_type, 0) + 1
        return counts

    def validate_input(self, context: PIIContext) -> bool:
        """Validate input for scoring stage"""
        entities: object = context.entities
        if not entities:
            return True  # No entities is valid

        if not isinstance(entities, list):
            return False

        for entity in entities:
            if not isinstance(entity, PIIEntity):
                return False

        return True

    def fallback(self, context: PIIContext) -> StageResult:
        """Fallback scoring - basic confidence assignment"""
        entities = context.entities.copy()

        for entity in entities:
            # Basic confidence based on entity type
            type_confidence = {
                "email": 0.8,
                "phone": 0.7,
                "ssn": 0.9,
                "credit_card": 0.9,
                "name": 0.6,
                "address": 0.5,
            }

            entity.confidence = type_confidence.get(entity.pii_type, 0.5)
            entity.metadata["fallback_scoring"] = True

        self.add_debug_info(
            context,
            "Scoring fallback used",
            {
                "reason": "main_scoring_failed",
                "fallback_type": "basic_confidence",
                "entities_processed": len(entities),
            },
        )

        return StageResult(
            success=True,
            stage_name=self.stage_name,
            execution_time_ms=0.0,
            entities=entities,
            metadata={
                "fallback_used": True,
                "fallback_type": "basic_confidence",
                "entities_processed": len(entities),
            },
        )
