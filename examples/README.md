# Examples (v0.4.2)

Runnable scripts demonstrating the public API. All use typed `ProcessResult` and canonical import paths.

| Script | Description | API keys |
|--------|-------------|----------|
| **[developer_preview_demo.py](developer_preview_demo.py)** | **Start here** - `process()` + AshaFit | None |
| [dropin_examples.py](dropin_examples.py) | `process`, `sanitize`, `optimize`, `wrap_llm` | None (mock wrap) |
| [basic_usage.py](basic_usage.py) | `Agent` with mock adapter | None |
| [adapter_usage.py](adapter_usage.py) | Provider adapter patterns | Optional |
| [provider_testing.py](provider_testing.py) | Smoke tests for providers | Optional |
| [integration_showcase.py](integration_showcase.py) | Framework integration snippets | None (prints only) |
| [fastapi_integration.py](fastapi_integration.py) | FastAPI middleware demo | None (`pip install fastapi uvicorn`) |
| [v2_examples.py](v2_examples.py) | Agent, routing, tracing patterns | None |

## Quick run

```bash
pip install -e .
python examples/developer_preview_demo.py
python examples/dropin_examples.py
python examples/basic_usage.py
```

Provider examples need extras and API keys:

```bash
pip install asha[openai]
export OPENAI_API_KEY=...
python examples/provider_testing.py
```

FastAPI example:

```bash
pip install asha[fastapi]  # or: pip install fastapi uvicorn
python examples/fastapi_integration.py
```

See [docs/examples.md](../docs/examples.md) for copy-paste patterns.
