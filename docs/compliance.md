# Compliance

**PrivySHA v0.4.1** — privacy tooling, not a certified compliance product.

---

## What PrivySHA provides

- PII detection and masking before LLM calls
- Configurable fail-closed mode (`mode="strict"`)
- Audit-friendly typed results (`ProcessResult.security`, traces)
- Local preprocessing without sending raw PII to cloud models (when self-hosted)

---

## What PrivySHA does not provide

- Legal compliance certification (GDPR, HIPAA, SOC 2, etc.)
- Data processing agreements or audit reports
- Guaranteed detection of all PII in all locales
- Replacement for organizational privacy policies

---

## Recommended practices

1. **Pin the version** — `privysha==0.4.1`
2. **Use `mode="strict"`** for regulated paths where failure must block
3. **Prefer `wrap_llm()`** over `auto_patch()` for scoped control
4. **Log `result.degraded`** in balanced mode — indicates fallback was used
5. **Review mask formats** — `[EMAIL_HASH]_*` tokens, not reversible by default
6. **Combine with org controls** — access policies, retention, DPA with LLM vendor

---

## Reversible masking

Only enable when you have a documented need to restore values in LLM output:

```python
from privysha.core.policy_config import PolicyConfig
sanitize(prompt, policy=PolicyConfig(reversible=True))
```

Store `masking_map` securely — it can reverse pseudonymization.

---

## Data residency

`process()` and `sanitize()` run locally. LLM calls via `Agent` or `wrap_llm` send **processed** prompts to the provider you configure.

---

## Related

- [security.md](security.md)
- [developer-preview.md](developer-preview.md)
