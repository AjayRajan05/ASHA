"""Metrics dashboard integration tests."""

from privysha.core.metrics_dashboard import dashboard
from privysha.pipeline.pipeline import Pipeline


def test_pipeline_records_dashboard_metrics():
    before = len(
        [e for e in dashboard.collector.events if e.event_type == "request"]
    )
    Pipeline(privacy=True).process("Hello john@example.com")
    after = len(
        [e for e in dashboard.collector.events if e.event_type == "request"]
    )
    assert after > before
