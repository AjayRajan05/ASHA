# PrivySHA Roadmap

**Privacy-first prompt compilation for LLM applications**

This roadmap reflects the actual project state as of **v0.3.0** (June 2026). Dates move forward from here — earlier docs incorrectly listed 1.0.0 in Q1 2025 and mixed 2024/2025/2026 timelines.

---

## Current status — v0.3.0 (June 2026)

**Developer preview.** APIs may change before 1.0.0.

### Shipped

- **Drop-in API**: `process()`, `wrap_llm()`, `optimize()`, `sanitize()` (+ async variants)
- **Policy modes**: `balanced`, `strict`, `lite`, `off`
- **PII detection**: rule-based default; optional ML via `pip install privysha[ml]`
- **7-stage pipeline**: security → IR → routing → compilation → optimization → generation → result
- **Adapters**: OpenAI, Anthropic, Gemini, Grok, Ollama, HuggingFace, Mock
- **Agent class**: pipeline + adapter with fallback and routing support
- **PrivyFit (preview)**: `recommend_local_model()`, `privysha recommend`
- **CLI**: `privysha`, `privysha quick-test`, `privysha examples`, `privysha benchmark`, `privysha recommend`
- **Integrations**: FastAPI, Flask, Django, LangChain, Instructor, Guardrails, LlamaIndex, OTEL
- **Benchmarks**: `benchmarks/run_benchmarks.py` with CI gates

Try the demo: `python examples/developer_preview_demo.py`

Feedback: [Developer Preview](developer-preview.md)

---

## PrivyFit — Local Model Advisor (0.3.0 preview)

See [local-advisor.md](local-advisor.md) for full documentation.

**Shipped in 0.3.0:**

- `recommend_local_model()` with workload fingerprinting
- HuggingFace catalog + offline fallback
- VRAM fit ranking, `privysha recommend` CLI
- `RoutingStrategy.LOCAL_PRIVACY`
- `Agent(local_model="auto")`, `wrap_llm(..., auto_select_local_model=True)`

**Before stable 1.0:**

- Harden catalog fetch and measured-speed calibration
- Expand fallback model set and benchmark evidence

---

## Planned releases (forward-looking)

### v0.4.0 (target: H2 2026)

- Prompt caching for repeated patterns
- Expanded international PII formats
- Enhanced CLI (batch processing, config profiles)
- Hardened routing defaults

### v0.5.0 (target: H2 2026)

- Cost-aware multi-model routing improvements
- Prometheus / OTEL metrics export expansion
- Additional framework adapters

### v1.0.0 (target: 2027, after community feedback)

- Stable public API guarantee
- Migration guide from 0.x finalized
- Production readiness review
- Documented SLA targets for fail-safe behavior

**Not committed for 1.0:** managed cloud service, multi-tenant SaaS, no-code workflow builder — these are long-term ideas only.

---

## Completed milestones

| Milestone | Version | Date |
|-----------|---------|------|
| Initial release | 0.1.0 | 2026-03-13 |
| Modular pipeline + drop-in API | 0.2.0 | 2026-05-23 |
| Policy gate, OTEL wiring, benchmark gates | 1.0.0 / 1.0.1 | 2026-05-24 |
| Preview re-release + PrivyFit | 0.3.0 | 2026-06-05 |

---

## How to influence the roadmap

- [GitHub Issues](https://github.com/AjayRajan05/privySHA/issues) — bugs and feature requests
- [GitHub Discussions](https://github.com/AjayRajan05/privySHA/discussions) — design feedback
- Pull requests — small, focused changes welcome; discuss large changes in an issue first

---

## Strategic focus

1. **Drop-in adoption** — `process()` and `wrap_llm()` must stay simple
2. **Fail-safe defaults** — never leak raw PII on pipeline failure (opt-in fail-closed for regulated workloads)
3. **Honest benchmarks** — publish reproducible numbers, not marketing claims
4. **Preview transparency** — document what works vs what is experimental
