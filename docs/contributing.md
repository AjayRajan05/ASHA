# Contributing

**PrivySHA v0.4.1** — development guide.

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
pytest --cov=privysha --cov-report=term -m "not slow"
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
src/privysha/
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
flake8 src/privysha --select=F401,F824
mypy src/privysha --ignore-missing-imports
```

Match existing conventions — minimal diffs, no drive-by refactors.

---

## Docs

```bash
pip install -e ".[docs]"
mkdocs serve
mkdocs build --strict
```

Update docs when changing public API. Root exports are only: `process`, `sanitize`, `optimize`, `Agent`.

---

## Release track

Current: **0.4.1 developer preview**. Breaking changes allowed in 0.x — document in `CHANGELOG.md` and `docs/migration-v0.4.md`.

---

## Pull requests

1. Fork and branch
2. Add tests for behavior changes
3. Run full pytest locally
4. Update relevant docs
5. Open PR with clear description

See [developer-preview.md](developer-preview.md) for scope.
