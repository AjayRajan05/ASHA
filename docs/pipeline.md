# Pipeline

**PrivySHA v0.3.0** — 7-stage modular processing pipeline.

---

## Overview

The `Pipeline` class in `pipeline/pipeline.py` orchestrates seven stages. Each stage inherits from `StageBase` and receives a shared `StageContext`.

```
Input
  → SecurityStage
  → IRGenerationStage
  → RoutingStage
  → CompilationStage
  → OptimizationStage
  → GenerationStage
  → ResultStage
  → Output dict
```

---

## Stages

### 1. Security Stage

**Module:** `pipeline/stages/security_stage.py`

- PII detection and masking (rule-based or hybrid ML)
- Prompt injection detection
- Threat scoring
- Secret/API key/JWT pattern matching

Controlled by: `privacy`, `security_level`, `pii_mode`, `policy_config`.

### 2. IR Generation Stage

**Module:** `pipeline/stages/ir_generation_stage.py`

- Parses prompt into Prompt IR
- Extracts intent, entities, constraints
- Uses `IRBuilder` from `ir/ir_builder.py`

### 3. Routing Stage

**Module:** `pipeline/stages/routing_stage.py`

- Selects model/provider via `ModelRouter`
- Supports `RoutingStrategy.LOCAL_PRIVACY` for PrivyFit
- Can be bypassed when routing is not configured

### 4. Compilation Stage

**Module:** `pipeline/stages/compilation_stage.py`

- Converts IR to structured prompt text
- Uses `PromptCompiler` from `compiler/prompt_compiler.py`

### 5. Optimization Stage

**Module:** `pipeline/stages/optimization_stage.py`

- MSDPC token reduction within `token_budget`
- Uses `PromptOptimizer` / `compiler/msdpc/`
- Respects `policy_config.optimization_level`

### 6. Generation Stage

**Module:** `pipeline/stages/generation_stage.py`

- LLM API call (when adapter is configured)
- Used by `Agent`, not by bare `process()`

### 7. Result Stage

**Module:** `pipeline/stages/result_stage.py`

- Assembles final output dict
- Collects metrics, security summary, timing

---

## Policy gate

When `mode="off"`, the policy gate (`pipeline/policy_gate.py`) returns early with a passthrough result — no stages run, no PII scrub applied.

For other modes, `PolicyConfig` presets control:

- Whether PII detection runs
- Optimization aggressiveness
- Debug diff generation
- Fail-closed behavior

---

## Using the pipeline directly

```python
from privysha import Pipeline

pipeline = Pipeline(
    privacy=True,
    token_budget=1200,
    security_level="MEDIUM",
    pii_mode="rule",
    policy_config=None,
)

result = pipeline.process(
    content="My email is john@example.com — analyze this.",
    trace=True,
)

print(result["prompts"]["optimized"])
print(result["security_result"])
print(result["success"])
```

### Result structure

```python
{
    "success": True,
    "prompts": {
        "original": "...",
        "sanitized": "...",
        "optimized": "...",
        "compiled": "...",
    },
    "security_result": {...},
    "metrics": {...},
}
```

---

## Stage configuration

Each stage can be configured via `pipeline.configure_stage()`:

```python
pipeline.configure_stage("security", {"enable_injection_detection": True})
pipeline.configure_stage("optimization", {"target_reduction": 0.3})
```

OTEL spans are wired through `StageBase.stage_span()` when `enable_otel()` is active.

---

## Tracing

Pass `trace=True` to `pipeline.process()` or `process()` to get stage-level timing and changes via `TraceContext`.

```python
result = process("prompt", trace=True, return_metrics=True)
print(result["trace"])
print(result["diff"])
```

See [debugging.md](debugging.md).

---

## Error handling

When `fallback_mode=True` (default), failed stages do not abort the pipeline. The result falls back to the last successful output.

`process()` wraps this with an additional fail-safe layer — it never raises on pipeline errors unless input validation fails.

---

## Related docs

- [Architecture](architecture.md) — package layout
- [Security](security.md) — security stage details
- [Optimization](optimization.md) — optimization stage details
- [Prompt IR](prompt-ir.md) — IR generation stage
