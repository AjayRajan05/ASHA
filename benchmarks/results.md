# ASHA Performance Benchmarks

> **Reproducible benchmarks - run locally to verify**
>
> ```bash
> python benchmarks/run_benchmarks.py --save
> ```
>
> Results are written to `benchmarks/output/results.json` and `benchmarks/output/summary.md`.
> The figures below are **reference targets** from internal testing; your results will vary
> by hardware, Python version, and prompt mix.

*Last updated: May 2026*

---

## How to Reproduce

```bash
# From repo root
pip install -e .
python benchmarks/run_benchmarks.py --save

# With a specific policy preset
python benchmarks/run_benchmarks.py --config strict --save
```

Sample prompts are in `benchmarks/sample_prompts.json`. The harness uses
`asha.core.benchmark.BenchmarkHarness` internally.

---

## Reference Results (Internal Testing)

| Metric | Typical Range | Notes |
|--------|---------------|-------|
| Token reduction | 5-15% | Depends on prompt verbosity; structured prompts unchanged |
| Processing latency | 20-80 ms | Rule-based PII mode, no ML |
| PII detection (rule mode) | High for email/phone/SSN | Validate on your data for compliance use |
| Fail-safe rate | ~100% | Original prompt returned on component failure |

---

## Sample Prompt Outcomes

### Customer Support (PII masking)

```
Before: "Hello! My name is John Smith and my email is john@company.com."
After:  PII masked, conversational filler reduced
```

### Data Analysis (verbose → compact)

```
Before: "Please analyze the sales data for Q4 2024. Email analyst@company.com."
After:  Contact info masked, redundant phrasing trimmed
```

### Structured JSON (no change expected)

```
Before: {"task": "summarize", "text": "Quarterly revenue increased 12%."}
After:  Unchanged - optimizer preserves structured input
```

---

## Competitive Notes

ASHA combines PII masking and token optimization in a single drop-in layer.
Compare tools on your own prompt set using `benchmarks/run_benchmarks.py`.

---

**Bottom line**: Run the benchmark harness locally before relying on any performance
or security figures in production.
