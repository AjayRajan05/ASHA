"""Metrics dashboard integration tests."""

from privysha import process
from privysha.core.metrics_dashboard import dashboard


def test_process_records_dashboard_metrics():
    before = len(
        [e for e in dashboard.collector.events if e.event_type == "request"]
    )
    process("Hello john@example.com")
    after = len(
        [e for e in dashboard.collector.events if e.event_type == "request"]
    )
    assert after > before
