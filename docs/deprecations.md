# Shim deprecation and removal policy

PrivySHA v0.4.1 completes the architecture redesign. **Removed symbols raise `AttributeError`** — there are no root lazy imports.

## Removed in v0.4.1

| Removed | Use instead |
|---------|-------------|
| `from privysha import wrap_llm` | `from privysha.integrations import wrap_llm` |
| `from privysha import auto_patch` | `from privysha.integrations import auto_patch` |
| `from privysha import Processor` | `from privysha.runtime import PromptProcessor` |
| `from privysha import Pipeline` | `process()` or `to_legacy_pipeline_dict()` |
| `from privysha import ProcessResult` | `from privysha.types import ProcessResult` |
| `security_fail_closed=` | `mode="strict"` or `mode="balanced"` |
| `privacy=`, `security=`, `compile=`, `optimize=` kwargs on `process()` | `mode=` or `policy=PolicyConfig(...)` |
| `ProcessResult.to_legacy_pipeline_dict()` | `privysha.compat.legacy_results.to_legacy_pipeline_dict` |

## Removed modules (v0.4.1 cleanup)

Legacy pipeline-era code removed from `src/`:

| Removed | Replacement |
|---------|-------------|
| `core/risk_analyzer.py` | Security via `core/security/service.py` |
| `core/semantic_optimizer.py` | `optimize()` / MSDPC in `core/compiler/` |
| `core/explainability.py` | `ProcessResult` fields + `trace=True` |
| `core/debug_trace.py` | `core/trace_context.py` |
| `core/diff_engine.py` | `TraceContext.generate_diff()` |
| `core/latency_budget.py` | `timeout_seconds` on `process()` |
| `core/modes.py` | `PolicyMode` in `core/policy_config.py` |
| `core/config.py` | `mode` + `PolicyConfig` per call |
| `debug/` package | `trace=True` / `debug=True` on `process()` |
| `runtime/router.py` | `Agent(routing_config=...)` |
| `runtime/routing/model_router.py` | `SmartRoutingAdapter` in adapters |

## Public API (v0.4.1)

Root exports only:

```python
from privysha import process, sanitize, optimize, Agent
```

Advanced:

```python
from privysha.runtime import PromptProcessor, ExecutionProfile
from privysha.integrations import wrap_llm, auto_patch
from privysha.types import ProcessResult, SanitizeResult
from privysha.core.policy_config import PolicyConfig
```

Legacy dict shapes (opt-in):

```python
from privysha.compat.legacy_results import to_legacy_pipeline_dict

result = process("prompt", include_legacy_detail=True)
legacy = to_legacy_pipeline_dict(result)
```

## Architecture

```
privysha/
├── core/          # engines, policy, security, compiler, _ir (internal)
├── runtime/       # PromptProcessor, resolve, Agent, adapters
├── integrations/  # wrap_llm, auto_patch, framework middleware
├── compat/        # legacy_results only (opt-in dict conversion)
├── types/         # ProcessResult, SanitizeResult
├── utils/         # dropin (process/sanitize/optimize)
├── cli/           # privysha CLI (ancillary)
└── __init__.py    # 5 exports only
```

Layer boundaries:

- `core/` must not import `runtime`, `integrations`, or `compat`
- `runtime/` must not import `integrations` or `compat`
- `types/` and `utils/` must not import `compat`
- `integrations/` may import `runtime` and `core`
- `compat/` may import anything (legacy dict helpers only)

## Policy configuration

Most callers only need `mode`:

```python
process(prompt, mode="balanced")
process(prompt, mode="strict")
```

Advanced knobs via `PolicyConfig`:

```python
from privysha.core.policy_config import PolicyConfig

process(
    prompt,
    policy=PolicyConfig(pii_mode="hybrid", reversible=True, preserve_intent=True),
)
```

## Safety semantics

| Mode | `process()` / `sanitize()` | Integrations (`mode != "off"`) |
|------|---------------------------|--------------------------------|
| `strict` | Raises on total failure | Processing strict; transport errors raise |
| `balanced` / `lite` | Degraded fallback | Processing balanced; transport errors raise |
| `off` | Passthrough | No processing; transport errors propagate |

`auto_patch(mode="strict")` defaults to strict for global SDK patching.
