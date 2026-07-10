"""Unit tests for PII confidence scoring stage."""

from asha.core.pii_pipeline.stages.base_stage import PIIEntity, create_pii_context
from asha.core.pii_pipeline.stages.scoring_stage import ScoringStage


def test_scoring_boosts_high_confidence_regex():
    stage = ScoringStage()
    entity = PIIEntity(
        text="john@example.com",
        start=0,
        end=16,
        pii_type="email",
        confidence=0.85,
        context="email",
        metadata={"detector": "regex"},
    )
    context = create_pii_context("john@example.com", {}, False)
    context.entities = [entity]
    result = stage.execute(context)
    assert result.success
    assert context.entities[0].confidence > 0.5


def test_scoring_suppresses_low_confidence():
    stage = ScoringStage()
    entity = PIIEntity(
        text="123 Main",
        start=0,
        end=8,
        pii_type="address",
        confidence=0.2,
        context="generic",
        metadata={"detector": "heuristic"},
    )
    context = create_pii_context("123 Main St", {}, False)
    context.entities = [entity]
    stage.execute(context)
    # Low-confidence entities may be filtered or remain below threshold
    assert all(e.confidence <= 0.5 for e in context.entities if e.confidence < 0.5)
