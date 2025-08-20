#!/usr/bin/env python3
"""
Combined Ethereum API service that tries Blockchair first and falls back to Etherscan
"""

from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import requests
import time

# Import both API implementations
from etherscan_api import EtherscanAPI

class CombinedEthereumAPI:
    """Combined API service that falls back to alternative APIs when one fails"""
    
    def __init__(self, blockchair_api=None, etherscan_api=None):
        """Initialize with both API implementations"""
        self.blockchair_api = blockchair_api
        self.etherscan_api = etherscan_api or EtherscanAPI()
        
    def get_balance(self, address: str) -> Dict[str, Any]:
        """Get Ethereum account balance with fallback"""
        try:
            # Try BlockchairAPI first
            if self.blockchair_api:
                try:
                    return self.blockchair_api.get_balance(address)
                except Exception as e:
                    print(f"Blockchair API failed for Ethereum balance, error: {str(e)}")
                    # If this is a 430 error (rate limit) sleep for a moment before falling back
                    if "430" in str(e) or "blacklist" in str(e).lower():
                        print("Blockchair API is rate limiting, falling back to Etherscan API")
                        time.sleep(1)  # Short delay to avoid rapid successive API calls
            
            # Fall back to EtherscanAPI
            return self.etherscan_api.get_balance(address)
            
        except Exception as e:
            print(f"All API services failed for Ethereum balance: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch Ethereum balance: {str(e)}")
    
    def get_ethereum_tokens(self, address: str) -> List[Dict[str, Any]]:
        """Get ERC-20 token balances with fallback"""
        try:
            # Try BlockchairAPI first
            if self.blockchair_api:
                try:
                    return self.blockchair_api.get_ethereum_tokens(address)
                except Exception as e:
                    print(f"Blockchair API failed for Ethereum tokens, error: {str(e)}")
                    # If this is a 430 error (rate limit) sleep for a moment before falling back
                    if "430" in str(e) or "blacklist" in str(e).lower():
                        print("Blockchair API is rate limiting, falling back to Etherscan API")
                        time.sleep(1)  # Short delay to avoid rapid successive API calls
            
            # Fall back to EtherscanAPI
            return self.etherscan_api.get_token_balances(address)
            
        except Exception as e:
            print(f"All API services failed for Ethereum tokens: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch Ethereum tokens: {str(e)}")
    
    def _get_eth_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Ethereum transactions with fallback"""
        try:
            # Try BlockchairAPI first
            if self.blockchair_api:
                try:
                    return self.blockchair_api._get_eth_transactions(address, limit)
                except Exception as e:
                    print(f"Blockchair API failed for Ethereum transactions, error: {str(e)}")
                    # If this is a 430 error (rate limit) sleep for a moment before falling back
                    if "430" in str(e) or "blacklist" in str(e).lower():
                        print("Blockchair API is rate limiting, falling back to Etherscan API")
                        time.sleep(1)  # Short delay to avoid rapid successive API calls
            
            # Fall back to EtherscanAPI
            return self.etherscan_api.get_transactions(address, limit)
            
        except Exception as e:
            print(f"All API services failed for Ethereum transactions: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch Ethereum transactions: {str(e)}")
    
    def get_ethereum_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get Ethereum transaction details with fallback"""
        try:
            # Try BlockchairAPI first
            if self.blockchair_api:
                try:
                    return self.blockchair_api.get_ethereum_transaction(tx_hash)
                except Exception as e:
                    print(f"Blockchair API failed for Ethereum transaction, error: {str(e)}")
                    # If this is a 430 error (rate limit) sleep for a moment before falling back
                    if "430" in str(e) or "blacklist" in str(e).lower():
                        print("Blockchair API is rate limiting, falling back to Etherscan API")
                        time.sleep(1)  # Short delay to avoid rapid successive API calls
            
            # Fall back to EtherscanAPI
            return self.etherscan_api.get_transaction(tx_hash)
            
        except Exception as e:
            print(f"All API services failed for Ethereum transaction: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch Ethereum transaction: {str(e)}")
