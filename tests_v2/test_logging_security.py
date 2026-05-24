"""Ensure raw secrets never appear in trace/metrics output."""

import json

from privysha.utils.dropin import process


SECRET_PROMPT = (
    "Contact john@secret.com SSN 123-45-6789 "
    "key sk-abcdefghijklmnopqrstuvwxyz1234567890"
)


def test_trace_output_no_raw_pii(capsys):
    process(
        SECRET_PROMPT,
        trace=True,
        log_output="json",
        return_metrics=True,
    )
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "john@secret.com" not in combined
    assert "123-45-6789" not in combined
    assert "sk-abcdefghijklmnopqrstuvwxyz1234567890" not in combined


def test_metrics_no_raw_pii_in_processed_output():
    result = process(SECRET_PROMPT, return_metrics=True)
    optimized = result.get("optimized", "")
    security = result.get("security_result", {})
    sanitized = security.get("sanitized_content", "")
    blob = json.dumps({"optimized": optimized, "sanitized": sanitized})
    assert "john@secret.com" not in blob
    assert "123-45-6789" not in blob
