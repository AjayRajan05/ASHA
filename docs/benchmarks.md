# Benchmarks

**PrivySHA v0.3.0** — reproducible performance measurements.

---

## Running benchmarks

```bash
pip install -e .
python benchmarks/run_benchmarks.py --save
```

Save and update baseline:

```bash
python benchmarks/run_benchmarks.py --save --update-baseline
```

Compare against baseline:

```bash
python benchmarks/run_benchmarks.py --compare benchmarks/baseline/results.json
```

Via CLI:

```bash
privysha benchmark --save
```

---

## Current baseline

From `benchmarks/baseline/summary.md` (generated 2026-05-24):

| Metric | Value |
|--------|-------|
| Tests | 10 (10 passed) |
| Avg token reduction | **43.9%** |
| False positive rate | **0.0%** |
| Fail-safe rate | **100.0%** |
| P95 latency | **76.4 ms** |
| P99 latency | **76.4 ms** |
| Avg latency (per test case) | **~1475 ms** |

Note: avg latency includes slow individual cases in the test suite. P95/P99 reflect the pipeline processing slice, not end-to-end API calls.

The baseline JSON records `privysha_version: 1.0.0` from when it was captured. Re-run `--update-baseline` after version bumps to refresh.

---

## What is measured

The harness (`benchmarks/run_benchmarks.py`) tests:

- PII detection and masking accuracy
- Token reduction percentage
- Processing latency (avg, P95, P99)
- Fail-safe behavior (pipeline never leaks raw PII on failure)
- False positive rate (teaching emails skipped)

Test prompts: `benchmarks/sample_prompts.json` (10 cases).

Metrics use tiktoken (`cl100k_base` encoding) where available.

---

## Expected ranges (rule-based PII, no ML)

| Metric | Typical range |
|--------|---------------|
| Token reduction | 5–15% on verbose prompts; up to ~44% on benchmark suite |
| P95 pipeline latency | ~50–80 ms |
| Fail-safe rate | ~100% |
| False positive rate | ~0% |

These are **not guarantees** — your prompts and hardware will differ.

---

## CI integration

Benchmarks run in CI on every push with quality gates:

- Fail-safe rate must remain 100%
- False positive rate must remain 0%
- Token reduction must not regress significantly vs baseline

---

## Custom prompts

```bash
python benchmarks/run_benchmarks.py --custom "My email is john@example.com"
privysha benchmark --custom "Analyze this dataset"
```

---

## Output locations

| Path | Description |
|------|-------------|
| `benchmarks/baseline/results.json` | Committed baseline |
| `benchmarks/baseline/summary.md` | Human-readable summary |
| `benchmarks/output/` | Timestamped run outputs |

See also `benchmarks/results.md` in the repo for methodology details.

---

## BenchmarkHarness (programmatic)

```python
from privysha import BenchmarkHarness

harness = BenchmarkHarness()
summary = harness.run_all(mode="balanced")
print(summary.avg_token_reduction)
print(summary.fail_safe_rate)
```

---

## Related docs

- [Optimization](optimization.md) — what affects token reduction
- [Performance Tuning](performance-tuning.md) — speed vs accuracy trade-offs
- [Developer Preview](developer-preview.md) — preview status
