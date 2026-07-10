"""
Multi-Stage PII Detection Pipeline - Advanced PII detection and masking

This package provides a comprehensive, multi-stage PII detection pipeline that
goes beyond simple regex matching to provide enterprise-grade PII protection.

Architecture:
7-stage compiler-style pipeline:
1. Normalization Layer - Text preprocessing and standardization
2. Multi-Detector Engine - Parallel PII detection
3. Confidence Scoring Engine - Calculate and adjust confidence scores
4. Context Resolution Engine - Understand context and adjust decisions
5. Masking Strategy Engine - Apply advanced masking strategies
6. Semantic Integrity Check - Ensure meaning is preserved
7. Verification Layer - Final validation and quality assurance
"""

from .pii_pipeline import PIIPipeline, detect_pii, mask_pii, verify_pii_masking
from .stages import (
    NormalizationStage,
    DetectionStage,
    ScoringStage,
    ContextStage,
    MaskingStage,
    IntegrityStage,
    VerificationStage,
)
from .stages.base_stage import PIIEntity, PIIContext, StageResult, create_pii_context

__all__ = [
    # Main pipeline
    "PIIPipeline",
    "detect_pii",
    "mask_pii",
    "verify_pii_masking",
    # Stages
    "NormalizationStage",
    "DetectionStage",
    "ScoringStage",
    "ContextStage",
    "MaskingStage",
    "IntegrityStage",
    "VerificationStage",
    # Base classes
    "PIIEntity",
    "PIIContext",
    "StageResult",
    "create_pii_context",
]
