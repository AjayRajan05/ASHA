# Benchmarks

Reproducible benchmark harness for PrivySHA security, optimization, and latency.

## Latest baseline (1.0.1)

| Metric | Value |
|--------|-------|
| Version | 1.0.1 |
| Tests | 10 (10 passed) |
| Avg latency | ~1272 ms |
| P95 latency | ~67 ms |
| P99 latency | ~76 ms |
| Avg token reduction | 43.9% |
| PII detected | 8 |
| False positive rate | 0.0% |
| Fail-safe rate | 100.0% |

## Run locally

```bash
python benchmarks/run_benchmarks.py --save
python benchmarks/run_benchmarks.py --compare benchmarks/baseline/results.json
```

## Update CI baseline

After a verified good run:

```bash
python benchmarks/run_benchmarks.py --save --update-baseline
```

Raw JSON lives in `benchmarks/baseline/results.json` in the repository.
