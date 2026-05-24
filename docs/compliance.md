# Compliance Considerations

PrivySHA is a **developer tool** for preprocessing LLM prompts. It is not a certified compliance product. Use this guide to understand how PrivySHA fits into common regulatory frameworks and what remains your responsibility.

---

## General principles

- **Local by default**: Rule-based mode (`pii_mode="rule"`) processes data on your infrastructure with no required external calls.
- **No telemetry by default**: PrivySHA does not phone home. Optional ML extras download models you explicitly install.
- **Fail-safe**: On errors, PrivySHA returns sanitized or original content — it does not crash your application.
- **Transparency**: Use `trace=True` and `return_metrics=True` to audit what changed.

---

## GDPR (EU)

| Topic | PrivySHA role | Your responsibility |
|-------|---------------|---------------------|
| **Lawful basis** | Tool only | Determine legal basis for processing personal data |
| **Data minimization** | Masks PII before LLM calls | Configure `mode="strict"`, review false negatives on your data |
| **Right to erasure** | Stateless by default; in-memory metrics optional | Clear logs/metrics you persist; do not log raw PII |
| **Cross-border transfer** | Rule mode keeps preprocessing local | Choose LLM providers/regions; review sub-processors |
| **DPIA** | Reduces LLM exposure of raw PII | Complete DPIA for your full stack including LLM vendor |

**Recommendation**: Run PrivySHA in `strict` mode for EU personal data; validate detection on representative datasets; document masking in your privacy notice as a technical measure.

---

## CCPA / CPRA (California)

| Topic | PrivySHA role | Your responsibility |
|-------|---------------|---------------------|
| **Sale/share of personal info** | Reduces accidental disclosure to LLM vendors | Disclose LLM subprocessors; honor opt-out rights |
| **Sensitive personal information** | Detects/masks SSN, email, phone, etc. | Tune policies; audit for missed categories |
| **Consumer requests** | Does not store consumer profiles | Implement access/delete flows in your systems |

---

## HIPAA (US healthcare)

PrivySHA is **not HIPAA-certified** and does not provide a BAA.

| Topic | Guidance |
|-------|----------|
| **PHI in prompts** | Do not send PHI to public LLMs without a BAA and full risk analysis |
| **PrivySHA as control** | May reduce accidental PHI leakage but is not sufficient alone |
| **Required measures** | Encryption, access controls, audit logging, BAAs with all vendors |

**Recommendation**: For HIPAA-regulated workloads, use on-prem or BAA-covered models, strict mode, and independent security review — not consumer LLM APIs alone.

---

## Logging and retention

```python
# Good: structured metrics without raw PII
result = process(user_input, return_metrics=True, trace=True)
log.info({"pii_detected": result["metrics"]["pii_detected"], "latency_ms": ...})

# Avoid: logging raw prompts in production
# log.info(user_input)  # may contain PII
```

Disable or rotate `MetricsDashboard` exports if you persist metrics to disk.

---

## Optional ML mode

`pip install privysha[ml]` may download spaCy/transformers models. For regulated data:

- Prefer **rule-based mode** (`pii_mode="rule"`, default)
- Restrict outbound network in production if required
- Document model provenance in your compliance packet

---

## Disclaimer

This document is informational only and does not constitute legal advice. Consult qualified counsel for compliance decisions specific to your jurisdiction and use case.
