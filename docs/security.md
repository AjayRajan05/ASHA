# Security

**ASHA v0.4.2** - PII detection, masking, and prompt injection checks.

Security runs as the first engine in `process()` and is the sole engine in `sanitize()`.

---

## Detected PII types

Rule-based detection (`core/security/pii_detector.py`, patterns in `core/security/patterns.py`):

| Type | Examples |
|------|----------|
| Email | `user@example.com` |
| Phone | `555-123-4567` |
| SSN | `123-45-6789` |
| Credit card | `4111-1111-1111-1111` |
| API key / secret | `sk-...` |
| JWT | `eyJ...` |
| IP address | `192.168.1.1` |
| Address / name | Heuristic with context keywords |

Teaching placeholders like `test@example.com` are skipped.

---

## Mask format

```
john@example.com  →  [EMAIL_HASH]_a1b2c3
555-123-4567      →  [PHONE_HASH]_d4e5f6
sk-abc123...      →  [REDACTED]
```

---

## PII detection mode

Set via `PolicyConfig`, not a top-level kwarg:

```python
from asha import process
from asha.core.policy_config import PolicyConfig

process("Contact john@example.com", policy=PolicyConfig(pii_mode="rule"))
process("...", policy=PolicyConfig(pii_mode="hybrid"))   # needs asha[ml]
```

| `pii_mode` | Description | Install |
|------------|-------------|---------|
| `rule` | Regex + heuristic (default) | Core only |
| `hybrid` | Rules + ML pipeline | `asha[ml]` |
| `ml_only` | Experimental ML-only | `asha[ml]` |

Missing ML deps fall back to `rule` with a warning.

---

## Safety modes

```python
from asha import process, sanitize

process(prompt, mode="balanced")  # fail-open fallback
process(prompt, mode="strict")      # raises ASHAProcessingError
sanitize(prompt, mode="strict")
```

| Mode | On total security failure |
|------|---------------------------|
| `balanced` / `lite` | Degraded result, `degraded=True` |
| `strict` | Raises |
| `off` | Passthrough |

---

## sanitize() only

```python
from asha import sanitize

result = sanitize("john@corp.com - summarize")
print(result.safe)
print(result.security.pii_detected)
```

---

## Reversible masking

```python
from asha import sanitize
from asha.core.policy_config import PolicyConfig
from asha.utils.unmask import unmask

result = sanitize(
    "Email alice@corp.com",
    policy=PolicyConfig(reversible=True),
)
restored = unmask(llm_output, result.security.masking_map)
```

---

## wrap_llm security

```python
from asha.integrations import wrap_llm

client = wrap_llm(openai_client, mode="balanced")
```

- Uses caller's `mode` for preprocessing
- Infrastructure/wrap failures raise when `mode != "off"` (never silently send raw prompts)

---

## Threat detection

Injection patterns and threat scoring run inside `core/security/service.py`. Results appear in `result.security.threats` and `result.security.threat_level`.

---

## Related

- [compliance.md](compliance.md) - GDPR/CCPA tooling notes
- [core-concepts.md](core-concepts.md) - modes and PolicyConfig
- [faq.md](faq.md)
