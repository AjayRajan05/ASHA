# Versioning Policy

PrivySHA follows [Semantic Versioning 2.0.0](https://semver.org/).

## Current release track

| Version | Status | Notes |
|---------|--------|-------|
| **0.3.x** | **Active — developer preview** | Current line; APIs may change |
| 1.0.x | Superseded | Released 2026-05-24, then project returned to 0.x preview track |
| 0.2.x | Previous preview | Modular pipeline, drop-in API |
| 0.1.x | Historical | Initial releases |

See [developer-preview.md](developer-preview.md) for scope and limitations.

## Release timeline

```
2026-03-13  0.1.0   Initial release
2026-05-23  0.2.0   Modular pipeline
2026-05-24  1.0.0   Brief stable release
2026-05-24  1.0.1   Patch
2026-06-05  0.3.0   Developer preview re-release (+ PrivyFit)
```

Future **1.0.0** (stable) is planned after community feedback on the 0.3.x preview — not before.

## Breaking changes

During **0.x**, breaking changes are allowed in any release. They are documented in `CHANGELOG.md` and `docs/migration.md`.

After **1.0.0** (when it ships as stable), breaking changes are reserved for major releases.

## Deprecation policy

- Deprecated APIs receive at least one minor release with warnings before removal.
- `DebugTracer` is deprecated in favor of `TraceContext` (see [debugging.md](debugging.md)).
- Experimental APIs (`auto_patch`, `pii_mode="ml_only"`, PrivyFit) may change with notice in release notes.

## Python support

PrivySHA **0.3.x** requires **Python 3.10+** (3.10, 3.11, 3.12 supported per classifiers).

## PyPI classifiers

Current package status: **Development Status :: 3 - Alpha** (developer preview).
