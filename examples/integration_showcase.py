#!/usr/bin/env python3
"""
Integration showcase (v0.4.2). Prints copy-paste snippets and runs one live demo.
"""

import json

from asha import process
from asha.integrations import wrap_llm

print("=" * 80)
print("ASHA INTEGRATION SHOWCASE (v0.4.2)")
print("=" * 80)

# 1. Direct usage
print("\n1. Direct usage")
print("-" * 60)
print("from asha import process")
print('result = process("Hey bro analyze this dataset", mode="balanced")')
print("print(result.output)")

prompt = (
    "Hey bro can you please help me analyze this dataset for anomalies? "
    "Contact john@email.com for details."
)
result = process(prompt, mode="balanced", debug=True)
print(f"\nBEFORE : {prompt}")
print(f"AFTER  : {result.output}")
if result.metrics:
    print(f"METRICS: {json.dumps(result.metrics.to_dict(), indent=2)}")

# 2. FastAPI
print("\n\n2. FastAPI (30 seconds)")
print("-" * 60)
print("from asha.integrations.fastapi import add_asha_middleware")
print('add_asha_middleware(app, privacy=True)  # maps to mode="balanced"')

# 3. Flask / Django
print("\n\n3. Flask / Django")
print("-" * 60)
print("from asha.integrations.flask import ASHAMiddleware")
print("ASHAMiddleware(app)")
print("# Django: add asha.integrations.django.middleware.ASHAMiddleware")

# 4. wrap_llm
print("\n\n4. wrap_llm (any provider client)")
print("-" * 60)
print("from asha.integrations import wrap_llm")
print('secure = wrap_llm(openai_client, mode="balanced")')

class _Mock:
    def generate(self, text: str) -> str:
        return f"ok: {text[:40]}"

wrapped = wrap_llm(_Mock(), mode="balanced")
print(f"\nLive mock: {wrapped.generate('john@email.com')}")

# 5. Agent
print("\n\n5. Agent")
print("-" * 60)
print("from asha import Agent")
print('agent = Agent(model="gpt-4o-mini", privacy=True)')
print("response = agent.run(prompt)")
print("details  = agent.run(prompt, trace=True)  # AgentResult")

# 6. Composition (Instructor)
print("\n\n6. Instructor composer")
print("-" * 60)
print("from asha.integrations.composition_strategy import compose_with_instructor")

# 7. Integration times (illustrative)
print("\n\n7. Typical integration effort")
print("-" * 60)
rows = [
    ("Direct process()", "10s", "process(prompt, mode='balanced')"),
    ("FastAPI middleware", "30s", "add_asha_middleware(app)"),
    ("wrap_llm client", "30s", "wrap_llm(client)"),
    ("Agent", "45s", "Agent(model=..., privacy=True)"),
]
print(f"{'Pattern':<22} {'Time':<8} {'Code'}")
print("-" * 70)
for name, t, code in rows:
    print(f"{name:<22} {t:<8} {code}")

print("\n" + "=" * 80)
print("See examples/ and docs/examples.md for runnable scripts.")
print("=" * 80)
