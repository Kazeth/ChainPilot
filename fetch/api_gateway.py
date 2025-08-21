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

HEADERS = {
    "Content-Type": "application/json"
}  # Simplified headers

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
    """Implementation using Blockchair API with support for multiple chains (BTC, ETH)"""
    BASE_URL = "https://api.blockchair.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def _detect_chain(self, address: str) -> str:
        """
        Detect the blockchain type based on address format
        Returns: "bitcoin", "ethereum", etc.
        """
        # Check if address is an Ethereum address
        if address.startswith("0x") and len(address) == 42:
            return "ethereum"
        # Otherwise default to Bitcoin
        return "bitcoin"
        
    def get_balance(self, address: str) -> Dict[str, Any]:
        chain = self._detect_chain(address)
        url = f"{self.BASE_URL}/{chain}/dashboards/address/{address}"
        params = {"key": self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch balance data for {chain}")
                
            address_data = data.get("data", {}).get(address, {})
            address_info = address_data.get("address", {})
            
            # Format response based on chain type
            if chain == "ethereum":
                return {
                    "confirmed": int(address_info.get("balance", 0)),
                    "unconfirmed": 0,  # Ethereum doesn't have unconfirmed balance in the same way
                    "total_received": int(address_info.get("received", 0)),
                    "total_sent": int(address_info.get("spent", 0)),
                    "transaction_count": address_info.get("transaction_count", 0),
                    "balance_eth": float(address_info.get("balance", 0)) / 1e18,  # Convert Wei to ETH
                    "currency": "ETH"
                }
            else:  # Bitcoin
                return {
                    "confirmed": address_info.get("balance", 0),
                    "unconfirmed": address_info.get("unconfirmed_balance", 0),
                    "total_received": address_info.get("received", 0),
                    "total_sent": address_info.get("spent", 0),
                    "transaction_count": address_info.get("transaction_count", 0),
                    "currency": "BTC"
                }
        except requests.RequestException as e:
            print(f"Error fetching {chain} balance from Blockchair: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_ethereum_tokens(self, address: str) -> List[Dict[str, Any]]:
        """Get ERC-20 token balances for an Ethereum address"""
        chain = self._detect_chain(address)
        if chain != "ethereum":
            raise HTTPException(status_code=400, detail="Address is not a valid Ethereum address")
            
        url = f"{self.BASE_URL}/ethereum/dashboards/address/{address}"
        params = {"erc_20": "true", "key": self.api_key} if self.api_key else {"erc_20": "true"}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch token data")
                
            address_data = data.get("data", {}).get(address, {})
            token_data = address_data.get("layer_2", {}).get("erc_20", [])
            
            # Format token data
            tokens = []
            for token in token_data:
                tokens.append({
                    "name": token.get("token_name", "Unknown"),
                    "symbol": token.get("token_symbol", "???"),
                    "balance": float(token.get("balance", 0)) / (10 ** int(token.get("token_decimals", 18))),
                    "balance_raw": token.get("balance", 0),
                    "token_address": token.get("token_address", ""),
                    "token_decimals": token.get("token_decimals", 18)
                })
                
            return tokens
        except requests.RequestException as e:
            print(f"Error fetching Ethereum tokens from Blockchair: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching token data: {str(e)}")
    
    def _get_eth_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent Ethereum transactions for an address"""
        url = f"{self.BASE_URL}/ethereum/dashboards/address/{address}"
        params = {"limit": limit, "key": self.api_key} if self.api_key else {"limit": limit}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch Ethereum transactions")
                
            address_data = data.get("data", {}).get(address, {})
            transactions = address_data.get("calls", [])
            
            result = []
            for tx in transactions:
                result.append({
                    "tx_hash": tx.get("transaction_hash", ""),
                    "block_id": tx.get("block_id", 0),
                    "time": tx.get("time", ""),
                    "from": tx.get("sender", ""),
                    "to": tx.get("recipient", ""),
                    "value": float(tx.get("value", 0)) / 1e18,  # Convert Wei to ETH
                    "value_raw": tx.get("value", 0),
                    "gas_used": tx.get("gas_used", 0),
                    "gas_price": tx.get("gas_price", 0),
                    "fee": float(tx.get("fee", 0)) / 1e18  # Convert Wei to ETH
                })
                
            return result
        except requests.RequestException as e:
            print(f"Error fetching Ethereum transactions from Blockchair: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching transaction data: {str(e)}")
    
    def get_ethereum_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get details for a specific Ethereum transaction"""
        url = f"{self.BASE_URL}/ethereum/dashboards/transaction/{tx_hash}"
        params = {"key": self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch Ethereum transaction")
                
            tx_data = data.get("data", {}).get(tx_hash, {})
            transaction = tx_data.get("transaction", {})
            calls = tx_data.get("calls", [])
            
            # Main transaction details
            result = {
                "hash": tx_hash,
                "block_id": transaction.get("block_id", 0),
                "time": transaction.get("time", ""),
                "from": transaction.get("sender", ""),
                "to": transaction.get("recipient", ""),
                "value": float(transaction.get("value", 0)) / 1e18,  # Convert Wei to ETH
                "value_raw": transaction.get("value", 0),
                "gas_used": transaction.get("gas_used", 0),
                "gas_limit": transaction.get("gas_limit", 0),
                "gas_price": transaction.get("gas_price", 0),
                "fee": float(transaction.get("fee", 0)) / 1e18,  # Convert Wei to ETH
                "status": transaction.get("status", ""),
                "calls": []
            }
            
            # Add call details if available
            for call in calls:
                result["calls"].append({
                    "call_id": call.get("call_id", ""),
                    "from": call.get("sender", ""),
                    "to": call.get("recipient", ""),
                    "value": float(call.get("value", 0)) / 1e18,  # Convert Wei to ETH
                    "input": call.get("input", ""),
                    "gas_used": call.get("gas_used", 0)
                })
                
            return result
        except requests.RequestException as e:
            print(f"Error fetching Ethereum transaction from Blockchair: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching transaction data: {str(e)}")
    
    def get_utxos(self, address: str) -> List[Dict[str, Any]]:
        chain = self._detect_chain(address)
        
        # For Ethereum, return transactions instead of UTXOs
        if chain == "ethereum":
            return self._get_eth_transactions(address)
        
        # For Bitcoin, continue with UTXO logic
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
    
    def _get_eth_transactions(self, address: str) -> List[Dict[str, Any]]:
        """Get recent Ethereum transactions for an address"""
        url = f"{self.BASE_URL}/ethereum/dashboards/address/{address}"
        params = {
            "key": self.api_key if self.api_key else {},
            "limit": 10  # Limit to 10 most recent transactions
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch Ethereum transaction data")
            
            address_data = data.get("data", {}).get(address, {})
            transactions = address_data.get("calls", [])
            
            formatted_txs = []
            for tx in transactions:
                formatted_txs.append({
                    "txid": tx.get("transaction_hash", ""),
                    "block_id": tx.get("block_id", 0),
                    "timestamp": tx.get("time", 0),
                    "value": tx.get("value", 0),
                    "value_eth": float(tx.get("value", 0)) / 1e18,  # Convert Wei to ETH
                    "from": tx.get("sender", ""),
                    "to": tx.get("recipient", ""),
                    "type": "sent" if tx.get("sender", "").lower() == address.lower() else "received",
                    "currency": "ETH"
                })
            
            return formatted_txs
        except requests.RequestException as e:
            print(f"Error fetching Ethereum transactions from Blockchair: {str(e)}")
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
    
    def get_eth_token_balances(self, address: str) -> List[Dict[str, Any]]:
        """Get ERC20 token balances for an Ethereum address"""
        url = f"{self.BASE_URL}/ethereum/dashboards/address/{address}"
        params = {"key": self.api_key, "erc_20": "true"} if self.api_key else {"erc_20": "true"}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("context", {}).get("code") != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch Ethereum token data")
                
            address_data = data.get("data", {}).get(address, {})
            tokens = address_data.get("layer_2", {}).get("erc_20", [])
            
            formatted_tokens = []
            for token in tokens:
                # Filter out zero balances
                if float(token.get("balance", 0)) > 0:
                    formatted_tokens.append({
                        "token_name": token.get("token_name", "Unknown"),
                        "token_symbol": token.get("token_symbol", "???"),
                        "token_address": token.get("token_address", ""),
                        "balance_raw": token.get("balance", "0"),
                        "balance": float(token.get("balance", "0")) / (10 ** int(token.get("token_decimals", 18))),
                        "token_decimals": int(token.get("token_decimals", 18))
                    })
            
            return formatted_tokens
        except requests.RequestException as e:
            print(f"Error fetching Ethereum token balances from Blockchair: {str(e)}")
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

class ICPLedgerAPI(BlockchainAPIService):
    """Implementation using Internet Computer Protocol Ledger API"""
    BASE_URL = "https://ledger-api.internetcomputer.org"
    
    def get_balance(self, address: str) -> Dict[str, Any]:
        """Get balance for an ICP account"""
        url = f"{self.BASE_URL}/accounts/{address}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Convert e8s (ICP's smallest unit) to ICP for display
            e8s_balance = int(data.get("balance", 0))
            icp_balance = e8s_balance / 100000000  # 1 ICP = 10^8 e8s
            
            return {
                "confirmed": e8s_balance,
                "unconfirmed": 0,  # ICP doesn't have unconfirmed balance concept
                "balance_e8s": e8s_balance,
                "balance_icp": icp_balance,
                "transaction_count": int(data.get("transaction_count", 0)),
                "updated_at": data.get("updated_at", 0),
                "currency": "ICP"
            }
        except requests.RequestException as e:
            print(f"Error fetching balance from ICP Ledger: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Get transactions for an ICP account"""
        # ICP doesn't use UTXOs, but we'll get transactions instead
        # Using the correct format: /accounts/{account_id}/transactions with query parameters
        url = f"{self.BASE_URL}/accounts/{address}/transactions"
        params = {
            "from_account": address,
            "to_account": address,
            "limit": 20,
            "offset": 0,
            "sort_by": "-block_height"  # Most recent first
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            blocks = data.get("blocks", [])
            
            # Format transactions in a UTXO-like format for compatibility
            formatted_txs = []
            for tx in blocks:
                # Get transaction details
                tx_hash = tx.get("transaction_hash", "")
                tx_type = tx.get("transfer_type", "TRANSFER") # Default to TRANSFER
                
                formatted_tx = {
                    "txid": tx_hash,
                    "height": tx.get("block_height", 0),
                    "timestamp": tx.get("created_at", 0),
                    "type": tx_type,
                    "amount_e8s": tx.get("amount", 0),
                    "fee_e8s": tx.get("fee", 0)
                }
                
                # Add from/to if available
                if "from_account_identifier" in tx:
                    formatted_tx["from"] = tx["from_account_identifier"]
                if "to_account_identifier" in tx:
                    formatted_tx["to"] = tx["to_account_identifier"]
                
                # Add memo if available
                if "memo" in tx:
                    formatted_tx["memo"] = tx["memo"]
                
                formatted_txs.append(formatted_tx)
            
            return formatted_txs
        except requests.RequestException as e:
            print(f"Error fetching transactions from ICP Ledger: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_fee_percentiles(self) -> List[float]:
        """Get fee information for ICP"""
        # Get standard fee from the /info endpoint
        url = f"{self.BASE_URL}/info"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Standard fee is usually fixed in ICP
            standard_fee = data.get("standard_fee", 10000)  # Default to 10000 e8s
            return [standard_fee]  # Return as list for compatibility
        except requests.RequestException as e:
            print(f"Error fetching fee info from ICP Ledger: {str(e)}")
            # Default value if API fails
            return [10000]  # Standard fee in e8s
    
    def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get detailed account information"""
        # First, validate the account address format
        if not self._is_valid_account_id(address):
            raise HTTPException(status_code=400, detail=f"Invalid ICP account ID format: {address}")
            
        # Updated to use the correct endpoint based on the API documentation
        account_url = f"{self.BASE_URL}/accounts/{address}"
        
        try:
            # Get account information
            account_response = requests.get(account_url)
            account_response.raise_for_status()
            account_data = account_response.json()
            
            # Convert e8s to ICP
            e8s_balance = int(account_data.get("balance", 0))
            icp_balance = e8s_balance / 100000000  # 1 ICP = 10^8 e8s
            
            result = {
                "address": address,
                "account_identifier": account_data.get("account_identifier", address),
                "balance_e8s": e8s_balance,
                "balance_icp": icp_balance,
                "transaction_count": int(account_data.get("transaction_count", 0)),
                "updated_at": account_data.get("updated_at", 0)
            }
            
            # Try to get transactions if needed
            try:
                transactions_url = f"{self.BASE_URL}/accounts/{address}/transactions"
                tx_response = requests.get(transactions_url)
                if tx_response.status_code == 200:
                    tx_data = tx_response.json()
                    transactions = tx_data.get("transactions", [])
                    result["recent_transactions"] = transactions[:5] if transactions else []
            except Exception as tx_error:
                print(f"Note: Could not fetch transactions: {str(tx_error)}")
                # Continue even if transactions fetch fails
                
            return result
        except requests.RequestException as e:
            print(f"Error fetching account info from ICP Ledger: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
            
    def _is_valid_account_id(self, address: str) -> bool:
        """Validate ICP account ID format
        ICP accounts can be in principal ID format or account ID format
        """
        # Simple validation - more comprehensive validation would involve checking
        # principal ID format and account ID format with proper checksums
        return len(address) >= 25 and len(address) <= 64
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get details for a specific transaction (supports both BTC and ICP)
        """
        # Check if this looks like a Bitcoin transaction hash
        if len(tx_hash) == 64 and all(c in "0123456789abcdefABCDEF" for c in tx_hash):
            # This is likely a Bitcoin transaction hash, try blockchain.info API
            try:
                btc_url = f"https://blockchain.info/rawtx/{tx_hash}"
                btc_response = requests.get(btc_url)
                btc_response.raise_for_status()
                btc_data = btc_response.json()
                
                # Add a flag to indicate this is a Bitcoin transaction
                btc_data["currency"] = "BTC"
                return btc_data
            except requests.RequestException as e:
                # If blockchain.info fails, try mempool.space
                try:
                    mempool_url = f"https://mempool.space/api/tx/{tx_hash}"
                    mempool_response = requests.get(mempool_url)
                    mempool_response.raise_for_status()
                    mempool_data = mempool_response.json()
                    
                    # Add a flag to indicate this is a Bitcoin transaction
                    mempool_data["currency"] = "BTC"
                    return mempool_data
                except requests.RequestException as mempool_error:
                    # If both Bitcoin APIs fail, continue to try ICP API
                    pass
        
        # Try ICP API - could be an ICP transaction hash or query by height
        try:
            # First try by hash
            tx_url = f"{self.BASE_URL}/transactions/{tx_hash}"
            response = requests.get(tx_url)
            response.raise_for_status()
            icp_data = response.json()
            
            # Add a flag to indicate this is an ICP transaction
            icp_data["currency"] = "ICP"
            return icp_data
        except requests.RequestException as tx_error:
            # If hash lookup fails, try as a block height
            try:
                # Check if tx_hash is a number (block height)
                if tx_hash.isdigit():
                    block_url = f"{self.BASE_URL}/blocks/{tx_hash}"
                    block_response = requests.get(block_url)
                    block_response.raise_for_status()
                    block_data = block_response.json()
                    
                    # Add a flag to indicate this is an ICP block
                    block_data["currency"] = "ICP"
                    block_data["is_block"] = True
                    return block_data
            except requests.RequestException as block_error:
                pass
            
            # If we've reached here, neither Bitcoin nor ICP lookups succeeded
            # Try one more time with blockchain.info raw block
            if tx_hash.isdigit():
                try:
                    btc_block_url = f"https://blockchain.info/rawblock/{tx_hash}"
                    btc_block_response = requests.get(btc_block_url)
                    btc_block_response.raise_for_status()
                    btc_block_data = btc_block_response.json()
                    
                    btc_block_data["currency"] = "BTC"
                    btc_block_data["is_block"] = True
                    return btc_block_data
                except requests.RequestException:
                    pass
            
            # All attempts failed
            error_msg = f"Failed to find transaction or block with ID: {tx_hash}"
            print(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
    
    def get_blocks(self, start: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get blocks from the ICP ledger"""
        url = f"{self.BASE_URL}/blocks"
        params = {"start": start, "limit": limit}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("blocks", [])
        except requests.RequestException as e:
            print(f"Error fetching blocks from ICP Ledger: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get ICP blockchain statistics"""
        url = f"{self.BASE_URL}/stats"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Add some computed metrics
            if "total_transactions" in data and "total_accounts" in data:
                data["avg_transactions_per_account"] = data["total_transactions"] / data["total_accounts"] if data["total_accounts"] > 0 else 0
                
            return data
        except requests.RequestException as e:
            print(f"Error fetching blockchain stats from ICP Ledger: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
            
    def get_latest_blocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get latest blocks from the ICP ledger"""
        # For latest blocks, we use start=0 (most recent block)
        return self.get_blocks(0, limit)
    
    def get_neuron_info(self, neuron_id: str) -> Dict[str, Any]:
        """Get information about an ICP neuron (staking)"""
        url = f"{self.BASE_URL}/neurons/{neuron_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching neuron info from ICP Ledger: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
            
    def get_canister_info(self, canister_id: str) -> Dict[str, Any]:
        """Get information about an ICP canister"""
        url = f"{self.BASE_URL}/canisters/{canister_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching canister info from ICP Ledger: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    
    def query_transactions(self, 
                          account_id: str,
                          from_account: Optional[str] = None,
                          to_account: Optional[str] = None,
                          transfer_type: Optional[str] = None,
                          max_block_index: Optional[int] = None,
                          limit: int = 10,
                          offset: int = 0,
                          sort_by: str = "-block_height") -> Dict[str, Any]:
        """
        Query transactions for a specific account with multiple filters based on the ICP Ledger API
        
        Args:
            account_id: The account identifier to query transactions for
            from_account: Filter by source account
            to_account: Filter by destination account
            transfer_type: Filter by transfer type (comma-separated: mint,burn,transfer)
            max_block_index: Maximum block index to include
            limit: Maximum number of results to return
            offset: Number of results to skip
            sort_by: Sort order (e.g. transfer_type,-block_height)
            
        Returns:
            Dict with total count and list of transaction blocks
        """
        url = f"{self.BASE_URL}/accounts/{account_id}/transactions"
        
        # Build query parameters
        params = {}
        if from_account:
            params["from_account"] = from_account
        if to_account:
            params["to_account"] = to_account
        if transfer_type:
            params["transfer_type"] = transfer_type
        if max_block_index is not None:
            params["max_block_index"] = max_block_index
        
        # Always include pagination and sorting
        params["limit"] = limit
        params["offset"] = offset
        params["sort_by"] = sort_by
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error querying transactions from ICP Ledger: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

# Import the Etherscan API for Ethereum support
from etherscan_api import EtherscanAPI

# Initialize API services - prefer mempool.space as it's more reliable for free usage
bitcoin_api_service = MemPoolAPI()
icp_api_service = ICPLedgerAPI()  # Add ICP service

# Use Etherscan API directly for Ethereum
ethereum_api_service = EtherscanAPI()  # Use Etherscan for Ethereum

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
    currency = data.get("currency", "BTC").upper()  # Default to BTC
    
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
    
    print(f"Getting balance for address: {address} (session: {session_id}, currency: {currency})")
    
    try:
        # Choose the appropriate API service based on currency
        if currency == "ICP":
            balance_data = icp_api_service.get_balance(address)
        elif currency == "ETH" or (address.startswith("0x") and len(address) == 42):
            balance_data = ethereum_api_service.get_balance(address)
        else:  # Default to Bitcoin
            balance_data = bitcoin_api_service.get_balance(address)
            
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
    currency = data.get("currency", "BTC").upper()  # Default to BTC
    
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
    
    print(f"Getting UTXOs/transactions for address: {address} (session: {session_id}, currency: {currency})")
    
    try:
        # Choose the appropriate API service based on currency
        if currency == "ICP":
            # For ICP, we return transactions instead of UTXOs
            utxo_data = icp_api_service.get_utxos(address)
        elif currency == "ETH" or (address.startswith("0x") and len(address) == 42):
            # For Ethereum, we return transactions instead of UTXOs
            utxo_data = ethereum_api_service._get_eth_transactions(address)
        else:  # Default to Bitcoin
            utxo_data = bitcoin_api_service.get_utxos(address)
            
        return utxo_data
    except Exception as e:
        print(f"Error getting UTXOs/transactions: {str(e)}")
        # Fallback to mock data if API fails
        return MOCK_DATA["utxos"]

@app.post("/get-current-fee-percentiles")
async def get_current_fee_percentiles(request: Request):
    data = await request.json() if request.headers.get("content-type") == "application/json" else {}
    currency = data.get("currency", "BTC").upper()  # Default to BTC
    
    try:
        # Choose the appropriate API service based on currency
        if currency == "ICP":
            fee_data = icp_api_service.get_fee_percentiles()
        else:  # Default to Bitcoin
            fee_data = bitcoin_api_service.get_fee_percentiles()
            
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

# Add Ethereum-specific endpoints
@app.get("/ethereum/account/{address}")
async def get_ethereum_account_info(address: str, session_id: str = "default_session"):
    """
    Get detailed information about an Ethereum account including balance and token balances
    """
    # Remember this address for future use, with ETH indicator
    wallet_memory.remember_wallet(f"{session_id}_eth", address)
    session_wallets[f"{session_id}_eth"] = address
    
    try:
        # Get basic account balance
        balance_data = ethereum_api_service.get_balance(address)
        
        # Get token balances
        try:
            token_balances = ethereum_api_service.get_ethereum_tokens(address)
            balance_data["tokens"] = token_balances
        except Exception as token_error:
            print(f"Error fetching Ethereum tokens: {str(token_error)}")
            balance_data["tokens"] = []
        
        # Get recent transactions
        try:
            transactions = ethereum_api_service._get_eth_transactions(address, 5)
            balance_data["recent_transactions"] = transactions
        except Exception as tx_error:
            print(f"Warning: Could not fetch ETH transactions: {str(tx_error)}")
            balance_data["recent_transactions"] = []
        
        return balance_data
    except Exception as e:
        print(f"Error getting Ethereum account info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Ethereum account data: {str(e)}")

@app.get("/ethereum/tokens/{address}")
async def get_ethereum_tokens(address: str, session_id: str = "default_session"):
    """
    Get ERC20 token balances for an Ethereum address
    """
    # Remember this address for future use
    wallet_memory.remember_wallet(f"{session_id}_eth", address)
    session_wallets[f"{session_id}_eth"] = address
    
    try:
        token_balances = ethereum_api_service.get_ethereum_tokens(address)
        return {"address": address, "tokens": token_balances}
    except Exception as e:
        print(f"Error getting Ethereum token balances: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Ethereum token data: {str(e)}")

@app.get("/ethereum/transaction/{tx_hash}")
async def get_ethereum_transaction(tx_hash: str):
    """
    Get details for a specific Ethereum transaction
    """
    try:
        # Use the Etherscan API for Ethereum transactions
        tx_data = ethereum_api_service.get_ethereum_transaction(tx_hash)
        
        # Add currency identifier
        tx_data["currency"] = "ETH"
        return tx_data
    except Exception as e:
        print(f"Error getting Ethereum transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Ethereum transaction: {str(e)}")

# Add specific ICP Ledger API endpoints
@app.get("/icp/account/{address}")
async def get_icp_account_info(address: str, session_id: str = "default_session"):
    """
    Get detailed information about an ICP account
    """
    # Remember this address for future use, with ICP indicator
    wallet_memory.remember_wallet(f"{session_id}_icp", address)
    session_wallets[f"{session_id}_icp"] = address
    
    try:
        account_info = icp_api_service.get_account_info(address)
        return account_info
    except Exception as e:
        print(f"Error getting ICP account info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP account data: {str(e)}")

@app.get("/icp/transaction/{tx_hash}")
async def get_icp_transaction(tx_hash: str):
    """
    Get details for a specific ICP transaction
    """
    try:
        # Use the ICPLedgerAPI directly for ICP transactions
        url = f"{icp_api_service.BASE_URL}/transactions/{tx_hash}"
        response = requests.get(url)
        response.raise_for_status()
        tx_data = response.json()
        
        # Add currency identifier
        tx_data["currency"] = "ICP"
        return tx_data
    except Exception as e:
        print(f"Error getting ICP transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP transaction: {str(e)}")

@app.get("/bitcoin/transaction/{tx_hash}")
async def get_bitcoin_transaction(tx_hash: str):
    """
    Get details for a specific Bitcoin transaction
    """
    try:
        # Use blockchain.info API for Bitcoin transactions
        response = requests.get(f"https://blockchain.info/rawtx/{tx_hash}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching Bitcoin transaction: {str(e)}"
        print(error_msg)
        # Try mempool.space as an alternative API
        try:
            response = requests.get(f"https://mempool.space/api/tx/{tx_hash}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e2:
            raise HTTPException(status_code=500, detail=f"{error_msg}. Alternative API also failed: {str(e2)}")

@app.get("/transaction/{tx_hash}")
async def get_any_transaction(tx_hash: str):
    """
    Smart transaction lookup that tries to determine if it's a Bitcoin or ICP transaction
    """
    try:
        # Use the ICP service which now has Bitcoin fallback built in
        transaction_data = icp_api_service.get_transaction(tx_hash)
        return transaction_data
    except Exception as e:
        print(f"Error in transaction lookup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching transaction data: {str(e)}")

@app.get("/icp/blocks")
async def get_icp_blocks(start: int = 0, limit: int = 10):
    """
    Get recent blocks from the ICP ledger
    """
    try:
        blocks = icp_api_service.get_blocks(start, limit)
        return {"blocks": blocks, "start": start, "limit": limit}
    except Exception as e:
        print(f"Error getting ICP blocks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP blocks: {str(e)}")

@app.get("/icp/fees")
async def get_icp_fees():
    """
    Get standard transaction fee for ICP
    """
    try:
        fees = icp_api_service.get_fee_percentiles()
        return {"standard_fee_e8s": fees[0], "standard_fee_icp": fees[0] / 100000000}
    except Exception as e:
        print(f"Error getting ICP fees: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP fees: {str(e)}")

@app.get("/icp/stats")
async def get_icp_stats():
    """
    Get ICP blockchain statistics
    """
    try:
        stats = icp_api_service.get_blockchain_stats()
        return stats
    except Exception as e:
        print(f"Error getting ICP stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP stats: {str(e)}")

@app.get("/icp/latest-blocks")
async def get_icp_latest_blocks(limit: int = 10):
    """
    Get latest blocks from the ICP ledger
    """
    try:
        blocks = icp_api_service.get_latest_blocks(limit)
        return {"blocks": blocks, "limit": limit}
    except Exception as e:
        print(f"Error getting ICP latest blocks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP latest blocks: {str(e)}")

@app.get("/icp/neuron/{neuron_id}")
async def get_icp_neuron(neuron_id: str):
    """
    Get information about an ICP neuron (staking)
    """
    try:
        neuron_info = icp_api_service.get_neuron_info(neuron_id)
        return neuron_info
    except Exception as e:
        print(f"Error getting ICP neuron: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP neuron: {str(e)}")

@app.get("/icp/canister/{canister_id}")
async def get_icp_canister(canister_id: str):
    """
    Get information about an ICP canister
    """
    try:
        canister_info = icp_api_service.get_canister_info(canister_id)
        return canister_info
    except Exception as e:
        print(f"Error getting ICP canister: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP canister: {str(e)}")

@app.get("/icp/account_balance/{address}")
async def get_icp_account_balance(address: str, session_id: str = "default_session"):
    """
    Get balance for an ICP account - alias for /icp/account/{address}/balance
    """
    return await get_icp_account_info(address, session_id)

@app.get("/icp/account_transactions/{address}")
async def get_icp_account_transactions(address: str, session_id: str = "default_session"):
    """
    Get transactions for an ICP account
    """
    # Remember this address for future use
    wallet_memory.remember_wallet(f"{session_id}_icp", address)
    
    try:
        transactions = icp_api_service.get_utxos(address)
        return {"address": address, "transactions": transactions}
    except Exception as e:
        print(f"Error getting ICP account transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP account transactions: {str(e)}")
async def get_icp_blockchain_info():
    """
    Get general information about the ICP blockchain
    """
    try:
        stats = icp_api_service.get_blockchain_stats()
        latest_blocks = icp_api_service.get_latest_blocks(5)
        fees = icp_api_service.get_fee_percentiles()
        
        return {
            "stats": stats,
            "latest_blocks": latest_blocks,
            "standard_fee_e8s": fees[0],
            "standard_fee_icp": fees[0] / 100000000
        }
    except Exception as e:
        print(f"Error getting ICP blockchain info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ICP blockchain info: {str(e)}")

@app.get("/icp/account/{address}/transactions")
async def query_icp_account_transactions(
    address: str,
    from_account: Optional[str] = None,
    to_account: Optional[str] = None,
    transfer_type: Optional[str] = None,
    max_block_index: Optional[int] = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "-block_height"
):
    """
    Query ICP transactions for a specific account with multiple filters
    
    This endpoint matches the ICP Ledger API's transaction query functionality:
    https://ledger-api.internetcomputer.org/swagger-ui/
    """
    try:
        results = icp_api_service.query_transactions(
            account_id=address,
            from_account=from_account,
            to_account=to_account,
            transfer_type=transfer_type,
            max_block_index=max_block_index,
            limit=limit,
            offset=offset,
            sort_by=sort_by
        )
        return results
    except Exception as e:
        print(f"Error querying ICP transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying ICP transactions: {str(e)}")

@app.get("/search-address/{address}")
async def search_address(address: str, session_id: str = "default_session", currency: str = "BTC"):
    is_icp = currency.upper() == "ICP"
    is_eth = currency.upper() == "ETH" or (address.startswith("0x") and len(address) == 42)
    
    # Remember this address for future use
    wallet_key = f"{session_id}_icp" if is_icp else f"{session_id}_eth" if is_eth else session_id
    wallet_memory.remember_wallet(wallet_key, address)
    session_wallets[wallet_key] = address
    
    try:
        if is_icp:
            # For ICP addresses, use the ICP API
            account_info = icp_api_service.get_account_info(address)
            return account_info
        elif is_eth:
            # For Ethereum addresses, use the Ethereum API
            try:
                # Get basic balance data
                balance_data = ethereum_api_service.get_balance(address)
                
                # Get token data
                token_data = ethereum_api_service.get_ethereum_tokens(address)
                
                # Format results
                result = {
                    "address": address,
                    "balance": balance_data,
                    "token_count": len(token_data),
                    "tokens": token_data[:5] if len(token_data) > 5 else token_data
                }
                
                return result
            except Exception as e:
                print(f"Error with Ethereum API: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error fetching Ethereum data: {str(e)}")
        else:
            # For Bitcoin addresses, use the Bitcoin API
            # Get basic balance data
            balance_data = bitcoin_api_service.get_balance(address)
            
            # Get UTXO data
            utxo_data = bitcoin_api_service.get_utxos(address)
            
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
async def search_current_wallet(session_id: str = "default_session", currency: str = "BTC"):
    """
    Search for information about the current saved wallet
    """
    # Determine if looking for ICP or BTC wallet based on currency parameter
    is_icp = currency.upper() == "ICP"
    is_eth = currency.upper() == "ETH"
    
    if is_eth:
        wallet_key = f"{session_id}_eth"
    elif is_icp:
        wallet_key = f"{session_id}_icp"
    else:
        wallet_key = session_id
    
    # Get the current wallet address
    if wallet_key in session_wallets:
        address = session_wallets[wallet_key]
    elif wallet_memory.has_wallet(wallet_key):
        address = wallet_memory.get_wallet(wallet_key)
    else:
        raise HTTPException(status_code=400, detail=f"No saved {currency} wallet found for this session")
    
    # Redirect to the regular search endpoint
    return await search_address(address, session_id, currency)

@app.get("/address-activity/{address}")
async def address_activity(address: str, session_id: str = "default_session", currency: str = "BTC"):
    """
    Get activity summary for a cryptocurrency address
    """
    # Determine if this is an ICP address or BTC address based on format or currency parameter
    is_icp = currency.upper() == "ICP"
    is_eth = currency.upper() == "ETH" or (address.startswith("0x") and len(address) == 42)
    
    # Remember this address for future use
    wallet_key = f"{session_id}_icp" if is_icp else f"{session_id}_eth" if is_eth else session_id
    wallet_memory.remember_wallet(wallet_key, address)
    session_wallets[wallet_key] = address
    
    try:
        if is_icp:
            # For ICP addresses, use the account info which includes transactions
            account_info = icp_api_service.get_account_info(address)
            transactions = account_info.get("recent_transactions", [])
            
            return {
                "address": address,
                "currency": "ICP",
                "transaction_count": account_info.get("transaction_count", 0),
                "incoming_transactions": account_info.get("incoming_transactions", 0),
                "outgoing_transactions": account_info.get("outgoing_transactions", 0),
                "balance_e8s": account_info.get("balance_e8s", 0),
                "balance_icp": account_info.get("balance_icp", 0),
                "recent_transactions": transactions
            }
        elif is_eth:
            # For Ethereum addresses, get account info and transactions
            try:
                # Get basic account info
                account_info = ethereum_api_service.get_balance(address)
                
                # Get transactions
                transactions = ethereum_api_service._get_eth_transactions(address, 10)
                
                return {
                    "address": address,
                    "currency": "ETH",
                    "transaction_count": account_info.get("transaction_count", 0),
                    "balance_wei": account_info.get("confirmed", 0),
                    "balance_eth": account_info.get("balance_eth", 0),
                    "total_received": account_info.get("total_received", 0),
                    "total_sent": account_info.get("total_sent", 0),
                    "recent_transactions": transactions
                }
            except Exception as e:
                print(f"Error with Ethereum activity: {str(e)}")
                return {
                    "address": address,
                    "currency": "ETH",
                    "error": f"Could not retrieve Ethereum transaction data: {str(e)}"
                }
        else:
            # For Bitcoin addresses, use the blockchain.com API
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
                "currency": "BTC",
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
            "currency": "ICP" if is_icp else "BTC",
            "error": f"Could not retrieve transaction data: {str(e)}"
        }

@app.get("/current-wallet-activity")
async def current_wallet_activity(session_id: str = "default_session", currency: str = "BTC"):
    """
    Get activity summary for the current saved wallet
    """
    # Determine wallet key based on currency
    is_icp = currency.upper() == "ICP"
    is_eth = currency.upper() == "ETH"
    
    if is_eth:
        wallet_key = f"{session_id}_eth"
    elif is_icp:
        wallet_key = f"{session_id}_icp"
    else:
        wallet_key = session_id
    
    # Get the current wallet address
    if wallet_key in session_wallets:
        address = session_wallets[wallet_key]
    elif wallet_memory.has_wallet(wallet_key):
        address = wallet_memory.get_wallet(wallet_key)
    else:
        raise HTTPException(status_code=400, detail=f"No saved {currency} wallet found for this session")
    
    # Redirect to the regular activity endpoint
    return await address_activity(address, session_id, currency)

if __name__ == "__main__":
    # Import and include the Ethereum router
    try:
        from ethereum_endpoints import router as ethereum_router
        app.include_router(ethereum_router)
        print("Ethereum endpoints registered successfully")
    except ImportError as e:
        print(f"Warning: Could not load Ethereum endpoints: {str(e)}")
    
    print("Starting API Gateway on http://0.0.0.0:8083")
    uvicorn.run(app, host="0.0.0.0", port=8083)