# Architecture

**PrivySHA v0.3.0** — compiler-inspired prompt processing pipeline.

---

## High-level flow

```
User Input
    │
    ▼
Security Stage        ← PII detection, injection checks, masking
    │
    ▼
IR Generation Stage   ← Intent, entities, constraints
    │
    ▼
Routing Stage         ← Model selection (optional)
    │
    ▼
Compilation Stage     ← IR → structured prompt
    │
    ▼
Optimization Stage    ← MSDPC token reduction
    │
    ▼
Generation Stage      ← LLM API call (Agent only)
    │
    ▼
Result Stage          ← Metrics, final assembly
```

For drop-in usage via `process()`, you interact with the pipeline as a black box. Use `trace=True` to inspect each stage.

---

## Package layout

```
src/privysha/
├── __init__.py              # Public API exports
├── agent.py                 # Agent class
├── adapters/                # Provider adapters
│   ├── factory.py           # AdapterFactory
│   ├── base.py              # BaseAdapter
│   ├── openai_adapter.py
│   ├── claude_adapter.py
│   ├── gemini_adapter.py
│   ├── grok_adapter.py
│   ├── ollama_adapter.py
│   ├── hf_adapter.py
│   ├── mock_adapter.py
│   └── universal_adapter.py
├── cli/                     # CLI entry point
│   ├── main.py
│   ├── benchmark_cli.py
│   └── recommend_cli.py
├── compiler/
│   ├── optimizer_engine.py  # PromptOptimizer
│   ├── prompt_compiler.py
│   └── msdpc/               # Token pruning engine
├── core/
│   ├── policy_config.py     # PolicyMode, PolicyConfig
│   ├── hybrid_pii.py        # ML-enhanced PII
│   ├── diff_engine.py       # Prompt diffs
│   ├── trace_context.py     # TraceContext (preferred tracing)
│   ├── benchmark.py         # BenchmarkHarness
│   └── pii_pipeline/        # Multi-stage PII pipeline
├── debug/
│   └── debugger.py          # PrivySHADebugger
├── integrations/            # Framework adapters
│   ├── fastapi/
│   ├── flask/
│   ├── django/
│   ├── langchain/
│   ├── llamaindex/
│   ├── otel.py
│   ├── framework_adapters.py
│   └── composition_strategy.py
├── ir/
│   ├── prompt_ir.py         # PromptIR, IntentType
│   └── ir_builder.py        # IRBuilder
├── local_advisor/           # PrivyFit
│   ├── advisor.py           # recommend_local_model()
│   ├── catalog/
│   ├── fit/
│   └── workload_profiler.py
├── parser/
│   └── prompt_ast.py
├── pipeline/
│   ├── pipeline.py          # Pipeline orchestrator
│   ├── policy_gate.py       # mode="off" passthrough
│   ├── contracts.py
│   ├── components/          # StageContext, StageBase
│   └── stages/              # Individual stage implementations
├── routing/
│   └── model_router.py      # ModelRouter, RoutingStrategy
├── security/
│   ├── patterns.py          # Canonical PII/threat patterns
│   ├── pii_detector.py      # Rule-based PII detector
│   ├── security_layer.py    # SecurityLayer
│   ├── masking_vault.py     # Reversible masking
│   └── service.py
└── utils/
    ├── dropin.py            # process, wrap_llm, optimize, sanitize
    ├── dropin_privacy.py
    ├── auto_patch.py
    ├── unmask.py
    └── wrapper.py           # UniversalWrapper
```

---

## Key design principles

### Drop-in first

The primary adoption path is four functions: `process()`, `wrap_llm()`, `optimize()`, `sanitize()`. Advanced components (`Pipeline`, `ModelRouter`, `SecurityLayer`) are available but optional.

### Fail-safe defaults

Pipeline stages catch errors and fall back gracefully. `process()` returns a security-scrubbed result rather than raising (fail-open). Opt into `security_fail_closed=True` for regulated workloads.

### Lazy loading

Advanced symbols load on first access via PEP 562 `__getattr__` in `__init__.py`. Core imports (`process`, `Agent`, etc.) are eager for fast startup.

### Policy-driven behavior

`PolicyConfig` presets (`balanced`, `strict`, `lite`, `off`) control which stages run and how aggressively they operate. The policy gate in `policy_gate.py` enables early passthrough for `mode="off"`.

---

## Adapter system

`AdapterFactory` creates provider-specific adapters:

| Provider | Extra | Env var |
|----------|-------|---------|
| OpenAI | `privysha[openai]` | `OPENAI_API_KEY` |
| Anthropic | `privysha[anthropic]` | `ANTHROPIC_API_KEY` |
| Gemini | `privysha[gemini]` | `GOOGLE_API_KEY` |
| Grok | — | `GROK_API_KEY` |
| Ollama | — | (local server) |
| HuggingFace | `privysha[transformers]` | — |
| Mock | — | (no key, for testing) |

`UniversalWrapper` wraps arbitrary clients. `wrap_llm()` is the user-facing entry point.

---

## PII detection architecture

Two layers:

1. **Rule-based** (`security/pii_detector.py`) — default, no downloads
2. **Multi-stage pipeline** (`core/pii_pipeline/`) — normalization → detection → verification → scoring → masking
3. **Hybrid ML** (`core/hybrid_pii.py`) — optional via `pip install privysha[ml]`

Canonical patterns live in `security/patterns.py` and are shared across detectors.

Mask format: `[EMAIL_HASH]_<suffix>`, `[PHONE_HASH]_<suffix>`, etc.

---

## Observability

- **TraceContext** (`core/trace_context.py`) — preferred tracing via `process(..., trace=True)`
- **OpenTelemetry** — optional via `pip install privysha[otel]` and `enable_otel()`
- **PrivySHADebugger** — comprehensive debug sessions via `debug_mode=True`
- **DiffEngine** — unified diffs via `process(..., debug=True)`

`DebugTracer` is deprecated — use `TraceContext`.

---

## Testing

```
tests/          # Core test suite
tests_v2/       # Extended tests (included in default pytest paths)
benchmarks/     # Reproducible benchmark harness
```

Default CI runs: `pytest -m "not integration"` (skips API-key tests).

Coverage gate: 40% (`--cov-fail-under=40`).

---

## Related docs

- [Pipeline](pipeline.md) — stage details
- [Prompt IR](prompt-ir.md) — IR structure
- [Routing](routing.md) — model selection
- [Security](security.md) — PII and threat handling
- [Debugging](debugging.md) — tracing and diffs
