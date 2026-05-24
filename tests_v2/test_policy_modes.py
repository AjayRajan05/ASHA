"""Tests for policy mode passthrough and stage guards."""

import pytest

from privysha import process


def test_mode_off_returns_byte_identical():
    prompt = "What is 2 + 2?"
    result = process(prompt, mode="off")
    assert result == prompt


def test_mode_off_with_pii_unchanged():
    prompt = "Email me at john@example.com"
    result = process(prompt, mode="off")
    assert result == prompt


def test_mode_strict_masks_pii():
    prompt = "Contact john@example.com"
    result = process(prompt, mode="strict")
    assert "john@example.com" not in str(result)


def test_mode_lite_processes_without_crash():
    prompt = "Hello, please summarize this document."
    result = process(prompt, mode="lite")
    assert isinstance(result, str)
    assert len(result) > 0


def test_privacy_false_skips_masking_in_balanced():
    prompt = "Reach me at secret@company.com for details"
    result = process(prompt, privacy=False, mode="balanced", return_metrics=True)
    assert result["security_result"]["pii_masked"] == 0
    assert "secret@company.com" in result["original"]
