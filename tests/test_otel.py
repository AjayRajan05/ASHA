"""OpenTelemetry optional integration tests."""

from asha.integrations.otel import enable_otel, get_tracer, trace_stage


def test_trace_stage_noop_when_otel_disabled():
    @trace_stage("unit_test")
    def add_one(x: int) -> int:
        return x + 1

    assert add_one(1) == 2


def test_get_tracer_none_by_default():
    assert get_tracer() is None


def test_enable_otel_returns_bool():
    result = enable_otel(service_name="asha-test")
    assert isinstance(result, bool)
    if result:
        assert get_tracer() is not None

        @trace_stage("enabled")
        def echo(value: str) -> str:
            return value

        assert echo("ok") == "ok"


def test_process_runs_with_otel_enabled_or_skipped():
    from asha import process

    enabled = enable_otel("asha-test-pipeline")
    result = process("Hello world", mode="off")
    assert result.output
    if not enabled:
        assert get_tracer() is None
