# Optimization

**ASHA v0.4.2** - token reduction via MSDPC.

---

## optimize()

Token compression only - no PII masking, no compile stage:

```python
from asha import optimize

result = optimize("Hey bro can you please analyze this dataset thoroughly")
print(result.output)
print(result.metrics.token_reduction_pct)
```

---

## process() with optimization

Full path includes security + compile + optimize:

```python
from asha import process

result = process("long verbose prompt...", token_budget=1200)
print(result.metrics.tokens_saved)
```

---

## Skip optimization when safe

```python
from asha.core.policy_config import PolicyConfig

process(
    prompt,
    policy=PolicyConfig(preserve_intent=True),
)
```

When no PII or threats are found, the original prompt may be returned unchanged.

---

## Modes and latency

| Mode | Optimization level |
|------|-------------------|
| `balanced` | Standard MSDPC |
| `strict` | Aggressive + fail-closed |
| `lite` | Reduced policy features |
| `off` | Skipped |

For minimum latency: `mode="off"` or `optimize()` alone on already-clean prompts.

---

## Metrics

```python
result = process(prompt)
m = result.metrics
print(m.token_reduction_pct)
print(m.tokens_saved)
print(m.processing_time_ms)
```

---

## optimize() vs process()

| Function | Security | Compile | Optimize |
|----------|----------|---------|----------|
| `optimize()` | No | No | Yes |
| `sanitize()` | Yes | No | No |
| `process()` | Yes | Yes | Yes |

---

## Related

- [performance-tuning.md](performance-tuning.md)
- [benchmarks.md](benchmarks.md)
