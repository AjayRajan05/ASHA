"""Tests for Agent helper methods."""

from privysha import Agent


class MockAdapter:
    def generate(self, prompt: str) -> str:
        return f"response:{prompt[:20]}"


def test_run_with_fallback_uses_compiled_prompt(monkeypatch):
    agent = Agent(model="mock")
    agent.adapter = MockAdapter()

    def fake_process(prompt):
        return {
            "prompts": {
                "original": prompt,
                "sanitized": prompt,
                "compiled": "compiled-version",
                "optimized": "optimized-version",
            }
        }

    monkeypatch.setattr(agent.pipeline, "process", fake_process)
    result = agent.run_with_fallback("hello")
    assert result.startswith("response:compiled-version")


def test_get_token_metrics_shape(monkeypatch):
    agent = Agent(model="mock")

    def fake_process(prompt):
        return {
            "prompts": {
                "original": "one two three four",
                "optimized": "one two",
                "compiled": "one two",
            }
        }

    monkeypatch.setattr(agent.pipeline, "process", fake_process)
    metrics = agent.get_token_metrics("one two three four")
    assert "raw_tokens" in metrics
    assert "optimized_tokens" in metrics
    assert "compiled_tokens" in metrics
    assert metrics["raw_tokens"] >= metrics["optimized_tokens"]
