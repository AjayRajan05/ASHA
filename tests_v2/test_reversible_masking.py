"""Tests for opt-in reversible PII masking."""

import json

import pytest

from privysha import sanitize, unmask
from privysha.utils.dropin import process


def test_sanitize_reversible_round_trip():
    prompt = "Email me at alice@example.com"
    result = sanitize(prompt, return_details=True, reversible=True)
    assert "masking_map" in result
    assert result["masking_map"]
    masked = result["sanitized"]
    assert "alice@example.com" not in masked
    restored = unmask(masked, result["masking_map"])
    assert "alice@example.com" in restored


def test_process_reversible_returns_map():
    prompt = "Contact bob@test.org about order 123"
    result = process(prompt, return_metrics=True, reversible=True)
    masking_map = result.get("masking_map") or result["metrics"].get("masking_map")
    assert masking_map
    assert "bob@test.org" in masking_map.values()
    assert "bob@test.org" not in result["optimized"]


def test_default_not_reversible():
    prompt = "Email carol@example.com"
    result = sanitize(prompt, return_details=True, reversible=False)
    assert "masking_map" not in result


def test_masking_map_not_in_trace_json(capsys):
    """Vault contents must not appear in console trace output."""
    prompt = "SSN 123-45-6789 email d@e.com"
    process(prompt, trace=True, log_output="json", reversible=True, return_metrics=True)
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "123-45-6789" not in combined
    assert "d@e.com" not in combined
