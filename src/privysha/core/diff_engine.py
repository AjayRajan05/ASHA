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

"""
Transparent Diff Engine for PrivySHA

Provides complete explainability of all transformations:
- Token-level diff
- Semantic diff (optional later)
- Change attribution
- Confidence scoring

Every transformation is explainable and developers can trust the system.
"""

import difflib
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class ChangeType(Enum):
    """Types of changes in the diff."""

    REMOVAL = "removal"
    ADDITION = "addition"
    MODIFICATION = "modification"
    MASKING = "masking"
    OPTIMIZATION = "optimization"
    SECURITY = "security"


@dataclass
class DiffChange:
    """Individual change in the diff."""

    change_type: ChangeType
    original: str
    modified: str
    position: Tuple[int, int]  # (start, end)
    confidence: float
    reason: str
    category: str  # "pii", "optimization", "security", etc.


@dataclass
class DiffResult:
    """Complete diff result with analysis."""

    original: str
    modified: str
    changes: List[DiffChange]
    token_reduction: int
    confidence_score: float
    processing_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original": self.original,
            "modified": self.modified,
            "changes": [
                {
                    "type": change.change_type.value,
                    "original": change.original,
                    "modified": change.modified,
                    "position": change.position,
                    "confidence": change.confidence,
                    "reason": change.reason,
                    "category": change.category,
                }
                for change in self.changes
            ],
            "token_reduction": self.token_reduction,
            "confidence_score": self.confidence_score,
            "processing_summary": self.processing_summary,
        }


class DiffEngine:
    """
    Transparent diff engine for explainable transformations.

    This engine makes every change visible and explainable,
    building developer trust in the system.
    """

    def __init__(self, enable_semantic: bool = False) -> None:
        """
        Initialize diff engine.

        Args:
            enable_semantic: Enable semantic analysis (future feature)
        """
        self.enable_semantic = enable_semantic
        self.pii_patterns = self._init_pii_patterns()
        self.optimization_patterns = self._init_optimization_patterns()

    def _init_pii_patterns(self) -> List[Dict[str, Any]]:
        """Initialize PII masking patterns for diff detection."""
        return [
            {
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "type": "email",
                "mask_prefix": "[EMAIL_HASH]",
            },
            {
                "pattern": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                "type": "phone",
                "mask_prefix": "[PHONE_HASH]",
            },
            {
                "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
                "type": "ssn",
                "mask_prefix": "[SSN_HASH]",
            },
            {
                "pattern": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                "type": "credit_card",
                "mask_prefix": "[CARD_HASH]",
            },
            {
                "pattern": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
                "type": "ip_address",
                "mask_prefix": "[IP_HASH]",
            },
        ]

    def _init_optimization_patterns(self) -> List[Dict[str, Any]]:
        """Initialize optimization patterns for diff detection."""
        return [
            {
                "pattern": r"\b(very|really|quite|rather|somewhat|extremely)\s+",
                "type": "filler_removal",
                "reason": "Removed filler word for conciseness",
            },
            {
                "pattern": r"\b(I would like to|I am looking for)\s+",
                "type": "phrase_optimization",
                "reason": "Simplified conversational phrase",
            },
            {
                "pattern": r"\s+",
                "type": "whitespace_optimization",
                "reason": "Normalized whitespace",
            },
            {
                "pattern": r"\n{3,}",
                "type": "newline_optimization",
                "reason": "Reduced excessive newlines",
            },
        ]

    def analyze_diff(
        self, original: str, modified: str, context: Optional[Dict[str, Any]] = None
    ) -> DiffResult:
        """
        Analyze differences between original and modified text.

        Args:
            original: Original text
            modified: Modified text
            context: Processing context for better analysis

        Returns:
            Detailed diff result with all changes explained
        """
        if original == modified:
            return DiffResult(
                original=original,
                modified=modified,
                changes=[],
                token_reduction=0,
                confidence_score=1.0,
                processing_summary={"status": "no_changes"},
            )

        # Detect changes
        changes = self._detect_changes(original, modified, context)

        # Calculate metrics
        token_reduction = self._calculate_token_reduction(original, modified)
        confidence_score = self._calculate_confidence_score(changes)

        # Generate processing summary
        processing_summary = self._generate_processing_summary(
            changes, token_reduction)

        return DiffResult(
            original=original,
            modified=modified,
            changes=changes,
            token_reduction=token_reduction,
            confidence_score=confidence_score,
            processing_summary=processing_summary,
        )

    def _detect_changes(
        self, original: str, modified: str, context: Optional[Dict[str, Any]]
    ) -> List[DiffChange]:
        """Detect and categorize all changes."""
        changes = []

        # Detect PII masking changes
        pii_changes = self._detect_pii_changes(original, modified)
        changes.extend(pii_changes)

        # Detect optimization changes
        opt_changes = self._detect_optimization_changes(original, modified)
        changes.extend(opt_changes)

        # Detect security-related changes
        security_changes = self._detect_security_changes(original, modified)
        changes.extend(security_changes)

        # Detect remaining changes with generic diff
        generic_changes = self._detect_generic_changes(
            original, modified, changes)
        changes.extend(generic_changes)

        # Sort by position
        changes.sort(key=lambda x: x.position[0])

        return changes

    def _detect_pii_changes(self, original: str, modified: str) -> List[DiffChange]:
        """Detect PII masking changes."""
        changes = []

        for pattern_info in self.pii_patterns:
            pattern = pattern_info["pattern"]
            pii_type = pattern_info["type"]
            mask_prefix = pattern_info["mask_prefix"]

            # Find all matches in original
            original_matches = list(re.finditer(pattern, original))

            for match in original_matches:
                original_text = match.group()
                start, end = match.span()

                # Look for corresponding masked version in modified
                masked_pattern = re.escape(mask_prefix) + r"_[a-f0-9]{8}"
                masked_match = re.search(
                    masked_pattern, modified[start: end + 20])

                if masked_match:
                    changes.append(
                        DiffChange(
                            change_type=ChangeType.MASKING,
                            original=original_text,
                            modified=masked_match.group(),
                            position=(start, end),
                            confidence=0.95,
                            reason=f"Masked {pii_type} for privacy protection",
                            category="pii",
                        )
                    )

        return changes

    def _detect_optimization_changes(
        self, original: str, modified: str
    ) -> List[DiffChange]:
        """Detect optimization-related changes."""
        changes = []

        for pattern_info in self.optimization_patterns:
            pattern = pattern_info["pattern"]
            opt_type = pattern_info["type"]
            reason = pattern_info["reason"]

            # Find matches in original
            original_matches = list(re.finditer(pattern, original))

            for match in original_matches:
                original_text = match.group()
                start, end = match.span()

                # Check if this part was changed in modified
                modified_segment = modified[start:end] if end < len(
                    modified) else ""

                if modified_segment != original_text:
                    changes.append(
                        DiffChange(
                            change_type=ChangeType.OPTIMIZATION,
                            original=original_text,
                            modified=modified_segment,
                            position=(start, end),
                            confidence=0.8,
                            reason=reason,
                            category="optimization",
                        )
                    )

        return changes

    def _detect_security_changes(
        self, original: str, modified: str
    ) -> List[DiffChange]:
        """Detect security-related changes (injection blocking, etc.)."""
        changes = []

        # Common security neutralization patterns
        security_patterns = [
            {
                "pattern": r"(?i)(drop\s+table|delete\s+from|insert\s+into)",
                "replacement": "[SQL_COMMAND_REMOVED]",
                "reason": "Removed potentially harmful SQL command",
            },
            {
                "pattern": r"(?i)(ignore\s+(all|previous)\s+instructions)",
                "replacement": "[INSTRUCTION_IGNORED]",
                "reason": "Blocked prompt injection attempt",
            },
            {
                "pattern": r"(?i)(jailbreak|uncensored|unrestricted)",
                "replacement": "[JAILBREAK_BLOCKED]",
                "reason": "Blocked jailbreak attempt",
            },
        ]

        for pattern_info in security_patterns:
            pattern = pattern_info["pattern"]
            replacement = pattern_info["replacement"]
            reason = pattern_info["reason"]

            # Find matches in original
            original_matches = list(re.finditer(pattern, original))

            for match in original_matches:
                original_text = match.group()
                start, end = match.span()

                # Check if it was replaced in modified
                if replacement in modified:
                    changes.append(
                        DiffChange(
                            change_type=ChangeType.MODIFICATION,
                            original=original_text,
                            modified=replacement,
                            position=(start, end),
                            confidence=0.9,
                            reason=reason,
                            category="security",
                        )
                    )

        return changes

    def _detect_generic_changes(
        self, original: str, modified: str, existing_changes: List[DiffChange]
    ) -> List[DiffChange]:
        """Detect remaining changes using generic diff algorithm."""
        changes = []

        # Create unified diff
        diff_lines = list(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                modified.splitlines(keepends=True),
                fromfile="original",
                tofile="modified",
                lineterm="",
            )
        )

        if not diff_lines:
            return changes

        # Parse diff lines to extract changes
        current_line = 0
        for line in diff_lines:
            if line.startswith("@@"):
                # Parse line numbers
                match = re.search(
                    r"-(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))?", line)
                if match:
                    current_line = int(match.group(3)) - 1
            elif line.startswith("-"):
                # Removed line
                changes.append(
                    DiffChange(
                        change_type=ChangeType.REMOVAL,
                        original=line[1:],
                        modified="",
                        position=(current_line, current_line + 1),
                        confidence=0.7,
                        reason="Line removed during processing",
                        category="generic",
                    )
                )
            elif line.startswith("+"):
                # Added line
                changes.append(
                    DiffChange(
                        change_type=ChangeType.ADDITION,
                        original="",
                        modified=line[1:],
                        position=(current_line, current_line + 1),
                        confidence=0.7,
                        reason="Line added during processing",
                        category="generic",
                    )
                )
                current_line += 1

        return changes

    def _calculate_token_reduction(self, original: str, modified: str) -> int:
        """Calculate token reduction between original and modified."""
        original_tokens = len(original.split())
        modified_tokens = len(modified.split())
        return original_tokens - modified_tokens

    def _calculate_confidence_score(self, changes: List[DiffChange]) -> float:
        """Calculate overall confidence score for all changes."""
        if not changes:
            return 1.0

        # Weight changes by type and confidence
        type_weights = {
            ChangeType.MASKING: 0.95,
            ChangeType.SECURITY: 0.9,
            ChangeType.OPTIMIZATION: 0.8,
            ChangeType.MODIFICATION: 0.7,
            ChangeType.REMOVAL: 0.6,
            ChangeType.ADDITION: 0.6,
        }

        weighted_sum = 0.0
        total_weight = 0.0

        for change in changes:
            weight = type_weights.get(change.change_type, 0.5)
            weighted_sum += change.confidence * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _generate_processing_summary(
        self, changes: List[DiffChange], token_reduction: int
    ) -> Dict[str, Any]:
        """Generate summary of processing changes."""
        # Count changes by category
        category_counts = {}
        for change in changes:
            category_counts[change.category] = (
                category_counts.get(change.category, 0) + 1
            )

        # Count changes by type
        type_counts = {}
        for change in changes:
            type_counts[change.change_type.value] = (
                type_counts.get(change.change_type.value, 0) + 1
            )

        return {
            "total_changes": len(changes),
            "token_reduction": token_reduction,
            "categories": category_counts,
            "change_types": type_counts,
            "has_security_changes": category_counts.get("security", 0) > 0,
            "has_pii_changes": category_counts.get("pii", 0) > 0,
            "has_optimization_changes": category_counts.get("optimization", 0) > 0,
            "processing_trustworthy": all(
                change.confidence >= 0.7 for change in changes
            ),
        }

    def format_diff(
        self, diff_result: DiffResult, format_type: str = "readable"
    ) -> str:
        """
        Format diff result for display.

        Args:
            diff_result: Diff result to format
            format_type: Format type ("readable", "json", "compact")

        Returns:
            Formatted diff string
        """
        if format_type == "json":
            return json.dumps(diff_result.to_dict(), indent=2)

        elif format_type == "compact":
            lines = [f"Changes: {len(diff_result.changes)}"]
            lines.append(f"Token reduction: {diff_result.token_reduction}")
            lines.append(f"Confidence: {diff_result.confidence_score:.2f}")
            return "\n".join(lines)

        else:  # readable format
            lines = []
            lines.append("=== PRIVYSHA DIFF ANALYSIS ===")
            lines.append(f"Original:  {diff_result.original[:50]}...")
            lines.append(f"Modified:  {diff_result.modified[:50]}...")
            lines.append("")
            lines.append(
                f"Summary: {len(diff_result.changes)} changes, "
                f"{diff_result.token_reduction} tokens reduced, "
                f"{diff_result.confidence_score:.2f} confidence"
            )
            lines.append("")

            if diff_result.changes:
                lines.append("DETAILED CHANGES:")
                for i, change in enumerate(diff_result.changes, 1):
                    lines.append(
                        f"{i}. [{change.category.upper()}] {change.change_type.value}"
                    )
                    lines.append(f"   Reason: {change.reason}")
                    lines.append(f"   Confidence: {change.confidence:.2f}")
                    if change.original:
                        lines.append(f"   Original: '{change.original}'")
                    if change.modified:
                        lines.append(f"   Modified: '{change.modified}'")
                    lines.append("")

            return "\n".join(lines)


# Convenience function for quick diff analysis
def analyze_changes(
    original: str, modified: str, context: Optional[Dict[str, Any]] = None
) -> DiffResult:
    """
    Quick function to analyze changes between two texts.

    Args:
        original: Original text
        modified: Modified text
        context: Processing context

    Returns:
        Diff analysis result
    """
    engine = DiffEngine()
    return engine.analyze_diff(original, modified, context)


def format_diff_summary(original: str, modified: str) -> str:
    """
    Get a quick, human-readable diff summary.

    Args:
        original: Original text
        modified: Modified text

    Returns:
        Formatted diff summary
    """
    diff_result = analyze_changes(original, modified)
    engine = DiffEngine()
    return engine.format_diff(diff_result, "readable")
