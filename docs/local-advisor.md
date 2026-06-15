# PrivyFit — Local Model Advisor

> **Preview in v0.4.1** — APIs may change before 1.0.0.

Recommends local LLMs for your prompt workload and hardware.

---

## Quick start

```python
from privysha.runtime.local_advisor.advisor import recommend_local_model

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
```

CLI:

```bash
privysha recommend --prompt "Analyze dataset" --gpu "RTX 4090"
privysha recommend --prompts ./benchmarks/sample_prompts.json --top 3
```

---

## Agent integration

```python
from privysha import Agent

agent = Agent(
    model="llama3",
    local_model="auto",
    sample_prompts=["Summarize this report."],
)
```

---

## wrap_llm + local selection

```python
from privysha.integrations import wrap_llm

client = wrap_llm(
    ollama_client,
    auto_select_local_model=True,
    sample_prompts=["Your typical app prompts..."],
)
```

---

## Optional dependencies

```bash
pip install privysha[local-advisor]
pip install privysha[local-advisor-gpu]   # NVIDIA VRAM detection
```

---

## Scoring

Combines hardware fit, workload fit (from compiled prompt stats), privacy requirements, and estimated speed.

---

## Related

- [routing.md](routing.md)
- [developer-preview.md](developer-preview.md)
