# Performance Tuning

**PrivySHA v0.3.0** — balancing speed, security, and token savings.

---

## Speed vs security vs savings

| Priority | Settings |
|----------|----------|
| **Speed** | `mode="lite"`, `pii_mode="rule"`, no `trace`/`debug` |
| **Security** | `mode="strict"`, `security_level="high"`, `pii_mode="hybrid"` |
| **Token savings** | `mode="strict"`, lower `token_budget` |
| **Semantic fidelity** | `preserve_intent=True` |

---

## Fastest configuration

```python
from privysha import process

result = process(
    prompt,
    mode="lite",
    pii_mode="rule",
    privacy=True,
)
```

Avoid in production hot paths:

- `trace=True` — adds stage tracing overhead
- `debug=True` — adds diff generation
- `debug_mode=True` — full debugger session
- `pii_mode="hybrid"` or `"ml_only"` — requires ML model loading

---

## Maximum security

```python
result = process(
    prompt,
    mode="strict",
    security_level="high",
    pii_mode="hybrid",       # requires privysha[ml]
    security_fail_closed=True,
)
```

---

## Maximum token savings

```python
result = process(
    prompt,
    mode="strict",
    token_budget=500,
)
```

Note: aggressive optimization may alter prompt semantics. Use `preserve_intent=True` if fidelity matters.

---

## Async for throughput

```python
import asyncio
from privysha import process_async

async def process_batch(prompts):
    tasks = [process_async(p, mode="lite") for p in prompts]
    return await asyncio.gather(*tasks)

results = asyncio.run(process_batch(prompts))
```

---

## Tuning parameters on process()

All tuning is per-call on `process()` — there is no global configure function.

| Parameter | Effect |
|-----------|--------|
| `mode` | Policy preset (balanced/strict/lite/off) |
| `pii_mode` | Detection method (rule/hybrid/ml_only) |
| `security_level` | Detection aggressiveness (low/medium/high) |
| `token_budget` | Optimization target (default 1200) |
| `preserve_intent` | Skip optimization on clean prompts |
| `timeout_seconds` | Abort after N seconds |
| `max_retries` | Retry on transient failure (default 0) |

---

## Agent performance

`Agent` does not accept `mode`, `pii_mode`, or `security_level`. It uses `Pipeline(privacy=..., token_budget=...)`.

For tuned preprocessing, use `process()` before calling your LLM, or configure the pipeline:

```python
from privysha import Agent

agent = Agent(model="mock", privacy=True, token_budget=800)
metrics = agent.get_token_metrics("your prompt")
print(metrics)
```

---

## Environment variables

| Variable | Used by | Notes |
|----------|---------|-------|
| `PRIVYSHA_MODEL` | `Agent.from_env()` | Default model name |
| `PRIVYSHA_TOKEN_BUDGET` | `Agent.from_env()` | Default token budget |
| `PRIVYSHA_CACHE_DIR` | Local advisor | Catalog cache path |

`PRIVYSHA_MODE` is **not** read by the library. Set `mode` on each `process()` call.

---

## Measuring performance

```python
import time
from privysha import process

start = time.perf_counter()
result = process("prompt", return_metrics=True, mode="balanced")
elapsed = (time.perf_counter() - start) * 1000

print(f"Wall time: {elapsed:.1f} ms")
print(f"Reported: {result['metrics']['processing_time_ms']} ms")
```

Run benchmarks:

```bash
python benchmarks/run_benchmarks.py --save
privysha benchmark --mode lite --save
```

See [benchmarks.md](benchmarks.md) for baseline numbers.

---

## Production recommendations

1. Use `mode="balanced"` as default
2. Disable `trace` and `debug` in production
3. Use `pii_mode="rule"` unless ML accuracy is required
4. Set `security_fail_closed=True` for regulated workloads
5. Monitor `return_metrics=True` periodically (not on every request)

---

## Related docs

- [Benchmarks](benchmarks.md)
- [Optimization](optimization.md)
- [Troubleshooting](troubleshooting.md)
