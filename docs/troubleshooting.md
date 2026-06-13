# Troubleshooting

**PrivySHA v0.3.0** — common issues and fixes.

---

## Installation

### ImportError: No module named 'privysha'

```bash
pip install privysha
# or from source:
pip install -e .
```

### ML features not working

```bash
pip install privysha[ml]
```

Required for `pii_mode="hybrid"` or `pii_mode="ml_only"`.

---

## PII not detected / not masked

**Wrong fix:** `security_level="low"` — this makes detection *less* aggressive.

**Correct fixes:**

```python
# Stronger policy mode
process(prompt, mode="strict")

# Higher security level
process(prompt, security_level="high")

# ML-enhanced detection
process(prompt, pii_mode="hybrid")  # requires privysha[ml]

# Ensure privacy is enabled (default)
process(prompt, privacy=True)
```

Check that `mode="off"` is not set — it bypasses all processing.

---

## Too much masking / false positives

Teaching emails like `test@example.com` are skipped by default. For other false positives:

```python
process(prompt, mode="lite")
process(prompt, security_level="low")
```

Use `trace=True, debug=True` to inspect what changed.

---

## Slow processing

```python
# Fastest settings
process(prompt, mode="lite", pii_mode="rule")

# Disable tracing overhead
process(prompt)  # no trace=True, no debug=True
```

ML modes (`hybrid`, `ml_only`) are significantly slower than `rule`.

---

## process() returns unexpected text

1. Check `mode` — `off` returns the original prompt unchanged
2. Check `preserve_intent=True` — skips optimization when no PII/threats found
3. Run with debug:

```python
result = process(prompt, debug=True, return_metrics=True)
print(result.get("fallback_reason"))
print(result.get("diff"))
```

---

## Agent errors

### OPENAI_API_KEY not found

Set environment variable or pass `api_key=`:

```bash
export OPENAI_API_KEY=your_key
```

Install the provider extra: `pip install privysha[openai]`

### Connection refused (Ollama)

Start the Ollama server:

```bash
ollama serve
ollama pull llama3
```

### Model not found

Check available models for the provider. Use `model="mock"` for testing without external services.

---

## wrap_llm issues

Ensure the client type is supported (OpenAI, Anthropic, or generic via `UniversalWrapper`).

```python
from privysha import wrap_llm
secure = wrap_llm(client, mode="balanced", privacy=True)
```

---

## CLI issues

Commands use **subcommands**, not all flags on the default command:

```bash
privysha "prompt"              # process a prompt
privysha quick-test            # NOT privysha --quick-test
privysha examples              # NOT privysha --examples
privysha benchmark --save
privysha recommend --prompt "Analyze data"
```

---

## Benchmark failures

```bash
pip install -e .
python benchmarks/run_benchmarks.py --save
```

Compare against baseline:

```bash
python benchmarks/run_benchmarks.py --compare benchmarks/baseline/results.json
```

---

## Debug workflow

When something goes wrong:

```python
result = process(
    prompt,
    trace=True,
    debug=True,
    return_metrics=True,
)

print("Optimized:", result["optimized"])
print("Fallback:", result.get("fallback_reason"))
print("Error:", result.get("original_error"))
print("Diff:", result.get("diff"))
print("PII:", result.get("metrics", {}).get("pii_detected"))
```

---

## Environment variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI adapter |
| `ANTHROPIC_API_KEY` | Anthropic adapter |
| `GOOGLE_API_KEY` | Gemini adapter |
| `GROK_API_KEY` | Grok adapter |
| `PRIVYSHA_CACHE_DIR` | Cache directory (local advisor) |

Note: `PRIVYSHA_MODE` is **not** read by the library. Set `mode` per function call.

---

## Still stuck?

1. Run `privysha quick-test` to verify installation
2. Run `python examples/developer_preview_demo.py`
3. Open a [GitHub issue](https://github.com/AjayRajan05/privySHA/issues) with your `debug=True` output

---

## Related docs

- [FAQ](faq.md)
- [Debugging](debugging.md)
- [Performance Tuning](performance-tuning.md)
