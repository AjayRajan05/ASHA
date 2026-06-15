# Versioning Policy

PrivySHA follows [Semantic Versioning 2.0.0](https://semver.org/).

---

## Current release

| Version | Status | Notes |
|---------|--------|-------|
| **0.4.1** | **Active — developer preview** | Architecture complete; pin in production |
| 0.4.0 | Superseded | Typed results introduced |
| 0.3.x | Previous preview | Dict/string returns, lazy root exports |
| 1.0.x (2026-05) | Retracted track | Brief release; project returned to 0.x |

PyPI classifier: **Development Status :: 3 - Alpha**

---

## What 0.4.1 means

- Root API frozen: `process`, `sanitize`, `optimize`, `Agent` only
- `Pipeline`, `Processor`, root `wrap_llm` **removed** (not deprecated)
- `process(mode=)` + `policy=PolicyConfig(...)` — no loose deprecated kwargs
- Layer boundaries enforced in CI

Breaking changes within 0.4.x are documented in the [CHANGELOG](https://github.com/AjayRajan05/privySHA/blob/main/CHANGELOG.md) and [migration-v0.4.md](migration-v0.4.md).

---

## Path to 1.0.0

1. **0.4.x** — Architecture and API surface settled (current)
2. **0.5.x** — API freeze; deprecation-only changes
3. **1.0.0** — Stable public API guarantee

---

## Breaking changes during 0.x

Allowed in any 0.x release. Documented in:

- `CHANGELOG.md` on GitHub
- `docs/migration-v0.4.md`
- `docs/deprecations.md`

After **1.0.0**, breaking changes require a major release.

---

## Deprecation policy (post-1.0)

- Deprecated APIs get at least one minor release with warnings before removal
- v0.4.1 removed several symbols **without** a deprecation period (breaking cleanup within 0.4.x)

---

## Python support

**Python 3.10+** (3.10, 3.11, 3.12 tested in CI).

---

## Pinning in production

```toml
# pyproject.toml or requirements.txt
privysha==0.4.1
```

Review the [CHANGELOG](https://github.com/AjayRajan05/privySHA/blob/main/CHANGELOG.md) before upgrading across minor versions.
