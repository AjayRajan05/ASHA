# Getting Started with PrivySHA

**Drop-in security + optimization layer for LLM apps**

This guide will help you get PrivySHA installed and running with your first optimized prompt.

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Install from PyPI

```bash
pip install privysha
```

### Optional Dependencies

Install extras for specific providers and integrations:

```bash
# LLM providers
pip install privysha[openai]
pip install privysha[anthropic]
pip install privysha[gemini]

# ML-enhanced PII detection
pip install privysha[ml]

# Framework integrations (FastAPI, LangChain, etc.)
pip install privysha[integrations]

# Everything
pip install privysha[all]
```

See [integrations.md](integrations.md) for the full extras table.

### Verify Installation

```python
from privysha import process
print("PrivySHA installed successfully!")
```

---

## 🎯 Your First Prompt

### Quick Start (3 lines)

```python
from privysha import process

result = process("My email is john@gmail.com. Analyze this dataset.")

print(result["text"])
print(result["meta"])
```

### Wrap Existing Client (Zero Refactor)

```python
from privysha import wrap_llm
import openai

client = openai.OpenAI()
secure_client = wrap_llm(client)

# Same interface, automatically secured
response = secure_client.chat.completions.create(
    messages=[{"role": "user", "content": "My email is john@gmail.com"}]
)
```

### With Metrics

```python
from privysha import process

result = process("prompt", return_metrics=True)
print(f"Token reduction: {result['token_reduction']}%")
print(f"PII detected: {len(result['security_result']['masked_entities'])}")
```

---

## 🛠️ CLI Tool

### Quick Demo

```bash
privysha "My email is john@gmail.com. Analyze this dataset."
```

### Quick Test Suite

```bash
privysha --quick-test
```

### See Examples

```bash
privysha --examples
```

### Debug Mode

```bash
privysha "prompt" --debug
```

---

## ⚙️ Processing Modes

```python
# Balanced (default) - Smart security + optimization
result = process(prompt, mode="balanced")

# Strict - Maximum security (mask all PII)
result = process(prompt, mode="strict")

# Lite - Minimal processing (low latency)
result = process(prompt, mode="lite")

# Off - No modification
result = process(prompt, mode="off")
```

---

## 🔑 API Keys (Optional)

PrivySHA works without API keys for basic processing. For LLM integration:

```bash
# OpenAI
export OPENAI_API_KEY=your_key

# Gemini
export GOOGLE_API_KEY=your_key

# Anthropic
export ANTHROPIC_API_KEY=your_key
```

---

## � Common Use Cases

```python
from privysha import Agent

agent = Agent(model="gpt-4o-mini")
response = agent.run("Your prompt here")
```

### Advanced (v2 Features)

Full control with fallbacks and routing:

```python
from privysha import Agent

agent = Agent(
    model="gpt-4o-mini",
    privacy=True,
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "grok", "model": "grok-beta"}
    ],
    optimization_level="aggressive"
)

result = agent.run("Complex prompt", trace=True)
```

---

## 📊 Understanding the Output

### Simple Response

```python
response = agent.run("Simple prompt")
print(response)
# Just the text response
```

### Advanced Result

```python
result = agent.run("Complex prompt", trace=True)

print("Response:", result["response"])
print("Tokens used:", result["token_usage"])
print("Optimization:", result["optimization_metrics"])
print("Security:", result["security_result"])
print("Model used:", result["model_info"])
```

### Example Output

```python
{
    "response": "The dataset shows 3 anomalies...",
    "token_usage": {
        "input_tokens": 38,
        "output_tokens": 45,
        "total_tokens": 83
    },
    "optimization_metrics": {
        "original_tokens": 120,
        "optimized_tokens": 38,
        "reduction_percentage": 68.3
    },
    "security_result": {
        "pii_detected": 2,
        "pii_masked": 2,
        "injection_attempts": 0
    },
    "model_info": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "fallback_used": False
    }
}
```

---

## 🛠️ Common Configurations

### Data Analysis

```python
from privysha import Agent

analyst = Agent(
    model="gpt-4o-mini",
    privacy=True,
    optimization_level="balanced"
)

result = analyst.run(
    "Analyze the sales data and identify trends",
    trace=True
)
```

### Chatbot

```python
from privysha import Agent

chatbot = Agent(
    model="gpt-4o-mini",
    privacy=True,
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"}
    ]
)

response = chatbot.run("User message about their data")
```

### Content Moderation

```python
from privysha import Agent

moderator = Agent(
    model="gpt-4o-mini",
    privacy=True,
    security_level="high"
)

result = moderator.run(
    "Check this content for policy violations",
    trace=True
)
```

---

## 🔍 Troubleshooting

### Common Issues

#### API Key Not Found
```
Error: OPENAI_API_KEY not found
```
**Solution**: Set environment variables or use .env file

#### Model Not Available
```
Error: Model 'gpt-4' not found
```
**Solution**: Check available models for each provider

#### Import Error
```
Error: No module named 'privysha'
```
**Solution**: `pip install privysha`

### Debug Mode

Always use `trace=True` for debugging:

```python
result = agent.run("prompt", trace=True)
agent.print_debug_trace()
```

This shows the full pipeline:
```
RAW → SANITIZED → IR → OPTIMIZED → COMPILED → RESPONSE
```

---

## 🎯 Next Steps

Now that you're set up:

1. **[Learn Core Concepts](core-concepts.md)** - Understand Prompt IR and Pipeline
2. **[Explore Pipeline](pipeline.md)** - Deep dive into processing stages
3. **[Check Examples](examples.md)** - Real-world use cases
4. **[API Reference](api-reference.md)** - Complete documentation

---

## 💡 Pro Tips

- **Always use `trace=True` during development**
- **Enable `privacy=True` for user data**
- **Set up fallback providers for production**
- **Monitor optimization metrics for cost savings**
- **Use debug traces for troubleshooting**

---

*Ready to dive deeper? Check out [Core Concepts](core-concepts.md) next!*
