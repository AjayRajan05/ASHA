# Processing Flow

**PrivySHA v0.4.1** — three engines, one orchestrator.

The old 7-stage `Pipeline` class was removed. `PromptProcessor` runs three core engines in order.

---

## Flow

```
User prompt
    │
    ▼
Security (run_security)
    │  PII detection, injection checks, masking
    ▼
Compile (compile_prompt)
    │  Internal IR → structured prompt (IR not public)
    ▼
Optimize (optimize_tokens)
    │  MSDPC token compression
    ▼
ProcessResult
```

`mode="off"` skips all engines via the policy gate.

---

## Entry points

| Function | Engines run |
|----------|-------------|
| `process()` | security → compile → optimize |
| `sanitize()` | security only |
| `optimize()` | optimize only |

```python
from privysha import process, sanitize, optimize

process("prompt with john@x.com")
sanitize("prompt with john@x.com")
optimize("long verbose prompt please analyze")
```

---

## Orchestrator

```python
from privysha.runtime import PromptProcessor

processor = PromptProcessor()
result = processor.run("prompt", mode="balanced")
```

Stage control uses `ExecutionProfile` or `PolicyConfig` — not `security=` / `compile=` / `optimize=` kwargs.

---

## Agent adds LLM generation

```
Agent.run(prompt)
  → PromptProcessor (preprocess)
  → Adapter.generate(processed prompt)
  → str or AgentResult
```

Model selection for multi-task apps:

```python
Agent(routing_config={"chat": "gpt-4o-mini", "code": "gpt-4o"})
```

See [routing.md](routing.md).

---

## Tracing

```python
result = process("prompt", trace=True, debug=True)
print(result.trace)
print(result.diff)
```

Uses `core/trace_context.py` — not the removed `PrivySHADebugger`.

---

## Legacy dict shape

Opt-in only:

```python
from privysha.compat.legacy_results import to_legacy_pipeline_dict

legacy = to_legacy_pipeline_dict(
    process("prompt", include_legacy_detail=True)
)
```

`routing_decision` appears only in legacy dicts (placeholder for compat).

---

## Related

- [architecture.md](architecture.md) — package layout
- [core-concepts.md](core-concepts.md) — modes and results
- [security.md](security.md) — first engine details
- [optimization.md](optimization.md) — third engine details
