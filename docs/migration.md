# Migration

**Migrating to PrivySHA** from other tools or older PrivySHA versions.

---

## From PrivySHA 0.3.x → 0.4.1

See the dedicated guide: **[migration-v0.4.md](migration-v0.4.md)**

Key changes:

- `ProcessResult` dataclass (not dict/string)
- Root imports frozen to four symbols
- `wrap_llm` → `privysha.integrations`
- Kwargs → `mode` + `PolicyConfig`
- `Pipeline` / `Processor` removed

---

## From Presidio / regex / spaCy

Replace ad-hoc PII scrubbing with:

```python
from privysha import sanitize, process

safe = sanitize(user_input).output
# or full path:
result = process(user_input, mode="strict")
```

PrivySHA adds injection checks and token optimization in `process()`.

---

## From manual prompt engineering

```python
from privysha import process

optimized = process(verbose_user_message).output
```

Use `mode="strict"` when failure must block, not degrade.

---

## From wrapping SDKs manually

```python
# Before: preprocess then call
safe = process(user_msg).output
client.chat.completions.create(..., messages=[{"role":"user","content": safe}])

# After
from privysha.integrations import wrap_llm
client = wrap_llm(client, mode="balanced")
client.chat.completions.create(...)  # automatic preprocessing
```

---

## Version pinning

```txt
privysha==0.4.1
```

Review [CHANGELOG.md on GitHub](https://github.com/AjayRajan05/privySHA/blob/main/CHANGELOG.md) before upgrading across 0.x minors.

---

## Related

- [deprecations.md](deprecations.md)
- [getting-started.md](getting-started.md)
