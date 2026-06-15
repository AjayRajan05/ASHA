"""Tests for Agent helper methods."""

from privysha import Agent
from privysha.types.results import MetricsInfo, ProcessResult


class MockAdapter:
    def generate(self, prompt: str) -> str:
        return f"response:{prompt[:20]}"


def test_run_with_fallback_uses_compiled_prompt(monkeypatch):
    agent = Agent(model="mock")
    agent.adapter = MockAdapter()

    def fake_run(prompt, **kwargs):
        return ProcessResult(
            output="compiled-version",
            original=prompt,
            degraded=False,
            degraded_reason=None,
            privacy_applied=True,
            security=None,
            metrics=MetricsInfo(0, 0.0, 0.0),
        )

    monkeypatch.setattr(agent.processor, "run", fake_run)
    result = agent.run_with_fallback("hello")
    assert result.startswith("response:compiled-version")


def test_get_token_metrics_shape(monkeypatch):
    agent = Agent(model="mock")

    def fake_run(prompt, **kwargs):
        return ProcessResult(
            output="one two",
            original="one two three four",
            degraded=False,
            degraded_reason=None,
            privacy_applied=True,
            security=None,
            metrics=MetricsInfo(2, 50.0, 0.0),
        )

    monkeypatch.setattr(agent.processor, "run", fake_run)
    metrics = agent.get_token_metrics("one two three four")
    assert "raw_tokens" in metrics
    assert "optimized_tokens" in metrics
    assert "compiled_tokens" in metrics
    assert metrics["raw_tokens"] >= metrics["optimized_tokens"]
