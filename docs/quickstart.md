# 🚀 PrivySHA Quickstart Guide

**Get started with PrivySHA in 5 minutes!**

---

## 📦 Installation

### Basic Installation
```bash
pip install privysha
```

### With ML Features (Optional)
```bash
pip install privysha[ml]
```

### With All Providers
```bash
pip install privysha[all]
```

---

## 🎯 Your First Prompt Processing

### **The Simplest Way**
```python
from privysha import process

result = process("Hey bro analyze my dataset with john@email.com")
print(result)
# Output: "analyze dataset with [EMAIL]_abc123"
```

### **With Metrics**
```python
from privysha import process

result = process(
    "Contact john@example.com for data analysis",
    return_metrics=True
)

print(f"Tokens saved: {result['token_reduction']}%")
print(f"PII detected: {result['security_result']['pii_masked']}")
```

---

## 🔒 Privacy & Security

### **Automatic PII Detection**
```python
from privysha import process

# Email, phone, SSN, credit card automatically detected
prompt = "Contact John Smith at john@company.com or 555-1234 or SSN 123-45-6789"
result = process(prompt, privacy=True)

print(result)
# Output: "Contact [NAME]_xyz at [EMAIL]_abc or [PHONE]_def or [SSN]_ghi"
```

### **Different PII Modes**
```python
# Rule-based (lightweight, default)
result = process(prompt, pii_mode="rule")

# Hybrid: Rules + ML (requires privysha[ml])
result = process(prompt, pii_mode="hybrid")  

# ML-only (experimental)
result = process(prompt, pii_mode="ml_only")
```

---

## 🤖 LLM Integration

### **OpenAI**
```python
import os
from privysha import Agent

os.environ["OPENAI_API_KEY"] = "your-api-key"

agent = Agent(model="gpt-4o-mini", privacy=True)
response = agent.run("Analyze this customer data")
```

### **Universal Wrapper**
```python
from privysha import wrap_llm
import openai

# Wrap any LLM client
client = openai.OpenAI(api_key="your-key")
secure_client = wrap_llm(client)

# Use normally - now automatically secured!
response = secure_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Analyze data with john@email.com"}]
)
```

---

## 📊 Observability & Debugging

### **Pipeline Tracing**
```python
from privysha import process

result = process(
    "Analyze data with john@example.com",
    trace=True,
    debug=True
)

# See exactly what changed
print(result["trace"]["final_output"])
# Output: "Analyze data with [EMAIL]_x92k"

# See diff view
print(result["diff"])
# Output:
# - Analyze data with john@example.com
# + Analyze data with [EMAIL]_x92k
```

### **Structured Logging**
```python
result = process(
    "Process sensitive data",
    trace=True,
    log_level="DEBUG",
    log_output="file",
    log_file="privysha.log"
)

# Full trace saved to file with detailed timing
```

---

## 🎛️ Advanced Usage

### **Custom Token Budget**
```python
from privysha import Agent

agent = Agent(
    model="gpt-4o-mini",
    privacy=True,
    token_budget=500  # Limit tokens for cost control
)

response = agent.run("Analyze this large dataset")
```

### **Different Security Levels**
```python
from privysha import process

# LOW: Basic PII detection
result = process(prompt, security_level="low")

# MEDIUM: Standard security (default)
result = process(prompt, security_level="medium") 

# HIGH: Maximum security
result = process(prompt, security_level="high")
```

### **Policy Modes**
```python
# STRICT: Maximum privacy and optimization
result = process(prompt, mode="strict")

# BALANCED: Good balance (default)
result = process(prompt, mode="balanced")

# LITE: Minimal processing
result = process(prompt, mode="lite")

# OFF: No processing
result = process(prompt, mode="off")
```

---

## 🔄 Async Processing

```python
import asyncio
from privysha import process_async

async def main():
    result = await process_async(
        "Process multiple prompts asynchronously",
        privacy=True
    )
    print(result)

asyncio.run(main())
```

---

## 📈 Performance Tips

### **Optimize for Speed**
```python
from privysha import process

# Fastest processing
result = process(
    prompt,
    mode="lite",           # Minimal processing
    security_level="low",    # Basic security
    pii_mode="rule"         # Fastest PII detection
)
```

### **Optimize for Cost**
```python
# Maximum cost savings
result = process(
    prompt,
    mode="strict",          # Maximum optimization
    token_budget=200,         # Aggressive token reduction
    pii_mode="hybrid"         # Best accuracy
)
```

---

## 🚨 Common Issues & Solutions

### **Issue: Import Error**
```bash
# Solution: Install in development mode
pip install -e .
```

### **Issue: ML Features Not Working**
```bash
# Solution: Install ML dependencies
pip install privysha[ml]
```

### **Issue: Slow Processing**
```python
# Solution: Use lite mode for speed
result = process(prompt, mode="lite")
```

### **Issue: Too Much PII Masked**
```python
# Solution: Adjust security level
result = process(prompt, security_level="low")
```

---

## 🎯 Next Steps

1. **Explore Examples**: Check `examples/` directory for real-world use cases
2. **Read Architecture**: Understand the pipeline in `docs/architecture.md`
3. **API Reference**: Detailed documentation in `docs/api-reference.md`
4. **Advanced Features**: Learn about observability, async processing, and more

---

## 🤝 Need Help?

- **Documentation**: [Full Documentation](https://github.com/AjayRajan05/privySHA)
- **Issues**: [Report Bugs](https://github.com/AjayRajan05/privySHA/issues)
- **Discussions**: [Community](https://github.com/AjayRajan05/privySHA/discussions)

---

**🎉 You're now ready to use PrivySHA!**

Your LLM applications now have:
- ✅ **Enterprise-grade security**
- ✅ **Automatic PII protection** 
- ✅ **Token optimization**
- ✅ **Full observability**
- ✅ **Multi-provider support**

*Start building secure, optimized AI applications today!*
