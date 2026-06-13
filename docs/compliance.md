# Compliance Considerations

**PrivySHA v0.3.0 developer preview** — privacy tooling, not a certified compliance product.

---

## Disclaimer

PrivySHA helps reduce PII exposure in LLM prompts through automated detection and masking. It does **not**:

- Provide legal compliance certification (GDPR, CCPA, HIPAA, etc.)
- Replace a Data Protection Impact Assessment (DPIA)
- Guarantee 100% PII detection in all cases
- Handle data at rest, data retention, or access control

Use PrivySHA as one layer in a broader privacy and security program.

---

## What PrivySHA provides

| Capability | How |
|------------|-----|
| PII detection | Rule-based (default) or ML-enhanced (`pii_mode="hybrid"`) |
| PII masking | Replaces detected values with hashed tokens |
| Injection detection | Identifies common prompt injection patterns |
| Audit trail | `trace=True`, `return_metrics=True` for processing records |
| Fail-closed mode | `security_fail_closed=True` blocks on total failure |
| Reversible masking | Opt-in `reversible=True` + `unmask()` |

---

## GDPR considerations

PrivySHA can help with GDPR Article 25 (data protection by design) by masking personal data before it reaches third-party LLM providers.

**Recommended settings for EU personal data:**

```python
from privysha import process

result = process(
    user_prompt,
    mode="strict",
    pii_mode="hybrid",           # higher accuracy
    security_fail_closed=True,   # block on failure
    return_metrics=True,
    trace=True,                  # audit trail
)
```

**You are still responsible for:**

- Lawful basis for processing
- Data Processing Agreements with LLM providers
- Right to erasure (reversible masking stores mappings — use with care)
- Cross-border data transfer assessments

---

## CCPA considerations

PrivySHA masks personal information before LLM transmission, reducing inadvertent disclosure.

Log `return_metrics=True` output for processing records, but ensure logs themselves do not contain unmasked PII.

---

## HIPAA considerations

PrivySHA is **not HIPAA-certified**. For healthcare workloads:

- Use `mode="strict"` and `security_fail_closed=True`
- Do not use `reversible=True` unless you have a secure vault for masking maps
- Conduct your own risk assessment
- Consider on-premise models via PrivyFit + Ollama

---

## Audit logging

```python
result = process(
    prompt,
    mode="strict",
    return_metrics=True,
    trace=True,
)

audit_record = {
    "pii_detected": result["metrics"]["pii_detected"],
    "pii_masked": result.get("pii_masked"),
    "risk_level": result["metrics"]["risk_level"],
    "threats_blocked": result["metrics"]["threats_blocked"],
    "processing_time_ms": result["metrics"]["processing_time_ms"],
}
# Store audit_record — do NOT store original unmasked prompt in logs
```

---

## Fail-open vs fail-closed

| Mode | Behavior | Use case |
|------|----------|----------|
| Fail-open (default) | Returns best-effort result on failure | General apps |
| Fail-closed | Returns blocked placeholder on failure | Regulated workloads |

```python
process(prompt, security_fail_closed=True)
```

---

## Data residency

PrivySHA processes data in-process on your infrastructure. It does not send data to external services unless:

- You use `pii_mode="hybrid"` or `"ml_only"` (local ML models)
- You use PrivyFit with `refresh_catalog=True` (HuggingFace API)
- Your LLM adapter sends the processed prompt to a provider API

For strict data residency, use local models (Ollama) with `RoutingStrategy.LOCAL_PRIVACY`.

---

## Related docs

- [Security](security.md)
- [Developer Preview](developer-preview.md)
- [Local Model Advisor](local-advisor.md)
