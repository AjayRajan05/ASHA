#!/usr/bin/env python3
"""ASHA drop-in examples (v0.4.2). No API keys required."""

from asha import Agent, optimize, process, sanitize
from asha.core.policy_config import PolicyConfig
from asha.integrations import wrap_llm

ORIGINAL = (
    "Hey bro can you please help me analyze this dataset for anomalies? "
    "Contact john@email.com for details."
)


def example_process() -> None:
    print("=== process() ===")
    result = process(ORIGINAL, mode="balanced")
    print(f"Original : {ORIGINAL}")
    print(f"Output   : {result.output}")
    if result.security:
        print(f"PII      : {result.security.pii_detected}")
    if result.metrics:
        print(f"Reduction: {result.metrics.token_reduction_pct:.1f}%")
    print()


def example_optimize() -> None:
    print("=== optimize() ===")
    wordy = (
        "Hey there! I was wondering if you could possibly help me by analyzing "
        "this dataset and letting me know if there are any unusual patterns?"
    )
    result = optimize(wordy)
    print(f"Original : {wordy[:60]}...")
    print(f"Output   : {result.output[:80]}...")
    if result.metrics:
        print(f"Reduction: {result.metrics.token_reduction_pct:.1f}%")
    print()


def example_sanitize() -> None:
    print("=== sanitize() ===")
    sensitive = (
        "Send results to john@email.com or call 555-123-4567. "
        "Card: 4111-1111-1111-1111."
    )
    result = sanitize(sensitive, policy=PolicyConfig(reversible=True))
    print(f"Original : {sensitive}")
    print(f"Output   : {result.output}")
    print(f"Safe     : {result.safe}")
    print()


def example_wrap_llm_mock() -> None:
    print("=== wrap_llm() with mock client ===")

    class MockClient:
        def generate(self, prompt: str) -> str:
            return f"Model saw: {prompt[:80]}..."

    client = wrap_llm(MockClient(), mode="balanced")
    out = client.generate("Analyze data from john@email.com")
    print(out)
    print()


def example_agent() -> None:
    print("=== Agent (mock) ===")
    agent = Agent(model="mock", privacy=True)
    print(agent.run("Summarize dataset with john@email.com"))
    print()


def example_integration_pattern() -> None:
    print("=== One-line integration pattern ===")

    def chatbot(user_input: str) -> str:
        safe = process(user_input, mode="balanced").output
        return f"Response to: {safe}"

    for msg in [
        "Hey bro help me analyze customer data",
        "Email manager@company.com about the report",
    ]:
        print(f"User: {msg}")
        print(f"Bot : {chatbot(msg)}")
    print()


if __name__ == "__main__":
    example_process()
    example_optimize()
    example_sanitize()
    example_wrap_llm_mock()
    example_agent()
    example_integration_pattern()
    print("Done.")
