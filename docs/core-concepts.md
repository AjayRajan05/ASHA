# Core Concepts

**v0.3.0 developer preview**

PrivySHA is a prompt compiler layer between your application and LLM providers. It transforms raw user input into structured, privacy-safe, token-efficient prompts.

---

## Primary API surface

| Function | Purpose |
|----------|---------|
| `process()` | Full pipeline — security + optimization |
| `wrap_llm()` | Wrap an existing LLM client |
| `optimize()` | Token optimization only |
| `sanitize()` | Security / PII masking only |
| `Agent` | Pipeline + LLM adapter |
| `recommend_local_model()` | PrivyFit local model advisor (preview) |

Async variants: `process_async`, `optimize_async`, `sanitize_async`.

Utility: `unmask()` for reversible masking (opt-in).

There is **no** global `configure()` function. Pass parameters per call or use `PolicyConfig` / `Agent` kwargs.

---

## Policy modes

Modes control how aggressively PrivySHA applies security and optimization. Implemented via `PolicyConfig` presets in `core/policy_config.py`.

| Mode | Security | Optimization | Use case |
|------|----------|--------------|----------|
| `balanced` | Standard PII + injection checks | Moderate token reduction | Default for most apps |
| `strict` | Maximum PII masking | Aggressive optimization | High-privacy workloads |
| `lite` | Basic checks only | Minimal changes | Low-latency paths |
| `off` | Disabled (passthrough) | Disabled | Testing, A/B baselines |

```python
from privysha import process

process("prompt", mode="balanced")  # default
process("prompt", mode="strict")
process("prompt", mode="lite")
process("prompt", mode="off")
```

`mode="off"` bypasses pipeline stages via the policy gate — the prompt is returned unchanged (no PII scrub).

---

## PII detection modes

Separate from policy mode — controls **how** PII is detected:

| `pii_mode` | Description | Requires |
|------------|-------------|----------|
| `rule` | Regex + heuristic detection (default) | Core package only |
| `hybrid` | Rules + ML models | `pip install privysha[ml]` |
| `ml_only` | ML-only (experimental) | `pip install privysha[ml]` |

If ML dependencies are missing, `hybrid` / `ml_only` fall back to `rule` with a warning.

---

## Security levels

`security_level` on `process()` maps to `SecurityLevel` internally:

| Level | Behavior |
|-------|----------|
| `low` | Basic PII detection |
| `medium` | Standard (default) |
| `high` | Enhanced detection and masking |

CLI `--mode` maps to security level: `balanced→medium`, `strict→high`, `lite→low`.

---

## Fail-safe design

By default, `process()` **does not raise** on pipeline errors. It returns a security-scrubbed fallback (fail-open).

For regulated workloads:

```python
process(prompt, security_fail_closed=True)
```

With `debug=True`, failed pipelines include `fallback_reason` and `original_error` in the response dict.

---

## Reversible masking

Opt-in only — use when you need to restore masked values in LLM output:

```python
from privysha import sanitize, unmask

result = sanitize("Email alice@corp.com", return_details=True, reversible=True)
safe_prompt = result["sanitized"]
llm_output = "Reply to alice@corp.com"
restored = unmask(llm_output, result["masking_map"])
```

---

## Pipeline overview

Prompts flow through seven stages (see [pipeline.md](pipeline.md)):

```
Input → Security → IR Generation → Routing → Compilation → Optimization → Generation → Result
```

For drop-in usage, you interact with `process()` — the pipeline runs internally.

---

## Prompt IR

PrivySHA builds a structured **Prompt IR** (intermediate representation) from natural language:

- Intent (analyze, create, summarize, …)
- Entities and constraints
- Privacy metadata

IR drives optimization and routing. See [prompt-ir.md](prompt-ir.md).

---

## Model routing

The `ModelRouter` selects providers based on task IR, cost, performance, and availability. Strategies include `LOCAL_PRIVACY` for PrivyFit-driven local model selection. See [routing.md](routing.md).

---

## Token optimization

The MSDPC optimizer compresses prompts within a `token_budget`. Typical savings:

- **5–15%** on verbose conversational prompts (common case)
- **Higher** on the benchmark test suite (~44% average — see [benchmarks.md](benchmarks.md))

Set `preserve_intent=True` on `process()` to skip optimization when no PII or threats are detected — useful when semantic fidelity matters more than token savings.

---

## Return shapes

### `process()` default

Returns a **string** (the optimized prompt).

### `process(..., return_metrics=True)`

```python
{
    "optimized": "...",
    "original": "...",
    "token_reduction": 12,          # percentage
    "pii_masked": True,
    "security_result": {...},
    "metrics": {
        "tokens_saved": 5,
        "cost_reduction": "8%",
        "processing_time_ms": 45,
        "pii_detected": ["email"],
        "risk_level": "low",
    },
}
```

### `process(..., trace=True, debug=True)`

Also includes `trace`, `diff`, and optionally `fallback_reason`.

---

## Agent vs drop-in functions

| Use case | API |
|----------|-----|
| Preprocess prompts only | `process()`, `sanitize()`, `optimize()` |
| Wrap existing SDK client | `wrap_llm()` |
| Full pipeline + LLM call | `Agent` |
| Local model recommendation | `recommend_local_model()` |

`Agent` accepts: `model`, `privacy`, `token_budget`, `provider`, `fallback_providers`, `routing_config`, `timeout`, `retries`, `api_key`, `local_model`, `sample_prompts`.

It does **not** accept `optimization_level`, `routing_strategy`, `security_level`, or `mode` directly — use `process()` for those.

---

## Progressive enhancement

Start with the simplest path and add features as needed:

1. `process(prompt)` — zero config
2. `process(prompt, mode="strict", return_metrics=True)` — tuned policy
3. `wrap_llm(client)` — transparent SDK integration
4. `Agent(model="mock")` — full pipeline + generation
5. `recommend_local_model(...)` — local deployment planning
