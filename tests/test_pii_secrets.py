"""PII secret detection and masking tests."""

from privysha import sanitize
from privysha.core.pii_pipeline.pii_pipeline import PIIPipeline


def test_sanitize_masks_api_key():
    prompt = "Use key sk-1234567890abcdefghijklmnop"
    result = sanitize(prompt)
    assert "sk-1234567890abcdefghijklmnop" not in str(result)


def test_sanitize_masks_jwt():
    token = "eyJhbGciOiJIUzI1NiIs.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    prompt = f"Authorization: Bearer {token}"
    result = sanitize(prompt)
    assert token not in str(result)


def test_hybrid_pipeline_masks_api_key():
    pipeline = PIIPipeline()
    text = "export OPENAI_API_KEY=sk-1234567890abcdefghijklmnop"
    result = pipeline.process(text)
    assert "sk-1234567890abcdefghijklmnop" not in result.get("masked_text", "")
