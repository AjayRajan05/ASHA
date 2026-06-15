# Benchmarks

**PrivySHA v0.4.1** — reproducible performance measurements.

---

## Run locally

```bash
pip install -e .
python benchmarks/run_benchmarks.py --save
```

```bash
python benchmarks/run_benchmarks.py --compare benchmarks/baseline/results.json
privysha benchmark --save
```

---

## What is measured

`benchmarks/run_benchmarks.py` via `core/benchmark.py`:

- PII detection and masking
- Token reduction %
- Latency (avg, P95, P99)
- Fail-safe behavior
- False positive rate (example emails skipped)

Test prompts: `benchmarks/sample_prompts.json`.

---

## Typical ranges (rule-based PII)

| Metric | Range |
|--------|-------|
| Token reduction | 5–15% typical; higher on benchmark suite |
| P95 pipeline latency | ~50–80 ms |
| Fail-safe rate | ~100% in CI gates |

Not guarantees — your hardware and prompts differ.

---

## CI gates

On every push (Ubuntu, Python 3.11):

- Architecture tests
- Coverage ≥ 50%
- Benchmark smoke + regression vs baseline
- Semantic equivalence ≥ 30%
- Prompt repair = 100%

---

## Programmatic

```python
from privysha.core.benchmark import BenchmarkHarness

harness = BenchmarkHarness()
summary = harness.run_all(mode="balanced")
```

---

## Output

| Path | Description |
|------|-------------|
| `benchmarks/baseline/results.json` | Committed baseline |
| `benchmarks/output/` | Timestamped runs |

Re-run `--update-baseline` after major version bumps.

---

## Related

- [optimization.md](optimization.md)
- [performance-tuning.md](performance-tuning.md)
