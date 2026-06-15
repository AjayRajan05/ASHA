# Prompt IR

**PrivySHA v0.4.1** — internal intermediate representation.

---

## Not public API

Prompt IR lives in `core/_ir/`. It is built internally by `compile_prompt()` and used by the compiler and optimizer.

**Do not import** `PromptIR` or `IRBuilder` in application code — the API may change without notice.

```python
from privysha import compile_prompt  # NOT available at root
```

Use `process()` or `optimize()` instead.

---

## What IR captures

When `compile_prompt()` runs inside `process()`:

- Intent (analyze, summarize, create, …)
- Entities and constraints
- Structure for MSDPC optimization

You never pass or receive IR objects from public functions.

---

## compile_prompt engine

```python
# Internal flow only:
# IRBuilder.parse(prompt) → PromptCompiler.compile(ir)
```

Exposed only via `process()` and `PromptProcessor`.

---

## Agent and routing

v0.4.1 does not expose IR-based `ModelRouter`. Task routing uses `Agent(routing_config={...})` with string model names.

---

## Related

- [architecture.md](architecture.md)
- [pipeline.md](pipeline.md)
