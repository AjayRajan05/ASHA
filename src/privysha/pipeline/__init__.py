"""
Modular Pipeline - Clean, maintainable pipeline architecture

This module provides a modular pipeline implementation that breaks down
the monolithic pipeline.py into individual, testable stages.
"""

from .pipeline import Pipeline
from .components import StageBase, StageResult, StageContext, create_context
from .stages import (
    SecurityStage,
    IRGenerationStage,
    RoutingStage,
    CompilationStage,
    OptimizationStage,
    GenerationStage,
    ResultStage,
)

__all__ = [
    "Pipeline",
    "StageBase",
    "StageResult",
    "StageContext",
    "create_context",
    "SecurityStage",
    "IRGenerationStage",
    "RoutingStage",
    "CompilationStage",
    "OptimizationStage",
    "GenerationStage",
    "ResultStage",
]
