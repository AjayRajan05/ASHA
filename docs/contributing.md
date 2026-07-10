# Contributing

**ASHA v0.4.2** - development guide.

---

## Setup

```bash
git clone https://github.com/AjayRajan05/privySHA.git
cd privySHA
pip install -e ".[dev]"
```

Python **3.10+** required.

---

## Run tests

```bash
# Full suite
pytest tests -q

# Architecture boundaries only
pytest tests/architecture -q

# With coverage (CI uses --cov-fail-under=50)
pytest --cov=asha --cov-report=term -m "not slow"
```

### Framework integration tests (optional deps)

```bash
pip install -e ".[integrations,flask,django,llamaindex]"
pip install "crewai>=0.80.0,<1.0.0" "langgraph>=0.2.0,<1.0.0"
pytest tests/test_framework_smoke.py tests/test_fastapi_integration.py \
  tests/test_django_integration.py tests/test_langchain_integration.py \
  tests/test_llamaindex_integration.py tests/test_instructor_integration.py -q
```

---

## Architecture rules

Enforced by `tests/architecture/test_boundaries.py`:

| Layer | Must not import |
|-------|-----------------|
| `core/` | `runtime`, `integrations`, `compat` |
| `runtime/` | `integrations`, `compat` |
| `types/` | `compat`, `runtime`, `integrations` |
| `utils/` | `compat` |

Do not reintroduce `Pipeline`, root lazy exports, or `compat/` on the `process()` hot path.

---

## Package layout

```
src/asha/
├── core/           # engines, policy, security, compiler
├── runtime/        # PromptProcessor, Agent, adapters
├── integrations/   # wrap_llm, auto_patch, middleware
├── types/          # ProcessResult, etc.
├── utils/          # dropin functions
├── compat/         # legacy_results only
└── cli/
```

---

## Code style

```bash
flake8 src/asha --select=F401,F824
mypy src/asha --ignore-missing-imports
```

Match existing conventions - minimal diffs, no drive-by refactors.

---

## Docs

```bash
pip install -e ".[docs]"
mkdocs serve
mkdocs build --strict
```

Update docs when changing public API. Root exports are: `process`, `sanitize`, `optimize`, `Agent`, `anchor`.

---

## Release track

Current: **0.4.2 developer preview**. Breaking changes allowed in 0.x - document in `CHANGELOG.md` and `docs/migration-v0.4.md`.

---

## Pull requests

1. Fork and branch
2. Add tests for behavior changes
3. Run full pytest locally
4. Update relevant docs
5. Open PR with clear description

See [developer-preview.md](developer-preview.md) for scope.
