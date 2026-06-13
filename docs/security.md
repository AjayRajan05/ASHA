# Security

**PrivySHA v0.3.0** — PII detection, masking, and prompt injection protection.

---

## Overview

PrivySHA detects and masks sensitive information before prompts reach LLM providers. Security runs as the first pipeline stage and is also available standalone via `sanitize()`.

---

## Detected PII types

Rule-based detection (`security/pii_detector.py`, patterns in `security/patterns.py`):

| Type | Examples |
|------|----------|
| Email | `user@example.com` |
| Phone | `555-123-4567`, `(555) 123-4567` |
| SSN | `123-45-6789` |
| Credit card | `4111-1111-1111-1111` |
| Address | Street addresses with context keywords |
| Name | Names near context keywords (heuristic) |
| API key / secret | `sk-...`, bearer tokens |
| JWT | `eyJ...` tokens |
| IP address | `192.168.1.1` |
| Date of birth | Near "birth", "dob" keywords |
| ZIP code | US postal codes |

Teaching placeholders like `test@example.com` are skipped via `is_example_email()` in `security/patterns.py`.

---

## Mask format

Detected values are replaced with hashed tokens:

```
john@example.com  →  [EMAIL_HASH]_a1b2c3
555-123-4567      →  [PHONE_HASH]_d4e5f6
sk-abc123...      →  [REDACTED]
```

Exact suffixes are deterministic hashes of the original value.

---

## PII detection modes

| Mode | Description | Install |
|------|-------------|---------|
| `rule` | Regex + heuristic (default) | Core only |
| `hybrid` | Rules + ML models | `pip install privysha[ml]` |
| `ml_only` | ML-only (experimental) | `pip install privysha[ml]` |

```python
from privysha import process, sanitize

process("Contact john@example.com", pii_mode="rule")
sanitize("Contact john@example.com", pii_mode="hybrid")
```

If ML dependencies are missing, modes fall back to `rule`.

---

## Policy modes and security

| Mode | Security behavior |
|------|-------------------|
| `strict` | Maximum PII masking, enhanced checks |
| `balanced` | Standard detection (default) |
| `lite` | Basic checks only |
| `off` | No security processing (passthrough) |

```python
process(prompt, mode="strict")
process(prompt, mode="off")  # no masking at all
```

---

## Security levels

Separate from policy mode — controls detection aggressiveness:

```python
process(prompt, security_level="low")     # basic
process(prompt, security_level="medium")  # default
process(prompt, security_level="high")    # enhanced
```

---

## Prompt injection detection

The security layer detects common injection patterns:

- "Ignore previous instructions"
- Role-play jailbreak attempts
- System prompt override patterns

Threats are scored and logged in `security_result.detected_threats`.

Control via pipeline stage config:

```python
pipeline.configure_stage("security", {
    "enable_injection_detection": True,
    "enable_pii_detection": True,
})
```

---

## Fail-open vs fail-closed

**Default (fail-open):** If the security pipeline fails entirely, `process()` returns a best-effort scrubbed result or the original prompt — it does not raise.

**Fail-closed (opt-in):** For regulated workloads:

```python
process(prompt, security_fail_closed=True)
sanitize(prompt, security_fail_closed=True)
```

Returns a blocked placeholder instead of raw PII on total failure.

Use `debug=True` to inspect `fallback_reason` and `original_error`.

---

## Reversible masking

Opt-in — stores a `masking_map` for post-LLM restoration:

```python
from privysha import sanitize, unmask

result = sanitize(
    "Email alice@corp.com",
    return_details=True,
    reversible=True,
)
safe = result["sanitized"]
restored = unmask(llm_output, result["masking_map"])
```

Uses `MaskingVault` in `security/masking_vault.py`.

---

## SecurityLayer (advanced)

Direct access for custom integrations:

```python
from privysha import SecurityLayer, SecurityLevel

layer = SecurityLayer(security_level=SecurityLevel.MEDIUM)
result = layer.scan("Contact john@email.com")
print(result["masked_text"])
print(result["pii_detected"])
```

---

## sanitize() vs process()

| Function | Security | Optimization |
|----------|----------|--------------|
| `sanitize()` | Yes | No |
| `process()` | Yes | Yes |
| `optimize()` | No | Yes |

```python
from privysha import sanitize

safe = sanitize("My SSN is 123-45-6789")
# or with details:
result = sanitize("prompt", return_details=True)
print(result["pii_detected"])
```

---

## Compliance note

PrivySHA provides **tooling** for privacy-aware prompt processing. It is not a certified compliance product. See [compliance.md](compliance.md) for GDPR/CCPA considerations.

---

## Related docs

- [Core Concepts](core-concepts.md) — modes and PII modes
- [Compliance](compliance.md) — regulatory considerations
- [Pipeline](pipeline.md) — security stage in context
