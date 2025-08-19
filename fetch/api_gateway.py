from fastapi import FastAPI, Request, HTTPException, Depends, Cookie
import uvicorn
from agent import process_query, wallet_memory
import asyncio
import json
import requests
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

# Add model for request data
class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

# In-memory session storage
session_wallets = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Services Configuration
class BlockchainAPIService:
    """Base class for blockchain API services"""
    def get_balance(self, address: str) -> Dict[str, Any]:
        raise NotImplementedError
    
    def get_utxos(self, address: str) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    def get_fee_percentiles(self) -> List[float]:
        raise NotImplementedError

class BlockchairAPI(BlockchainAPIService):
    """Implementation using Blockchair API"""
    BASE_URL = "https://api.blockchair.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        
    def get_balance(self, address: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/bitcoin/dashboards/address/{address}"
        params = {"key": self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch balance data")
                
            address_data = data.get("data", {}).get(address, {})
            address_info = address_data.get("address", {})
            
            return {
                "confirmed": address_info.get("balance", 0),
                "unconfirmed": address_info.get("unconfirmed_balance", 0),
                "total_received": address_info.get("received", 0),
                "total_sent": address_info.get("spent", 0),
                "transaction_count": address_info.get("transaction_count", 0)
            }
        except requests.RequestException as e:
            print(f"Error fetching balance from Blockchair: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_utxos(self, address: str) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/bitcoin/dashboards/address/{address}"
        params = {"key": self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch UTXO data")
                
            address_data = data.get("data", {}).get(address, {})
            utxos = address_data.get("utxo", [])
            
            formatted_utxos = []
            for utxo in utxos:
                formatted_utxos.append({
                    "txid": utxo.get("transaction_hash", ""),
                    "vout": utxo.get("index", 0),
                    "value": utxo.get("value", 0),
                    "confirmations": utxo.get("block_id", 0)  # Not exact confirmations but block_id as a proxy
                })
            
            return formatted_utxos
        except requests.RequestException as e:
            print(f"Error fetching UTXOs from Blockchair: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_fee_percentiles(self) -> List[float]:
        url = f"{self.BASE_URL}/bitcoin/stats"
        params = {"key": self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch fee data")
            
            # Extract fee estimates from the response - this is a simplification
            # Blockchair doesn't provide percentiles directly, so we're extrapolating
            stats = data.get("data", {})
            
            # Get median fee (convert from BTC/kB to sat/byte)
            median_fee = stats.get("median_transaction_fee_24h", 10000)  # Default to 10000 sats
            median_fee_sat_byte = median_fee / 1000  # Convert to sat/byte
            
            # Generate a range of fee estimates based on the median
            factors = [0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
            fee_percentiles = [round(median_fee_sat_byte * factor, 1) for factor in factors]
            
            return fee_percentiles
        except requests.RequestException as e:
            print(f"Error fetching fee data from Blockchair: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

class MemPoolAPI(BlockchainAPIService):
    """Implementation using mempool.space API"""
    BASE_URL = "https://mempool.space/api"
    
    def get_balance(self, address: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/address/{address}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            return {
                "confirmed": data.get("chain_stats", {}).get("funded_txo_sum", 0) - 
                            data.get("chain_stats", {}).get("spent_txo_sum", 0),
                "unconfirmed": data.get("mempool_stats", {}).get("funded_txo_sum", 0) - 
                              data.get("mempool_stats", {}).get("spent_txo_sum", 0),
                "total_received": data.get("chain_stats", {}).get("funded_txo_sum", 0),
                "total_sent": data.get("chain_stats", {}).get("spent_txo_sum", 0),
                "transaction_count": data.get("chain_stats", {}).get("tx_count", 0)
            }
        except requests.RequestException as e:
            print(f"Error fetching balance from MemPool: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_utxos(self, address: str) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/address/{address}/utxo"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            utxos = response.json()
            
            formatted_utxos = []
            for utxo in utxos:
                formatted_utxos.append({
                    "txid": utxo.get("txid", ""),
                    "vout": utxo.get("vout", 0),
                    "value": utxo.get("value", 0),
                    "confirmations": utxo.get("status", {}).get("confirmed", False)
                })
            
            return formatted_utxos
        except requests.RequestException as e:
            print(f"Error fetching UTXOs from MemPool: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_fee_percentiles(self) -> List[float]:
        url = f"{self.BASE_URL}/v1/fees/recommended"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Create a list of 10 fee levels based on the three provided by mempool.space
            fastestFee = data.get("fastestFee", 100)
            halfHourFee = data.get("halfHourFee", 50)
            hourFee = data.get("hourFee", 20)
            economyFee = data.get("economyFee", 10) if "economyFee" in data else hourFee // 2
            minimumFee = data.get("minimumFee", 1) if "minimumFee" in data else 1
            
            # Generate 10 fee levels
            fee_percentiles = [
                minimumFee,
                economyFee,
                (economyFee + hourFee) // 2,
                hourFee,
                (hourFee + halfHourFee) // 2,
                halfHourFee,
                (halfHourFee + fastestFee) // 2,
                fastestFee,
                int(fastestFee * 1.2),
                int(fastestFee * 1.5)
            ]
            
            return fee_percentiles
        except requests.RequestException as e:
            print(f"Error fetching fee data from MemPool: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

# Initialize API service - prefer mempool.space as it's more reliable for free usage
api_service = MemPoolAPI()

# For fallback, keep the mock data
MOCK_DATA = {
    "balance": {
        "confirmed": 1250000,  # in satoshis
        "unconfirmed": 0
    },
    "utxos": [
        {
            "txid": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
            "vout": 0,
            "value": 1000000,  # in satoshis
            "confirmations": 6
        },
        {
            "txid": "z6y5x4w3v2u1t0s9r8q7p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1",
            "vout": 1,
            "value": 250000,  # in satoshis
            "confirmations": 3
        }
    ],
    "fee_percentiles": [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]  # Simplified for example
}

@app.post("/ask")
async def ask(request: QuestionRequest):
    question = request.question
    session_id = request.session_id or "default_session"
    
    class DummyCtx:
        logger = type("logger", (), {"info": print, "error": print})()

    # Run process_query with the session ID
    answer = await process_query(question, DummyCtx(), session_id)
    return {"answer": answer, "session_id": session_id}

# Add a new endpoint to explicitly set the "current wallet"
@app.post("/set-current-wallet")
async def set_current_wallet(request: Request):
    data = await request.json()
    address = data.get("address")
    session_id = data.get("session_id", "default_session")
    
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    # Store in both the agent's memory and our local session storage
    wallet_memory.remember_wallet(session_id, address)
    session_wallets[session_id] = address
    
    return {
        "status": "success", 
        "message": f"Wallet {address} set as current wallet for session {session_id}", 
        "address": address, 
        "session_id": session_id
    }

# Add endpoint to get the current wallet
@app.get("/get-current-wallet")
async def get_current_wallet(session_id: str = "default_session"):
    # Try to get from our local storage first
    address = session_wallets.get(session_id)
    
    # If not found, try the agent's memory
    if not address and wallet_memory.has_wallet(session_id):
        address = wallet_memory.get_wallet(session_id)
        # Sync it to our local storage
        session_wallets[session_id] = address
    
    if not address:
        return {"status": "not_found", "message": "No wallet set for this session"}
    
    return {"status": "success", "address": address, "session_id": session_id}

@app.post("/get-balance")
async def get_balance(request: Request):
    data = await request.json()
    address = data.get("address")
    session_id = data.get("session_id", "default_session")
    
    # If no address provided, try to use the saved one
    if not address:
        if session_id in session_wallets:
            address = session_wallets[session_id]
        elif wallet_memory.has_wallet(session_id):
            address = wallet_memory.get_wallet(session_id)
        else:
            raise HTTPException(status_code=400, detail="No address provided and no saved wallet found")
    else:
        # Remember this address for future use
        wallet_memory.remember_wallet(session_id, address)
        session_wallets[session_id] = address
    
    print(f"Getting balance for address: {address} (session: {session_id})")
    
    try:
        # Try to get real data from API
        balance_data = api_service.get_balance(address)
        return balance_data
    except Exception as e:
        print(f"Error getting balance: {str(e)}")
        # Fallback to mock data if API fails
        return MOCK_DATA["balance"]

@app.post("/get-utxos")
async def get_utxos(request: Request):
    data = await request.json()
    address = data.get("address")
    session_id = data.get("session_id", "default_session")
    
    # If no address provided, try to use the saved one
    if not address:
        if session_id in session_wallets:
            address = session_wallets[session_id]
        elif wallet_memory.has_wallet(session_id):
            address = wallet_memory.get_wallet(session_id)
        else:
            raise HTTPException(status_code=400, detail="No address provided and no saved wallet found")
    else:
        # Remember this address for future use
        wallet_memory.remember_wallet(session_id, address)
        session_wallets[session_id] = address
    
    print(f"Getting UTXOs for address: {address} (session: {session_id})")
    
    try:
        # Try to get real data from API
        utxo_data = api_service.get_utxos(address)
        return utxo_data
    except Exception as e:
        print(f"Error getting UTXOs: {str(e)}")
        # Fallback to mock data if API fails
        return MOCK_DATA["utxos"]

@app.post("/get-current-fee-percentiles")
async def get_current_fee_percentiles():
    try:
        # Try to get real data from API
        fee_data = api_service.get_fee_percentiles()
        return fee_data
    except Exception as e:
        print(f"Error getting fee percentiles: {str(e)}")
        # Fallback to mock data if API fails
        return MOCK_DATA["fee_percentiles"]

# Add new endpoint to generate a wallet address
@app.post("/generate-wallet")
async def generate_wallet():
    """
    Generate a new Bitcoin wallet address
    This is just a placeholder that returns a mock wallet.
    In production, you would use a secure method to generate wallets.
    """
    # This is a simplified mock - in real applications you would 
    # generate proper wallets using a crypto library
    mock_wallet = {
        "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
        "privateKey": "[REDACTED]",  # Never return real private keys
        "publicKey": "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
        "type": "P2WPKH",
        "network": "mainnet"
    }
    return mock_wallet

@app.get("/search-address/{address}")
async def search_address(address: str, session_id: str = "default_session"):
    """
    Search for information about a Bitcoin address
    This endpoint combines data from multiple sources for a comprehensive view
    """
    # Remember this address for future use
    wallet_memory.remember_wallet(session_id, address)
    session_wallets[session_id] = address
    
    try:
        # Get basic balance data
        balance_data = api_service.get_balance(address)
        
        # Get UTXO data
        utxo_data = api_service.get_utxos(address)
        
        # Calculate total value in UTXOs
        total_utxo_value = sum(utxo.get("value", 0) for utxo in utxo_data)
        
        # Format results
        result = {
            "address": address,
            "balance": balance_data,
            "utxo_count": len(utxo_data),
            "total_utxo_value": total_utxo_value,
            "sample_utxos": utxo_data[:5] if len(utxo_data) > 5 else utxo_data
        }
        
        return result
    except Exception as e:
        print(f"Error searching address: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching address: {str(e)}")

@app.get("/search-current-wallet")
async def search_current_wallet(session_id: str = "default_session"):
    """
    Search for information about the current saved wallet
    """
    # Get the current wallet address
    if session_id in session_wallets:
        address = session_wallets[session_id]
    elif wallet_memory.has_wallet(session_id):
        address = wallet_memory.get_wallet(session_id)
    else:
        raise HTTPException(status_code=400, detail="No saved wallet found for this session")
    
    # Redirect to the regular search endpoint
    return await search_address(address, session_id)

@app.get("/address-activity/{address}")
async def address_activity(address: str, session_id: str = "default_session"):
    """
    Get activity summary for a Bitcoin address
    """
    # Remember this address for future use
    wallet_memory.remember_wallet(session_id, address)
    session_wallets[session_id] = address
    
    try:
        # Call the blockchain.com API for transaction history
        # This API is just an example - consider rate limits in production
        url = f"https://blockchain.info/rawaddr/{address}?limit=5"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract recent transactions
        transactions = []
        for tx in data.get("txs", [])[:5]:  # Limit to 5 most recent
            # Determine if this transaction is sending or receiving
            inputs = [inp for inp in tx.get("inputs", []) 
                      if inp.get("prev_out", {}).get("addr") == address]
            outputs = [out for out in tx.get("out", []) 
                       if out.get("addr") == address]
            
            # Calculate values
            input_value = sum(inp.get("prev_out", {}).get("value", 0) for inp in inputs)
            output_value = sum(out.get("value", 0) for out in outputs)
            
            # Determine transaction type
            tx_type = "unknown"
            if input_value > 0 and output_value > 0:
                tx_type = "self"
            elif input_value > 0:
                tx_type = "sent"
            elif output_value > 0:
                tx_type = "received"
            
            # Net change for this address
            net_change = output_value - input_value
            
            transactions.append({
                "txid": tx.get("hash", ""),
                "time": tx.get("time", 0),
                "type": tx_type,
                "net_change": net_change,
                "confirmations": tx.get("block_height", 0)
            })
        
        return {
            "address": address,
            "n_tx": data.get("n_tx", 0),
            "total_received": data.get("total_received", 0),
            "total_sent": data.get("total_sent", 0),
            "final_balance": data.get("final_balance", 0),
            "recent_transactions": transactions
        }
    except Exception as e:
        print(f"Error getting address activity: {str(e)}")
        # Return simplified response if API fails
        return {
            "address": address,
            "error": f"Could not retrieve transaction data: {str(e)}"
        }

@app.get("/current-wallet-activity")
async def current_wallet_activity(session_id: str = "default_session"):
    """
    Get activity summary for the current saved wallet
    """
    # Get the current wallet address
    if session_id in session_wallets:
        address = session_wallets[session_id]
    elif wallet_memory.has_wallet(session_id):
        address = wallet_memory.get_wallet(session_id)
    else:
        raise HTTPException(status_code=400, detail="No saved wallet found for this session")
    
    # Redirect to the regular activity endpoint
    return await address_activity(address, session_id)

if __name__ == "__main__":
    print("Starting API Gateway on http://0.0.0.0:8083")
    uvicorn.run(app, host="0.0.0.0", port=8083)