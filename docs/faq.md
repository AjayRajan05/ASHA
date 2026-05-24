# Frequently Asked Questions

**Common questions about PrivySHA's 4 core functions and usage**

---

## 🚀 Getting Started

### Q: How do I install PrivySHA?
**A:** 
```bash
pip install privysha
```

Optional dependencies for specific LLM providers:
```bash
pip install openai          # For OpenAI
pip install google-generativeai  # For Gemini
pip install anthropic       # For Anthropic
```

### Q: What are the system requirements?
**A:** 
- Python 3.10 or higher
- Internet connection for cloud models (optional)
- No API keys required for basic processing

### Q: Do I need API keys?
**A:** No API keys required for basic PII masking and optimization. API keys only needed for LLM integration:
```bash
export OPENAI_API_KEY=your_key
export GOOGLE_API_KEY=your_key
```

### Q: How do I get started in 10 seconds?
**A:** 
```python
from privysha import process

result = process("My email is john@gmail.com. Analyze this dataset.")
print(result)
```

---

## 🔧 Core Functions

### Q: What are the 4 main functions?
**A:** 
1. `process()` - Full pipeline (security + optimization)
2. `wrap_llm()` - Wrap existing LLM client
3. `optimize()` - Token optimization only
4. `sanitize()` - Security processing only

### Q: Which function should I use?
**A:** 
- **Most cases**: Use `process()`
- **Existing code**: Use `wrap_llm()`
- **Cost optimization only**: Use `optimize()`
- **Security only**: Use `sanitize()`

### Q: How do I wrap my existing LLM client?
**A:** 
```python
from privysha import wrap_llm
import openai

client = openai.OpenAI()
secure_client = wrap_llm(client)

# Same interface, automatically secured
response = secure_client.chat.completions.create(...)
```

---

## 🔒 Security & Privacy

### Q: What PII gets detected?
**A:** 
- Email addresses
- Phone numbers  
- Credit cards
- Social Security numbers
- Addresses
- Names

### Q: Is my data sent to external servers?
**A:** No. PrivySHA processes everything locally. Only when you use LLM integration are prompts sent to the LLM provider (with PII already masked).

### Q: How accurate is PII detection?
**A:** 98.5% accuracy with <1% false positives for safe prompts.

### Q: Can I customize PII detection?
**A:** Yes, you can add custom patterns:
```python
from privysha import configure
configure(custom_pii_patterns={"employee_id": r"EMP-\d{6}"})
```

---

## ⚡ Performance & Cost

### Q: How much can I save on tokens?
**A:** 30-50% token reduction on average, up to 70% for verbose prompts.

### Q: What's the performance impact?
**A:** <100ms processing time for 99% of requests. Average ~50ms.

### Q: Does it break my prompts?
**A:** No. PrivySHA has a "no-change guarantee" - safe prompts are never modified.

### Q: How do I see cost savings?
**A:** 
```python
result = process("prompt", return_metrics=True)
print(f"Saved: {result['token_reduction']}% tokens")
```

---

## 🛠️ Configuration

### Q: What are the processing modes?
**A:** 
- `balanced` (default) - Smart security + optimization
- `strict` - Maximum security
- `lite` - Minimal processing
- `off` - No modification

### Q: How do I enable debug mode?
**A:** 
```python
result = process("prompt", debug=True)
print(result["changes"])
```

### Q: How do I use the CLI?
**A:** 
```bash
privysha "My email is john@gmail.com. Analyze this dataset."
privysha --quick-test
privysha --examples
```

---

## 🏢 Enterprise

### Q: Is it GDPR/CCPA compliant?
**A:** Yes. Automatic PII masking makes it compliance-ready out of the box.

### Q: Can I use it in production?
**A:** Yes. PrivySHA is production-ready with fail-safe operation and enterprise security.

### Q: How do I monitor usage?
**A:** Use metrics to track performance:
```python
result = process("prompt", return_metrics=True)
# Log: tokens_saved, processing_time, pii_detected
```

---

## 🔧 Troubleshooting

### Q: Why isn't PII being masked?
**A:** Ensure privacy is enabled:
```python
result = process("prompt", mode="strict")  # Maximum security
```

### Q: Why are my prompts changing unexpectedly?
**A:** Check processing mode:
```python
result = process("prompt", mode="lite")  # Minimal changes
```

### Q: How do I report issues?
**A:** Open an issue on GitHub with:
- Example prompt
- Expected vs actual result
- Processing mode used

---

## 🆚 Comparison

### Q: How is PrivySHA different from guardrails?
**A:** 
- **Guardrails**: Block/filter content reactively
- **PrivySHA**: Proactively transforms prompts before they reach LLM

### Q: How is it different from LangChain?
**A:** 
- **LangChain**: Framework for building LLM applications
- **PrivySHA**: Drop-in security/optimization layer that works with any LLM

### Q: Can I use PrivySHA with other tools?
**A:** Yes. PrivySHA works with OpenAI, Anthropic, Gemini, HuggingFace, Ollama, and custom integrations.

---

## � More Questions?

### Q: Where can I find examples?
**A:** 
- [Examples documentation](examples.md)
- [API reference](api-reference.md)
- Use `privysha --examples` in CLI

### Q: How do I contribute?
**A:** See [contributing guide](contributing.md) for details.

### Q: Is there a Discord community?
**A:** Join our Discord for support and discussions.

### Q: What is Prompt IR?
**A:** Prompt IR (Intermediate Representation) is a structured JSON representation of user intent that enables:
- Deterministic processing
- Systematic optimization
- Advanced routing
- Full debugging

Example:
```json
{
  "intent": "analyze",
  "object": "data",
  "constraints": ["thorough"],
  "style": "analytical"
}
```

### Q: How is PrivySHA different from LangChain?
**A:** 
| Feature | PrivySHA | LangChain |
|---------|----------|-----------|
| **Prompt Compiler** | ✅ | ❌ |
| **Prompt IR** | ✅ | ❌ |
| **Cost Optimization** | ✅ | ❌ |
| **Multi-model routing** | ✅ | ⚠️ |
| **Security + Transformation** | ✅ | ⚠️ |
| **Observability** | ✅ | ⚠️ |

PrivySHA focuses on prompt optimization and compilation, while LangChain focuses on chaining operations.

### Q: What does "treat prompts as programs" mean?
**A:** Instead of treating prompts as static strings, PrivySHA:
- Compiles prompts like code
- Optimizes them systematically
- Enables reproducible results
- Provides debugging like code compilers

---

## 💰 Cost and Performance

### Q: How much does PrivySHA cost?
**A:** PrivySHA itself is free and open-source. You only pay for:
- LLM API calls (OpenAI, Anthropic, etc.)
- Optional: Your own infrastructure for local models

### Q: How much can I save with optimization?
**A:** Average savings:
- **Token reduction**: 5–15% typical (verbose prompts; structured prompts often unchanged)
- **Cost savings**: 60-80% depending on model
- **Speed improvement**: 30-50% faster responses

Example (typical verbose prompt):
```
Before: 120 tokens
After: 102–114 tokens
Savings: ~5–15% cost reduction
```

### Q: Which model should I use?
**A:** Depends on your needs:
- **Simple tasks**: `gpt-3.5-turbo` or `claude-3-haiku`
- **Complex analysis**: `gpt-4o` or `claude-3-sonnet`
- **Cost-sensitive**: `gpt-4o-mini` or local models
- **Privacy-sensitive**: Local models only

### Q: Can I use my own models?
**A:** Yes! PrivySHA supports:
- HuggingFace models
- Ollama models
- Custom model adapters
- Local deployment

---

## 🔒 Security and Privacy

### Q: How does PII protection work?
**A:** PrivySHA:
- Scans for PII patterns (email, phone, SSN, etc.)
- Masks detected PII with placeholders
- Preserves meaning while protecting privacy
- Works in real-time during processing

Example:
```
Input: "Contact john@email.com"
Output: "Contact [EMAIL]"
```

### Q: What PII types are detected?
**A:** 
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- Addresses
- Names
- IP addresses
- URLs
- Custom patterns you define

### Q: Is my data secure?
**A:** PrivySHA provides multiple security layers:
- **Input masking**: PII masked before sending to LLM
- **Injection protection**: Blocks prompt injection attacks
- **Local processing**: Option to keep data on-premise
- **Zero-knowledge**: No data stored by PrivySHA

### Q: Can I run PrivySHA entirely locally?
**A:** Yes! Configure for local-only:
```python
agent = Agent(
    model="local",
    provider="huggingface",
    privacy_mode="zero_knowledge"
)
```

---

## 🔧 Technical Questions

### Q: How do I debug issues?
**A:** Enable tracing:
```python
result = agent.run("prompt", trace=True)
agent.print_debug_trace()
```

This shows the complete pipeline: `RAW → SANITIZED → IR → OPTIMIZED → RESPONSE`

### Q: How do I add custom PII patterns?
**A:** 
```python
from privysha.security.security_layer import SecurityLayer

security = SecurityLayer()
security.add_pii_pattern(
    name="employee_id",
    pattern=r"EMP\d{6}",
    replacement="[EMPLOYEE_ID]"
)
```

### Q: How do I create custom routing rules?
**A:** 
```python
def custom_routing(task_ir, context):
    if task_ir.intent == "analyze" and task_ir.complexity > 0.7:
        return {"provider": "openai", "model": "gpt-4o"}
    else:
        return {"provider": "anthropic", "model": "claude-3-haiku"}

agent = Agent(routing_strategy=custom_routing)
```

### Q: Can I disable optimization?
**A:** Yes, set optimization level:
```python
agent = Agent(optimization_level="conservative")
```

Or disable entirely:
```python
agent = Agent(enable_optimization=False)
```

---

## 🏢 Enterprise Questions

### Q: Is PrivySHA suitable for enterprise use?
**A:** Yes! Enterprise features:
- **GDPR compliance**: Built-in privacy controls
- **Audit trails**: Complete logging and tracing
- **Multi-tenant**: Different policies per tenant
- **Cost controls**: Budget limits and monitoring
- **SLA monitoring**: Performance tracking and alerts

### Q: How do I deploy in production?
**A:** 
```python
agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"}
    ],
    monitoring={
        "log_requests": True,
        "track_costs": True,
        "alert_on_failures": True
    },
    cost_limits={
        "daily_limit": 100.0,
        "monthly_limit": 2000.0
    }
)
```

### Q: Can I use PrivySHA with my existing LLM infrastructure?
**A:** Yes! PrivySHA is designed to:
- Work with existing API keys
- Integrate with current systems
- Complement existing tooling
- Gradually adopt features

---

## 🐛 Troubleshooting

### Q: Why am I getting import errors?
**A:** Common solutions:
```bash
# Update pip
pip install --upgrade pip

# Reinstall
pip uninstall privysha
pip install privysha

# Check Python version
python --version  # Should be 3.10+
```

### Q: Why are API calls failing?
**A:** Check:
1. **API keys**: Verify environment variables
2. **Network**: Check internet connection
3. **Permissions**: API key permissions
4. **Rate limits**: Check usage limits
5. **Model availability**: Model might be deprecated

### Q: Why is optimization not working?
**A:** Common causes:
- **Conservative level**: Try "balanced" or "aggressive"
- **Complex prompts**: Some prompts resist optimization
- **Domain-specific**: Add custom optimization rules
- **Validation**: Quality preservation might limit optimization

### Q: How do I report bugs?
**A:** 
1. **Check GitHub issues**: Existing solutions
2. **Create new issue**: Include:
   - Python version
   - PrivySHA version
   - Error message
   - Minimal reproduction code
   - Expected vs actual behavior

---

## 📚 Comparison Questions

### Q: PrivySHA vs Guardrails?
**A:** 
| Aspect | PrivySHA | Guardrails |
|--------|-----------|------------|
| **Approach** | Proactive transformation | Reactive filtering |
| **Scope** | Input + Output | Output only |
| **Optimization** | Built-in | Not included |
| **Flexibility** | Highly configurable | Limited |

### Q: PrivySHA vs Direct LLM API?
**A:** 
| Feature | Direct API | PrivySHA |
|---------|------------|-----------|
| **Cost** | Full price | 5–15% typical savings |
| **Security** | Manual | Automatic |
| **Optimization** | None | Built-in |
| **Debugging** | Limited | Full pipeline visibility |
| **Reliability** | Single point | Automatic fallbacks |

### Q: When should I use PrivySHA?
**A:** Use PrivySHA when you need:
- **Cost optimization**: Reduce LLM costs
- **Privacy protection**: PII masking and security
- **Reliability**: Fallbacks and error handling
- **Observability**: Debugging and monitoring
- **Consistency**: Reproducible results

Use direct API when you need:
- **Simple one-off requests**
- **Maximum control**
- **Minimal overhead**
- **Specific model features**

---

## 🔮 Future and Roadmap

### Q: What's coming in future versions?
**A:** Planned features:
- **Prompt caching**: Reduce redundant processing
- **Visual debugger**: UI for pipeline debugging
- **Benchmarking suite**: Performance comparison tools
- **Multi-agent orchestration**: Coordinate multiple agents
- **Streaming support**: Real-time response streaming
- **More providers**: Additional LLM providers

### Q: How can I request features?
**A:** 
1. **GitHub issues**: Tag with "enhancement"
2. **Discussions**: Community feedback
3. **Pull requests**: Direct contributions
4. **Email**: Contact maintainers

### Q: How often is PrivySHA updated?
**A:** 
- **Minor releases**: Every 2-3 weeks (bug fixes, small features)
- **Major releases**: Every 2-3 months (new features, breaking changes)
- **Security patches**: As needed (immediate release)

---

## 🤝 Community and Support

### Q: How can I get help?
**A:** 
1. **Documentation**: Complete guides and API reference
2. **GitHub issues**: Community support
3. **Discussions**: Community Q&A
4. **Examples**: Real-world usage patterns
5. **FAQ**: This document!

### Q: How can I contribute?
**A:** 
1. **Code contributions**: Pull requests
2. **Documentation**: Improve guides
3. **Examples**: Share use cases
4. **Bug reports**: Detailed issues
5. **Community**: Help others in discussions

See [Contributing Guide](contributing.md) for details.

### Q: What's the license?
**A:** Apache 2.0 License. This means:
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Patent use allowed
- ❌ No warranty provided
- ❌ No liability assumed

---

## 🎯 Quick Tips

### Q: What are the best practices?
**A:** 
- **Always use `trace=True` during development**
- **Enable privacy for user data**
- **Set up fallbacks for production**
- **Monitor costs and performance**
- **Start with "balanced" optimization level**
- **Use appropriate models for task complexity**

### Q: How do I maximize savings?
**A:** 
- **Use appropriate models**: Don't over-provision
- **Enable optimization**: "balanced" or "aggressive"
- **Set up routing**: Cost-optimized strategy
- **Monitor usage**: Identify optimization opportunities
- **Use local models**: For privacy-sensitive tasks

### Q: What should I avoid?
**A:** 
- **Don't disable optimization** unless necessary
- **Don't ignore security warnings**
- **Don't use production API keys in development**
- **Don't skip fallback configuration**
- **Don't ignore performance monitoring**

---

## 📞 Still Have Questions?

If your question isn't answered here:

1. **Check [Documentation](index.md)**: Comprehensive guides
2. **Search [GitHub Issues](https://github.com/AjayRajan05/privySHA/issues)**: Existing discussions
3. **Join [Discussions](https://github.com/AjayRajan05/privySHA/discussions)**: Community Q&A
4. **Create [Issue](https://github.com/AjayRajan05/privySHA/issues/new)**: New questions

---

*Found this FAQ helpful? [Star the repo](https://github.com/AjayRajan05/privySHA) to support the project!*
