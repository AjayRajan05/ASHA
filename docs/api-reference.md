# API Reference

**PrivySHA v0.3.0** — developer preview. See [developer-preview.md](developer-preview.md).

---

## Core functions

### process()

Full pipeline: security + optimization.

```python
from privysha import process

result = process(
    prompt: str,
    privacy: bool = True,
    token_budget: int = 1200,
    return_metrics: bool = False,
    debug: bool = False,
    security_level: str = "medium",
    verbose: bool = False,
    mode: str = "balanced",
    pii_mode: str = "rule",
    reversible: bool = False,
    security_fail_closed: bool = False,
    trace: bool = False,
    log_level: str = "INFO",
    log_output: str = "console",
    log_file: str | None = None,
    preserve_intent: bool = False,
    max_retries: int = 0,
    timeout_seconds: float | None = None,
) -> str | dict
```

**Modes:** `balanced`, `strict`, `lite`, `off`

**PII modes:** `rule`, `hybrid`, `ml_only`

**Returns:** `str` by default; `dict` when `return_metrics=True` or `debug=True`.

**Fail-safe:** Does not raise on pipeline errors (fail-open). Use `security_fail_closed=True` for regulated workloads.

---

### wrap_llm()

Wrap an LLM client so outgoing prompts are preprocessed.

```python
from privysha import wrap_llm

secure_client = wrap_llm(
    client,
    mode: str = "balanced",
    privacy: bool = True,
    auto_select_local_model: bool = False,
    sample_prompts: list[str] | None = None,
)
```

Returns a client with the same interface as the original. Supports OpenAI, Anthropic, and generic clients via `UniversalWrapper`.

---

### optimize()

Token optimization only — no security processing.

```python
from privysha import optimize

result = optimize(
    prompt: str,
    mode: str = "balanced",
    return_metrics: bool = False,
    token_budget: int = 1200,
)
```

---

### sanitize()

Security processing only — no optimization.

```python
from privysha import sanitize

result = sanitize(
    prompt: str,
    mode: str = "balanced",
    return_details: bool = False,
    reversible: bool = False,
    security_fail_closed: bool = False,
    pii_mode: str = "rule",
)
```

With `return_details=True`:

```python
{
    "sanitized": "...",
    "original": "...",
    "is_safe": True,
    "pii_detected": [...],
    "masking_map": {...},  # when reversible=True
}
```

---

### unmask()

Restore masked values in LLM output (requires `reversible=True` during sanitize/process).

```python
from privysha import unmask

restored = unmask(llm_output, masking_map)
```

---

### Async variants

```python
from privysha import process_async, optimize_async, sanitize_async

result = await process_async("prompt", mode="balanced")
```

---

## recommend_local_model()

PrivyFit local model advisor (preview).

```python
from privysha import recommend_local_model

report = recommend_local_model(
    prompts: list[str] | None = None,
    prompts_file: str | None = None,
    mode: str = "balanced",
    top: int = 5,
    gpu: str | None = None,
    vram_gb: float | None = None,
    cpu_only: bool = False,
    refresh_catalog: bool = False,
    preferred_quant: str | None = None,
    probe: bool = False,
) -> RecommendationReport
```

See [local-advisor.md](local-advisor.md).

---

## Agent

Pipeline + LLM adapter.

```python
from privysha import Agent

agent = Agent(
    model: str = "gpt-4o-mini",
    privacy: bool = True,
    token_budget: int = 1200,
    provider: str | None = None,
    fallback_providers: list[dict] | None = None,
    routing_config: dict | None = None,
    timeout: int = 10,
    retries: int = 3,
    api_key: str | None = None,
    local_model: str | None = None,
    sample_prompts: list[str] | None = None,
)
```

### run()

```python
result = agent.run(
    prompt: str,
    trace: bool = False,
    task_type: str = "chat",
) -> str | dict
```

Returns **string** response by default. With `trace=True`, returns full pipeline dict plus `response` and `adapter_info`.

### Other methods

- `run_with_fallback(prompt, trace=False, fallback_adapters=None)`
- `get_token_metrics(prompt)` — token counts for original vs optimized
- `print_debug_trace()` — print last trace to console

---

## Pipeline

Direct pipeline access for advanced use:

```python
from privysha import Pipeline

pipeline = Pipeline(
    privacy=True,
    token_budget=1200,
    security_level="MEDIUM",
    pii_mode="rule",
    policy_config=None,
    reversible=False,
)

result = pipeline.process(content="prompt", trace=False)
```

Result dict includes `prompts` (original, sanitized, optimized, compiled), `security_result`, `success`, and metrics.

---

## AdapterFactory

```python
from privysha import AdapterFactory

adapter = AdapterFactory.create(provider="openai", model="gpt-4o-mini")
adapter = AdapterFactory.create(provider="mock")
adapter = AdapterFactory.create_with_fallbacks(...)
adapter = AdapterFactory.create_smart_routing(routing_config)
```

Supported providers: `openai`, `anthropic`, `gemini`, `ollama`, `huggingface`, `grok`, `mock`.

---

## ModelRouter

```python
from privysha import ModelRouter, RoutingStrategy

router = ModelRouter(default_strategy=RoutingStrategy.HYBRID)
decision = router.route(ir, constraints={})
```

Strategies: `TASK_BASED`, `COST_BASED`, `PERFORMANCE_BASED`, `AVAILABILITY_BASED`, `HYBRID`, `LOCAL_PRIVACY`.

See [routing.md](routing.md).

---

## PolicyConfig

```python
from privysha import PolicyConfig, PolicyMode

config = PolicyConfig.from_mode(PolicyMode.BALANCED)
config = PolicyConfig.from_mode("strict", deterministic=True)
```

Modes: `BALANCED`, `STRICT`, `LITE`, `OFF`.

---

## auto_patch

Opt-in monkey-patch for OpenAI / Anthropic SDKs:

```python
from privysha import auto_patch, get_patch_status, disable_auto_patch

auto_patch()  # patches SDK to preprocess prompts
status = get_patch_status()
disable_auto_patch()
```

Experimental — may change before 1.0.

---

## CLI

Entry point: `privysha` (via `privysha.cli:main`).

| Command | Description |
|---------|-------------|
| `privysha "prompt"` | Process a prompt (demo) |
| `privysha quick-test` | Built-in test suite |
| `privysha examples` | Show example transformations |
| `privysha benchmark` | Run benchmark harness |
| `privysha recommend` | PrivyFit local model advisor |

Options on demo command: `--debug`, `--mode`, `--stages`, `--context`, `--debug-mode`.

---

## Framework integrations

Lazy-loaded from `privysha`:

```python
from privysha import (
    add_privysha_to_fastapi,
    wrap_langchain_llm,
    compose_with_instructor,
    compose_with_guardrails,
    compose_with_langchain,
    enable_otel,
)
```

See [integrations.md](integrations.md).

---

## Environment variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | OpenAI adapter | API key |
| `ANTHROPIC_API_KEY` | Anthropic adapter | API key |
| `GOOGLE_API_KEY` | Gemini adapter | API key |
| `GROK_API_KEY` | Grok adapter | API key |
| `PRIVYSHA_MODEL` | `Agent.from_env()` | Default model |
| `PRIVYSHA_TOKEN_BUDGET` | `Agent.from_env()` | Default token budget |
| `PRIVYSHA_CACHE_DIR` | Local advisor catalog | Cache directory |

Note: `PRIVYSHA_MODE` is **not** read by the library — set `mode` per call.

---

## Response format reference

### process() with return_metrics=True

```python
{
    "optimized": "processed prompt",
    "original": "original prompt",
    "token_reduction": 12,
    "pii_masked": True,
    "security_result": {
        "is_safe": True,
        "masked_entities": ["email"],
    },
    "metrics": {
        "tokens_saved": 5,
        "cost_reduction": "8%",
        "processing_time_ms": 45,
        "pii_detected": ["email"],
        "risk_level": "low",
        "threats_blocked": 0,
    },
}
```

With `debug=True`, also includes `fallback_reason`, `original_error`, and `changes`.

---

## Lazy-loaded advanced symbols

These load on first access (PEP 562):

`PromptIR`, `IRBuilder`, `SecurityLayer`, `PromptOptimizer`, `HybridPIIDetector`, `DiffEngine`, `BenchmarkHarness`, `TraceContext`, `MetricsDashboard`, and integration helpers.

Full list in `src/privysha/__init__.py` → `__all__`.
