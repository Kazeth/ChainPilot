#!/usr/bin/env python3
"""
Ethereum-specific API endpoints for ChainPilot
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List, Optional
import requests
import json

# Initialize the API router
router = APIRouter(prefix="/ethereum", tags=["ethereum"])

@router.get("/account/{address}")
async def get_ethereum_account(address: str, session_id: str = "default_session"):
    """
    Get Ethereum account information
    """
    # Import BlockchairAPI only when needed to avoid circular imports
    from api_gateway import ethereum_api_service
    
    # Validate Ethereum address format
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
    
    try:
        # Get basic account info
        account_info = ethereum_api_service.get_balance(address)
        
        # Format the response
        result = {
            "address": address,
            "balance_wei": account_info.get("confirmed", 0),
            "balance_eth": account_info.get("balance_eth", 0),
            "transaction_count": account_info.get("transaction_count", 0),
            "total_received": account_info.get("total_received", 0),
            "total_sent": account_info.get("total_sent", 0),
            "currency": "ETH"
        }
        
        return result
    except Exception as e:
        print(f"Error fetching Ethereum account: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Ethereum account: {str(e)}")

@router.get("/tokens/{address}")
async def get_ethereum_tokens(address: str, session_id: str = "default_session"):
    """
    Get Ethereum ERC-20 token balances for an address
    """
    # Import BlockchairAPI only when needed to avoid circular imports
    from api_gateway import ethereum_api_service
    
    # Validate Ethereum address format
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
    
    try:
        # Get token balances
        tokens = ethereum_api_service.get_token_balances(address)
        
        # Format the response
        result = {
            "address": address,
            "token_count": len(tokens),
            "tokens": tokens
        }
        
        return result
    except Exception as e:
        print(f"Error fetching Ethereum tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Ethereum tokens: {str(e)}")

@router.get("/transaction/{tx_hash}")
async def get_ethereum_transaction(tx_hash: str):
    """
    Get details for a specific Ethereum transaction
    """
    # Import BlockchairAPI only when needed to avoid circular imports
    from api_gateway import ethereum_api_service
    
    # Validate Ethereum transaction hash format
    if not tx_hash.startswith("0x"):
        tx_hash = "0x" + tx_hash  # Add 0x prefix if missing
        
    if len(tx_hash) != 66:
        raise HTTPException(status_code=400, detail="Invalid Ethereum transaction hash format")
    
    try:
        # Get transaction details
        transaction = ethereum_api_service.get_transaction(tx_hash)
        
        return transaction
    except Exception as e:
        print(f"Error fetching Ethereum transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Ethereum transaction: {str(e)}")

@router.get("/transactions/{address}")
async def get_ethereum_transactions(
    address: str, 
    limit: int = 10, 
    offset: int = 0,
    session_id: str = "default_session"
):
    """
    Get recent Ethereum transactions for an address
    """
    # Import BlockchairAPI only when needed to avoid circular imports
    from api_gateway import ethereum_api_service
    
    # Validate Ethereum address format
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
    
    try:
        # Get transactions
        transactions = ethereum_api_service.get_transactions(address, limit)
        
        # Format the response
        result = {
            "address": address,
            "transaction_count": len(transactions),
            "transactions": transactions
        }
        
        return result
    except Exception as e:
        print(f"Error fetching Ethereum transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Ethereum transactions: {str(e)}")
