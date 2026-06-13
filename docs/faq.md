# FAQ

**PrivySHA v0.3.0 developer preview** — frequently asked questions.

---

## General

### What is PrivySHA?

A drop-in security and optimization layer for LLM applications. It masks PII, reduces tokens, and blocks prompt injection before prompts reach LLM providers.

### Is PrivySHA production-ready?

**No.** Version 0.3.0 is a developer preview. APIs may change before 1.0.0. Use for experiments and feedback. See [developer-preview.md](developer-preview.md).

### What Python version is required?

Python **3.10+** (3.10, 3.11, 3.12 supported).

### How do I install it?

```bash
pip install privysha
```

Or from source: `pip install -e .`

---

## API

### What are the main functions?

| Function | Purpose |
|----------|---------|
| `process()` | Full pipeline (security + optimization) |
| `wrap_llm()` | Wrap existing LLM client |
| `optimize()` | Token optimization only |
| `sanitize()` | Security / PII only |
| `Agent` | Pipeline + LLM generation |
| `recommend_local_model()` | PrivyFit local model advisor |

### Is there a global configure() function?

**No.** Pass parameters per call (`mode`, `pii_mode`, etc.) or use `PolicyConfig` / `Agent` kwargs.

### What does process() return?

A **string** by default. Pass `return_metrics=True` for a dict with `optimized`, `token_reduction`, `security_result`, etc.

### Does process() raise on errors?

**No** (fail-open by default). It returns a security-scrubbed fallback. Use `security_fail_closed=True` for regulated workloads. Use `debug=True` for `fallback_reason`.

---

## Modes

### What are the processing modes?

| Mode | Description |
|------|-------------|
| `balanced` | Default — security + optimization |
| `strict` | Maximum PII masking |
| `lite` | Minimal processing |
| `off` | Passthrough — no changes |

### What are PII modes?

| Mode | Description |
|------|-------------|
| `rule` | Regex + heuristic (default, no downloads) |
| `hybrid` | Rules + ML (requires `privysha[ml]`) |
| `ml_only` | ML-only (experimental) |

---

## Performance

### How much token reduction should I expect?

**5–15%** on typical verbose prompts. The benchmark test suite averages **~44%** but results vary widely. Already-concise prompts may see little or no reduction.

### How fast is processing?

Benchmark P95 pipeline latency is **~76 ms** per test case. End-to-end latency depends on prompt length, ML mode, and hardware. There is no sub-50ms guarantee.

### How do I make it faster?

```python
process(prompt, mode="lite", pii_mode="rule")
```

Disable tracing in production: avoid `trace=True` and `debug=True`.

---

## Security

### What PII types are detected?

Emails, phones, SSNs, credit cards, addresses, names (heuristic), API keys, JWTs, IP addresses, and more. See [security.md](security.md).

### What mask format is used?

`[EMAIL_HASH]_<suffix>`, `[PHONE_HASH]_<suffix>`, `[REDACTED]` for secrets.

### Is PrivySHA GDPR compliant?

PrivySHA provides **tooling** for privacy-aware processing. It is not a certified compliance product. See [compliance.md](compliance.md).

---

## Agent

### What parameters does Agent accept?

`model`, `privacy`, `token_budget`, `provider`, `fallback_providers`, `routing_config`, `timeout`, `retries`, `api_key`, `local_model`, `sample_prompts`.

It does **not** accept `mode`, `optimization_level`, `routing_strategy`, or `security_level` directly.

### What does Agent.run() return?

A **string** (the LLM response) by default. With `trace=True`, returns the full pipeline dict plus `response`.

---

## PrivyFit

### What is PrivyFit?

A local model advisor that recommends LLMs based on your compiled prompt workload and hardware. See [local-advisor.md](local-advisor.md).

### Does it require a GPU?

No. It works with CPU-only ranking and an offline catalog. GPU detection requires `pip install privysha[local-advisor-gpu]`.

---

## Integrations

### Which frameworks are supported?

FastAPI, Flask, Django, LangChain, Instructor, Guardrails, LlamaIndex, OpenTelemetry. See [integrations.md](integrations.md).

### Do I need API keys for basic processing?

No. `process()` and `sanitize()` work without API keys. LLM adapters require provider credentials.

---

## Contributing

### How do I report bugs?

[GitHub Issues](https://github.com/AjayRajan05/privySHA/issues)

### How do I contribute?

See [contributing.md](contributing.md).

---

## Related docs

- [Getting Started](getting-started.md)
- [Troubleshooting](troubleshooting.md)
- [Developer Preview](developer-preview.md)
