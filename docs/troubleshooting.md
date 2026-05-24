# 🔧 PrivySHA Troubleshooting Guide

**Solutions to common issues when using PrivySHA**

---

## 🚨 Quick Fixes

### **Installation Issues**

#### Issue: `ImportError: No module named 'privysha'`
```bash
# Solution 1: Install in development mode
pip install -e .

# Solution 2: Check Python path
python -c "import sys; print(sys.path)"

# Solution 3: Reinstall
pip uninstall privysha
pip install privysha
```

#### Issue: `ModuleNotFoundError: No module named 'spacy'`
```bash
# ML features require additional packages
pip install privysha[ml]

# Or install manually
pip install spacy>=3.4.0
python -m spacy download en_core_web_sm
```

#### Issue: `DLL load failed` (Windows)
```bash
# Solution: Install Microsoft Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then reinstall
pip uninstall privysha
pip install privysha
```

---

## 🔒 PII Detection Issues

### **Issue: PII Not Being Detected**

#### Symptoms
```python
from privysha import process
result = process("Contact john@example.com")
print(result)  # Still shows email
```

#### Solutions

**1. Check PII Mode**
```python
# Ensure ML mode is available
result = process(prompt, pii_mode="hybrid")  # Better accuracy

# Check if ML is installed
try:
    import spacy
    print("ML available")
except ImportError:
    print("Install: pip install privysha[ml]")
```

**2. Adjust Security Level**
```python
# Lower security level for more sensitive detection
result = process(prompt, security_level="low")
```

**3. Check Context Keywords**
```python
# PII detection uses context - add relevant keywords
prompt = "Contact email john@example.com for business inquiry"
# More likely to detect than "john@example.com" alone
```

### **Issue: Too Much PII Being Masked**

#### Solutions

**1. Use Lower Security Level**
```python
result = process(prompt, security_level="low")
```

**2. Disable Privacy (Use with Caution)**
```python
result = process(prompt, privacy=False)
```

**3. Custom Context**
```python
# Add legitimate context to reduce false positives
prompt = "My work email is john@example.com - please contact me"
```

---

## ⚡ Performance Issues

### **Issue: Slow Processing (>1 second)**

#### Solutions

**1. Use Lite Mode**
```python
result = process(prompt, mode="lite")
```

**2. Disable Expensive Features**
```python
result = process(
    prompt,
    pii_mode="rule",      # Fastest PII detection
    security_level="low",    # Minimal security checks
    debug=False             # No debug overhead
)
```

**3. Reduce Token Budget**
```python
result = process(prompt, token_budget=500)  # Less optimization work
```

**4. Use Async Processing**
```python
from privysha import process_async

result = await process_async(prompt)
```

### **Issue: High Memory Usage**

#### Solutions

**1. Disable Observability**
```python
result = process(prompt, trace=False, debug=False)
```

**2. Process in Batches**
```python
from privysha import process

prompts = ["prompt1", "prompt2", "prompt3"]
results = [process(p) for p in prompts]
```

**3. Use Pipeline Directly**
```python
from privysha import Pipeline

pipeline = Pipeline(privacy=True, debug_enabled=False)
result = pipeline.process(content)
```

---

## 🔌 LLM Integration Issues

### **Issue: OpenAI Integration Failing**

#### Symptoms
```python
from privysha import Agent
agent = Agent(model="gpt-4o-mini")
response = agent.run("test")
# Error: Authentication failed
```

#### Solutions

**1. Check API Key**
```python
import os
from privysha import Agent

# Set environment variable
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Or pass directly (less secure)
agent = Agent(model="gpt-4o-mini", api_key="your-api-key")
```

**2. Check Model Availability**
```python
# Use available models
agent = Agent(model="gpt-3.5-turbo")  # More widely available
```

**3. Add Timeout**
```python
agent = Agent(
    model="gpt-4o-mini",
    timeout=30,  # 30 second timeout
    retries=2
)
```

### **Issue: Wrapper Not Working**

#### Symptoms
```python
from privysha import wrap_llm
import openai

client = openai.OpenAI(api_key="key")
wrapped = wrap_llm(client)

response = wrapped.chat.completions.create(...)  # No security applied
```

#### Solutions

**1. Check Method Name**
```python
# Ensure you're using a generation method
response = wrapped.generate(...)  # Not messages.create(...)
```

**2. Use Universal Wrapper**
```python
from privysha import UniversalWrapper

wrapper = UniversalWrapper(client)
wrapped_client = wrapper.wrap_client(client)
```

**3. Debug Wrapper**
```python
# Enable debug to see what's happening
wrapped = wrap_llm(client, mode="balanced", debug=True)
response = wrapped.chat.completions.create(...)
print(f"Processed: {wrapped.last_prompt}")
```

---

## 🐛 Debugging Issues

### **Issue: Trace Not Working**

#### Symptoms
```python
result = process(prompt, trace=True)
print(result.get("trace"))  # None or empty
```

#### Solutions

**1. Check Log Level**
```python
# Use DEBUG level for maximum information
result = process(prompt, trace=True, log_level="DEBUG")
```

**2. Enable File Logging**
```python
result = process(
    prompt,
    trace=True,
    log_output="file",
    log_file="debug.log"
)
# Check debug.log file for details
```

**3. Check Pipeline Stages**
```python
from privysha import Pipeline

pipeline = Pipeline(debug_enabled=True)
result = pipeline.process(prompt, trace=True)

# Check each stage in result["trace"]["stages"]
```

### **Issue: Metrics Not Available**

#### Solutions

**1. Enable Return Metrics**
```python
result = process(prompt, return_metrics=True)
print(result["metrics"])
```

**2. Check Pipeline Metrics**
```python
result = process(prompt, trace=True)
print(result["trace"]["metrics"])
```

---

## 🌐 Network Issues

### **Issue: Connection Timeouts**

#### Solutions

**1. Increase Timeout**
```python
agent = Agent(timeout=60)  # 60 second timeout
```

**2. Use Fallback Models**
```python
agent = Agent(
    model="gpt-3.5-turbo",  # Faster model
    fallback_providers=[{"provider": "openai", "model": "gpt-3.5-turbo"}]
)
```

**3. Configure Retries**
```python
agent = Agent(retries=5, backoff_factor=2)
```

### **Issue: Rate Limiting**

#### Solutions

**1. Implement Exponential Backoff**
```python
import time
from privysha import Agent

agent = Agent(retries=3)
for attempt in range(3):
    try:
        response = agent.run(prompt)
        break
    except Exception as e:
        if "rate limit" in str(e).lower():
            time.sleep(2 ** attempt)  # 2, 4, 8 seconds
        else:
            raise
```

**2. Use Multiple API Keys**
```python
# Round-robin between multiple keys
api_keys = ["key1", "key2", "key3"]
agent = Agent(api_key=api_keys[attempt % len(api_keys)])
```

---

## 🏗️ Architecture Issues

### **Issue: Circular Import Errors**

#### Symptoms
```
ImportError: cannot import name 'PIIDetector' from partially initialized module
```

#### Solutions

**1. Use Lazy Loading**
```python
# This is now fixed in PrivySHA v0.2.0+
# PII detector loads only when needed
```

**2. Clear Python Cache**
```bash
# Clear Python bytecode cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf
```

**3. Reinstall in Development Mode**
```bash
pip uninstall privysha
pip install -e .
```

---

## 📱 Environment-Specific Issues

### **Windows Issues**

#### Issue: Path Length Errors
```bash
# Use shorter paths or enable long paths
# Windows has 260 character path limit
```

#### Issue: Permission Errors
```bash
# Run as administrator or install in user directory
pip install --user privysha
```

### **macOS Issues**

#### Issue: Python Version Conflicts
```bash
# Use Python 3.10+ with pyenv
pyenv install 3.10.14
pyenv local 3.10.14
pip install privysha
```

### **Linux Issues**

#### Issue: System Python Conflicts
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install privysha
```

---

## 🔍 Debug Mode

### **Enable Comprehensive Debugging**
```python
from privysha import process

# Maximum debugging information
result = process(
    prompt,
    trace=True,           # Full pipeline trace
    debug=True,           # Diff view
    log_level="DEBUG",     # All log messages
    return_metrics=True,    # Detailed metrics
    log_output="file",     # Save to file
    log_file="debug.log"    # Log file location
)

# Print comprehensive debug info
print("=== PIPELINE TRACE ===")
for stage in result["trace"]["stages"]:
    print(f"Stage: {stage['name']}")
    print(f"  Input: {stage['input'][:50]}...")
    print(f"  Output: {stage['output'][:50]}...")
    print(f"  Latency: {stage['latency_ms']}ms")
    if stage.get("changes"):
        print(f"  Changes: {len(stage['changes'])}")

print("\n=== METRICS ===")
print(result["metrics"])
```

---

## 📞 Getting Help

### **Check Version**
```python
from privysha import __version__
print(f"PrivySHA version: {__version__}")
```

### **System Information**
```python
import sys, platform, os
from privysha import __version__

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"PrivySHA: {__version__}")
```

### **Create Bug Report**
```python
# Include this information in bug reports
import sys, platform
from privysha import __version__

bug_info = f"""
Python: {sys.version}
Platform: {platform.platform()}
PrivySHA: {__version__}
Error: [Your error message]
Steps to reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected behavior: [What should happen]
Actual behavior: [What actually happened]
"""

# Post to: https://github.com/AjayRajan05/privySHA/issues
```

---

## 🎯 Performance Optimization

### **Benchmark Your Setup**
```python
import time
from privysha import process

start_time = time.time()
result = process("Your test prompt here")
end_time = time.time()

print(f"Processing time: {(end_time - start_time) * 1000:.2f}ms")
print(f"Tokens saved: {result.get('metrics', {}).get('tokens_saved', 0)}")
```

### **Optimize for Your Use Case**
```python
# For high-throughput processing
from privysha import process_async

async def process_batch(prompts):
    tasks = [process_async(p) for p in prompts]
    return await asyncio.gather(*tasks)

# For memory-constrained environments  
from privysha import process

result = process(
    prompt,
    mode="lite",           # Minimal processing
    security_level="low",   # Basic security
    trace=False,            # No overhead
    pii_mode="rule"         # Fastest PII
)
```

---

## 🚀 Still Having Issues?

1. **Check Documentation**: [Full Docs](https://github.com/AjayRajan05/privySHA)
2. **Search Issues**: [Known Issues](https://github.com/AjayRajan05/privySHA/issues)
3. **Ask Community**: [Discussions](https://github.com/AjayRajan05/privySHA/discussions)
4. **Create Minimal Example**: Test with simplest possible case

---

## 📈 Pro Tips

### **For Production**
- Use `mode="balanced"` for best performance/security tradeoff
- Enable `trace=True` for debugging, disable in production
- Set appropriate `token_budget` for cost control
- Use async processing for high-throughput applications

### **For Development**
- Use `debug=True` during development
- Start with `pii_mode="rule"` for fastest iteration
- Use `log_level="DEBUG"` for detailed troubleshooting
- Test with different `security_level` settings

---

**🎉 Most issues are resolved with proper configuration and understanding of the processing pipeline!**
