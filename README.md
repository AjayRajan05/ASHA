# PrivySHA

<p align="center">
<strong>Privacy-First Prompt Compilation Framework for AI Systems</strong>
</p>

<p align="center">
Transform raw prompts into optimized, structured, privacy-safe prompts before they reach LLMs.
</p>

<p align="center">

![PyPI](https://img.shields.io/badge/pypi-v1.0.1-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Status](https://img.shields.io/badge/status-stable-green)
![Tests](https://img.shields.io/badge/tests-pytest-green)

</p>

---

# Overview

PrivySHA is an **open-source prompt optimization and compilation framework** designed for modern AI applications.

Instead of sending **raw user prompts** directly to Large Language Models, PrivySHA introduces a **compiler-style processing pipeline** that transforms prompts into structured, optimized instructions.

This improves:

• privacy
• token efficiency
• prompt reliability
• system observability

PrivySHA acts as a **prompt compiler layer** between your application and any LLM.

> **Status:** v1.0.0 — drop-in PII masking and prompt optimization.
> Requires Python 3.10+. Install with `pip install privysha` and use `process()` / `wrap_llm()` as the primary APIs.

---

# Motivation

Most LLM applications look like this:

```
User Prompt → LLM
```

This causes problems:

| Problem              | Result                 |
| -------------------- | ---------------------- |
| Unstructured prompts | inconsistent responses |
| Excess tokens        | higher API costs       |
| PII leakage          | privacy risk           |
| Prompt drift         | unreliable outputs     |
| No observability     | hard debugging         |

PrivySHA introduces a structured pipeline:

```
User Prompt → PrivySHA → Optimized Prompt → LLM
```

---

# Key Features

### Privacy-First Processing

PrivySHA detects and masks sensitive information such as:

* email addresses
* phone numbers
* personal identifiers

Example:

Input

```
John's email is john@email.com analyze this dataset
```

Output

```
<PERSON_HASH> email <EMAIL_HASH> analyze dataset
```

---

### Prompt Sanitization

Removes conversational filler.

Example

```
Hey bro can you analyze this dataset for anomalies?
```

becomes

```
analyze dataset for anomalies
```

---

### Prompt AST

PrivySHA converts prompts into structured representations.

Example

```
intent: analyze
object: dataset
task: anomaly_detection
```

This allows the system to perform **compiler-style optimizations**.

---

### Token Optimization

Prompts are compressed to reduce token usage.

Example

```
Analyze this dataset for anomalies and patterns
```

becomes

```
@analyze(dataset)
```

---

### Modular Prompt Pipeline

PrivySHA processes prompts through multiple stages.

```
User Prompt
   │
   ▼
Parser
   │
   ▼
Sanitizer
   │
   ▼
PII Detection
   │
   ▼
Optimizer
   │
   ▼
Context Injector
   │
   ▼
Prompt Compiler
   │
   ▼
Model Adapter
   │
   ▼
LLM Response
```

Each stage can be customized or replaced.

---

# Installation

## Basic Installation (Lightweight)

```bash
pip install privysha
```

**Instant setup** - No downloads, works immediately with rule-based PII detection.

## Advanced Features (Optional)

For ML-enhanced PII detection and advanced features:

```bash
pip install privysha[ml]
```

**ML features include:**
- Enhanced PII detection with transformer models
- Higher accuracy for complex PII patterns
- Context-aware entity recognition

## Provider-Specific

```bash
# OpenAI support
pip install privysha[openai]

# Anthropic Claude support  
pip install privysha[anthropic]

# Google Gemini support
pip install privysha[gemini]

# All providers + ML features
pip install privysha[all]
```

Requirements:

* Python 3.10+

---

# Quick Start

## Drop-in Functions (Easiest)

```python
from privysha import process

# Simple processing
result = process("Hey bro analyze my dataset with john@example.com")
print(result)  # "analyze dataset with <EMAIL_HASH>"

# With ML-enhanced PII detection (requires pip install privysha[ml])
result = process("Contact john@example.com for details", pii_mode="hybrid")
print(result)  # Enhanced PII detection with transformer models
```

## Agent Class (Full Control)

```python
from privysha import Agent

agent = Agent(
    model="mock",  # Use "gpt-4o-mini" for OpenAI, "llama3" for Ollama
    privacy=True,
    token_budget=1200
)

response = agent.run(
    "Hey bro can you analyze this dataset for anomalies?"
)

print(response)
```

PrivySHA automatically:

1. sanitizes the prompt
2. removes personal language
3. masks sensitive data
4. optimizes token usage
5. compiles a structured prompt

## Progressive Enhancement

Choose your PII detection level:

```python
# Rule-based only (lightweight, default)
process("Contact john@example.com", pii_mode="rule")

# Hybrid: Rules + ML (requires pip install privysha[ml])
process("Contact john@example.com", pii_mode="hybrid")

# ML-only (experimental, requires pip install privysha[ml])
process("Contact john@example.com", pii_mode="ml_only")
```

---

# Usage Examples

## Model Providers

### OpenAI (Requires API Key)

```python
import os
from privysha import Agent

os.environ["OPENAI_API_KEY"] = "your-api-key"

agent = Agent(model="gpt-4o-mini")
response = agent.run("Analyze this data")
```

### Ollama (Requires Local Server)

```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3
```

```python
from privysha import Agent

agent = Agent(model="llama3")
response = agent.run("Analyze this data")
```

### HuggingFace (Requires Transformers)

```python
from privysha import Agent

agent = Agent(model="microsoft/DialoGPT-medium")
response = agent.run("Analyze this data")
```

## Real-World Applications

### Data Analysis Pipeline

```python
from privysha import Agent

agent = Agent(model="gpt-4o-mini", privacy=True)

def analyze_data(data_description):
    prompt = f"Analyze this dataset for patterns: {data_description}"
    return agent.run(prompt)

# Usage
result = analyze_data("Sales data from Q1 2024 with customer emails")
```

### Customer Support

```python
from privysha import Agent

agent = Agent(model="gpt-4o-mini", privacy=True)

def support_query(customer_message):
    # PII will be automatically masked
    return agent.run(customer_message)

# Usage
response = support_query("Help me with order #12345, email john@example.com")
```

### Content Moderation

```python
from privysha import Agent

agent = Agent(model="gpt-4o-mini", privacy=True)

def moderate_content(user_content):
    return agent.run(f"Review this content for policy violations: {user_content}")

# Usage
moderation_result = moderate_content("Check this post from user@social.com")
```

---

# Debugging Prompt Transformations

PrivySHA exposes the full pipeline trace.

```python
result = agent.run(prompt, trace=True)

print(result)
```

Example output

```
RAW PROMPT
Hey bro analyze this dataset

SANITIZED
analyze dataset

OPTIMIZED
@analyze(dataset)

COMPILED
SYSTEM:
You are a data scientist

TASK:
analyze dataset
```

This allows developers to **debug prompt engineering systematically**.

---

# Production Deployment

## Security Best Practices

```python
import os
from privysha import Agent

# Always use environment variables for API keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Production configuration
agent = Agent(
    model="gpt-4o-mini",
    privacy=True,  # Always enable in production
    token_budget=2000  # Adjust based on your needs
)

def process_prompt(user_input):
    """Process user input with privacy protection"""
    try:
        response = agent.run(user_input)
        return response
    except Exception as e:
        return f"Error processing prompt: {e}"
```

## Monitoring & Debugging

```python
import time
from privysha import Agent

agent = Agent(model="gpt-4o-mini", privacy=True)

def monitored_process(prompt):
    start_time = time.time()
    
    result = agent.run(prompt, trace=True)
    
    processing_time = time.time() - start_time
    
    # Log metrics (without sensitive data)
    print(f"Processing time: {processing_time:.2f}s")
    print(f"Token optimization: {len(result['raw_prompt'])} -> {len(result['optimized'])}")
    
    return result["response"]
```

## Testing Your Setup

```python
from privysha import Agent

# Test without external services
agent = Agent(model="mock", privacy=True)
response = agent.run("Test prompt with email@example.com")
print(response)

# Test pipeline stages
result = agent.run("Hey bro analyze my dataset john@example.com", trace=True)

# Verify PII masking
assert "john@example.com" not in result["sanitized"]
assert "<EMAIL_HASH>" in result["sanitized"]

# Verify sanitization
assert "bro" not in result["sanitized"]
```

---

# Supported Model Providers

PrivySHA integrates with multiple model providers.

| Provider    | Type               |
| ----------- | ------------------ |
| OpenAI      | hosted APIs        |
| Ollama      | local LLM runtime  |
| HuggingFace | transformer models |

Example:

```python
Agent(model="gpt-4o-mini")
```

or

```python
Agent(model="llama3")
```

---

# Architecture

PrivySHA follows a **compiler-inspired, modular pipeline architecture**.

```mermaid
flowchart LR
    UserInput[User Input] --> Security[Security Stage]
    Security --> IR[IR Generation]
    IR --> Routing[Model Routing]
    Routing --> Compile[Compilation]
    Compile --> Optimize[Optimization]
    Optimize --> LLM[LLM Provider]
    LLM --> Result[Result Assembly]
```

```
privysha/
├── agent.py                 # High-level Agent API
├── utils/
│   ├── dropin.py            # process(), wrap_llm(), optimize(), sanitize()
│   └── pii_detector.py      # Rule-based PII detection
├── pipeline/
│   ├── pipeline.py          # 7-stage orchestrator
│   └── stages/              # Security, IR, Routing, Compilation, Optimization, Generation, Result
├── core/
│   └── pii_pipeline/        # Multi-stage PII detection pipeline
├── compiler/
│   └── msdpc/               # Token optimization engine
├── security/                # Threat detection and masking
├── adapters/                # OpenAI, Claude, Gemini, Grok, Ollama, HuggingFace, Mock
├── integrations/            # FastAPI, Flask, Django, LangChain, LlamaIndex
├── cli/                     # privysha command-line tool
└── ir/                      # Prompt intermediate representation
```

---

# Documentation

- [📖 Quickstart Guide](docs/quickstart.md) - 5-minute walkthrough
- [🔧 Troubleshooting Guide](docs/troubleshooting.md) - Common issues & solutions
- [⚡ Performance Tuning](docs/performance-tuning.md) - Optimization guide
- [🔄 Migration Guide](docs/migration.md) - From other solutions
- [📚 API Reference](docs/api-reference.md) - Complete documentation
- [🏗️ Architecture](docs/architecture.md) - System design
- [🤝 Contributing](docs/contributing.md) - Development guide

Build the docs site locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Optional integrations: `pip install privysha[integrations]` or `pip install privysha[fastapi,langchain,instructor]`

See [docs/publishing.md](docs/publishing.md) for PyPI trusted publishing setup.

---

# Running Tests

```bash
# Unit tests (no API keys required)
pytest -m "not integration"

# Full suite including integration tests (requires GEMINI_API_KEY)
pytest
```

Or run the readiness check:

```bash
pytest tests/comprehensive_test.py -v
```

Tests validate:

* prompt sanitization
* token optimization
* pipeline execution
* PII masking
* adapter functionality

---

# Troubleshooting

## Common Issues

1. **Import Error**: `pip install -e .` in development
2. **Connection Refused**: Start Ollama server or check API keys
3. **Memory Issues**: Reduce `token_budget` or use smaller models
4. **PII Not Masked**: Ensure `privacy=True`

## Debug Mode

```python
# Enable full debugging
result = agent.run(prompt, trace=True)

# Print all stages
for stage, output in result.items():
    if stage != "response":
        print(f"{stage.upper()}:")
        print(f"  {output}")
        print()
```

---

# Comparison

| Feature             | PrivySHA | Traditional Prompting |
| ------------------- | -------- | --------------------- |
| Prompt Sanitization | ✓        | ✗                     |
| PII Protection      | ✓        | ✗                     |
| Token Optimization  | ✓        | ✗                     |
| Pipeline Debugging  | ✓        | ✗                     |

PrivySHA introduces a **structured prompt lifecycle** rather than raw prompt usage.

---

# Performance Benchmarks

Reproducible benchmarks are included in the repo. Typical results (rule-based PII, no ML):

| Metric | Typical range |
|--------|---------------|
| Token reduction | 5–15% on verbose prompts |
| Processing latency | 20–80 ms |
| Fail-safe rate | ~100% |

```bash
pip install -e .
python benchmarks/run_benchmarks.py --save
```

Results are written to `benchmarks/output/`. See [benchmarks/results.md](benchmarks/results.md) for methodology and reference numbers. Benchmarks also run in CI on every push.

---

# Contributing

Contributions are welcome.

Steps:

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Submit a pull request

Before submitting:

```
pytest
```

---

# Roadmap

Future versions will include:

* advanced prompt AST analysis
* prompt caching engine
* cost-aware optimization
* multi-model routing

---

# License

This project is licensed under the **Apache 2.0 License**.

See the LICENSE file for details.

---

# Acknowledgements

PrivySHA is inspired by ideas from modern AI tooling ecosystems and compiler design.

It explores the idea of treating prompts as **structured programs** rather than raw text.

---

# Support the Project

If you find this project useful:

⭐ Star the repository
🐛 Report issues
💡 Suggest improvements
