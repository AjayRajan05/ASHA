# PrivySHA Documentation

**Drop-in security + optimization layer for LLM apps**

PrivySHA automatically masks PII, reduces tokens, and blocks prompt injection attacks - all with zero code changes.

---

## 🚀 Quick Start

**New to PrivySHA?** Start here:

- **[Getting Started](getting-started.md)** - Installation and first example
- **[API Reference](api-reference.md)** - Core functions: process, wrap_llm, optimize, sanitize
- **[Examples](examples.md)** - Real-world use cases
- **[Integrations](integrations.md)** - FastAPI, LangChain, Instructor, Guardrails

---

## 🧱 Core Documentation

### Essential Guides
- **[Getting Started](getting-started.md)** - Installation, setup, first prompt
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Examples](examples.md)** - Real-world use cases and patterns
- **[Integrations](integrations.md)** - Framework composition guides

### Key Features
- **[Security](security.md)** - PII masking and injection protection
- **[Compliance](compliance.md)** - GDPR, CCPA, HIPAA considerations
- **[Optimization](optimization.md)** - Token reduction and cost savings
- **[Processing Modes](core-concepts.md)** - balanced, strict, lite, off modes
- **[CLI Tool](getting-started.md#cli-tool)** - Quick testing and debugging

### Advanced
- **[Architecture](architecture.md)** - System design and components
- **[Debugging](debugging.md)** - Full pipeline tracing
- **[FAQ](faq.md)** - Common questions

### Project
- **[Contributing](contributing.md)** - How to contribute
- **[Migration](migration.md)** - Upgrade from Presidio, regex, spaCy, etc.
- **[Troubleshooting](troubleshooting.md)** - Common issues and fixes
- **[Benchmarks](benchmarks.md)** - Reproducible performance numbers

---

## 🎯 Why PrivySHA?

### Traditional LLM Usage
```
User → Prompt → LLM → Response
```

**Problems:**
- ❌ Unstructured prompts
- ❌ High token cost
- ❌ No privacy guarantees
- ❌ No control over model selection
- ❌ No debugging visibility

### With PrivySHA
```
User → Sanitization → Prompt IR → Optimization → Best Model → Response
```

**Benefits:**
- ✅ Structured, reproducible prompts
- ✅ 5–15% typical token reduction (see [benchmarks.md](benchmarks.md))
- ✅ Built-in privacy protection
- ✅ Intelligent model routing
- ✅ Full debugging traces

---

## 📊 Key Metrics

| Feature | Traditional | PrivySHA | Improvement |
|---------|------------|-----------|------------|
| **Token Usage** | 120 tokens | 102–114 tokens | **5–15% reduction** |
| **Privacy** | None | Built-in PII masking | **Full protection** |
| **Debugging** | Limited | Full pipeline traces | **Complete visibility** |
| **Model Selection** | Manual | Intelligent routing | **Automatic optimization** |

---

## 🛠️ Installation

```bash
pip install privysha
```

### Quick Example

```python
from privysha import Agent

agent = Agent(model="gpt-4o-mini", privacy=True)

response = agent.run(
    "Hey bro can you analyze this dataset for anomalies?"
)

print(response)
```

---

## 🧠 Philosophy

PrivySHA treats prompts as:

> **Programs, not strings**

This enables:
- **Reproducibility** - Same input → same output
- **Optimization** - Systematic improvements
- **Composability** - Building blocks for complex systems
- **Debugging** - Step-by-step visibility

---

## 🏗️ What Makes PrivySHA Different?

| Feature | PrivySHA | LangChain | Guardrails |
|---------|----------|-----------|------------|
| **Prompt Compiler** | ✅ | ❌ | ❌ |
| **Prompt IR** | ✅ | ❌ | ❌ |
| **Cost Optimization** | ✅ | ❌ | ❌ |
| **Multi-model routing** | ✅ | ⚠️ | ❌ |
| **Security + Transformation** | ✅ | ⚠️ | ✅ |
| **Observability** | ✅ | ⚠️ | ⚠️ |

---

## 🚀 Next Steps

1. **[Install PrivySHA](getting-started.md#installation)**
2. **[Set up API keys](getting-started.md#api-keys-optional)**
3. **[Run your first prompt](getting-started.md#your-first-prompt)**
4. **[Explore advanced features](core-concepts.md)**

---

## 🤝 Community

- **GitHub**: [AjayRajan05/privySHA](https://github.com/AjayRajan05/privySHA)
- **Issues**: [Report bugs](https://github.com/AjayRajan05/privySHA/issues)
- **Contributing**: [How to contribute](contributing.md)

---

*Ready to transform your LLM prompts? Let's get started!*
