#!/usr/bin/env python3
"""
Debug script for Etherscan token balances
"""

import sys
import os
import json
import requests
import time

# Import Etherscan API
from etherscan_api import EtherscanAPI

def debug_token_fetch():
    """Debug token balance fetching"""
    print("Debugging Etherscan token balance fetching...")
    
    # Create EtherscanAPI instance
    etherscan = EtherscanAPI()
    
    # Use a known address with tokens - Vitalik's wallet
    test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    # Step 1: Print API key (first few chars)
    api_key = etherscan.api_key
    masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "None"
    print(f"Using API key: {masked_key}")
    
    # Step 2: Test the token transaction endpoint directly
    print("\nStep 2: Testing token transaction endpoint directly...")
    tokentx_params = {
        "module": "account",
        "action": "tokentx",
        "address": test_address,
        "page": 1,
        "offset": 5,  # Only get 5 for debugging
        "sort": "desc",
        "apikey": etherscan.api_key
    }
    
    try:
        response = requests.get(etherscan.BASE_URL, params=tokentx_params)
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        print(f"Message: {data.get('message')}")
        
        if data.get("status") == "1":
            token_txs = data.get("result", [])
            print(f"Found {len(token_txs)} token transactions")
            
            if token_txs:
                # Print the first token transaction
                first_tx = token_txs[0]
                print("\nFirst token transaction:")
                print(f"  Token Name: {first_tx.get('tokenName')}")
                print(f"  Token Symbol: {first_tx.get('tokenSymbol')}")
                print(f"  Token Address: {first_tx.get('contractAddress')}")
                print(f"  Token Decimal: {first_tx.get('tokenDecimal')}")
                
                # Step 3: Test token balance endpoint for this token
                print("\nStep 3: Testing token balance endpoint for this token...")
                token_address = first_tx.get('contractAddress')
                
                balance_params = {
                    "module": "account",
                    "action": "tokenbalance",
                    "contractaddress": token_address,
                    "address": test_address,
                    "tag": "latest",
                    "apikey": etherscan.api_key
                }
                
                balance_resp = requests.get(etherscan.BASE_URL, params=balance_params)
                balance_data = balance_resp.json()
                print(f"Balance response: {json.dumps(balance_data, indent=2)}")
                
                if balance_data.get("status") == "1":
                    balance_raw = int(balance_data.get("result", "0"))
                    token_decimals = int(first_tx.get("tokenDecimal", 18))
                    balance = float(balance_raw) / (10 ** token_decimals)
                    
                    print(f"Token balance (raw): {balance_raw}")
                    print(f"Token balance (formatted): {balance}")
                else:
                    print(f"Error getting token balance: {balance_data.get('message')}")
                    
                    # Step 4: Try alternative endpoint
                    print("\nStep 4: Trying alternative endpoint (tokenbalancelist)...")
                    alt_params = {
                        "module": "account",
                        "action": "tokenlist",
                        "address": test_address,
                        "apikey": etherscan.api_key
                    }
                    
                    alt_resp = requests.get(etherscan.BASE_URL, params=alt_params)
                    alt_data = alt_resp.json()
                    print(f"Alternative response: {json.dumps(alt_data, indent=2)}")
        else:
            print(f"Error: {data.get('message')}")
            
    except Exception as e:
        print(f"Error testing token endpoint: {str(e)}")
    
    # Step 5: Test the full method
    print("\nStep 5: Testing get_token_balances method...")
    try:
        tokens = etherscan.get_token_balances(test_address)
        print(f"Found {len(tokens)} tokens with balances")
        if tokens:
            print("First token:")
            print(json.dumps(tokens[0], indent=2))
    except Exception as e:
        print(f"Error in get_token_balances: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_token_fetch()
