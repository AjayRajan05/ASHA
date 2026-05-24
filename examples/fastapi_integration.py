#!/usr/bin/env python3
"""
FastAPI Integration Example

Demonstrates how PrivySHA middleware works as a drop-in security layer
for FastAPI applications.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json

# Import PrivySHA middleware
from privysha.integrations.fastapi import add_privysha_middleware

# Create FastAPI app
app = FastAPI(title="Chat API with PrivySHA Protection")

# Add PrivySHA middleware - ONE LINE ADDITION!
add_privysha_middleware(
    app, 
    privacy=True,
    token_budget=1200,
    debug_mode=True  # Shows processing info
)

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-4o-mini"

class ChatResponse(BaseModel):
    choices: List[Dict[str, Any]]

# Mock LLM service (in real app, this would call OpenAI/Anthropic/etc.)
def mock_llm_service(messages: List[ChatMessage], model: str) -> Dict[str, Any]:
    """Mock LLM service that processes messages."""
    user_message = next((msg.content for msg in messages if msg.role == "user"), "")
    
    # In real usage, this would call the actual LLM API
    response_content = f"Processed by {model}: {user_message}"
    
    return {
        "choices": [{
            "message": {
                "content": response_content,
                "role": "assistant"
            }
        }]
    }

# API endpoints
@app.post("/chat/completions")
async def chat_completions(request: ChatRequest) -> ChatResponse:
    """
    Chat completions endpoint.
    
    NOTE: PrivySHA middleware automatically processes all prompts
    before they reach this endpoint. No changes needed here!
    """
    try:
        # Process request (prompts already optimized by PrivySHA)
        response = mock_llm_service(request.messages, request.model)
        return ChatResponse(**response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/completions")
async def completions(prompt: str, model: str = "gpt-4o-mini") -> ChatResponse:
    """
    Simple completions endpoint.
    
    PrivySHA middleware automatically processes the prompt parameter.
    """
    messages = [{"role": "user", "content": prompt}]
    response = mock_llm_service(messages, model)
    return ChatResponse(**response)

@app.get("/")
async def root():
    """Root endpoint showing the API is running."""
    return {
        "message": "Chat API with PrivySHA Protection",
        "endpoints": [
            "/chat/completions",
            "/completions",
            "/health"
        ],
        "protection": "All prompts automatically processed by PrivySHA"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "privysha": "active"}

# Example usage (for testing)
if __name__ == "__main__":
    import uvicorn
    
    print("Starting FastAPI app with PrivySHA middleware...")
    print("Test with:")
    print('curl -X POST "http://localhost:8000/chat/completions" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"messages": [{"role": "user", "content": "Hey bro analyze dataset with john@email.com"}]}\'')
    print()
    print("Check response headers for PrivySHA processing info!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
