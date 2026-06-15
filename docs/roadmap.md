# Roadmap

Forward-looking plan from **v0.4.1** (June 2026). Dates are estimates.

---

## Shipped in v0.4.1

- Frozen root API (`process`, `sanitize`, `optimize`, `Agent`)
- `PromptProcessor` as sole orchestrator (security → compile → optimize)
- Typed `ProcessResult` / `SanitizeResult` / `OptimizeResult`
- Unified `mode=` safety semantics
- `runtime/resolve.py` — no compat on hot path
- Architecture boundary tests in CI
- Dead legacy code removed (`Pipeline`, `ModelRouter`, `debug/` package, etc.)
- `wrap_llm` / `auto_patch` in `privysha.integrations`

---

## v0.5.x (target: H2 2026)

- API freeze — deprecation warnings only, no breaking removals
- Docs and examples fully aligned to 0.4.1+
- Integration test matrix with optional deps in CI
- Prompt caching for repeated patterns
- Expanded international PII formats
- PyPI classifier → Beta

---

## v1.0.0 (target: after community feedback)

- Stable public API guarantee
- Migration guide finalized
- Production readiness checklist (security review, SLA docs)
- Documented support policy

**Not committed for 1.0:** managed cloud service, multi-tenant SaaS.

---

## Preview features (may change anytime)

| Feature | Module |
|---------|--------|
| PrivyFit local advisor | `runtime/local_advisor/` |
| Hybrid ML PII | `core/hybrid_pii.py` + `pii_pipeline/` |
| `auto_patch()` | `integrations/auto_patch.py` |
| Framework middleware | `integrations/fastapi`, `langchain`, etc. |

---

## Long-term ideas

- Cost-aware multi-model routing
- Prometheus metrics export expansion
- Prompt caching engine
- Additional framework adapters

See [developer-preview.md](developer-preview.md) for current limitations.
