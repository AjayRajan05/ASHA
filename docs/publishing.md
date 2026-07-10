# Publishing

**Current release: v0.4.2** (developer preview, Alpha classifier).

See [versioning.md](versioning.md).

---

## Build

```bash
pip install build twine
python -m build
twine check dist/*
```

CI runs wheel build and fresh-install smoke test on every push.

---

## Version bump

Update version in:

- `pyproject.toml` → `[project].version`
- `src/asha/__init__.py` → `__version__`
- `CHANGELOG.md`

Tag: `v0.4.2` (must match `pyproject.toml`).

---

## TestPyPI / PyPI

Workflows: `.github/workflows/publish-testpypi.yml`, `publish.yml`.

Smoke test after install:

```bash
python -c "from asha import process, sanitize; print(process('hello'))"
python -c "from asha.integrations import wrap_llm; print(wrap_llm)"
```

---

## Classifiers

Current: `Development Status :: 3 - Alpha`

Planned for 0.5+: Beta after API freeze period.

---

## Related

- [developer-preview.md](developer-preview.md)
- [roadmap.md](roadmap.md)
