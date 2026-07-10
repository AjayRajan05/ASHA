# Examples

**ASHA v0.4.2** - copy-paste patterns with valid imports.

---

## Basic processing

```python
from asha import process

result = process("My email is john@example.com. Analyze this dataset.")
print(result)                          # str → optimized output
print(result.security.pii_detected)
print(result.metrics.token_reduction_pct)
```

---

## Strict mode (regulated workloads)

```python
from asha import process

result = process("Sensitive prompt with PII", mode="strict")
```

Raises `ASHAProcessingError` on total failure instead of degraded fallback.

---

## Wrap OpenAI client

```python
import os
from asha.integrations import wrap_llm
import openai

os.environ["OPENAI_API_KEY"] = "your-key"
client = wrap_llm(openai.OpenAI(), mode="balanced")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Data from john@example.com"}],
)
```

---

## Security only

```python
from asha import sanitize
from asha.core.policy_config import PolicyConfig

result = sanitize(
    "Contact john@corp.com",
    policy=PolicyConfig(reversible=True),
)
print(result.output)
print(result.security.masking_map)
```

---

## Optimize only

```python
from asha import optimize

result = optimize("Hey bro can you please analyze this dataset")
print(result.output)
```

---

## Hybrid PII

```python
from asha import process
from asha.core.policy_config import PolicyConfig

result = process(
    "Contact john@example.com",
    policy=PolicyConfig(pii_mode="hybrid"),
)
```

Requires `pip install asha[ml]`.

---

## Agent with mock (no API key)

```python
from asha import Agent

agent = Agent(model="mock", privacy=True)
print(agent.run("Summarize sales data from john@example.com"))
```

---

## Agent with tracing

```python
from asha import Agent

agent = Agent(model="mock")
result = agent.run("prompt", trace=True)
print(result.output)
print(result.response)
```

---

## Smart routing

```python
from asha import Agent

agent = Agent(
    model="gpt-4o-mini",
    routing_config={
        "chat": "gpt-4o-mini",
        "analysis": "gpt-4o",
    },
)
agent.run("Analyze Q1 revenue", task_type="analysis")
```

---

## Async

```python
import asyncio
from asha.utils.dropin import process_async

async def main():
    result = await process_async("prompt", mode="balanced")
    print(result.output)

asyncio.run(main())
```

---

## Trace and diff

```python
from asha import process

result = process("john@x.com - analyze", trace=True, debug=True)
print(result.trace)
print(result.diff)
```

---

## Local model advisor (preview)

```python
from asha.runtime.local_advisor.advisor import recommend_local_model

report = recommend_local_model(
    prompts=["Summarize with john@x.com"],
    mode="balanced",
    top=3,
)
print(report.top_pick)
```

---

## Related

- [api-reference.md](api-reference.md)
- [getting-started.md](getting-started.md)
