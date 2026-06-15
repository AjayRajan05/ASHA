#!/usr/bin/env python3
"""
PrivySHA developer preview — minimal end-to-end demo (no API keys required).

Run from repo root:
    pip install -e .
    python examples/developer_preview_demo.py
"""

from privysha import process
from privysha.runtime.local_advisor.advisor import recommend_local_model


def main() -> None:
    prompt = (
        "Hey! My email is alex@company.com — please analyze this sales dataset "
        "and suggest anomalies."
    )

    print("=== 1. Drop-in prompt processing ===")
    result = process(prompt, mode="balanced")
    print("Original :", prompt)
    print("Optimized:", result.output)
    if result.security:
        print("PII types :", result.security.pii_detected)
    if result.metrics:
        print("Token reduction:", f"{result.metrics.token_reduction_pct}%")

    print("\n=== 2. PrivyFit local model hint (offline catalog OK) ===")
    report = recommend_local_model(
        prompts=[prompt, "Write a Python function to validate JWT tokens."],
        mode="balanced",
        gpu="RTX 4090",
        top=1,
    )
    pick = report.top_pick
    if pick:
        print("Top pick  :", pick.model_id)
        print("Ollama    :", pick.ollama_pull_name)
        print("Reason    :", pick.reasoning)
    else:
        print("No model fit this simulated hardware/workload profile.")

    print("\nDone. Feedback welcome: https://github.com/AjayRajan05/privySHA/issues")


if __name__ == "__main__":
    main()
