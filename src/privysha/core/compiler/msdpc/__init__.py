"""
MSDPC - Multi-Stage Deterministic Prompt Compiler

A modular, research-backed prompt optimization system that achieves
30-60% token reduction without ML/LLM dependencies.
"""

from .intent_extractor import IntentExtractor, IntentType, IntentExtractionResult
from .semantic_compressor import SemanticCompressor, CompressionResult
from .structure_builder import StructureBuilder, StructureResult
from .token_pruner import TokenPruner, PruningResult
from .output_shaper import OutputShaper, ShapingResult
from .template_engine import TemplateEngine, TemplateResult
from .metrics_engine import MetricsEngine, QualityMetrics
from .optimizer import MSDPCOptimizer, OptimizationMetrics

__all__ = [
    "IntentExtractor",
    "IntentType",
    "IntentExtractionResult",
    "SemanticCompressor",
    "CompressionResult",
    "StructureBuilder",
    "StructureResult",
    "TokenPruner",
    "PruningResult",
    "OutputShaper",
    "ShapingResult",
    "TemplateEngine",
    "TemplateResult",
    "MetricsEngine",
    "QualityMetrics",
    "MSDPCOptimizer",
    "OptimizationMetrics",
]
