from fastapi import FastAPI, Request, HTTPException
import uvicorn
import asyncio
import json
import requests
import re
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
    "confirmed": 50000,  # 0.0005 BTC in satoshis
    "unconfirmed": 0,
    "currency": "BTC"
}

async def process_balance_query(question: str, session_id: str = "default_session") -> str:
    """Process balance queries directly without ASI1 API"""
    try:
        # Extract Bitcoin address from question
        bitcoin_address_pattern = r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b'
        address_match = re.search(bitcoin_address_pattern, question)
        
        if address_match and "balance" in question.lower():
            detected_address = address_match.group(0)
            print(f"Remembered Bitcoin wallet address: {detected_address} for user: {session_id}")
            
            # Use mock data for now (you can replace this with real API calls later)
            confirmed_sats = MOCK_BALANCE_DATA["confirmed"]
            unconfirmed_sats = MOCK_BALANCE_DATA["unconfirmed"]
            total_sats = confirmed_sats + unconfirmed_sats
            
            # Convert satoshis to BTC for display (1 BTC = 100,000,000 satoshis)
            confirmed_btc = confirmed_sats / 100000000
            unconfirmed_btc = unconfirmed_sats / 100000000
            total_btc = total_sats / 100000000
            
            return f"💰 **Bitcoin Wallet Balance**\n\n" \
                   f"Address: `{detected_address}`\n\n" \
                   f"Confirmed: {confirmed_btc:.8f} BTC\n" \
                   f"Unconfirmed: {unconfirmed_btc:.8f} BTC\n" \
                   f"Total: {total_btc:.8f} BTC\n\n" \
                   f"_(Mock data for testing - replace with real blockchain API)_"
        
        # Default response for non-balance queries
        return "I can help you check Bitcoin wallet balances. Please provide a Bitcoin address and ask for its balance."
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return f"Error processing your request: {str(e)}"

@app.post("/ask")
async def ask(request: QuestionRequest):
    question = request.question
    session_id = request.session_id or "default_session"
    
    print(f"Received question: {question}")
    print(f"Session ID: {session_id}")
    
    # Process the query
    answer = await process_balance_query(question, session_id)
    return {"answer": answer, "session_id": session_id}

@app.get("/")
async def root():
    return {"message": "Fixed API Gateway is running", "endpoints": ["/ask"]}

if __name__ == "__main__":
    print("Starting Fixed API Gateway on http://0.0.0.0:8085")
    uvicorn.run(app, host="0.0.0.0", port=8085)
