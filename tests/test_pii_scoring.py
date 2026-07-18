"""Unit tests for PII confidence scoring stage."""

from asha.core.pii_pipeline.stages.base_stage import PIIEntity, create_pii_context
from asha.core.pii_pipeline.stages.scoring_stage import ScoringStage


def test_scoring_boosts_high_confidence_regex():
    """High-confidence regex-detected email should remain above threshold."""
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
    # Regex-detected email with 0.85 base confidence should stay high
    scored = context.entities[0]
    assert scored.confidence >= 0.5, (
        f"Expected high-confidence email to stay >= 0.5, got {scored.confidence}"
    )


def test_scoring_low_confidence_address_stays_low():
    """Low-confidence heuristic address should not be boosted above threshold."""
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
    result = stage.execute(context)
    assert result.success
    # Low-confidence heuristic should not be artificially boosted high
    scored = context.entities[0]
    assert scored.confidence <= 0.6, (
        f"Expected low-confidence address to stay <= 0.6, got {scored.confidence}"
    )


def test_scoring_ssn_high_confidence():
    """SSN pattern with high confidence should stay high after scoring."""
    stage = ScoringStage()
    entity = PIIEntity(
        text="123-45-6789",
        start=0,
        end=11,
        pii_type="ssn",
        confidence=0.95,
        context="ssn",
        metadata={"detector": "regex"},
    )
    context = create_pii_context("My SSN is 123-45-6789", {}, False)
    context.entities = [entity]
    result = stage.execute(context)
    assert result.success
    assert context.entities[0].confidence >= 0.8


def test_scoring_does_not_crash_on_empty_entities():
    """Scoring stage should handle empty entity list gracefully."""
    stage = ScoringStage()
    context = create_pii_context("No PII here", {}, False)
    context.entities = []
    result = stage.execute(context)
    assert result.success
    assert len(context.entities) == 0
