"""PII pipeline full-flow tests.

Tests the complete 7-stage pipeline: normalization → detection → scoring →
context → masking → integrity → verification.
"""

import pytest
from asha.core.pii_pipeline.pii_pipeline import PIIPipeline
from asha.core.pii_pipeline.stages.base_stage import PIIEntity, create_pii_context


def test_pii_pipeline_full_flow():
    """Test the complete 7-stage PII pipeline flow."""
    pipeline = PIIPipeline(debug_enabled=True)

    input_text = "Contact John Doe at john.doe@example.com or call (555) 123-4567. My SSN is 123-45-6789."

    result = pipeline.process(input_text)

    assert result["success"] is True
    assert "masked_text" in result
    assert "entities" in result
    assert "stage_results" in result
    assert "processing_summary" in result

    # Check PII was detected - specific types
    entities = result["entities"]
    entity_types = [e["pii_type"] for e in entities]

    assert "name" in entity_types, f"Expected 'name' in {entity_types}"
    assert "email" in entity_types, f"Expected 'email' in {entity_types}"
    assert "ssn" in entity_types, f"Expected 'ssn' in {entity_types}"

    # Check masking was applied
    masked_text = result["masked_text"]
    assert "John Doe" not in masked_text
    assert "john.doe@example.com" not in masked_text
    assert "123-45-6789" not in masked_text

    # Verify all 7 stages were executed and succeeded
    stage_results = result["stage_results"]
    expected_stages = [
        'normalization', 'detection', 'scoring',
        'context', 'masking', 'integrity', 'verification'
    ]
    for stage in expected_stages:
        assert stage in stage_results, f"Stage '{stage}' missing from results"
        assert stage_results[stage]["success"] is True, f"Stage '{stage}' failed"


def test_pii_pipeline_obfuscation():
    """Test normalization stage handles obfuscated PII."""
    pipeline = PIIPipeline()

    input_text = "Reach me at john [at] example [dot] com"
    result = pipeline.process(input_text)

    # Normalization stage should succeed
    norm_result = result["stage_results"]["normalization"]
    assert norm_result["success"] is True

    # The obfuscated tokens should be normalized away
    assert "[at]" not in result["masked_text"]
    assert "[dot]" not in result["masked_text"]


def test_pii_pipeline_intent_context():
    """Test context stage's intent detection."""
    pipeline = PIIPipeline()

    # Teaching intent should reduce confidence
    teaching_text = "For example, you might have an email like test@example.com"
    result = pipeline.process(teaching_text)

    context_result = result["stage_results"]["context"]
    assert context_result["success"] is True
    assert "detected_intent" in context_result["metadata"]
    # Teaching context should be recognized
    detected = context_result["metadata"]["detected_intent"]
    assert detected == "teaching", f"Expected 'teaching' intent, got '{detected}'"

    # Personal intent should boost confidence
    personal_text = "My private email is john.doe@realmail.com"
    result = pipeline.process(personal_text)
    context_result = result["stage_results"]["context"]
    assert context_result["success"] is True
    detected = context_result["metadata"]["detected_intent"]
    assert detected == "personal", f"Expected 'personal' intent, got '{detected}'"


def test_pii_pipeline_integrity_repair():
    """Test integrity stage succeeds and reports repair status."""
    pipeline = PIIPipeline()

    input_text = "John Doe and Jane Smith are here."
    result = pipeline.process(input_text)

    integrity_result = result["stage_results"]["integrity"]
    assert integrity_result["success"] is True
    # Integrity stage must have metadata about repairs
    assert "metadata" in integrity_result


def test_pii_pipeline_verification():
    """Test verification stage produces a complete report."""
    pipeline = PIIPipeline()
    input_text = "Call me at 555-123-4567"
    result = pipeline.process(input_text)

    assert "verification_report" in result
    report = result["verification_report"]
    assert report["summary"]["verification_passed"] is True
    assert "pii_leak_analysis" in report


def test_pii_pipeline_no_pii():
    """Pipeline should succeed and not mask anything for clean text."""
    pipeline = PIIPipeline()
    input_text = "What is the capital of France?"
    result = pipeline.process(input_text)

    assert result["success"] is True
    # No entities should be detected
    assert len(result["entities"]) == 0
    # Text should be mostly unchanged
    assert "France" in result["masked_text"]


def test_pii_pipeline_multiple_emails():
    """Pipeline should detect and mask all emails."""
    pipeline = PIIPipeline()
    input_text = "Email alice@corp.com or bob@corp.com for info"
    result = pipeline.process(input_text)

    assert result["success"] is True
    masked = result["masked_text"]
    assert "alice@corp.com" not in masked
    assert "bob@corp.com" not in masked

    email_entities = [e for e in result["entities"] if e["pii_type"] == "email"]
    assert len(email_entities) >= 2


if __name__ == "__main__":
    pytest.main([__file__])
