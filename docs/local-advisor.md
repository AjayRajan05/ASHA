# PrivyFit — Local Model Advisor

> **Status: Preview in v0.3.0** — APIs may change before 1.0.0. See [developer-preview.md](developer-preview.md).

PrivyFit recommends **local LLM models for your application on your hardware**. Unlike generic hardware-only tools, PrivyFit analyzes your **compiled prompt workload**, **privacy requirements**, and **IR-derived intent** before ranking models.

## Quick start

```python
from privysha import recommend_local_model

report = recommend_local_model(
    prompts=[
        "My email is john@company.com — analyze this dataset.",
        "Write a Python function to validate API keys.",
    ],
    mode="strict",
    top=3,
)

print(report.top_pick.model_id)
print(report.top_pick.ollama_pull_name)
print(report.top_pick.reasoning)
```

CLI:

```bash
privysha recommend --prompts ./benchmarks/sample_prompts.json --mode strict --top 3
privysha recommend --prompt "Analyze dataset" --gpu "RTX 4090" --json
privysha recommend --prompt "Build a REST client" --probe
```

## How PrivyFit differs from whichllm

| | whichllm | PrivyFit (PrivySHA) |
|--|----------|---------------------|
| Primary input | Hardware | Hardware + **your prompts** |
| Token budget | User context length | **Post-compilation** token stats |
| Privacy | None | PII rate, strict mode, local-only |
| Ranking | Global benchmarks | Workload fit × hardware fit |
| Integration | Standalone CLI | `recommend_local_model()`, router, `wrap_llm` |

## Scoring axes

```text
final_score = hardware_fit × workload_fit × privacy_compliance × speed_usability
```

- **hardware_fit** — VRAM/RAM fit (full GPU > partial offload > CPU)
- **workload_fit** — Intent/specialization match, compiled context headroom
- **privacy_compliance** — Instruction-following threshold when PII present
- **speed_usability** — Estimated tok/s vs minimum usable thresholds

## Optional dependencies

```bash
pip install privysha[local-advisor]       # HuggingFace live catalog
pip install privysha[local-advisor-gpu]   # NVIDIA VRAM detection
```

Without extras, PrivyFit uses the bundled offline catalog (`fallback.json`) and stdlib hardware detection.

## Pipeline integration

### Model router (privacy-forced local)

```python
from privysha.routing import ModelRouter, RoutingStrategy

router = ModelRouter(default_strategy=RoutingStrategy.LOCAL_PRIVACY)
decision = router.route(
    ir,
    constraints={
        "sample_prompts": ["..."],
        "mode": "strict",
        "force_local": True,
    },
)
```

### Agent auto-select

```python
from privysha import Agent

agent = Agent(
    local_model="auto",
    sample_prompts=["Analyze customer feedback with PII."],
    privacy=True,
)
```

### wrap_llm auto-select

```python
from privysha import wrap_llm
import ollama

client = ollama.Client()
secure = wrap_llm(
    client,
    auto_select_local_model=True,
    sample_prompts=MY_PROMPTS,
)
```

## Optional Ollama probe

Pass `probe=True` to run a short micro-benchmark on top candidates when Ollama is running locally:

```python
report = recommend_local_model(prompts=[...], probe=True)
```

## Cache location

Model catalog cache: `~/.cache/privysha/local_models/models.json` (6h TTL).

Override with `PRIVYSHA_CACHE_DIR`.
