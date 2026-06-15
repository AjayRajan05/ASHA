#!/usr/bin/env python3
"""
Adapter usage examples (v0.4.1).

Shows how Agent picks providers from model names. Mock adapter always works;
others need API keys and optional extras.
"""

from privysha import Agent


def try_agent(model: str, label: str) -> None:
    try:
        agent = Agent(model=model, privacy=True)
        print(f"  {label}: adapter created for {model!r}")
    except Exception as exc:
        print(f"  {label}: {type(exc).__name__} — {exc}")


def main() -> None:
    print("PrivySHA adapter patterns (v0.4.1)")
    print("=" * 50)

    print("\nMock (always works):")
    agent = Agent(model="mock", privacy=True)
    print(f"  Response: {agent.run('Test prompt with a@b.com')[:80]}...")

    print("\nOpenAI-style models (need OPENAI_API_KEY + privysha[openai]):")
    for model in ("gpt-4o-mini", "gpt-4o"):
        try_agent(model, "openai")

    print("\nAnthropic-style (need ANTHROPIC_API_KEY + privysha[anthropic]):")
    try_agent("claude-3-haiku-20240307", "anthropic")

    print("\nHuggingFace-style (need privysha[transformers]):")
    try_agent("microsoft/DialoGPT-medium", "huggingface")

    print("\nOllama-style (need local Ollama server):")
    try_agent("llama3", "ollama")

    print("\nSmart routing:")
    agent = Agent(
        model="gpt-4o-mini",
        routing_config={"chat": "mock", "analysis": "mock"},
    )
    print(f"  analysis task: {agent.run('Analyze Q1 data', task_type='analysis')[:60]}...")

    print("\nCanonical imports:")
    print("  from privysha import Agent")
    print("  from privysha.integrations import wrap_llm")
    print("  from privysha.runtime.adapters.factory import AdapterFactory")


if __name__ == "__main__":
    main()
