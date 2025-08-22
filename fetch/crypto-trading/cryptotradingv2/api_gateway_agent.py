from fastapi import FastAPI, Request, HTTPException, Depends, Cookie
import uvicorn
import asyncio
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent

from fastapi.middleware.cors import CORSMiddleware
from comprehensive_user_agent import handle_chat_message

# Define the request model
class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

# Create FastAPI app
fastapi_app = FastAPI()


fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "Content-Type": "application/json"
}  # Simplified headers

@fastapi_app.get("/")
async def root():
    return {"status": "ok", "message": "ChainPilot Trading Assistant API is running"}

@fastapi_app.get("/status")
async def status():
    return {
        "status": "online",
        "api_version": "1.0.0",
        "services": {
            "user_agent": "running",
            "chat_protocol": "active"
        }
    }

@fastapi_app.post("/ask")
async def ask(request: QuestionRequest):
    question = request.question
    session_id = request.session_id or "default_session"
    
    # Import what we need
    
    # Create a custom context that captures the response
    class CaptureResponseContext:
        def __init__(self):
            self.logger = type("logger", (), {"info": print, "error": print})()
            self.response = None
            
        async def send(self, recipient, message):
            # Capture the response message
            if hasattr(message, 'content') and message.content:
                content_obj = message.content[0]
                if hasattr(content_obj, 'text'):
                    self.response = content_obj.text
    
    # Create capture context
    ctx = CaptureResponseContext()
    
    # Create a chat message with TextContent
    mock_chat_message = ChatMessage(content=[TextContent(text=question)])
    
    try:
        # Process the message
        await handle_chat_message(ctx, "api_user", mock_chat_message)
        
        # If we didn't get a response through ctx.send, process the message directly
        if ctx.response is None:
            # Try using a simple analysis query
            if question.lower().startswith("analyze"):
                parts = question.split()
                if len(parts) > 1:
                    symbol = parts[1].upper()
                    ctx.response = f"⏰ Analyzing {symbol}... Please wait 15-20 seconds for a comprehensive analysis."
                else:
                    ctx.response = "Please specify a cryptocurrency to analyze, for example: 'analyze BTC'"
            else:
                # Default fallback response
                ctx.response = "I'm processing your request. For best results, try commands like 'analyze BTC', 'technical ETH', or 'help'."
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        ctx.response = f"Error processing your request: {str(e)}"
    
    return {"answer": ctx.response or "Processing your request...", "session_id": session_id}

# To run both FastAPI and the agent, use uvicorn in a separate process:
# uvicorn comprehensive_user_agent:fastapi_app --host 0.0.0.0 --port 8088



if __name__ == "__main__":
    # import uvicorn
    # If you want to include additional routers, do it here
    # Example:
    # try:
    #     from ethereum_endpoints import router as ethereum_router
    #     fastapi_app.include_router(ethereum_router)
    #     print("Ethereum endpoints registered successfully")
    # except ImportError as e:
    #     print(f"Warning: Could not load Ethereum endpoints: {str(e)}")

    print("Starting Agent API Gateway on http://0.0.0.0:8082")
    uvicorn.run("api_gateway_agent:fastapi_app", host="0.0.0.0", port=8082)