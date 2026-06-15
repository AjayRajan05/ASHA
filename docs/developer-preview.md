# Developer Preview (v0.4.1)

PrivySHA **0.4.1** completes the architecture redesign. The core API is clear and layer boundaries are enforced by tests — but the project remains on the **0.x preview track** until community feedback supports a 1.0 stable release.

---

## What works today

| Area | Status |
|------|--------|
| `process()`, `sanitize()`, `optimize()` | Stable within 0.4.x |
| `wrap_llm()` via `privysha.integrations` | Production-suitable with pinned version |
| Typed results (`ProcessResult`, etc.) | Default since v0.4.0 |
| Policy modes (`balanced`, `strict`, `lite`, `off`) | Unified safety semantics |
| PII masking (rule-based) | Default, no extra installs |
| Provider adapters (OpenAI, Anthropic, Gemini, Ollama, Mock, …) | Optional extras |
| Architecture tests | CI enforces layer boundaries |
| Benchmarks + CI gates | Reproducible baseline |

---

## Preview / evolving

| Area | Notes |
|------|-------|
| PrivyFit (`recommend_local_model`) | Preview — APIs may change |
| `auto_patch()` | Global SDK monkey-patch — prefer `wrap_llm()` |
| Hybrid / ML PII (`pii_mode="hybrid"`) | Requires `privysha[ml]` |
| Framework integrations | Tested when optional deps installed |
| Agent smart routing | `routing_config` dict, not full IR-based routing |

---

## Not ready yet

- **Stable 1.0 API guarantee** — 0.x may still have breaking changes
- **Certified compliance product** — tooling only; see [compliance.md](compliance.md)
- **Semantic optimization guarantees** — MSDPC compression; benchmark semantic-equivalence gate is ~30%
- **Enterprise multi-tenant routing at scale**

---

## Who should use it now

| Use case | Recommendation |
|----------|----------------|
| Preprocess prompts before LLM calls | Yes — pin `privysha==0.4.1` |
| Wrap OpenAI/Anthropic clients | Yes — use `wrap_llm()` |
| Regulated workload as sole compliance control | No — add your own review |
| Library dependency without version pin | Wait for 1.0.0 |
| Global SDK patching in shared runtimes | Avoid `auto_patch()` — use `wrap_llm()` |

---

## Public API (v0.4.1)

```python
from privysha import process, sanitize, optimize, Agent
from privysha.integrations import wrap_llm, auto_patch
from privysha.runtime import PromptProcessor
from privysha.types import ProcessResult
from privysha.core.policy_config import PolicyConfig
```

Root lazy exports (`Pipeline`, `Processor`, `wrap_llm` at root) were **removed**, not deprecated.

---

## Try it

```bash
pip install privysha
python -c "from privysha import process; print(process('Contact a@b.com'))"
```

Or from source:

```bash
pip install -e .
python examples/developer_preview_demo.py
```

---

## Versioning

- **0.4.x** — Architecture-complete preview; pin in production
- **0.5.x** — Planned API freeze period before 1.0
- **1.0.0** — Stable public API (target after feedback)

See [versioning.md](versioning.md) and [roadmap.md](roadmap.md).

---

## Feedback

Open a [GitHub issue](https://github.com/AjayRajan05/privySHA/issues) with:

1. Does `process()` / `wrap_llm()` fit your app without heavy refactoring?
2. Are modes (`strict` / `balanced`) clear for your security needs?
3. What providers or PII types are missing?
