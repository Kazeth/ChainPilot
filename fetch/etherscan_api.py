#!/usr/bin/env python3
"""
Etherscan API client for Ethereum blockchain data
"""

import requests
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

class EtherscanAPI:
    """Implementation using Etherscan API for Ethereum blockchain data"""
    
    # Base URL for Etherscan API (mainnet)
    BASE_URL = "https://api.etherscan.io/v2/api"
    
    def __init__(self, api_key: Optional[str] = None):
        # Free API key with 5 calls per second rate limit
        # Get your own API key at https://etherscan.io/apis
        self.api_key = api_key or "MIWU92VZ2HJ6M3TNZNID871477URI8PJHG"
    
    def get_balance(self, address: str) -> Dict[str, Any]:
        """Get Ethereum account balance"""
        url = self.BASE_URL
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                error_msg = data.get("message", "Unknown error")
                print(f"Etherscan API error: {error_msg}")
                raise HTTPException(status_code=400, detail=f"Failed to fetch Ethereum balance: {error_msg}")
            
            # Get transaction count
            tx_count_params = {
                "module": "proxy",
                "action": "eth_getTransactionCount",
                "address": address,
                "tag": "latest",
                "apikey": self.api_key
            }
            tx_count_resp = requests.get(url, params=tx_count_params)
            tx_count_resp.raise_for_status()
            tx_count_data = tx_count_resp.json()
            tx_count = int(tx_count_data.get("result", "0x0"), 16) if tx_count_data.get("status") == "1" else 0
            
            # Format the response
            balance_wei = int(data.get("result", 0))
            return {
                "confirmed": balance_wei,
                "unconfirmed": 0,  # Ethereum doesn't have unconfirmed balance concept
                "total_received": 0,  # Not directly available via Etherscan simple API
                "total_sent": 0,     # Not directly available via Etherscan simple API
                "transaction_count": tx_count,
                "balance_eth": float(balance_wei) / 1e18,  # Convert Wei to ETH
                "currency": "ETH"
            }
        except requests.RequestException as e:
            print(f"Error fetching Ethereum balance from Etherscan: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_token_balances(self, address: str) -> List[Dict[str, Any]]:
        """Get ERC-20 token balances for an Ethereum address"""
        url = self.BASE_URL
        params = {
            "module": "account",
            "action": "tokentx",  # Token transfer events
            "address": address,
            "page": 1,
            "offset": 100,  # Get last 100 token transfers
            "sort": "desc",
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                if "No transactions found" in data.get("message", ""):
                    return []  # No token transactions
                error_msg = data.get("message", "Unknown error")
                print(f"Etherscan API error: {error_msg}")
                raise HTTPException(status_code=400, detail=f"Failed to fetch token data: {error_msg}")
            
            # Process token transfers to find unique tokens
            tokens = {}
            for tx in data.get("result", []):
                token_address = tx.get("contractAddress", "").lower()
                if token_address not in tokens:
                    # Check token balance
                    token_balance_params = {
                        "module": "account",
                        "action": "tokenbalance",
                        "contractaddress": token_address,
                        "address": address,
                        "tag": "latest",
                        "apikey": self.api_key
                    }
                    balance_resp = requests.get(url, params=token_balance_params)
                    balance_data = balance_resp.json()
                    
                    if balance_data.get("status") == "1":
                        balance_raw = int(balance_data.get("result", "0"))
                        if balance_raw > 0:  # Only include tokens with non-zero balance
                            token_name = tx.get("tokenName", "Unknown")
                            token_symbol = tx.get("tokenSymbol", "???")
                            token_decimals = int(tx.get("tokenDecimal", 18))
                            
                            tokens[token_address] = {
                                "name": token_name,
                                "symbol": token_symbol,
                                "balance": float(balance_raw) / (10 ** token_decimals),
                                "balance_raw": balance_raw,
                                "token_address": token_address,
                                "token_decimals": token_decimals
                            }
            
            return list(tokens.values())
        except requests.RequestException as e:
            print(f"Error fetching Ethereum tokens from Etherscan: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching token data: {str(e)}")
    
    def get_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Ethereum transactions for an address"""
        url = self.BASE_URL
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "page": 1,
            "offset": limit,
            "sort": "desc",
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1" and "No transactions found" not in data.get("message", ""):
                error_msg = data.get("message", "Unknown error")
                print(f"Etherscan API error: {error_msg}")
                raise HTTPException(status_code=400, detail=f"Failed to fetch transaction data: {error_msg}")
            
            result = []
            for tx in data.get("result", []):
                # Format transaction data
                result.append({
                    "tx_hash": tx.get("hash", ""),
                    "block_id": int(tx.get("blockNumber", 0)),
                    "time": tx.get("timeStamp", ""),
                    "from": tx.get("from", ""),
                    "to": tx.get("to", ""),
                    "value": float(tx.get("value", 0)) / 1e18,  # Convert Wei to ETH
                    "value_raw": tx.get("value", 0),
                    "gas_used": int(tx.get("gasUsed", 0)),
                    "gas_price": int(tx.get("gasPrice", 0)),
                    "fee": float(int(tx.get("gasUsed", 0)) * int(tx.get("gasPrice", 0))) / 1e18  # Gas * gasPrice in ETH
                })
            
            return result
        except requests.RequestException as e:
            print(f"Error fetching Ethereum transactions from Etherscan: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching transaction data: {str(e)}")
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get details for a specific Ethereum transaction"""
        url = self.BASE_URL
        params = {
            "module": "proxy",
            "action": "eth_getTransactionByHash",
            "txhash": tx_hash,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            tx_data = response.json()
            
            if tx_data.get("error") or not tx_data.get("result"):
                error_msg = tx_data.get("error", {}).get("message", "Transaction not found")
                print(f"Etherscan API error: {error_msg}")
                raise HTTPException(status_code=400, detail=f"Failed to fetch transaction: {error_msg}")
            
            # Get transaction receipt for more details
            receipt_params = {
                "module": "proxy",
                "action": "eth_getTransactionReceipt",
                "txhash": tx_hash,
                "apikey": self.api_key
            }
            receipt_resp = requests.get(url, params=receipt_params)
            receipt_resp.raise_for_status()
            receipt_data = receipt_resp.json()
            
            tx = tx_data.get("result", {})
            receipt = receipt_data.get("result", {})
            
            # Convert hex values to integers
            block_id = int(tx.get("blockNumber", "0x0"), 16) if tx.get("blockNumber") else 0
            gas_limit = int(tx.get("gas", "0x0"), 16)
            gas_price = int(tx.get("gasPrice", "0x0"), 16)
            gas_used = int(receipt.get("gasUsed", "0x0"), 16) if receipt else 0
            value_wei = int(tx.get("value", "0x0"), 16)
            
            # Get block info to get timestamp
            if block_id > 0:
                block_params = {
                    "module": "proxy",
                    "action": "eth_getBlockByNumber",
                    "tag": hex(block_id),
                    "boolean": "true",
                    "apikey": self.api_key
                }
                block_resp = requests.get(url, params=block_params)
                block_resp.raise_for_status()
                block_data = block_resp.json()
                block = block_data.get("result", {})
                timestamp = int(block.get("timestamp", "0x0"), 16) if block.get("timestamp") else 0
            else:
                timestamp = 0
            
            # Format the result
            result = {
                "hash": tx_hash,
                "block_id": block_id,
                "time": timestamp,
                "from": tx.get("from", ""),
                "to": tx.get("to", ""),
                "value": float(value_wei) / 1e18,  # Convert Wei to ETH
                "value_raw": value_wei,
                "gas_used": gas_used,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "fee": float(gas_used * gas_price) / 1e18,  # Gas used * gas price in ETH
                "status": "success" if receipt.get("status") == "0x1" else "failed",
                "calls": []  # Internal transactions would require another API call
            }
            
            return result
        except requests.RequestException as e:
            print(f"Error fetching Ethereum transaction from Etherscan: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching transaction data: {str(e)}")
            
    # Alias methods to match the naming conventions used elsewhere in the codebase
    def get_ethereum_tokens(self, address: str) -> List[Dict[str, Any]]:
        """Alias for get_token_balances to maintain compatibility"""
        return self.get_token_balances(address)
        
    def _get_eth_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Alias for get_transactions to maintain compatibility"""
        return self.get_transactions(address, limit)
        
    def get_ethereum_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Alias for get_transaction to maintain compatibility"""
        return self.get_transaction(tx_hash)
