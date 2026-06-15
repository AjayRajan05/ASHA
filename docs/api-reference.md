# API Reference

**PrivySHA v0.4.1** — canonical signatures and import paths.

---

## Import map

```python
# Root (only these)
from privysha import process, sanitize, optimize, Agent

# Subpackages
from privysha.integrations import wrap_llm, auto_patch
from privysha.runtime import PromptProcessor, ExecutionProfile
from privysha.types import ProcessResult, SanitizeResult, OptimizeResult, AgentResult
from privysha.core.policy_config import PolicyConfig, PolicyMode
from privysha.utils.dropin import process_async, optimize_async, sanitize_async
from privysha.utils.unmask import unmask
from privysha.runtime.local_advisor.advisor import recommend_local_model
from privysha.runtime.adapters.factory import AdapterFactory
from privysha.compat.legacy_results import to_legacy_pipeline_dict
```

---

## Result types

```python
result = process("prompt")  # ProcessResult

result.output
result.original
result.degraded
result.degraded_reason
result.security       # SecurityInfo | None
result.metrics        # MetricsInfo | None
result.trace          # dict | None (trace=True)
result.diff           # str | None (debug=True)
str(result)           # == result.output
result.to_dict()      # legacy dict shape
```

---

## process()

```python
from privysha import process
from privysha.core.policy_config import PolicyConfig

result = process(
    prompt: str,
    mode: str = "balanced",           # strict | balanced | lite | off
    *,
    policy: PolicyConfig | None = None,
    token_budget: int = 1200,
    trace: bool = False,
    debug: bool = False,
    max_retries: int = 0,
    timeout_seconds: float | None = None,
    verbose: bool = False,
    log_level: str = "INFO",
    log_output: str = "console",
    log_file: str | None = None,
    include_legacy_detail: bool = False,
) -> ProcessResult
```

| Mode | Behavior |
|------|----------|
| `strict` | Fail-closed — raises on total failure |
| `balanced` | Fail-open fallback (default) |
| `lite` | Minimal policy; fail-open |
| `off` | Passthrough |

`PolicyConfig` fields: `pii_mode`, `reversible`, `preserve_intent`, `security_level`, stage enable flags.

---

## sanitize()

```python
from privysha import sanitize

result = sanitize(
    prompt: str,
    mode: str = "balanced",
    *,
    policy: PolicyConfig | None = None,
    trace: bool = False,
    debug: bool = False,
    max_retries: int = 0,
    timeout_seconds: float | None = None,
    verbose: bool = False,
) -> SanitizeResult
```

---

## optimize()

```python
from privysha import optimize

result = optimize(
    prompt: str,
    *,
    token_budget: int = 1200,
    trace: bool = False,
    debug: bool = False,
    timeout_seconds: float | None = None,
) -> OptimizeResult
```

Token compression only — no security or compile stages.

---

## wrap_llm()

```python
from privysha.integrations import wrap_llm

client = wrap_llm(
    client,
    mode: str = "balanced",
    token_budget: int = 1200,
    auto_select_local_model: bool = False,
    sample_prompts: list[str] | None = None,
)
```

- `mode="off"` — no preprocessing
- Processing errors: strict raises; balanced degrades
- Wrap infrastructure errors raise when `mode != "off"`

---

## auto_patch()

```python
from privysha.integrations import auto_patch
from privysha.integrations.auto_patch import (
    get_patch_status,
    disable_auto_patch,
    enable_auto_patch,
)

auto_patch(mode: str = "strict", enable: bool = True, verbose: bool = False)
```

Globally patches installed SDKs. **Prefer `wrap_llm()`** for production.

---

## Async

```python
from privysha.utils.dropin import process_async, sanitize_async, optimize_async

result = await process_async("prompt", mode="balanced")
```

---

## unmask()

```python
from privysha.utils.unmask import unmask

restored = unmask(llm_output, masking_map)
```

Requires `policy=PolicyConfig(reversible=True)` during `process()` / `sanitize()`.

---

## Agent

```python
from privysha import Agent

agent = Agent(
    model: str = "gpt-4o-mini",
    privacy: bool = True,
    token_budget: int = 1200,
    provider: str | None = None,
    fallback_providers: list[dict] | None = None,
    routing_config: dict[str, str] | None = None,
    timeout: int = 10,
    retries: int = 3,
    api_key: str | None = None,
    local_model: str | None = None,
    sample_prompts: list[str] | None = None,
)

# Returns str by default
response = agent.run(prompt, trace=False, task_type="chat")

# Returns AgentResult when trace=True
result = agent.run(prompt, trace=True)
```

`privacy=True` → internal `mode="strict"`. `privacy=False` → `mode="off"`.

---

## PromptProcessor

```python
from privysha.runtime import PromptProcessor, ExecutionProfile

processor = PromptProcessor()
result = processor.run("prompt", mode="balanced", profile=ExecutionProfile(...))
```

---

## recommend_local_model()

```python
from privysha.runtime.local_advisor.advisor import recommend_local_model

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
)
```

Preview API — see [local-advisor.md](local-advisor.md).

---

## AdapterFactory

```python
from privysha.runtime.adapters.factory import AdapterFactory

adapter = AdapterFactory.create(provider="openai", model="gpt-4o-mini")
adapter = AdapterFactory.create(provider="mock")
adapter = AdapterFactory.create_smart_routing({"chat": "gpt-4o-mini"})
```

Providers: `openai`, `anthropic`, `gemini`, `ollama`, `huggingface`, `grok`, `mock`.

---

## Legacy dict

```python
from privysha.compat.legacy_results import to_legacy_pipeline_dict

legacy = to_legacy_pipeline_dict(
    process("prompt", include_legacy_detail=True)
)
```

---

## CLI

| Command | Description |
|---------|-------------|
| `privysha "prompt"` | Demo process |
| `privysha quick-test` | Built-in tests |
| `privysha examples` | Sample transformations |
| `privysha benchmark` | Benchmark harness |
| `privysha recommend` | PrivyFit advisor |

---

## Environment variables

| Variable | Used by |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI adapter |
| `ANTHROPIC_API_KEY` | Anthropic adapter |
| `GOOGLE_API_KEY` | Gemini adapter |
| `GROK_API_KEY` | Grok adapter |
| `PRIVYSHA_MODEL` | `Agent.from_env()` |
| `PRIVYSHA_TOKEN_BUDGET` | `Agent.from_env()` |
| `PRIVYSHA_CACHE_DIR` | Local advisor catalog |

`mode` is **not** read from env — set per call.

---

## Errors

| Exception | When |
|-----------|------|
| `PrivySHAProcessingError` | `mode="strict"` total failure |
| `TypeError` | Unknown kwargs on `process()` / `sanitize()` |
| `AttributeError` | Removed root exports (`wrap_llm`, `Pipeline`, etc.) |

See [migration-v0.4.md](migration-v0.4.md) and [deprecations.md](deprecations.md).
