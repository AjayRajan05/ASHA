# Debugging

**PrivySHA v0.3.0** — pipeline tracing and diff inspection.

---

## Quick start

```python
from privysha import process

result = process(
    "Analyze data with john@example.com",
    trace=True,
    debug=True,
    return_metrics=True,
)

print(result["optimized"])
print(result["diff"])
print(result["trace"])
```

---

## TraceContext (recommended)

`TraceContext` in `core/trace_context.py` is the preferred tracing mechanism. Enable it via `trace=True` on `process()` or `pipeline.process()`.

It records:

- Stage names and execution order
- Input/output at each stage
- Timing per stage
- Changes made

```python
result = process("prompt", trace=True, return_metrics=True)
trace = result.get("trace", {})
print(trace.get("stages"))
print(trace.get("final_output"))
```

---

## Debug mode

`debug=True` adds diagnostic fields to the response:

```python
result = process("prompt", debug=True, return_metrics=True)
print(result.get("fallback_reason"))   # if pipeline fell back
print(result.get("original_error"))    # underlying error
print(result.get("changes"))           # list of changes
print(result.get("diff"))              # unified diff
```

---

## DiffEngine

Unified diffs between original and processed prompts:

```python
result = process(
    "Contact john@example.com for analysis",
    debug=True,
    return_metrics=True,
)
print(result["diff"])
# --- original
# +++ modified
# -Contact john@example.com for analysis
# +Contact [EMAIL_HASH]_abc for analysis
```

Direct access:

```python
from privysha import DiffEngine

engine = DiffEngine()
diff = engine.generate_diff(original, modified)
```

---

## Agent tracing

```python
from privysha import Agent

agent = Agent(model="mock", privacy=True)
result = agent.run("prompt with john@example.com", trace=True)

print(result["prompts"]["original"])
print(result["prompts"]["sanitized"])
print(result["prompts"]["optimized"])
print(result["prompts"]["compiled"])
print(result["response"])
print(result["adapter_info"])
```

Without `trace=True`, `agent.run()` returns only the response string.

---

## PrivySHADebugger

Comprehensive debug sessions via `debug_mode=True`:

```python
result = process("prompt", debug_mode=True, return_metrics=True)
print(result.get("comprehensive_debug"))
```

Used internally by the CLI `--debug-mode` flag.

---

## Deprecated: DebugTracer

`DebugTracer` still loads (with a deprecation warning) but should not be used in new code:

```python
# Deprecated — use trace=True on process() instead
from privysha import DebugTracer  # warns on import
```

Migration: replace `DebugTracer` usage with `process(..., trace=True)` and `TraceContext`.

---

## CLI debugging

```bash
# Basic debug metrics
privysha "My email is john@gmail.com" --debug

# Comprehensive debugger
privysha "prompt" --debug-mode

# Stage-based processing
privysha "prompt" --stages --context '{"role": "analyst"}'
```

---

## OpenTelemetry

Optional distributed tracing:

```bash
pip install privysha[otel]
```

```python
from privysha import enable_otel

enable_otel()
result = process("prompt", trace=True)
```

OTEL spans are wired through `StageBase.stage_span()` in all pipeline stages.

---

## Structured logging

```python
result = process(
    "prompt",
    trace=True,
    log_level="DEBUG",
    log_output="file",
    log_file="privysha.log",
)
```

Log levels: `ERROR`, `WARN`, `INFO`, `DEBUG`.

Output destinations: `console`, `file`, `json`.

---

## Troubleshooting with traces

Common debugging workflow:

1. Run with `trace=True, debug=True, return_metrics=True`
2. Check `fallback_reason` — was there a pipeline failure?
3. Inspect `diff` — what changed?
4. Review `security_result` — was PII detected?
5. Check `metrics.processing_time_ms` — performance OK?

See [troubleshooting.md](troubleshooting.md) for common issues.

---

## Related docs

- [Pipeline](pipeline.md) — stage details
- [Architecture](architecture.md) — TraceContext location
- [API Reference](api-reference.md) — all debug parameters
