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
Semantic Token Optimizer - Phase 2 Core Differentiator

Preserves meaning while reducing tokens through:
- Intent Extraction: Core purpose identification
- Filler Removal: Eliminate redundant words/phrases
- Dependency Parsing: Preserve grammatical structure
- Intent Templates: Reconstruct optimized prompts

This beats simple text compression by maintaining LLM quality.
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

# Try to import NLP libraries
try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available, using rule-based optimization only")

try:
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available, using rule-based optimization only")


class OptimizationLevel(Enum):
    """Optimization aggressiveness levels."""

    CONSERVATIVE = "conservative"  # Preserve most meaning
    BALANCED = "balanced"  # Good balance
    AGGRESSIVE = "aggressive"  # Maximum reduction


@dataclass
class OptimizationResult:
    """Result of semantic optimization."""

    original_text: str
    optimized_text: str
    token_reduction: int
    token_reduction_percentage: float
    preserved_intent: str
    optimization_level: OptimizationLevel
    processing_time_ms: float
    changes_made: List[str]
    confidence_score: float


class IntentExtractor:
    """Extract core intent from prompts."""

    def __init__(self) -> None:
        """Initialize intent extractor."""
        self.intent_patterns = self._init_intent_patterns()
        self.action_keywords = self._init_action_keywords()
        self.nlp = None

        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print(
                    "Warning: spaCy model not found, install with: python -m spacy download en_core_web_sm"
                )

    def _init_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent pattern templates."""
        return {
            "analyze": [
                r"(?i)\b(analyze|examine|investigate|study|review|inspect|scrutinize)\b",
                r"(?i)\b(look at|check out|go through|break down)\b",
            ],
            "generate": [
                r"(?i)\b(generate|create|make|produce|write|compose|draft)\b",
                r"(?i)\b(come up with|put together|build)\b",
            ],
            "compare": [
                r"(?i)\b(compare|contrast|differentiate|distinguish|versus|vs)\b",
                r"(?i)\b(side by side|head to head)\b",
            ],
            "summarize": [
                r"(?i)\b(summarize|sum up|recap|outline|condense)\b",
                r"(?i)\b(give me the gist|bottom line)\b",
            ],
            "explain": [
                r"(?i)\b(explain|describe|detail|elaborate|clarify)\b",
                r"(?i)\b(tell me about|walk me through)\b",
            ],
            "translate": [
                r"(?i)\b(translate|convert|change|transform)\b",
                r"(?i)\b(turn into|make into)\b",
            ],
            "classify": [
                r"(?i)\b(classify|categorize|group|sort|organize)\b",
                r"(?i)\b(put into|bucket)\b",
            ],
            "predict": [
                r"(?i)\b(predict|forecast|anticipate|expect|estimate)\b",
                r"(?i)\b(what will|how likely)\b",
            ],
        }

    def _init_action_keywords(self) -> Set[str]:
        """Initialize action keywords."""
        return {
            "analyze",
            "examine",
            "investigate",
            "study",
            "review",
            "inspect",
            "scrutinize",
            "generate",
            "create",
            "make",
            "produce",
            "write",
            "compose",
            "draft",
            "build",
            "compare",
            "contrast",
            "differentiate",
            "distinguish",
            "versus",
            "vs",
            "summarize",
            "sum up",
            "recap",
            "outline",
            "condense",
            "gist",
            "explain",
            "describe",
            "detail",
            "elaborate",
            "clarify",
            "tell",
            "walk",
            "translate",
            "convert",
            "change",
            "transform",
            "turn",
            "make",
            "classify",
            "categorize",
            "group",
            "sort",
            "organize",
            "bucket",
            "predict",
            "forecast",
            "anticipate",
            "expect",
            "estimate",
        }

    def extract_intent(self, text: str) -> Tuple[str, float]:
        """
        Extract primary intent from text.

        Returns:
            Tuple of (intent_type, confidence_score)
        """
        intent_scores: Dict[str, float] = {}

        # Pattern-based detection
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, text))
                score += matches
            intent_scores[intent] = score

        # NLP-based detection if available
        if self.nlp:
            nlp_scores = self._extract_with_nlp(text)
            for intent, score in nlp_scores.items():
                intent_scores[intent] = intent_scores.get(intent, 0) + score

        # Select best intent
        if intent_scores:
            best_intent = max(intent_scores, key=lambda k: intent_scores[k])
            confidence = min(
                1.0, intent_scores[best_intent] / 3.0)  # Normalize
            return best_intent, confidence
        else:
            return "general", 0.5

    def _extract_with_nlp(self, text: str) -> Dict[str, float]:
        """Extract intent using spaCy NLP."""
        if not self.nlp:
            return {}

        doc = self.nlp(text)
        intent_scores: Dict[str, float] = {}

        # Look for action verbs
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_.lower() in self.action_keywords:
                # Map verb to intent
                intent = self._verb_to_intent(token.lemma_.lower())
                if intent:
                    intent_scores[intent] = intent_scores.get(intent, 0) + 1

        return intent_scores

    def _verb_to_intent(self, verb: str) -> Optional[str]:
        """Map verb to intent category."""
        verb_to_intent_map = {
            "analyze": "analyze",
            "examine": "analyze",
            "study": "analyze",
            "review": "analyze",
            "generate": "generate",
            "create": "generate",
            "make": "generate",
            "write": "generate",
            "compare": "compare",
            "contrast": "compare",
            "differentiate": "compare",
            "summarize": "summarize",
            "recap": "summarize",
            "outline": "summarize",
            "explain": "explain",
            "describe": "explain",
            "detail": "explain",
            "translate": "translate",
            "convert": "translate",
            "transform": "translate",
            "classify": "classify",
            "categorize": "classify",
            "group": "classify",
            "predict": "predict",
            "forecast": "predict",
            "estimate": "predict",
        }
        return verb_to_intent_map.get(verb)


class FillerRemover:
    """Remove filler words and phrases while preserving meaning."""

    def __init__(self) -> None:
        """Initialize filler remover."""
        self.filler_words = self._init_filler_words()
        self.filler_phrases = self._init_filler_phrases()
        self.redundant_patterns = self._init_redundant_patterns()

        if NLTK_AVAILABLE:
            try:
                self.stop_words = set(stopwords.words("english"))
                self.lemmatizer = WordNetLemmatizer()
            except:
                self.stop_words = set()
                self.lemmatizer = None
        else:
            self.stop_words = set()
            self.lemmatizer = None

    def _init_filler_words(self) -> Set[str]:
        """Initialize filler words to remove."""
        return {
            "very",
            "really",
            "quite",
            "rather",
            "somewhat",
            "pretty",
            "fairly",
            "just",
            "simply",
            "basically",
            "actually",
            "literally",
            "honestly",
            "definitely",
            "probably",
            "possibly",
            "perhaps",
            "maybe",
            "might",
            "seem",
            "appear",
            "look",
            "sound",
            "feel",
            "tend",
            "usually",
            "generally",
            "typically",
            "normally",
            "commonly",
            "often",
            "frequently",
            "sometimes",
            "occasionally",
            "rarely",
            "seldom",
            "hardly",
            "scarcely",
            "uh",
            "um",
            "er",
            "ah",
            "well",
            "so",
            "like",
            "you know",
            "I mean",
            "kind of",
            "sort of",
            "type of",
            "style of",
            "way of",
            "form of",
        }

    def _init_filler_phrases(self) -> List[str]:
        """Initialize filler phrases to remove."""
        return [
            r"\bI would like to\b",
            r"\bI am looking for\b",
            r"\bI want to\b",
            r"\bI need to\b",
            r"\bCan you please\b",
            r"\bCould you please\b",
            r"\bWould you please\b",
            r"\bI was wondering if\b",
            r"\bI was hoping to\b",
            r"\bI think that\b",
            r"\bI believe that\b",
            r"\bIn my opinion\b",
            r"\bFrom my perspective\b",
            r"\bAs far as I can tell\b",
            r"\bTo be honest\b",
            r"\bTo be frank\b",
            r"\bIf you don't mind\b",
            r"\bIf possible\b",
            r"\bWhen you get a chance\b",
        ]

    def _init_redundant_patterns(self) -> List[Tuple[str, str]]:
        """Initialize redundant patterns and their replacements."""
        return [
            # Redundant adjectives
            (r"\bvery very\b", "very"),
            (r"\breally really\b", "really"),
            (r"\bquite quite\b", "quite"),
            # Redundant phrases
            (r"\bin order to\b", "to"),
            (r"\bdue to the fact that\b", "because"),
            (r"\bin spite of the fact that\b", "although"),
            (r"\bwith regard to\b", "about"),
            (r"\bin reference to\b", "about"),
            (r"\bas a result of\b", "because"),
            (r"\bfor the purpose of\b", "to"),
            # Wordy expressions
            (r"\bat this point in time\b", "now"),
            (r"\bat the present time\b", "now"),
            (r"\bin the near future\b", "soon"),
            (r"\bin the event that\b", "if"),
            (r"\bon the occasion that\b", "when"),
            (r"\buntil such time as\b", "until"),
            # Conversational fillers
            (r"\byou know what I mean\b", ""),
            (r"\bas it were\b", ""),
            (r"\bso to speak\b", ""),
            (r"\bif you will\b", ""),
        ]

    def remove_fillers(
        self, text: str, level: OptimizationLevel
    ) -> Tuple[str, List[str]]:
        """
        Remove filler words and phrases.

        Returns:
            Tuple of (cleaned_text, changes_made)
        """
        changes = []
        cleaned = text

        if level == OptimizationLevel.CONSERVATIVE:
            # Only remove obvious fillers
            for phrase_pattern in self.filler_phrases[:5]:  # Most common
                if re.search(phrase_pattern, cleaned, re.IGNORECASE):
                    cleaned = re.sub(phrase_pattern, "",
                                     cleaned, flags=re.IGNORECASE)
                    changes.append(f"Removed phrase: {phrase_pattern}")

        elif level == OptimizationLevel.BALANCED:
            # Remove most fillers
            for phrase_pattern in self.filler_phrases:
                if re.search(phrase_pattern, cleaned, re.IGNORECASE):
                    cleaned = re.sub(phrase_pattern, "",
                                     cleaned, flags=re.IGNORECASE)
                    changes.append(f"Removed phrase: {phrase_pattern}")

            # Remove filler words (conservative)
            words = cleaned.split()
            filtered_words = []
            for word in words:
                word_lower = word.lower().strip(".,!?;:")
                if word_lower not in self.filler_words:
                    filtered_words.append(word)
                else:
                    changes.append(f"Removed filler word: {word}")

            cleaned = " ".join(filtered_words)

        else:  # AGGRESSIVE
            # Remove all fillers aggressively
            for phrase_pattern in self.filler_phrases:
                if re.search(phrase_pattern, cleaned, re.IGNORECASE):
                    cleaned = re.sub(phrase_pattern, "",
                                     cleaned, flags=re.IGNORECASE)
                    changes.append(f"Removed phrase: {phrase_pattern}")

            # Remove redundant patterns
            for pattern, replacement in self.redundant_patterns:
                if re.search(pattern, cleaned, re.IGNORECASE):
                    cleaned = re.sub(pattern, replacement,
                                     cleaned, flags=re.IGNORECASE)
                    changes.append(
                        f"Replaced pattern: {pattern} -> {replacement}")

            # Remove filler words and stop words
            words = cleaned.split()
            filtered_words = []
            for word in words:
                word_lower = word.lower().strip(".,!?;:")
                if (
                    word_lower not in self.filler_words
                    and word_lower not in self.stop_words
                    and len(word) > 1
                ):
                    filtered_words.append(word)
                else:
                    changes.append(f"Removed filler/stop word: {word}")

            cleaned = " ".join(filtered_words)

        # Clean up extra whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned, changes


class DependencyParser:
    """Preserve grammatical structure during optimization."""

    def __init__(self) -> None:
        """Initialize dependency parser."""
        self.nlp = None

        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found for dependency parsing")

    def preserve_structure(self, text: str) -> Tuple[str, List[str]]:
        """
        Preserve grammatical structure while optimizing.

        Returns:
            Tuple of (structured_text, changes_made)
        """
        if not self.nlp:
            return text, ["No dependency parsing available"]

        changes = []
        doc = self.nlp(text)

        # Extract key components
        subjects = []
        verbs = []
        objects = []
        modifiers = []

        for token in doc:
            if token.dep_ in ["nsubj", "nsubjpass"]:
                subjects.append(token.text)
            elif token.pos_ == "VERB":
                verbs.append(token.lemma_)
            elif token.dep_ in ["dobj", "iobj", "obj"]:
                objects.append(token.text)
            elif token.dep_ in ["amod", "advmod", "prep"]:
                modifiers.append(token.text)

        # Reconstruct sentence preserving key relationships
        if subjects and verbs:
            # Simple SVO reconstruction
            structured_parts = []

            # Add subject
            if subjects:
                structured_parts.append(subjects[0])

            # Add verb
            if verbs:
                structured_parts.append(verbs[0])

            # Add object
            if objects:
                structured_parts.append(objects[0])

            # Add important modifiers
            important_modifiers = [m for m in modifiers if len(m) > 3][:2]
            structured_parts.extend(important_modifiers)

            structured_text = " ".join(structured_parts)
            changes.append("Reconstructed using dependency parsing")
        else:
            structured_text = text
            changes.append("No clear structure found")

        return structured_text, changes


class IntentTemplateReconstructor:
    """Reconstruct optimized prompts using intent templates."""

    def __init__(self) -> None:
        """Initialize intent template reconstructor."""
        self.templates = self._init_templates()

    def _init_templates(self) -> Dict[str, List[str]]:
        """Initialize intent-based templates."""
        return {
            "analyze": [
                "{intent} {target}",
                "{intent} {target} for {purpose}",
                "{intent} {target} focusing on {aspect}",
            ],
            "generate": [
                "{intent} {target}",
                "{intent} {target} about {topic}",
                "{intent} {target} with {specification}",
            ],
            "compare": [
                "{intent} {target1} and {target2}",
                "{intent} {target1} vs {target2}",
                "{intent} {target1} and {target2} for {purpose}",
            ],
            "summarize": [
                "{intent} {target}",
                "{intent} {target} in {length}",
                "{intent} {target} highlighting {points}",
            ],
            "explain": [
                "{intent} {target}",
                "{intent} {target} for {audience}",
                "{intent} how {target} works",
            ],
            "translate": [
                "{intent} {target} to {language}",
                "{intent} {target} from {source} to {target}",
                "{intent} {target}",
            ],
            "classify": [
                "{intent} {target}",
                "{intent} {target} into {categories}",
                "{intent} {target} by {criteria}",
            ],
            "predict": [
                "{intent} {target}",
                "{intent} {target} for {timeframe}",
                "{intent} what will happen to {target}",
            ],
            "general": [
                "{target}",
                "{target} for {purpose}",
                "{target} with {context}",
            ],
        }

    def reconstruct(
        self, intent: str, entities: Dict[str, str], level: OptimizationLevel
    ) -> Tuple[str, List[str]]:
        """
        Reconstruct optimized prompt using intent template.

        Args:
            intent: Detected intent
            entities: Extracted entities (target, purpose, etc.)
            level: Optimization level

        Returns:
            Tuple of (reconstructed_text, changes_made)
        """
        changes = []

        # Get templates for intent
        templates = self.templates.get(intent, self.templates["general"])

        # Select template based on optimization level
        if level == OptimizationLevel.CONSERVATIVE:
            # Use most detailed template
            template = max(templates, key=len)
        elif level == OptimizationLevel.BALANCED:
            # Use medium template
            templates.sort(key=len)
            template = templates[len(templates) // 2]
        else:  # AGGRESSIVE
            # Use shortest template
            template = min(templates, key=len)

        # Fill template
        try:
            reconstructed = template.format(**entities)
            changes.append(f"Applied {intent} template")
        except KeyError as e:
            # Missing entity, use fallback
            reconstructed = entities.get("target", "Unknown task")
            changes.append(f"Template fallback (missing {e})")

        return reconstructed, changes


class SemanticTokenOptimizer:
    """
    Main Semantic Token Optimizer - Phase 2 Core Differentiator

    Architecture:
    Input → Intent Extraction
          → Filler Removal
          → Dependency Parsing
          → Intent Template Reconstruction
          → Optimized Output
    """

    def __init__(
        self, optimization_level: OptimizationLevel = OptimizationLevel.BALANCED
    ) -> None:
        """
        Initialize semantic optimizer.

        Args:
            optimization_level: How aggressively to optimize
        """
        self.optimization_level = optimization_level
        self.intent_extractor = IntentExtractor()
        self.filler_remover = FillerRemover()
        self.dependency_parser = DependencyParser()
        self.template_reconstructor = IntentTemplateReconstructor()

    def optimize(self, text: str) -> OptimizationResult:
        """
        Optimize text while preserving meaning.

        Args:
            text: Input text to optimize

        Returns:
            OptimizationResult with optimized text and metrics
        """
        import time

        start_time = time.time()

        original_tokens = len(text.split())
        changes_made = []

        # Step 1: Extract intent
        intent, intent_confidence = self.intent_extractor.extract_intent(text)
        changes_made.append(
            f"Detected intent: {intent} (confidence: {intent_confidence:.2f})"
        )

        # Step 2: Remove fillers
        cleaned_text, filler_changes = self.filler_remover.remove_fillers(
            text, self.optimization_level
        )
        changes_made.extend(filler_changes)

        # Step 3: Preserve grammatical structure
        structured_text, structure_changes = self.dependency_parser.preserve_structure(
            cleaned_text
        )
        changes_made.extend(structure_changes)

        # Step 4: Extract entities for template reconstruction
        entities = self._extract_entities(structured_text, intent)

        # Step 5: Reconstruct using intent template
        optimized_text, template_changes = self.template_reconstructor.reconstruct(
            intent, entities, self.optimization_level
        )
        changes_made.extend(template_changes)

        # Calculate metrics
        optimized_tokens = len(optimized_text.split())
        token_reduction = original_tokens - optimized_tokens
        token_reduction_percentage = (
            (token_reduction / original_tokens * 100) if original_tokens > 0 else 0
        )

        processing_time = (time.time() - start_time) * 1000

        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            intent_confidence, token_reduction_percentage, len(changes_made)
        )

        return OptimizationResult(
            original_text=text,
            optimized_text=optimized_text,
            token_reduction=token_reduction,
            token_reduction_percentage=token_reduction_percentage,
            preserved_intent=intent,
            optimization_level=self.optimization_level,
            processing_time_ms=processing_time,
            changes_made=changes_made,
            confidence_score=confidence_score,
        )

    def _extract_entities(self, text: str, intent: str) -> Dict[str, str]:
        """Extract entities for template reconstruction."""
        entities = {"target": text}  # Default

        # Simple entity extraction (can be enhanced with NLP)
        if self.dependency_parser.nlp:
            doc = self.dependency_parser.nlp(text)

            # Extract nouns as potential targets
            nouns = [token.text for token in doc if token.pos_ == "NOUN"]
            if nouns:
                entities["target"] = nouns[0]

            # Look for purpose indicators
            purpose_words = ["for", "to", "because", "since", "as"]
            for i, token in enumerate(doc):
                if token.text.lower() in purpose_words and i + 1 < len(doc):
                    entities["purpose"] = doc[i + 1].text
                    break

        return entities

    def _calculate_confidence(
        self, intent_confidence: float, token_reduction: float, changes_count: int
    ) -> float:
        """Calculate overall confidence score."""
        # Base confidence from intent detection
        confidence = intent_confidence * 0.4

        # Boost for reasonable token reduction (10-40%)
        if 10 <= token_reduction <= 40:
            confidence += 0.3
        elif 5 <= token_reduction <= 50:
            confidence += 0.2
        else:
            confidence += 0.1

        # Boost for reasonable number of changes
        if 2 <= changes_count <= 8:
            confidence += 0.2
        elif 1 <= changes_count <= 12:
            confidence += 0.1
        else:
            confidence += 0.05

        # Boost for preserved intent
        if intent_confidence > 0.7:
            confidence += 0.1

        return min(1.0, confidence)

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization capabilities and statistics."""
        return {
            "optimization_level": self.optimization_level.value,
            "spacy_available": SPACY_AVAILABLE,
            "nltk_available": NLTK_AVAILABLE,
            "supported_intents": list(self.intent_extractor.intent_patterns.keys()),
            "filler_words_count": len(self.filler_remover.filler_words),
            "template_count": sum(
                len(templates)
                for templates in self.template_reconstructor.templates.values()
            ),
        }


# Convenience function for easy usage
def optimize_semantically(text: str, level: str = "balanced") -> OptimizationResult:
    """
    Optimize text semantically while preserving meaning.

    Args:
        text: Input text to optimize
        level: Optimization level ("conservative", "balanced", "aggressive")

    Returns:
        OptimizationResult with optimized text
    """
    level_map = {
        "conservative": OptimizationLevel.CONSERVATIVE,
        "balanced": OptimizationLevel.BALANCED,
        "aggressive": OptimizationLevel.AGGRESSIVE,
    }

    optimization_level = level_map.get(
        level.lower(), OptimizationLevel.BALANCED)
    optimizer = SemanticTokenOptimizer(optimization_level)
    return optimizer.optimize(text)


# Quick test function
def test_semantic_optimizer() -> None:
    """Test the semantic optimizer."""
    test_texts = [
        "Hey bro, can you please kindly analyze this dataset for any potential anomalies that might exist",
        "I was wondering if you could possibly generate a comprehensive summary of the quarterly sales report",
        "Would you mind comparing the performance metrics of product A versus product B for me please",
        "I would really appreciate it if you could explain how machine learning algorithms work in detail",
    ]

    print("Testing Semantic Token Optimizer:")
    print("=" * 60)

    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}:")
        print(f"Original: {text}")

        result = optimize_semantically(text, "balanced")

        print(f"Optimized: {result.optimized_text}")
        print(f"Intent: {result.preserved_intent}")
        print(
            f"Token reduction: {result.token_reduction} ({result.token_reduction_percentage:.1f}%)"
        )
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Processing time: {result.processing_time_ms:.1f}ms")

        if result.changes_made:
            print("Changes:", " | ".join(result.changes_made[:3]))


if __name__ == "__main__":
    test_semantic_optimizer()
