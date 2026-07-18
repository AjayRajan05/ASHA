"""PII secret detection and masking tests."""

from asha import sanitize
from asha.core.pii_pipeline.pii_pipeline import PIIPipeline
from asha.core.security.pii_detector import PIIDetector


def test_sanitize_masks_api_key():
    prompt = "Use key sk-1234567890abcdefghijklmnop"
    result = sanitize(prompt)
    assert "sk-1234567890abcdefghijklmnop" not in str(result)
    assert "[API_KEY_HASH]" in result.output or "sk-1234567890" not in result.output


def test_sanitize_masks_jwt():
    token = "eyJhbGciOiJIUzI1NiIs.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    prompt = f"Authorization: Bearer {token}"
    result = sanitize(prompt)
    assert token not in str(result)


def test_hybrid_pipeline_masks_api_key():
    pipeline = PIIPipeline()
    text = "export OPENAI_API_KEY=sk-1234567890abcdefghijklmnop"
    result = pipeline.process(text)
    assert result["success"] is True
    assert "sk-1234567890abcdefghijklmnop" not in result.get("masked_text", "")


def test_detector_detects_api_key_type():
    """PIIDetector must identify api_key as a PII type."""
    detector = PIIDetector()
    text = "Use key sk-1234567890abcdefghijklmnopqrstuvwxyz for access"
    types = detector.detect_pii_types(text)
    assert "api_key" in types


def test_detector_detects_jwt_type():
    """PIIDetector must identify jwt_token as a PII type."""
    detector = PIIDetector()
    jwt = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    types = detector.detect_pii_types(f"Authorization: {jwt}")
    assert "jwt_token" in types


def test_sanitize_masks_aws_style_key():
    """AWS-style access key IDs should be detected."""
    key = "AKIAIOSFODNN7EXAMPLE"
    prompt = f"aws_access_key_id = {key}"
    result = sanitize(prompt)
    # The key should be masked or at least not present in raw form
    assert key not in result.output or "[" in result.output
