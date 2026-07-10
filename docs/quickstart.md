# Quickstart Guide

**Get started with ASHA in 5 minutes** (v0.4.2 developer preview)

---

## Install

```bash
pip install asha
```

Or from source:

```bash
pip install -e .
python examples/developer_preview_demo.py
```

---

## Process a prompt

```python
from asha import process

result = process("Hey bro analyze my dataset with john@email.com")
print(result)  # ProcessResult - str() returns optimized output
```

With typed fields:

```python
result = process("Contact john@example.com for data analysis", mode="balanced")
print(result.output)
print(result.metrics)
print(result.security)
```

---

## Privacy and security

PII is detected and masked automatically (emails, phones, SSNs, API keys, etc.):

```python
prompt = "Contact John at john@company.com or 555-123-4567"
result = process(prompt, mode="strict")
print(result.output)
# Sensitive values replaced with [EMAIL_HASH]_..., [PHONE_HASH]_..., etc.
```

For regulated workloads, use fail-closed mode:

```python
process(prompt, mode="strict")
```

---

## Wrap an LLM client

```python
from asha.integrations import wrap_llm
import openai

client = openai.OpenAI()
secure = wrap_llm(client, mode="balanced")

response = secure.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Analyze data with john@email.com"}],
)
```

Use `mode="off"` for passthrough without preprocessing.

---

## Policy modes

| Mode | Behavior |
|------|----------|
| `balanced` | Default - security + optimization |
| `strict` | Fail-closed on total failure |
| `lite` | Minimal policy features |
| `off` | Passthrough - no modification |

```python
process(prompt, mode="lite")
process(prompt, mode="off")
```

Advanced policy via `PolicyConfig`:

```python
from asha.core.policy_config import PolicyConfig

process(prompt, policy=PolicyConfig(pii_mode="hybrid", reversible=True))
```

---

## Debugging

```python
result = process(
    "Analyze data with john@example.com",
    trace=True,
    debug=True,
)
print(result.trace)
print(result.diff)
```

---

## Async

```python
import asyncio
from asha.utils.dropin import process_async

async def main():
    result = await process_async("prompt", mode="balanced")
    print(result)

asyncio.run(main())
```

---

## Agent

```python
from asha import Agent

agent = Agent(model="mock")
response = agent.run("Summarize this dataset")
print(response)
```

---

## Canonical imports

```python
from asha import process, sanitize, optimize, Agent
from asha.runtime import PromptProcessor
from asha.integrations import wrap_llm, auto_patch
from asha.types import ProcessResult
from asha.core.policy_config import PolicyConfig
```

See [api-reference.md](api-reference.md) and [deprecations.md](deprecations.md).
