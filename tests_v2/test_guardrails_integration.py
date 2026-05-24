"""Guardrails AI integration automated tests — Gap 17.

Tests the compose_with_guardrails() helper using mock guard objects so no
`guardrails-ai` package is required.
"""

import pytest
from unittest.mock import MagicMock

from privysha import process


# ---------------------------------------------------------------------------
# compose_with_guardrails API surface
# ---------------------------------------------------------------------------


def test_compose_with_guardrails_importable():
    from privysha import compose_with_guardrails

    assert callable(compose_with_guardrails)


def test_compose_with_guardrails_returns_composer():
    from privysha import compose_with_guardrails

    mock_guard = MagicMock()
    composer = compose_with_guardrails(mock_guard)
    assert composer is not None
    assert hasattr(composer, "validate_with_privysha")


def test_validate_with_privysha_masks_pii():
    """PII must be removed from the prompt before Guardrails validates it."""
    from privysha import compose_with_guardrails

    mock_guard = MagicMock()
    mock_guard.validate.return_value = MagicMock(validated_output="ok")

    composer = compose_with_guardrails(mock_guard)
    result = composer.validate_with_privysha(
        prompt="User john@example.com wants a refund",
        guard=mock_guard,
    )

    assert "secure_prompt" in result
    assert "john@example.com" not in result["secure_prompt"]
    mock_guard.validate.assert_called_once()


def test_validate_with_privysha_calls_guard():
    """Guardrails validate() must always be invoked."""
    from privysha import compose_with_guardrails

    mock_guard = MagicMock()
    mock_guard.validate.return_value = MagicMock(validated_output="validated")

    composer = compose_with_guardrails(mock_guard)
    composer.validate_with_privysha(
        prompt="Summarize quarterly earnings",
        guard=mock_guard,
    )

    mock_guard.validate.assert_called_once()


def test_validate_with_privysha_returns_validation_passed():
    """Result dict must include a validation_passed key."""
    from privysha import compose_with_guardrails

    mock_guard_result = MagicMock()
    mock_guard_result.validated_output = "ok"
    mock_guard_result.validation_passed = True  # explicit bool, not MagicMock

    mock_guard = MagicMock()
    mock_guard.validate.return_value = mock_guard_result

    composer = compose_with_guardrails(mock_guard)
    result = composer.validate_with_privysha(
        prompt="Analyze data",
        guard=mock_guard,
    )

    assert "validation_passed" in result
    assert result["validation_passed"] is True


def test_validate_with_privysha_handles_guard_failure():
    """If guard.validate() raises, result should still be returned (fail-safe)."""
    from privysha import compose_with_guardrails

    mock_guard = MagicMock()
    mock_guard.validate.side_effect = RuntimeError("guard failed")

    composer = compose_with_guardrails(mock_guard)
    # Should not raise — fail-safe
    result = composer.validate_with_privysha(
        prompt="Test prompt",
        guard=mock_guard,
    )
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Smoke test with real guardrails-ai package (skipped if not installed)
# ---------------------------------------------------------------------------


def test_guardrails_package_smoke():
    pytest.importorskip("guardrails")
    from privysha import compose_with_guardrails

    composer = compose_with_guardrails()
    assert composer is not None
