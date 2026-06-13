# Prompt IR

**PrivySHA v0.3.0** — structured intermediate representation for prompts.

---

## What is Prompt IR?

Prompt IR (Intermediate Representation) is a structured object that captures the semantic content of a natural language prompt. It enables compiler-style optimization and intelligent model routing.

Instead of treating prompts as opaque strings, PrivySHA extracts:

- **Intent** — what the user wants (analyze, create, summarize, …)
- **Object** — what the intent acts upon (dataset, code, email, …)
- **Constraints** — requirements (thorough, concise, GDPR-compliant, …)
- **Entities** — named entities detected in the prompt
- **Privacy metadata** — PII presence, sensitivity level

---

## IntentType enum

Defined in `ir/prompt_ir.py`:

```python
from privysha import IntentType

# Available intents include:
# ANALYZE, CREATE, MODIFY, DELETE, SUMMARIZE, TRANSLATE,
# EXPLAIN, COMPARE, CLASSIFY, GENERATE, QUERY, OTHER
```

---

## PromptIR class

```python
from privysha import PromptIR

ir = PromptIR({
    "intent": "analyze",
    "object": "dataset",
    "constraints": ["thorough"],
    "style": "analytical",
})

print(ir.intent)
print(ir.to_dict())
```

---

## IRBuilder

Builds PromptIR from natural language:

```python
from privysha import IRBuilder

builder = IRBuilder()
ir = builder.generate("Analyze this dataset for anomalies")

print(ir.intent)     # analyze
print(ir.object)     # dataset
```

Custom intent patterns:

```python
builder.add_intent_pattern(
    name="visualize",
    patterns=["plot", "chart", "graph", "visualize"],
)
```

---

## PromptCompiler

Converts IR back to optimized prompt text:

```python
from privysha import PromptCompiler

compiler = PromptCompiler()
compiled = compiler.compile(ir)
```

Used internally by the compilation pipeline stage.

---

## IR in the pipeline

IR generation is stage 2 of the 7-stage pipeline:

```
Security → IR Generation → Routing → Compilation → Optimization → ...
```

The IR drives:

- **Routing** — `ModelRouter.route(ir, constraints)` selects the best model
- **Compilation** — IR → structured prompt text
- **Optimization** — MSDPC operates on compiled output

For drop-in usage, IR is built internally — you don't need to interact with it directly.

---

## PrivyFit workload profiling

PrivyFit uses compiled prompt stats (token counts, IR-derived intent) to rank local models:

```python
from privysha import recommend_local_model

report = recommend_local_model(
    prompts=["Analyze customer feedback with PII."],
    mode="strict",
)
```

See [local-advisor.md](local-advisor.md).

---

## Routing integration

```python
from privysha import ModelRouter, RoutingStrategy

router = ModelRouter(default_strategy=RoutingStrategy.TASK_BASED)
decision = router.route(ir, constraints={"force_local": False})
print(decision.selected_model.name)
print(decision.reasoning)
```

See [routing.md](routing.md).

---

## Related docs

- [Pipeline](pipeline.md) — IR generation stage
- [Architecture](architecture.md) — `ir/` package layout
- [Routing](routing.md) — model selection based on IR
