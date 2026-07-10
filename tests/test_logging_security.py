"""Ensure raw secrets never appear in trace/metrics output."""

import json

from asha.types.results import ProcessResult
from asha.utils.dropin import process

from conftest import output_of


SECRET_PROMPT = (
    "Contact john@secret.com SSN 123-45-6789 "
    "key sk-abcdefghijklmnopqrstuvwxyz1234567890"
)


def test_trace_output_no_raw_pii(capsys):
    process(
        SECRET_PROMPT,
        trace=True,
        log_output="json",
    )
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "john@secret.com" not in combined
    assert "123-45-6789" not in combined
    assert "sk-abcdefghijklmnopqrstuvwxyz1234567890" not in combined


def test_metrics_no_raw_pii_in_processed_output():
    result = process(SECRET_PROMPT)
    assert isinstance(result, ProcessResult)
    optimized = output_of(result)
    security = result.security.to_dict() if result.security else {}
    sanitized = security.get("sanitized_content", "")
    blob = json.dumps({"optimized": optimized, "sanitized": sanitized})
    assert "john@secret.com" not in blob
    assert "123-45-6789" not in blob
