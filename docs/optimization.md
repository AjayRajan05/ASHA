# Optimization

**PrivySHA v0.3.0** — token reduction via the MSDPC optimizer.

---

## Overview

PrivySHA compresses prompts to reduce token usage and API cost. Optimization runs as a pipeline stage (after security and IR compilation) and is also available standalone via `optimize()`.

---

## Quick usage

```python
from privysha import process, optimize

# Full pipeline (security + optimization)
result = process("Hey bro can you please analyze this dataset for me?", return_metrics=True)
print(result["optimized"])
print(f"Reduction: {result['token_reduction']}%")

# Optimization only (no security)
compressed = optimize("Very long verbose prompt that needs compression")
```

---

## Expected savings

Token reduction depends on prompt verbosity:

| Prompt type | Typical reduction |
|-------------|-------------------|
| Conversational / verbose | 5–15% |
| Benchmark test suite (10 cases) | ~44% average |
| Already concise prompts | 0–5% (may be unchanged) |

Run benchmarks locally for your workload:

```bash
python benchmarks/run_benchmarks.py --save
```

See [benchmarks.md](benchmarks.md) for methodology and baseline numbers.

Do not expect guaranteed 30–50% or 70% reductions — results vary by prompt.

---

## Policy modes

Modes control optimization aggressiveness via `PolicyConfig`:

| Mode | Optimization |
|------|--------------|
| `strict` | Aggressive compression |
| `balanced` | Moderate (default) |
| `lite` | Minimal changes |
| `off` | No optimization |

```python
process(prompt, mode="strict")   # maximum compression
process(prompt, mode="lite")     # speed over savings
process(prompt, mode="off")      # no changes
```

---

## Token budget

```python
process(prompt, token_budget=500)
optimize(prompt, token_budget=500)
```

Default: `1200`. Lower budgets produce more aggressive compression.

---

## Preserve intent

When semantic fidelity matters more than token savings:

```python
process(prompt, preserve_intent=True)
```

If no PII and no threats are detected, the original prompt is returned unchanged — preventing the optimizer from rewriting clean prompts.

---

## MSDPC engine

The Multi-Stage Dynamic Prompt Compiler (`compiler/msdpc/`) applies:

- Filler word removal
- Constraint consolidation
- Object simplification
- Template-based compression

Advanced access:

```python
from privysha import PromptOptimizer

optimizer = PromptOptimizer(level="balanced")
result = optimizer.optimize(ir)
print(result["reduction_percentage"])
```

---

## Semantic optimizer

Optional semantic optimization via `core/semantic_optimizer.py`:

```python
from privysha import optimize_semantically

result = optimize_semantically("Analyze this comprehensive dataset thoroughly")
```

Separate from the main pipeline optimizer — experimental.

---

## Metrics

With `return_metrics=True`:

```python
result = optimize("long prompt here", return_metrics=True)
print(result["token_reduction"])       # percentage
print(result["metrics"]["tokens_saved"])
print(result["metrics"]["compression_ratio"])
```

Cost estimates in metrics use Gemini-1.5-flash pricing as a reference point.

---

## optimize() vs process()

| Function | Security | Optimization |
|----------|----------|--------------|
| `optimize()` | No | Yes |
| `process()` | Yes | Yes |
| `sanitize()` | Yes | No |

Use `optimize()` when you only need compression without PII handling.

---

## Performance tips

For fastest processing:

```python
process(prompt, mode="lite", pii_mode="rule")
```

For maximum savings:

```python
process(prompt, mode="strict", token_budget=500)
```

See [performance-tuning.md](performance-tuning.md).

---

## Related docs

- [Benchmarks](benchmarks.md) — reproducible numbers
- [Pipeline](pipeline.md) — optimization stage
- [Core Concepts](core-concepts.md) — modes and preserve_intent
