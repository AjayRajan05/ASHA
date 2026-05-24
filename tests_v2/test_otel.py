"""OpenTelemetry optional integration tests."""

from privysha.integrations.otel import enable_otel, get_tracer, trace_stage


def test_trace_stage_noop_when_otel_disabled():
    @trace_stage("unit_test")
    def add_one(x: int) -> int:
        return x + 1

    assert add_one(1) == 2


def test_get_tracer_none_by_default():
    assert get_tracer() is None


def test_enable_otel_returns_bool():
    result = enable_otel(service_name="privysha-test")
    assert isinstance(result, bool)
    if result:
        assert get_tracer() is not None

        @trace_stage("enabled")
        def echo(value: str) -> str:
            return value

        assert echo("ok") == "ok"


def test_pipeline_runs_with_otel_enabled_or_skipped():
    from privysha.pipeline.pipeline import Pipeline

    enabled = enable_otel("privysha-test-pipeline")
    pipeline = Pipeline(privacy=True, token_budget=800)
    result = pipeline.process("Hello world")
    assert result.get("success") is not False or "prompts" in result
    if not enabled:
        assert get_tracer() is None
