# Examples

Runnable scripts demonstrating PrivySHA integration patterns.

| Script | Description |
|--------|-------------|
| [dropin_examples.py](dropin_examples.py) | Core API: `process`, `wrap_llm`, `optimize`, `sanitize` |
| [basic_usage.py](basic_usage.py) | Agent and routing basics |
| [adapter_usage.py](adapter_usage.py) | Provider adapters |
| [provider_testing.py](provider_testing.py) | OpenAI, Claude, Gemini, Ollama, HF smoke tests |
| [fastapi_integration.py](fastapi_integration.py) | FastAPI middleware |
| [instructor_guardrails_example.py](instructor_guardrails_example.py) | Instructor + Guardrails composition (mock, no API keys) |
| [integration_showcase.py](integration_showcase.py) | Multi-framework overview |
| [oh_shock_moments.py](oh_shock_moments.py) | Before/after PII and injection demos |
| [fastapi_integration_example.py](fastapi_integration_example.py) | Extended FastAPI middleware example |

## Quick run

```bash
pip install -e .
python examples/dropin_examples.py
python examples/instructor_guardrails_example.py
```

Most examples use `pip install -e .` from the repo root. Provider examples require optional extras and API keys — see each script's header comments.
