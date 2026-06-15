# Getting Started

**PrivySHA v0.4.1** — install, run your first prompt, wrap a client.

---

## Install

```bash
pip install privysha
```

Requires **Python 3.10+**.

### Optional extras

```bash
pip install privysha[openai]         # OpenAI adapter + wrap_llm
pip install privysha[anthropic]      # Anthropic
pip install privysha[gemini]         # Google Gemini
pip install privysha[ml]             # Hybrid PII (spaCy + transformers)
pip install privysha[integrations]   # Framework middleware
pip install privysha[local-advisor]  # PrivyFit catalog
pip install privysha[all]            # Everything
```

### Verify

```python
from privysha import process

result = process("Hello world")
print(result.output)
```

---

## Your first prompt

```python
from privysha import process

result = process("My email is john@gmail.com. Analyze this dataset.")
print(result)                              # optimized string
print(result.security.pii_detected)        # ['email', ...]
print(result.metrics.token_reduction_pct)  # e.g. 12.0
```

`process()` always returns a **`ProcessResult`** dataclass. `str(result)` equals `result.output`.

---

## Wrap an LLM client

```python
from privysha.integrations import wrap_llm
import openai

client = wrap_llm(openai.OpenAI(), mode="balanced")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Email john@corp.com about Q1 data"}],
)
```

Requires `pip install privysha[openai]` and `OPENAI_API_KEY`.

Use `mode="off"` to disable preprocessing. Use `mode="strict"` for fail-closed behavior.

---

## Processing modes

| Mode | Behavior |
|------|----------|
| `balanced` | Default — security + optimization, fail-open on errors |
| `strict` | Fail-closed — raises `PrivySHAProcessingError` on total failure |
| `lite` | Minimal policy features, same fail-open semantics as balanced |
| `off` | Passthrough — prompt unchanged |

```python
process(prompt, mode="strict")
process(prompt, mode="off")
```

---

## Advanced policy

PII mode, reversible masking, and other knobs use `PolicyConfig`:

```python
from privysha.core.policy_config import PolicyConfig

process(
    prompt,
    policy=PolicyConfig(pii_mode="hybrid", reversible=True),
)
```

`pii_mode="hybrid"` requires `pip install privysha[ml]`.

---

## Separate functions

```python
from privysha import sanitize, optimize

sanitize("john@x.com")   # security only → SanitizeResult
optimize("long prompt")  # tokens only → OptimizeResult
```

---

## Agent

Preprocess and call an LLM in one step:

```python
from privysha import Agent

agent = Agent(model="mock", privacy=True)
print(agent.run("Analyze sales with john@example.com"))
```

`privacy=True` maps to `mode="strict"` internally. `privacy=False` disables preprocessing.

With tracing:

```python
result = agent.run("prompt", trace=True)  # AgentResult
print(result.output)
print(result.response)
```

---

## CLI

```bash
privysha "My email is john@gmail.com — analyze data"
privysha "prompt" --debug --mode strict
privysha quick-test
privysha benchmark --save
privysha recommend --prompt "Analyze dataset" --gpu "RTX 4090"
```

---

## API keys

`process()` and `sanitize()` work **without** API keys. LLM adapters need provider credentials:

```bash
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
export GOOGLE_API_KEY=...
```

---

## Next steps

1. [Core Concepts](core-concepts.md) — results, modes, policy
2. [API Reference](api-reference.md) — full signatures
3. [Security](security.md) — PII and fail-closed behavior
4. [Migration v0.4](migration-v0.4.md) — if upgrading from 0.3.x
