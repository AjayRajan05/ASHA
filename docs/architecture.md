# Architecture

**PrivySHA v0.4.1** — compiler-inspired prompt processing with strict layer boundaries.

---

## High-level flow

```
User Input
    │
    ▼
Security (run_security)     ← PII detection, injection checks, masking
    │
    ▼
Compilation (compile_prompt) ← IR → structured prompt (internal IR only)
    │
    ▼
Optimization (optimize_tokens) ← MSDPC token reduction
    │
    ▼
ProcessResult               ← typed output, metrics, optional trace
```

For drop-in usage via `process()`, you interact with the pipeline as a black box. Use `trace=True` to inspect each stage.

`Agent` adds model routing and LLM generation on top of preprocessing.

---

## Package layout

```
src/privysha/
├── __init__.py              # 5 exports: process, sanitize, optimize, Agent, __version__
├── core/                    # engines, policy, security, compiler, _ir (internal)
│   ├── engines.py           # sanitize_text, compile_prompt, optimize_tokens
│   ├── policy_config.py     # PolicyMode, PolicyConfig
│   ├── policy_resolution.py # mode + policy → pipeline config
│   ├── safety.py            # SafetyMode from policy mode
│   ├── security/            # PII, threats, masking
│   ├── compiler/            # PromptCompiler, MSDPC optimizer
│   ├── _ir/                 # Internal IR — not public API
│   └── pii_pipeline/        # Multi-phase PII detection (not main pipeline stages)
├── runtime/                 # orchestration
│   ├── processor.py         # PromptProcessor — only orchestrator
│   ├── resolve.py           # Hot-path argument resolution for process/sanitize
│   ├── agent.py             # Agent
│   ├── adapters/            # Provider-specific LLM clients
│   ├── routing/             # Model selection (Agent concern)
│   └── local_advisor/       # PrivyFit local model recommendations
├── integrations/            # wrap_llm, auto_patch, framework middleware
│   ├── llm_wrap.py
│   ├── auto_patch.py
│   ├── fastapi/, flask/, django/, langchain/, llamaindex/
│   └── otel.py
├── compat/                  # Opt-in legacy dict conversion only
│   ├── legacy_results.py    # to_legacy_pipeline_dict()
│   └── warnings.py
├── types/                   # ProcessResult, SanitizeResult, OptimizeResult
├── utils/                   # dropin (process/sanitize/optimize), unmask
└── cli/                     # privysha CLI (ancillary)
```

---

## Layer boundaries

| Layer | May import | Must not import |
|-------|------------|-----------------|
| `core/` | stdlib, third-party | `runtime`, `integrations`, `compat` |
| `runtime/` | `core`, `types` | `integrations`, `compat` |
| `types/` | `core` (minimal) | `compat`, `runtime`, `integrations` |
| `utils/` | `runtime`, `core`, `types` | `compat` |
| `integrations/` | `runtime`, `core`, `utils` | — |
| `compat/` | anything | — (legacy helpers only) |

Enforced by `tests/architecture/test_boundaries.py`.

---

## Key design principles

### Drop-in first

Primary adoption: `process()`, `sanitize()`, `optimize()`. Integrations via `privysha.integrations.wrap_llm`.

### Safety modes

| Mode | Behavior |
|------|----------|
| `strict` | Fail-closed — raises on total failure |
| `balanced` | Fail-open with rule-based PII fallback (default) |
| `lite` | Minimal policy features; same fail-open semantics as balanced |
| `off` | Passthrough |

Configure advanced policy via `PolicyConfig(pii_mode=..., reversible=..., preserve_intent=...)`.

### Policy resolution

`utils/dropin.process()` → `runtime/resolve.resolve_process_call()` → `PromptProcessor.run(profile, mode)`.

No `compat/` on the hot path.

### Legacy dict shapes

Opt-in only:

```python
from privysha.compat.legacy_results import to_legacy_pipeline_dict
legacy = to_legacy_pipeline_dict(process("prompt", include_legacy_detail=True))
```

---

## Adapter system

`AdapterFactory` in `runtime/adapters/` creates provider-specific adapters. `wrap_llm()` in `integrations/llm_wrap.py` is the user-facing entry point.

---

## PII detection architecture

1. **Rule-based** (`core/security/`) — default, no downloads
2. **Multi-phase pipeline** (`core/pii_pipeline/stages/`) — normalization → detection → verification → scoring → masking
3. **Hybrid ML** (`core/hybrid_pii.py`) — optional via `pip install privysha[ml]`

---

## Observability

- **TraceContext** — `process(..., trace=True)`
- **OpenTelemetry** — optional via `pip install privysha[otel]`
- **DebugStage** — renamed from `PipelineStage` in `debug/`

---

## Testing

```
tests/              # Full test suite
tests/architecture/ # Layer boundary enforcement
tests/imports/      # Import graph
tests/public_api/   # Root export freeze
tests/contracts/    # API contracts (e.g. optimize vs sanitize)
```

CI runs: `pytest tests`

---

## Related docs

- [API Reference](api-reference.md)
- [Deprecations](deprecations.md)
- [Security](security.md)
- [Debugging](debugging.md)
