# Core Concepts

**PrivySHA v0.4.1**

PrivySHA preprocesses prompts: detect PII, check threats, compile structure, compress tokens. You call one function; the engines run inside `PromptProcessor`.

---

## Public API

### Root package (only these)

```python
from privysha import process, sanitize, optimize, Agent
```

### Common subpackage imports

```python
from privysha.integrations import wrap_llm
from privysha.types import ProcessResult, SanitizeResult, OptimizeResult
from privysha.core.policy_config import PolicyConfig
from privysha.runtime import PromptProcessor
from privysha.utils.dropin import process_async
from privysha.utils.unmask import unmask
from privysha.runtime.local_advisor.advisor import recommend_local_model
```

There is **no** global `configure()`. Pass `mode` and `policy` per call.

---

## Processing flow

```
process(prompt)
  → resolve mode + PolicyConfig
  → PromptProcessor.run()
      → run_security()      # PII, injection, masking
      → compile_prompt()    # internal IR → structured text
      → optimize_tokens()   # MSDPC compression
  → ProcessResult
```

`sanitize()` runs security only. `optimize()` runs token compression only.

---

## Policy modes

| Mode | Security | Optimization | On total failure |
|------|----------|--------------|------------------|
| `balanced` | Standard | Yes | Fail-open + fallback |
| `strict` | Maximum | Yes | Raises `PrivySHAProcessingError` |
| `lite` | Minimal features | Reduced | Fail-open (same as balanced) |
| `off` | Skipped | Skipped | Passthrough |

```python
process("prompt", mode="balanced")  # default
process("prompt", mode="strict")
process("prompt", mode="off")
```

---

## PolicyConfig

Advanced knobs are **not** top-level kwargs on `process()`:

```python
from privysha.core.policy_config import PolicyConfig

process(
    prompt,
    policy=PolicyConfig(
        pii_mode="rule",       # rule | hybrid | ml_only
        reversible=False,
        preserve_intent=False,
        security_level="medium",
    ),
)
```

| Field | Purpose |
|-------|---------|
| `pii_mode` | Detection strategy (`hybrid` needs `privysha[ml]`) |
| `reversible` | Store masking map for `unmask()` |
| `preserve_intent` | Skip optimization when no PII/threats |
| `security_level` | `low` / `medium` / `high` |

---

## Result types

### ProcessResult

```python
result = process("prompt")
result.output          # processed text
result.original        # input text
result.degraded        # True if fallback path used
result.security        # SecurityInfo (PII, threats)
result.metrics         # tokens, timing
result.trace           # when trace=True
result.diff            # when debug=True
str(result)            # same as result.output
```

### SanitizeResult / OptimizeResult

Same pattern — `.output`, `.security` (sanitize), `.metrics` (optimize).

Legacy dict: `result.to_dict()` or `privysha.compat.legacy_results.to_legacy_pipeline_dict(result)`.

---

## Fail-open vs fail-closed

| API | Default | Strict |
|-----|---------|--------|
| `process()` / `sanitize()` | Fail-open fallback | `mode="strict"` raises |
| `wrap_llm()` | Uses caller `mode` | Transport errors raise when `mode != "off"` |
| `auto_patch()` | Default `mode="strict"` | Configurable |

---

## Reversible masking

```python
from privysha import sanitize
from privysha.core.policy_config import PolicyConfig
from privysha.utils.unmask import unmask

result = sanitize(
    "Email alice@corp.com",
    policy=PolicyConfig(reversible=True),
)
safe = result.output
restored = unmask("Reply to alice@corp.com", result.security.masking_map)
```

---

## Agent vs drop-in

| Goal | Use |
|------|-----|
| Preprocess only | `process()`, `sanitize()`, `optimize()` |
| Wrap existing SDK | `wrap_llm(client)` |
| Preprocess + LLM call | `Agent(model=...)` |
| Task-based model pick | `Agent(routing_config={"chat": "gpt-4o-mini", ...})` |
| Local model advice | `recommend_local_model()` |

`Agent(privacy=True)` enables preprocessing with strict internal mode. `privacy=False` disables it.

---

## Internal vs public

**Public:** `process`, engines behavior via modes, typed results.

**Internal (do not import in app code):** `core/_ir/`, `core/pii_pipeline/` stages, compiler internals.

IR is built inside `compile_prompt()` — never passed as a public argument.
