# FAQ

**ASHA v0.4.2**

---

## General

### What is ASHA?

A drop-in layer that masks PII, checks prompt injection patterns, and compresses tokens before prompts reach LLM providers.

### Is it production-ready?

**For pinned pilots: yes, with monitoring.** Architecture is complete in 0.4.2. **For stable semver: not until 1.0.0.** Use `asha==0.4.2` and read [developer-preview.md](developer-preview.md).

### Python version?

**3.10+** (3.10, 3.11, 3.12 in CI).

---

## API

### What can I import from the root?

```python
from asha import process, sanitize, optimize, Agent
```

Nothing else - no `wrap_llm`, `Pipeline`, or `Processor` at root.

### Where is wrap_llm?

```python
from asha.integrations import wrap_llm
```

### What does process() return?

A **`ProcessResult`** dataclass. `str(result)` returns `result.output`.

### Does process() raise?

- **`mode="balanced"`** (default): fail-open - degraded fallback, `result.degraded=True`
- **`mode="strict"`**: raises `ASHAProcessingError` on total failure

### How do I get metrics?

```python
result = process("prompt")
print(result.metrics.token_reduction_pct)
print(result.security.pii_detected)
```

No `return_metrics=True` - use typed fields.

### How do I set pii_mode or reversible?

```python
from asha.core.policy_config import PolicyConfig
process(prompt, policy=PolicyConfig(pii_mode="hybrid", reversible=True))
```

Top-level `pii_mode=` on `process()` raises `TypeError`.

---

## Modes

| Mode | Description |
|------|-------------|
| `balanced` | Default - security + optimization |
| `strict` | Fail-closed |
| `lite` | Minimal policy features |
| `off` | Passthrough |

---

## Performance

### Token reduction?

Typically **5-15%** on verbose prompts. Already-short prompts may see little change. See [benchmarks.md](benchmarks.md).

### Speed?

Roughly **20-80 ms** for rule-based PII on typical prompts. Use `mode="lite"` or `mode="off"` for lower latency.

---

## Security

### What PII is detected?

Emails, phones, SSNs, credit cards, API keys, JWTs, IPs, and more. See [security.md](security.md).

### GDPR compliant?

ASHA is **privacy tooling**, not a certified compliance product. See [compliance.md](compliance.md).

---

## Agent

### Key parameters?

`model`, `privacy`, `token_budget`, `provider`, `routing_config`, `local_model`, `sample_prompts`.

### What does run() return?

**String** by default. **`AgentResult`** when `trace=True`.

---

## Removed in v0.4.1

| Removed | Use instead |
|---------|-------------|
| `Pipeline`, `Processor` | `process()` or `PromptProcessor` |
| Root `wrap_llm` | `asha.integrations.wrap_llm` |
| `security_fail_closed=` | `mode="strict"` |
| `return_metrics=True` | `result.metrics` |
| `ModelRouter` | `Agent(routing_config=...)` |

Full list: [deprecations.md](deprecations.md).

---

## Related

- [Getting Started](getting-started.md)
- [Troubleshooting](troubleshooting.md)
- [Migration v0.4](migration-v0.4.md)
