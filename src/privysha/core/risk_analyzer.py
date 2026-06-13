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
Enhanced risk analyzer with intelligent AUTO mode decision logic.

This provides smarter mode selection beyond basic mapping.
"""

import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class RiskAssessment:
    """Basic risk assessment for prompt analysis."""

    score: float
    confidence: float
    recommended_mode: str
    reasoning: str
    level: str = "medium"
    detected_pii_types: List[str] = field(default_factory=list)
    injection_indicators: List[str] = field(default_factory=list)


class RiskAnalyzer:
    """Basic risk analyzer for prompt assessment."""

    def analyze(self, prompt: str) -> RiskAssessment:
        """Analyze prompt risk and return assessment."""
        # Simple risk analysis based on prompt content
        risk_score = 0.5
        confidence = 0.8
        recommended_mode = "balanced"
        reasoning = "Standard prompt analysis"
        level = "medium"
        detected_pii_types: List[str] = []
        injection_indicators: List[str] = []

        return RiskAssessment(
            score=risk_score,
            confidence=confidence,
            recommended_mode=recommended_mode,
            reasoning=reasoning,
            level=level,
            detected_pii_types=detected_pii_types,
            injection_indicators=injection_indicators,
        )


@dataclass
class EnhancedRiskAssessment(RiskAssessment):
    """Enhanced risk assessment with additional context analysis."""

    prompt_length: int = 0
    business_context_score: float = 0.0
    complexity_score: float = 0.0
    contextual_factors: Dict[str, Any] = field(default_factory=dict)
    auto_mode_reasoning: str = ""
    confidence_boost: float = 0.0


class EnhancedRiskAnalyzer(RiskAnalyzer):
    """
    Enhanced risk analyzer with intelligent AUTO mode decision logic.

    Provides smarter mode selection based on:
    - Prompt complexity analysis
    - Business vs personal context detection
    - Multi-factor risk assessment
    - Adaptive threshold adjustment
    """

    def __init__(self) -> None:
        super().__init__()
        # Enhanced patterns for better detection
        self.business_keywords = [
            "customer",
            "client",
            "business",
            "professional",
            "company",
            "organization",
            "support",
            "sales",
            "service",
            "product",
            "market",
            "industry",
            "enterprise",
            "corporate",
            "commercial",
        ]

        self.personal_keywords = [
            "personal",
            "private",
            "individual",
            "my",
            "mine",
            "own",
            "home",
            "family",
            "personal",
            "private",
            "confidential",
        ]

        self.complexity_indicators = [
            r"\b\d+\s+words?\b",  # Word count
            r"```",  # Code blocks
            r"\{.*\}",  # JSON structures
            r"#{1,6}\s+",  # Markdown headers
            r"analyze.*and.*analyze",  # Repetitive tasks
            # Redundant explanations
            r"\b(explain|describe|detail)\b.*\b(explain|describe|detail)\b",
        ]

        self.contextual_weights = {
            "pii_weight": 0.4,
            "injection_weight": 0.3,
            "complexity_weight": 0.2,
            "context_weight": 0.1,
        }

    def analyze(self, prompt: str) -> EnhancedRiskAssessment:
        """
        Enhanced risk analysis with intelligent mode recommendation.

        Args:
            prompt: Input prompt to analyze

        Returns:
            EnhancedRiskAssessment with detailed context and smart mode recommendation
        """
        # Base risk analysis
        base_assessment = super().analyze(prompt)

        # Enhanced context analysis
        prompt_length = len(prompt)
        business_context_score = self._analyze_business_context(prompt)
        complexity_score = self._analyze_complexity_enhanced(prompt)
        contextual_factors = self._analyze_contextual_factors(prompt)

        # Enhanced mode recommendation
        recommended_mode, reasoning = self._intelligent_mode_recommendation(
            base_assessment.level,
            base_assessment.detected_pii_types,
            base_assessment.injection_indicators,
            prompt_length,
            business_context_score,
            complexity_score,
            contextual_factors,
        )

        # Calculate confidence boost
        confidence_boost = self._calculate_confidence_boost(
            base_assessment.detected_pii_types,
            base_assessment.injection_indicators,
            business_context_score,
            complexity_score,
        )

        return EnhancedRiskAssessment(
            score=base_assessment.score,
            confidence=base_assessment.confidence + confidence_boost,
            recommended_mode=recommended_mode,
            reasoning=base_assessment.reasoning,
            level=base_assessment.level,
            detected_pii_types=base_assessment.detected_pii_types,
            injection_indicators=base_assessment.injection_indicators,
            prompt_length=prompt_length,
            business_context_score=business_context_score,
            complexity_score=complexity_score,
            contextual_factors=contextual_factors,
            auto_mode_reasoning=reasoning,
        )

    def _analyze_business_context(self, prompt: str) -> float:
        """
        Analyze business vs personal context of the prompt.

        Returns:
            Business context score (0.0-1.0)
        """
        prompt_lower = prompt.lower()

        business_count = sum(
            1 for keyword in self.business_keywords if keyword in prompt_lower
        )
        personal_count = sum(
            1 for keyword in self.personal_keywords if keyword in prompt_lower
        )

        total_indicators = business_count + personal_count

        if total_indicators == 0:
            return 0.5  # Neutral

        business_ratio = business_count / total_indicators
        return business_ratio

    def _analyze_complexity_enhanced(self, prompt: str) -> float:
        """
        Enhanced complexity analysis with multiple factors.

        Returns:
            Complexity score (0.0-1.0)
        """
        complexity_score = 0.0

        # Word count complexity
        words = prompt.split()
        word_count = len(words)

        if word_count > 200:
            complexity_score += 0.4  # Very long
        elif word_count > 100:
            complexity_score += 0.3  # Long
        elif word_count > 50:
            complexity_score += 0.2  # Medium
        else:
            complexity_score += 0.1  # Short

        # Structural complexity indicators
        for pattern in self.complexity_indicators:
            if re.search(pattern, prompt, re.IGNORECASE):
                complexity_score += 0.2

        # Cap at 1.0
        return min(complexity_score, 1.0)

    def _analyze_contextual_factors(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze contextual factors for risk assessment.

        Returns:
            Dictionary of contextual factors
        """
        factors = {}

        # Time-sensitive indicators
        time_sensitive = any(
            keyword in prompt.lower()
            for keyword in ["urgent", "asap", "immediately", "emergency", "critical"]
        )
        factors["time_sensitive"] = time_sensitive

        # Compliance indicators
        compliance_keywords = ["gdpr", "hipaa",
                               "pci", "sox", "compliance", "audit"]
        compliance_mentioned = any(
            keyword in prompt.lower() for keyword in compliance_keywords
        )
        factors["compliance_context"] = compliance_mentioned

        # Multi-tenancy indicators
        multi_tenant_keywords = [
            "tenant", "organization", "company", "department"]
        multi_tenant_context = any(
            keyword in prompt.lower() for keyword in multi_tenant_keywords
        )
        factors["multi_tenant_context"] = multi_tenant_context

        # Data sensitivity indicators
        data_sensitive = any(
            keyword in prompt.lower()
            for keyword in ["sensitive", "confidential", "proprietary", "secret"]
        )
        factors["data_sensitivity"] = data_sensitive

        return factors

    def _intelligent_mode_recommendation(
        self,
        risk_level: str,
        pii_types: List[str],
        injection_indicators: List[str],
        prompt_length: int,
        business_context_score: float,
        complexity_score: float,
        contextual_factors: Dict[str, Any],
    ) -> Tuple[Any, str]:
        """
        Intelligent mode recommendation based on comprehensive analysis.

        Args:
            risk_level: Base risk level
            pii_types: Detected PII types
            injection_indicators: Injection indicators
            prompt_length: Length of prompt
            business_context_score: Business context score
            complexity_score: Complexity score
            contextual_factors: Contextual factors

        Returns:
            Tuple of (recommended_mode, reasoning)
        """
        from ..core.modes import ProcessingMode

        # Critical threats always get STRICT mode
        if risk_level in ["critical"] or injection_indicators:
            return (
                ProcessingMode.STRICT,
                "Critical security threats detected - using STRICT mode for maximum protection",
            )

        # High complexity prompts get LITE mode (prioritize speed)
        if complexity_score > 0.7:
            return (
                ProcessingMode.LITE,
                "High prompt complexity detected - using LITE mode for performance",
            )

        # High PII risk gets STRICT mode
        if len(pii_types) >= 3:
            return (
                ProcessingMode.STRICT,
                "Multiple PII types detected - using STRICT mode for maximum privacy protection",
            )

        # Business context with moderate risk gets BALANCED mode
        if business_context_score > 0.6 and risk_level in ["medium"]:
            return (
                ProcessingMode.BALANCED,
                "Business context detected - using BALANCED mode for optimal protection/performance balance",
            )

        # Personal context with any risk gets STRICT mode
        if business_context_score < 0.4 and risk_level in ["medium", "high"]:
            return (
                ProcessingMode.STRICT,
                "Personal context detected - using STRICT mode for enhanced privacy protection",
            )

        # Short prompts with low risk get OFF mode
        if prompt_length < 30 and risk_level == "low":
            return (
                ProcessingMode.OFF,
                "Short low-risk prompt - using OFF mode for minimal processing",
            )

        # Time-sensitive gets LITE mode
        if contextual_factors.get("time_sensitive", False):
            return (
                ProcessingMode.LITE,
                "Time-sensitive request - using LITE mode for fast processing",
            )

        # Compliance context gets STRICT mode
        if contextual_factors.get("compliance_context", False):
            return (
                ProcessingMode.STRICT,
                "Compliance context detected - using STRICT mode for regulatory requirements",
            )

        # Default to BALANCED for moderate complexity/risk
        if complexity_score >= 0.5 or risk_level in ["medium", "high"]:
            return (
                ProcessingMode.BALANCED,
                "Moderate complexity/risk detected - using BALANCED mode for balanced approach",
            )

        # Low complexity/risk gets LITE mode
        return (
            ProcessingMode.LITE,
            "Low complexity/risk detected - using LITE mode for lightweight processing",
        )

    def _calculate_confidence_boost(
        self,
        pii_types: List[str],
        injection_indicators: List[str],
        business_context_score: float,
        complexity_score: float,
    ) -> float:
        """
        Calculate confidence boost based on multiple factors.

        Returns:
            Confidence boost (0.0-0.3)
        """
        boost = 0.0

        # Boost for multiple PII types
        if len(pii_types) >= 2:
            boost += 0.1

        # Boost for injection indicators
        if injection_indicators:
            boost += 0.15

        # Boost for business context
        if business_context_score > 0.7:
            boost += 0.05

        # Reduce boost for very high complexity (less confidence)
        if complexity_score > 0.8:
            boost -= 0.1

        return max(0.0, min(boost, 0.3))
