# Routing

**PrivySHA v0.3.0** — intelligent model selection (preview).

---

## Overview

The `ModelRouter` in `routing/model_router.py` selects the best LLM provider and model based on task IR, cost, performance, availability, and privacy constraints.

Routing runs as stage 3 of the pipeline and is also used by `Agent` when `routing_config` is provided.

---

## RoutingStrategy enum

```python
from privysha import RoutingStrategy

RoutingStrategy.TASK_BASED        # Match model to task intent
RoutingStrategy.COST_BASED        # Minimize cost
RoutingStrategy.PERFORMANCE_BASED # Minimize latency
RoutingStrategy.AVAILABILITY_BASED # Prefer available models
RoutingStrategy.HYBRID            # Balance all factors (default)
RoutingStrategy.LOCAL_PRIVACY     # Force local model (PrivyFit)
```

---

## Basic usage

```python
from privysha import ModelRouter, RoutingStrategy, IRBuilder

builder = IRBuilder()
ir = builder.generate("Analyze this dataset for anomalies")

router = ModelRouter(default_strategy=RoutingStrategy.HYBRID)
decision = router.route(ir)

print(decision.selected_model.name)
print(decision.selected_model.provider)
print(decision.reasoning)
print(decision.confidence_score)
```

---

## LOCAL_PRIVACY strategy

Forces local model selection via PrivyFit:

```python
router = ModelRouter(default_strategy=RoutingStrategy.LOCAL_PRIVACY)
decision = router.route(
    ir,
    constraints={
        "sample_prompts": ["My email is john@x.com — analyze dataset."],
        "mode": "strict",
        "force_local": True,
    },
)
```

See [local-advisor.md](local-advisor.md).

---

## Agent routing

### Smart routing

```python
from privysha import Agent

agent = Agent(
    model="gpt-4o-mini",
    routing_config={
        "analyze": {"provider": "openai", "model": "gpt-4o"},
        "summarize": {"provider": "openai", "model": "gpt-4o-mini"},
    },
)
```

When `routing_config` is set, `AdapterFactory.create_smart_routing()` is used.

### Fallback providers

```python
agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "ollama", "model": "llama3"},
    ],
)
```

### Auto local model (PrivyFit)

```python
agent = Agent(
    local_model="auto",
    sample_prompts=["Analyze customer feedback with PII."],
    privacy=True,
)
```

---

## wrap_llm auto-select

```python
from privysha import wrap_llm

secure = wrap_llm(
    client,
    auto_select_local_model=True,
    sample_prompts=["Analyze dataset with PII."],
)
```

Uses the last `recommend_local_model()` report or runs recommendation internally.

---

## ModelConfig

Each routable model is described by a `ModelConfig`:

```python
@dataclass
class ModelConfig:
    name: str
    provider: str
    capability: ModelCapability
    cost_per_1k_tokens: float
    avg_latency_ms: int
    max_tokens: int
    supports_streaming: bool
    reliability_score: float
    specializations: list[str]
```

---

## RoutingDecision

```python
@dataclass
class RoutingDecision:
    selected_model: ModelConfig
    routing_strategy: RoutingStrategy
    confidence_score: float
    reasoning: str
    alternative_models: list[ModelConfig]
    estimated_cost: float
    estimated_latency: int
```

---

## Provider inference

`Agent` auto-detects provider from model name:

| Model pattern | Provider |
|---------------|----------|
| `gpt-*` | openai |
| `claude-*` | anthropic |
| `gemini-*` | gemini |
| `grok-*` | grok |
| `org/model` | huggingface |
| `mock` | mock |
| Other | ollama |

Override with `provider=` kwarg.

---

## Status

Model routing is **preview** in 0.3.0. APIs and default strategies may change before 1.0.0.

---

## Related docs

- [Local Model Advisor](local-advisor.md) — PrivyFit integration
- [Model Gateway](model-gateway.md) — adapter and wrap_llm patterns
- [Pipeline](pipeline.md) — routing stage
