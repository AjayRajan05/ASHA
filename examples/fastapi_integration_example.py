#!/usr/bin/env python3
"""
FastAPI integration (v0.4.1).

Add PrivySHA to an existing FastAPI app with one middleware call.
``privacy=True`` maps to internal mode ``balanced``.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Import PrivySHA middleware
from privysha.integrations.fastapi import add_privysha_middleware

# Create FastAPI app (your existing app)
app = FastAPI(title="AI Chat API", version="1.0.0")

# Add CORS (your existing middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ONE LINE ADDITION - Add PrivySHA middleware
add_privysha_middleware(app, privacy=True, debug_mode=True)

# Your existing Pydantic models (no changes needed)
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7

class ChatResponse(BaseModel):
    choices: List[dict]
    usage: dict

# Your existing endpoints (no changes needed)
@app.post("/chat/completions")
async def chat_completions(request: ChatRequest) -> ChatResponse:
    """
    Your existing chat endpoint - now automatically secured and optimized by PrivySHA!
    
    PrivySHA middleware will automatically:
    1. Extract prompts from request.messages
    2. Process them through security and optimization pipeline
    3. Forward optimized prompts to this endpoint
    4. Add security headers to response
    """
    
    # Your existing logic - no changes needed
    # In a real app, this would call your LLM provider
    user_message = next((msg.content for msg in request.messages if msg.role == "user"), "")
    
    # Mock LLM response (replace with your actual LLM call)
    response_text = f"Processed your request: {user_message[:100]}..."
    
    return ChatResponse(
        choices=[{"message": {"role": "assistant", "content": response_text}}],
        usage={"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80}
    )

@app.post("/completions")
async def completions(prompt: str, model: str = "text-davinci-003") -> ChatResponse:
    """
    Simple completions endpoint - also automatically processed by PrivySHA
    """
    # Your existing logic
    response_text = f"Completed: {prompt[:50]}..."
    
    return ChatResponse(
        choices=[{"text": response_text}],
        usage={"prompt_tokens": 25, "completion_tokens": 15, "total_tokens": 40}
    )

@app.post("/generate")
async def generate(input_text: str) -> dict:
    """
    Custom generate endpoint - automatically processed by PrivySHA
    """
    return {"generated_text": f"Generated: {input_text[:50]}..."}

@app.get("/health")
async def health():
    """Health check endpoint - not processed by PrivySHA"""
    return {"status": "healthy"}

# Admin endpoint to see PrivySHA processing stats
@app.get("/admin/privysha-stats")
async def privysha_stats():
    """
    View PrivySHA processing statistics (when debug_mode=True)
    These headers are automatically added by PrivySHA middleware:
    - X-PrivySHA-Processed: true
    - X-PrivySHA-Prompts: number of prompts processed
    - X-PrivySHA-Token-Reduction: average token reduction percentage
    """
    return {
        "message": "Check response headers for PrivySHA processing stats",
        "headers_to_look_for": [
            "X-PrivySHA-Processed",
            "X-PrivySHA-Prompts", 
            "X-PrivySHA-Token-Reduction"
        ]
    }

if __name__ == "__main__":
    print("Starting FastAPI app with PrivySHA middleware...")
    print("PrivySHA will automatically process:")
    print("- POST /chat/completions")
    print("- POST /completions") 
    print("- POST /generate")
    print("\nTest with curl:")
    print('curl -X POST "http://localhost:8000/chat/completions" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"messages": [{"role": "user", "content": "Hey bro analyze dataset with john@email.com"}]}\'')
    print("\nCheck response headers for PrivySHA processing info!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
