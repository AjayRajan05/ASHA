# Quickstart Guide

**Get started with PrivySHA in 5 minutes** (v0.3.0 developer preview)

---

## Install

```bash
pip install privysha
```

Or from source:

```bash
pip install -e .
python examples/developer_preview_demo.py
```

---

## Process a prompt

```python
from privysha import process

# Returns a string by default
result = process("Hey bro analyze my dataset with john@email.com")
print(result)
# PII masked, filler reduced — exact output depends on mode
```

With metrics:

```python
result = process(
    "Contact john@example.com for data analysis",
    return_metrics=True,
)
print(result["optimized"])
print(f"Token reduction: {result['token_reduction']}%")
print(f"PII masked: {result.get('pii_masked', False)}")
```

---

## Privacy and security

PII is detected and masked automatically (emails, phones, SSNs, API keys, etc.):

```python
prompt = "Contact John at john@company.com or 555-123-4567"
result = process(prompt, mode="strict", return_metrics=True)
print(result["optimized"])
# Sensitive values replaced with [EMAIL_HASH]_..., [PHONE_HASH]_..., etc.
```

For regulated workloads, opt into fail-closed behavior:

```python
process(prompt, security_fail_closed=True)
```

---

## Wrap an LLM client

```python
from privysha import wrap_llm
import openai

client = openai.OpenAI()
secure = wrap_llm(client, mode="balanced", privacy=True)

response = secure.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Analyze data with john@email.com"}],
)
```

---

## Policy modes

| Mode | Behavior |
|------|----------|
| `balanced` | Default — security + optimization |
| `strict` | Maximum PII masking and optimization |
| `lite` | Minimal processing, faster |
| `off` | Passthrough — no modification |

```python
process(prompt, mode="lite")
process(prompt, mode="off")
```

---

## Debugging

```python
result = process(
    "Analyze data with john@example.com",
    trace=True,
    debug=True,
    return_metrics=True,
)
print(result.get("diff"))          # unified diff
print(result.get("trace"))         # stage trace
print(result.get("fallback_reason"))  # if pipeline fell back
```

Use `TraceContext` (via `trace=True`) instead of the deprecated `DebugTracer`.

---

## Async

```python
import asyncio
from privysha import process_async

async def main():
    result = await process_async("prompt", mode="balanced")
    print(result)

asyncio.run(main())
```

---

## PrivyFit (local model advisor)

```python
from privysha import recommend_local_model

report = recommend_local_model(
    prompts=["My email is john@x.com — analyze this dataset."],
    mode="strict",
    top=3,
)
print(report.top_pick.ollama_pull_name)
```

See [local-advisor.md](local-advisor.md).

---

## CLI

```bash
privysha "My email is john@gmail.com. Analyze this."
privysha quick-test
privysha examples
```

---

## Next steps

- [Getting Started](getting-started.md) — full setup guide
- [API Reference](api-reference.md) — all parameters
- [Benchmarks](benchmarks.md) — performance expectations
- [Developer Preview](developer-preview.md) — what to expect in 0.x
