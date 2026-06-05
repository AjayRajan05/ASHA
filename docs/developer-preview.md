# Developer Preview (v0.3.0)

PrivySHA is in **early development**. Treat this release as a developer preview: useful for experiments and feedback, not as a frozen production dependency until **1.0.0**.

## What works today

| Area | Status |
|------|--------|
| Drop-in APIs (`process`, `wrap_llm`, `optimize`, `sanitize`) | Working — primary focus |
| PII masking & prompt optimization | Working — modes: `balanced`, `strict`, `lite` |
| Provider adapters (OpenAI, Anthropic, Gemini, Ollama, …) | Working — optional extras |
| PrivyFit local model advisor | **Preview** — `recommend_local_model()`, `privysha recommend` |
| Pipeline / routing / Agent | **Preview** — APIs may change |
| Benchmarks & CI | Reproducible baseline in `benchmarks/` |

## Not ready yet

- Stable 1.0 API guarantee (expect breaking changes in 0.x)
- Full enterprise compliance reporting
- Production-hardened multi-tenant routing at scale
- Complete HuggingFace catalog parity with dedicated hardware tools
- Measured-speed calibration for all GPU backends

See the full [roadmap](roadmap.md).

## Try it in 60 seconds

```bash
pip install -e .
python examples/developer_preview_demo.py
```

Or:

```python
from privysha import process

print(process("My email is user@example.com — summarize this report."))
```

## Semantic versioning

- **0.x** — Developer preview; breaking changes allowed
- **1.0.0** — First stable API (planned after community feedback)

## How to give feedback

We are actively looking for **bug reports, UX feedback, and feature requests** at this stage. Small, focused PRs are welcome; large architectural changes are best discussed in an issue first.

**Please tell us:**

1. Is `pip install -e .` and the [developer preview demo](../examples/developer_preview_demo.py) intuitive?
2. Does `process()` / `wrap_llm()` fit your app without heavy refactoring?
3. For PrivyFit: did recommendations match your workload and hardware expectations?
4. What PII types or providers are missing for your use case?

Open a [GitHub issue](https://github.com/AjayRajan05/privySHA/issues) with the `feedback` label, or comment on the release announcement.

## Announcement draft

Use this when posting to GitHub Discussions, Hacker News, Reddit, or Dev.to:

---

**Title:** PrivySHA 0.3.0 — developer preview: privacy-first prompt compiler + local LLM advisor

**Body:**

We are opening PrivySHA for early feedback. It sits between your app and any LLM to mask PII, compress prompts, and (new in 0.3) suggest local models for your workload via **PrivyFit**.

```bash
pip install privysha  # or pip install -e . from source
python examples/developer_preview_demo.py
```

**Status:** 0.x developer preview — APIs may change before 1.0.

We would love feedback on:

- Setup and first-run experience
- Whether drop-in `process()` / `wrap_llm()` fits real projects
- PrivyFit recommendations for your prompts + GPU

Repo: https://github.com/AjayRajan05/privySHA  
Docs: [Developer preview](developer-preview.md) · [Local advisor](local-advisor.md)

---

## License

Apache 2.0 — see [LICENSE](../LICENSE). You may use, modify, and contribute under those terms.
