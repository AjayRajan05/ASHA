# Performance Tuning

**ASHA v0.4.2**

---

## Trade-offs

| Priority | Settings |
|----------|----------|
| **Speed** | `mode="lite"` or `mode="off"`, `pii_mode="rule"` |
| **Security** | `mode="strict"`, `PolicyConfig(pii_mode="hybrid")` |
| **Token savings** | `mode="strict"`, lower `token_budget` |
| **Semantic fidelity** | `PolicyConfig(preserve_intent=True)` |

---

## Fastest path

```python
from asha import process

result = process(prompt, mode="lite")
# or
result = process(prompt, mode="off")
```

Avoid in hot paths: `trace=True`, `debug=True`, `pii_mode="hybrid"` (ML load).

---

## Maximum security

```python
from asha import process
from asha.core.policy_config import PolicyConfig

result = process(
    prompt,
    mode="strict",
    policy=PolicyConfig(pii_mode="hybrid", security_level="high"),
)
```

---

## Async batching

```python
import asyncio
from asha.utils.dropin import process_async

async def batch(prompts):
    return await asyncio.gather(
        *[process_async(p, mode="lite") for p in prompts]
    )
```

---

## Tunable parameters

All per-call on `process()` - no global config.

| Parameter | Effect |
|-----------|--------|
| `mode` | Policy preset |
| `policy` | `pii_mode`, `security_level`, `preserve_intent`, etc. |
| `token_budget` | Optimization target (default 1200) |
| `timeout_seconds` | Abort after N seconds |
| `max_retries` | Retry transient failures |

---

## Agent

`Agent(privacy=True)` uses strict internal preprocessing. Tune via `token_budget` or preprocess with `process()` yourself.

```python
from asha import Agent

agent = Agent(model="mock", privacy=True, token_budget=800)
```

---

## Measuring

```python
import time
from asha import process

start = time.perf_counter()
result = process("prompt", mode="balanced")
print(f"Wall: {(time.perf_counter()-start)*1000:.1f} ms")
print(f"Reported: {result.metrics.processing_time_ms} ms")
```

```bash
python benchmarks/run_benchmarks.py --save
```

See [benchmarks.md](benchmarks.md).

---

## Production checklist

1. Default `mode="balanced"`
2. No `trace`/`debug` on every request
3. `pii_mode="rule"` unless ML needed
4. `mode="strict"` for regulated paths
5. Monitor `result.degraded` in logs
6. Pin `asha==0.4.2`
