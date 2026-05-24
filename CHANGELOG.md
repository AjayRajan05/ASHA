# Changelog

All notable changes to this project will be documented in this format.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

---

## [1.0.1] - 2026-05-24

### Added
- **`security_fail_closed`** opt-in on `process()` / `sanitize()` for regulated workloads
- **OTEL pipeline wiring** — `stage_span()` in all pipeline stages via `StageBase`
- **Benchmark P95/P99** latency percentiles in harness and CI output
- **~60 new tests** — optimize, wrap_llm negatives, phone/address PII, FastAPI, fail-closed, edge matrix, framework smoke, hybrid PII
- **Expanded extras** — `integrations`, `all`, `[llamaindex]` in pyproject.toml
- **Publish workflow gates** — benchmark compare, twine check, fresh wheel smoke

### Fixed
- **`process_async`** input validation parity with sync `process()`
- **Docs** — fail-open/fail-closed in security.md; Flask/Django/LlamaIndex/OTEL in integrations.md; Python 3.10+ in troubleshooting
- **Debug transparency** — `fallback_reason` and `original_error` in `debug=True` responses

### Changed
- CI coverage gate documented at **40%** (matches `--cov-fail-under=40`)

---

## [1.0.0] - 2026-05-24

### Stable Release

First stable release. Policy modes, PII detection, and drop-in wrappers behave
consistently; benchmarks and CI enforce quality gates.

### Added
- **Policy gate**: `mode="off"` and disabled security/optimization flags bypass
  pipeline stages via passthrough (`pipeline/policy_gate.py`)
- **Canonical PII patterns**: `security/patterns.py` shared across detectors,
  verification, and masking
- **Benchmark harness**: tiktoken metrics, expanded `sample_prompts.json` (10 cases),
  false-positive and fail-safe rate gates
- **OpenTelemetry extra**: `pip install privysha[otel]` with `enable_otel()` for
  optional stage span export
- **Docs site**: full MkDocs Material config, GitHub Pages deploy workflow
- **CI hardening**: coverage gate (55%), docs build, benchmark quality gates,
  dependabot, publish workflow test gate
- **Tests**: policy modes, auto_patch mocks, PII secrets/FP, threat scoring,
  async streaming, agent helpers, backward compat, otel

### Fixed
- **`mode="off"` still masked PII**: early passthrough + post-pipeline scrub skip
- **`Agent` token metrics**: use `prompts.compiled` structure and tiktoken counts
- **`wrap_llm`**: forwards `privacy` and `token_budget`; nested OpenAI streaming
- **`auto_patch`**: replaces last user message only; Anthropic v1 `Messages.create`;
  proper unpatch via `_restore_original()`
- **PII false positives**: `test@example.com` and teaching placeholders skipped
- **Secrets**: API keys/JWT/bearer patterns verified and masked with `[REDACTED]`
- **`run_security`**: honors `enable_pii_detection` / `enable_injection_detection`

### Changed
- **Version unified to 1.0.0** across `pyproject.toml`, `__init__.py`, README, docs
- **Publish trigger**: GitHub Release (published) or manual dispatch — not tag-only

### Release checklist (manual)
- Configure GitHub `pypi` environment for trusted publishing (see `docs/publishing.md`)
- Create GitHub Release `v1.0.0` after CI is green to trigger PyPI publish

---

## [0.2.0] - 2026-05-23

### Production-Stable Release

This release completes the modular pipeline refactor and stabilizes the public
drop-in API (`process`, `wrap_llm`, `optimize`, `sanitize`) for general use.

### Added
- **Opt-in reversible masking**: `reversible=True` on `process()`/`sanitize()`, `unmask()` helper, `MaskingVault`
- **Observability**: `TraceContext.log_warn()`, `LatencyBudgetEnforcer` wired in pipeline, `DebugTracer` deprecated
- **CI hardening**: mypy, wheel build + twine check, regression benchmark baseline, slow test job
- **Docs site**: `mkdocs.yml` with navigation to existing docs
- **Test suite expansion**: reversible masking, scoring, logging security, masking collision, performance, adapter mocks
- **Domain-owned PII detector**: `security/pii_detector.py` (compatibility shim at `utils/pii_detector.py`)
- **Pipeline contracts**: `pipeline/contracts.py` for shared types
- **Privacy helpers**: `utils/dropin_privacy.py` (`build_security_summary`, `extract_pii_types`)
- **Reproducible benchmarks**: `benchmarks/run_benchmarks.py` and `benchmarks/sample_prompts.json`
- **Lazy public API**: Advanced symbols load on first access (PEP 562) for faster imports
- **CI lint step**: flake8 F401/F824 checks in GitHub Actions
- **Integration test marker**: API-key tests skipped by default in CI

### Fixed
- **Unified `StageContext`**: Single canonical class in `pipeline/components/stage_context.py`
- **`process()` metrics**: `pii_detected` populated correctly; `debug_trace` no longer breaks result assembly
- **`SecurityResult` handling**: Dict and dataclass representations supported across drop-in utilities
- **Integration adapters**: Delegate to `process()` instead of composing core services directly
- **Async paths**: `process_async`, `optimize_async`, `sanitize_async` use shared security helpers
- **Duplicate `ThreatType`** in `__all__`
- **~109 unused import** lint issues across the codebase
- **`comprehensive_test.py`**: No longer checks for deleted `pipeline.py` / `stages/` paths
- **Integration tests**: No longer call `sys.exit(1)` when API keys are missing

### Changed
- **PyPI classifier**: `Development Status :: 5 - Production/Stable`
- **Version unified to 0.2.0** across `pyproject.toml`, `__init__.py`, README, and docs
- **README architecture**: Updated to reflect `pipeline/` modular layout
- **Public API**: Core surface limited to `process`, `wrap_llm`, `optimize`, `sanitize`, `Agent`, `Pipeline`, `AdapterFactory`
- **Test suite**: `tests_v2/` included in default test paths
- **Performance claims**: Benchmark docs reference reproducible harness output

### Release checklist (manual)
- Configure GitHub `pypi` environment for trusted publishing (see `.github/workflows/publish.yml`)
- Tag `v0.2.0` and run publish workflow after CI is green

---

## [0.1.7] - 2026-04-28

### PROGRESSIVE ENHANCEMENT RELEASE

### Added
- **Progressive Enhancement Architecture**: ML features now opt-in with `pii_mode` parameter
- **Lightweight Default**: No automatic model downloads, instant startup
- **Multi-stage PII Pipeline**: Advanced detection in `core/pii_pipeline/`
- **Hybrid PII Detector**: Optional ML-enhanced detection via `privysha[ml]`

### Changed
- **Modular pipeline layout**: `pipeline/` package replaces monolithic `pipeline.py`
- **Drop-in API**: `process`, `wrap_llm`, `optimize`, `sanitize` as primary entry points

---

## [0.1.2] - 2026-04-23

### Added
- **Universal Adapter System**: Support for OpenAI, Anthropic, Grok, HuggingFace, and Ollama providers
- **Smart Routing**: Task-based intelligent model selection with fallback logic
- **Security Layer**: Advanced injection detection and threat analysis
- **Prompt IR (Intermediate Representation)**: Structured prompt compilation
- **Model Router**: Automatic provider selection based on task complexity
- **Debug Tracing**: Complete pipeline visibility and performance metrics
- **Comprehensive Documentation**: Full ReadTheDocs integration
- **PyPI Publishing**: Ready for production distribution

### Enhanced
- **Agent Class**: Complete v2 functionality with v1 compatibility
- **Pipeline Architecture**: Full 7-stage processing pipeline
- **Optimizer Engine**: Advanced token reduction (30-70% cost savings)
- **Universal Model Adapter**: Retry logic and automatic failover
- **Factory Pattern**: Enhanced adapter creation with fallback support

### Fixed
- **Missing Dependencies**: Added accelerate>=0.20.0 for HuggingFace compatibility
- **Test Framework**: Fixed test functions to use proper assertions
- **HuggingFace Adapter**: Resolved device_map compatibility issues
- **IR Builder**: Enhanced to handle both object and dict formats
- **Package Metadata**: Complete README.md with all required sections

### Infrastructure
- **Build System**: Proper setuptools configuration with src layout
- **Testing**: 51 passing tests (excluding HF adapter tests requiring API keys)
- **Documentation**: Complete README with installation, quick start, and API reference
- **Distribution**: Both wheel and source distribution passing Twine checks

---

## [0.1.0] - 2026-03-13

### Added

Initial development release of **PrivySHA**.

Core features:

- Prompt sanitization
- PII masking
- Prompt AST parsing
- Token optimization
- Context injection
- Prompt compilation pipeline

Adapters:

- OpenAI adapter
- Ollama adapter
- HuggingFace adapter

Developer features:

- Pipeline trace debugging
- Modular stage architecture
- Python package distribution
- PyPI installation support

Testing:

- Sanitizer tests
- Optimizer tests
- Pipeline tests
