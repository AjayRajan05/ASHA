import pytest
from privysha.utils.dropin import process, wrap_llm, optimize, sanitize

class MockLLM:
    """Mock LLM client for testing wrap_llm."""
    class Chat:
        class Completions:
            def create(self, messages, **kwargs):
                return type('Response', (), {
                    'choices': [
                        type('Choice', (), {
                            'message': type('Message', (), {
                                'content': f"Echo: {messages[-1]['content']}"
                            })()
                        })()
                    ]
                })()
        completions = Completions()
    chat = Chat()

def test_dropin_process_basic():
    """Test the main process() drop-in function."""
    prompt = "My name is John Doe, email john@doe.com"
    
    # Basic usage
    result = process(prompt)
    assert isinstance(result, str)
    assert "John Doe" not in result
    assert "john@doe.com" not in result

def test_dropin_process_metrics():
    """Test process() with metrics return."""
    prompt = "Analyze this data: 123-45-6789"
    
    result = process(prompt, return_metrics=True)
    assert isinstance(result, dict)
    assert "optimized" in result
    assert "metrics" in result
    assert "ssn" in result["metrics"]["pii_detected"]

def test_dropin_wrap_llm():
    """Test the wrap_llm() decorator/wrapper."""
    client = MockLLM()
    secure_client = wrap_llm(client)
    
    prompt = "Contact john@doe.com"
    response = secure_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = response.choices[0].message.content
    assert "john@doe.com" not in content
    assert len(content) > 0

def test_dropin_optimize():
    """Test the optimize() utility."""
    prompt = "A very very very very long prompt that can be made shorter."
    
    optimized = optimize(prompt, token_budget=5)
    assert isinstance(optimized, str)
    assert len(optimized.split()) < len(prompt.split())

def test_dropin_sanitize():
    """Test the sanitize() security-only utility."""
    prompt = "Dangerous prompt with PII john@doe.com"
    
    sanitized = sanitize(prompt)
    assert "john@doe.com" not in sanitized
    assert "[EMAIL" in sanitized

if __name__ == "__main__":
    pytest.main([__file__])
