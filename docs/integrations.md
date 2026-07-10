# Integrations

**ASHA v0.4.2** - framework middleware and LLM wrapping.

---

## wrap_llm (recommended)

```python
from asha.integrations import wrap_llm
import openai

client = wrap_llm(openai.OpenAI(), mode="balanced")
```

Import from **`asha.integrations`**, not root.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `mode` | `balanced` | `strict`, `lite`, `off` |
| `token_budget` | `1200` | Passed to internal `process()` |

---

## auto_patch (use with caution)

```python
from asha.integrations import auto_patch, disable_auto_patch

auto_patch(mode="strict")
# ... application code ...
disable_auto_patch()
```

Globally monkey-patches SDKs. Prefer per-client `wrap_llm()` in production.

---

## Framework middleware

Install extras first:

```bash
pip install asha[integrations]
# or specific: asha[fastapi], asha[langchain], etc.
```

| Framework | Module |
|-----------|--------|
| FastAPI | `asha.integrations.fastapi` |
| Flask | `asha.integrations.flask` |
| Django | `asha.integrations.django` |
| LangChain | `asha.integrations.langchain` |
| LlamaIndex | `asha.integrations.llamaindex` |
| Instructor | `asha.integrations.composition_strategy` |
| OpenTelemetry | `asha.integrations.otel` |

Middleware uses `mode="balanced"` or `mode="off"` - not the removed `privacy=` kwarg.

---

## Composition helpers

```python
from asha.integrations.composition_strategy import (
    compose_with_instructor,
    compose_with_langchain,
)
```

Requires optional deps (`instructor`, `langchain`).

---

## Testing integrations locally

Integration tests skip when optional deps are missing:

```bash
pip install asha[integrations]
pytest tests/test_fastapi_integration.py -q
```

---

## Related

- [model-gateway.md](model-gateway.md) - adapters
- [api-reference.md](api-reference.md)
