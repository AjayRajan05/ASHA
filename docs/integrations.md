# Integrations

**PrivySHA v0.4.1** — framework middleware and LLM wrapping.

---

## wrap_llm (recommended)

```python
from privysha.integrations import wrap_llm
import openai

client = wrap_llm(openai.OpenAI(), mode="balanced")
```

Import from **`privysha.integrations`**, not root.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `mode` | `balanced` | `strict`, `lite`, `off` |
| `token_budget` | `1200` | Passed to internal `process()` |

---

## auto_patch (use with caution)

```python
from privysha.integrations import auto_patch, disable_auto_patch

auto_patch(mode="strict")
# ... application code ...
disable_auto_patch()
```

Globally monkey-patches SDKs. Prefer per-client `wrap_llm()` in production.

---

## Framework middleware

Install extras first:

```bash
pip install privysha[integrations]
# or specific: privysha[fastapi], privysha[langchain], etc.
```

| Framework | Module |
|-----------|--------|
| FastAPI | `privysha.integrations.fastapi` |
| Flask | `privysha.integrations.flask` |
| Django | `privysha.integrations.django` |
| LangChain | `privysha.integrations.langchain` |
| LlamaIndex | `privysha.integrations.llamaindex` |
| Instructor | `privysha.integrations.composition_strategy` |
| OpenTelemetry | `privysha.integrations.otel` |

Middleware uses `mode="balanced"` or `mode="off"` — not the removed `privacy=` kwarg.

---

## Composition helpers

```python
from privysha.integrations.composition_strategy import (
    compose_with_instructor,
    compose_with_langchain,
)
```

Requires optional deps (`instructor`, `langchain`).

---

## Testing integrations locally

Integration tests skip when optional deps are missing:

```bash
pip install privysha[integrations]
pytest tests/test_fastapi_integration.py -q
```

---

## Related

- [model-gateway.md](model-gateway.md) — adapters
- [api-reference.md](api-reference.md)
