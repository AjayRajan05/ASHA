#!/usr/bin/env python3
"""
Provider smoke tests (v0.4.2).

Tests basic APIs without keys; optional provider tests when API keys are set.
"""

import os
import time

from asha import Agent, optimize, process, sanitize
from asha.core.policy_config import PolicyConfig
from asha.integrations import wrap_llm

TEST_PROMPT = (
    "Hey bro can you please help me analyze this dataset for anomalies? "
    "Contact john@email.com for details."
)


def test_basic_functionality() -> None:
    print("=== Basic ASHA APIs ===")

    result = process(TEST_PROMPT, mode="balanced")
    print(f"process output : {result.output[:80]}...")
    if result.metrics:
        print(f"token reduction: {result.metrics.token_reduction_pct:.1f}%")
    if result.security:
        print(f"safe           : {result.security.safe}")

    opt = optimize(TEST_PROMPT)
    print(f"optimize output: {opt.output[:80]}...")

    san = sanitize(TEST_PROMPT, policy=PolicyConfig(reversible=True))
    print(f"sanitize output: {san.output[:80]}...")
    print(f"sanitize safe  : {san.safe}")
    print("Basic tests OK.\n")


def test_agent_mock() -> None:
    print("=== Agent (mock) ===")
    agent = Agent(model="mock", privacy=True)
    traced = agent.run(TEST_PROMPT, trace=True)
    print(f"processed: {traced.output[:60]}...")
    print(f"response : {str(traced.response)[:60]}...")
    if traced.metrics:
        print(f"reduction: {traced.metrics.token_reduction_pct:.1f}%")
    print("Agent mock OK.\n")


def test_openai() -> None:
    print("=== OpenAI (optional) ===")
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set - skipped.\n")
        return
    try:
        import openai

        client = wrap_llm(openai.OpenAI(), mode="balanced")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Summarize: dataset with john@email.com",
                }
            ],
            max_tokens=40,
        )
        print(response.choices[0].message.content[:100])
        agent = Agent(model="gpt-4o-mini", privacy=True)
        result = agent.run("Analyze dataset anomalies", trace=True)
        print(f"Agent output: {str(result.response)[:80]}...")
        print("OpenAI OK.\n")
    except ImportError:
        print("openai not installed - skipped.\n")
    except Exception as exc:
        print(f"OpenAI failed: {exc}\n")


def test_gemini() -> None:
    print("=== Gemini (optional) ===")
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY / GEMINI_API_KEY not set - skipped.\n")
        return
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        client = wrap_llm(genai.GenerativeModel("gemini-1.5-flash"), mode="balanced")
        response = client.generate_content("Summarize dataset with john@email.com")
        print(str(response.text)[:100])
        print("Gemini OK.\n")
    except ImportError:
        print("google-generativeai not installed - skipped.\n")
    except Exception as exc:
        print(f"Gemini failed: {exc}\n")


def test_anthropic() -> None:
    print("=== Anthropic (optional) ===")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set - skipped.\n")
        return
    try:
        import anthropic

        client = wrap_llm(anthropic.Anthropic(), mode="balanced")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=40,
            messages=[
                {
                    "role": "user",
                    "content": "Summarize dataset with john@email.com",
                }
            ],
        )
        print(response.content[0].text[:100])
        print("Anthropic OK.\n")
    except ImportError:
        print("anthropic not installed - skipped.\n")
    except Exception as exc:
        print(f"Anthropic failed: {exc}\n")


def test_performance() -> None:
    print("=== Batch performance ===")
    prompts = [
        "Hey bro analyze this dataset for anomalies",
        "Review customer data and email sarah@company.com",
        "Help me understand these financial records",
        "Check logs and contact support@help.com if needed",
        "Analyze user behavior patterns and recommend actions",
    ]
    start = time.time()
    results = [process(p, mode="balanced") for p in prompts]
    elapsed = time.time() - start
    avg_reduction = sum(
        r.metrics.token_reduction_pct for r in results if r.metrics
    ) / len(results)
    print(f"{len(prompts)} prompts in {elapsed:.2f}s ({elapsed / len(prompts):.3f}s each)")
    print(f"avg token reduction: {avg_reduction:.1f}%")
    print("Performance OK.\n")


def test_wrap_llm_mock() -> None:
    print("=== wrap_llm mock clients ===")

    class MockOpenAI:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    content = kwargs["messages"][0]["content"]
                    return type(
                        "R",
                        (),
                        {
                            "choices": [
                                type(
                                    "C",
                                    (),
                                    {
                                        "message": type(
                                            "M", (), {"content": content}
                                        )()
                                    },
                                )()
                            ]
                        },
                    )()

    wrapped = wrap_llm(MockOpenAI(), mode="balanced")
    out = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": "Data from john@email.com"}]
    )
    text = out.choices[0].message.content
    print(f"wrapped call returned: {text[:60]}...")
    print("wrap_llm OK.\n")


def main() -> None:
    print("ASHA provider testing (v0.4.2)")
    print("=" * 50)
    test_basic_functionality()
    test_agent_mock()
    test_wrap_llm_mock()
    test_performance()
    test_openai()
    test_gemini()
    test_anthropic()
    print("=" * 50)
    print("Done.")


if __name__ == "__main__":
    main()
