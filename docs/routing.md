# Routing

**ASHA v0.4.2** - task-based model selection via `Agent`.

The standalone `ModelRouter` class was removed in v0.4.1. Routing is handled by `SmartRoutingAdapter` when you pass `routing_config` to `Agent`.

---

## Smart routing

```python
from asha import Agent

agent = Agent(
    routing_config={
        "chat": "gpt-4o-mini",
        "analysis": "gpt-4o",
        "code": "gpt-4o",
    },
)

response = agent.run("Analyze Q1 revenue", task_type="analysis")
```

`task_type` selects which entry in `routing_config` to use.

---

## Fallback providers

```python
agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku-20240307"},
        {"provider": "ollama", "model": "llama3"},
    ],
)
```

Use `agent.run_with_fallback()` for explicit fallback behavior.

---

## Local model (AshaFit)

```python
agent = Agent(
    local_model="auto",
    sample_prompts=["Analyze customer feedback with PII."],
    privacy=True,
)
```

AshaFit picks a local model from your prompt corpus and hardware. Preview API - see [local-advisor.md](local-advisor.md).

---

## wrap_llm auto-select

```python
from asha.integrations import wrap_llm

client = wrap_llm(
    ollama_client,
    auto_select_local_model=True,
    sample_prompts=["Typical prompts from your app..."],
)
```

---

## Provider auto-detection

`Agent` infers provider from model name when `provider` is omitted:

| Pattern | Provider |
|---------|----------|
| `gpt-*` | openai |
| `claude-*` | anthropic |
| `gemini-*` | gemini |
| `grok-*` | grok |
| `org/model` | huggingface |
| `mock` | mock |
| Other | ollama |

Override with `provider="openai"` etc.

---

## What was removed

| Removed (v0.4.2) | Replacement |
|------------------|---------------|
| `ModelRouter` | `Agent(routing_config=...)` |
| `RoutingStrategy` enum | Task-type dict keys |
| IR-based `router.route(ir)` | Not exposed in public API |

---

## Status

Smart routing is **preview** - `routing_config` shape may evolve before 1.0.0.

---

## Related

- [local-advisor.md](local-advisor.md)
- [model-gateway.md](model-gateway.md)
- [pipeline.md](pipeline.md)
