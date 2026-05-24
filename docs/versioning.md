# Versioning Policy

PrivySHA follows [Semantic Versioning 2.0.0](https://semver.org/).

## Supported releases

| Version | Status |
|---------|--------|
| 1.x | Active |
| 0.x | Maintenance only |

## Breaking changes

Breaking changes are reserved for major releases and documented in `CHANGELOG.md` and `docs/migration.md`.

## Deprecation policy

- Deprecated APIs receive at least one minor release with warnings before removal.
- Experimental APIs (`auto_patch`, ML-only modes) may change with notice in release notes.

## Python support

PrivySHA 1.0 requires **Python 3.10+**.
