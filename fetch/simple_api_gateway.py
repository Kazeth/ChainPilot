from fastapi import FastAPI, Request, HTTPException
import uvicorn
import asyncio
import json
import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Add model for request data
class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mock data for testing
MOCK_BALANCE_DATA = {
    "address": "bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs",
    "confirmed": 50000,
    "unconfirmed": 0,
    "total": 50000,
    "currency": "BTC"
}

@app.post("/ask")
async def ask(request: QuestionRequest):
    question = request.question.lower()
    session_id = request.session_id or "default_session"
    
    # Simple keyword-based processing for testing
    if "balance" in question and "bitcoin" in question:
        # Extract bitcoin address from question if present
        import re
        bitcoin_address_pattern = r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b'
        address_match = re.search(bitcoin_address_pattern, request.question)
        
        if address_match:
            address = address_match.group(0)
            # Format a nice response
            confirmed_btc = MOCK_BALANCE_DATA["confirmed"] / 100000000
            total_btc = MOCK_BALANCE_DATA["total"] / 100000000
            
            answer = f"💰 **Bitcoin Wallet Balance**\n\n"
            answer += f"Address: `{address}`\n\n"
            answer += f"Confirmed: {confirmed_btc:.8f} BTC\n"
            answer += f"Total: {total_btc:.8f} BTC\n\n"
            answer += f"_(This is mock data for testing purposes)_"
            
            return {"answer": answer, "session_id": session_id}
    
    # Default response for other queries
    answer = "I'm a cryptocurrency assistant. I can help you with Bitcoin balance queries. Try asking: 'get balance bitcoin address bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs'"
    return {"answer": answer, "session_id": session_id}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Simple API Gateway is running"}

if __name__ == "__main__":
    print("Starting Simple API Gateway on http://0.0.0.0:8084")
    uvicorn.run(app, host="0.0.0.0", port=8084)
