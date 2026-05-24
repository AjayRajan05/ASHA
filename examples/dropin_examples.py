#!/usr/bin/env python3
"""
PrivySHA Drop-in Examples

These examples demonstrate the CRITICAL drop-in functionality that makes
PrivySHA feel like a utility, not a system replacement.

Key patterns:
1. process() - One-line prompt processing
2. wrap_llm() - Wrap any LLM client
3. optimize() - Token optimization only
4. sanitize() - Security only
"""

from privysha import process, wrap_llm, optimize, sanitize, Agent
import json

# Example 1: Simple process() - THE MOST IMPORTANT ADOPTION PATH
print("=== Example 1: process() - Drop-in Processing ===")
original = "Hey bro can you please help me analyze this dataset for anomalies? Contact john@email.com for details."
optimized = process(original)

print(f"Original: {original}")
print(f"Optimized: {optimized}")
print()

# Example 2: process() with metrics - SHOW IMMEDIATE VALUE
print("=== Example 2: process() with Metrics ===")
result = process(original, return_metrics=True)

print(f"Original: {result['original']}")
print(f"Optimized: {result['optimized']}")
print(f"Token Reduction: {result['token_reduction']}%")
print(f"Security Safe: {result['security_result']['is_safe']}")
print()

# Example 3: optimize() - TOKEN REDUCTION ONLY
print("=== Example 3: optimize() - Token Reduction Only ===")
wordy_prompt = "Hey there! I was wondering if you could possibly help me by analyzing this dataset and letting me know if there are any anomalies or unusual patterns that I should be aware of? Thanks so much!"
optimized_only = optimize(wordy_prompt, return_metrics=True)

print(f"Original: {wordy_prompt}")
print(f"Optimized: {optimized_only['optimized']}")
print(f"Token Reduction: {optimized_only['token_reduction']}%")
print()

# Example 4: sanitize() - SECURITY ONLY
print("=== Example 4: sanitize() - Security Only ===")
sensitive_prompt = "Please analyze the data and send results to john@email.com or call 555-123-4567. My credit card is 4111-1111-1111-1111."
sanitized = sanitize(sensitive_prompt, return_details=True)

print(f"Original: {sanitized['original']}")
print(f"Sanitized: {sanitized['sanitized']}")
print(f"Safe: {sanitized['is_safe']}")
print(f"Threats: {len(sanitized['threats'])}")
print()

# Example 5: wrap_llm() - EXISTING CLIENT WRAPPING
print("=== Example 5: wrap_llm() - Client Wrapping ===")

# Mock client demonstration
class MockOpenAIClient:
    """Mock OpenAI client for demonstration"""
    def chat(self):
        return MockChatCompletions()

class MockChatCompletions:
    def create(self, messages, **kwargs):
        # In real usage, this would call OpenAI API
        user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), '')
        return {"choices": [{"message": {"content": f"Processed: {user_message}"}}]}

# Mock Gemini client for demonstration
class MockGeminiClient:
    """Mock Gemini client for demonstration"""
    def __init__(self):
        pass
    
    def generate_content(self, prompt):
        return type('Response', (), {'text': f"Gemini processed: {prompt[:50]}..."})()

# Test with different clients
print("Testing with OpenAI client:")
openai_client = MockOpenAIClient()
secure_openai = wrap_llm(openai_client)
response = secure_openai.chat.completions.create(
    messages=[{"role": "user", "content": "Hey bro analyze dataset with john@email.com"}]
)
print(f"OpenAI Response: {response['choices'][0]['message']['content']}")

print("\nTesting with Gemini client:")
gemini_client = MockGeminiClient()
secure_gemini = wrap_llm(gemini_client)
print(f"Gemini client detected: {secure_gemini.get_client_info()['client_type']}")
response = secure_gemini.generate_content("Hey bro analyze dataset with john@email.com")
print(f"Gemini Response: {response.text}")
print()

# Example 6: Before/After Comparison - PROOF OF VALUE
print("=== Example 6: Before/After Comparison ===")

test_prompts = [
    "Hey bro can you analyze this dataset for anomalies?",
    "Please help me understand this customer data and send insights to sarah@company.com",
    "I was wondering if you could possibly help me by reviewing these financial records and identifying any suspicious transactions?",
    "Can you please analyze the user behavior patterns and provide recommendations for improvement? Contact support@help.com for questions.",
]

print("BEFORE PRIVYSHA:")
total_tokens_before = 0
for i, prompt in enumerate(test_prompts, 1):
    tokens = len(prompt.split()) * 1.3  # Rough token estimate
    total_tokens_before += tokens
    print(f"{i}. {prompt[:60]}... (~{int(tokens)} tokens)")

print(f"\nTotal tokens before: {int(total_tokens_before)}")

print("\nAFTER PRIVYSHA:")
total_tokens_after = 0
for i, prompt in enumerate(test_prompts, 1):
    result = process(prompt, return_metrics=True)
    optimized = result['optimized']
    tokens = len(optimized.split()) * 1.3
    total_tokens_after += tokens
    reduction = result['token_reduction']
    print(f"{i}. {optimized[:60]}... (~{int(tokens)} tokens, {reduction}% reduction)")

print(f"\nTotal tokens after: {int(total_tokens_after)}")
print(f"Overall reduction: {int((1 - total_tokens_after/total_tokens_before) * 100)}%")
print()

# Example 7: Real-world Integration Pattern
print("=== Example 7: Real-world Integration Pattern ===")

def existing_chatbot_function(user_input: str) -> str:
    """
    Example of integrating PrivySHA into existing chatbot function
    WITHOUT changing the function signature or behavior.
    """
    # ONE LINE ADDITION - that's it!
    processed_input = process(user_input, privacy=True)
    
    # Rest of the function remains exactly the same
    # ... existing logic ...
    return f"Response to: {processed_input}"

# Test the integrated function
user_messages = [
    "Hey bro help me analyze customer data",
    "Please review this report and send to manager@company.com",
    "Can you check these logs for errors?"
]

for msg in user_messages:
    response = existing_chatbot_function(msg)
    print(f"User: {msg}")
    print(f"Bot: {response}")
    print()

print("=== Summary ===")
print("✅ process() - One-line drop-in processing")
print("✅ wrap_llm() - Existing client wrapping") 
print("✅ optimize() - Token reduction only")
print("✅ sanitize() - Security only")
print("✅ Immediate value with metrics")
print("✅ No architecture changes required")
print("✅ Works with existing code")
