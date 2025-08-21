import aiohttp
import requests  # Keep for other functions temporarily
import json
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
)
from uagents import Agent, Context, Protocol
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import re  # For regex matching

# ASI1 API settings
# Create yours at: https://asi1.ai/dashboard/api-keys
ASI1_API_KEY = "sk_f31d6a0de98f412b91427e2ee7e8dc2957a8bd305a1146869d500252c187a224"
ASI1_BASE_URL = "https://api.asi1.ai/v1"
ASI1_HEADERS = {
    "Authorization": f"Bearer {ASI1_API_KEY}",
    "Content-Type": "application/json"
}

# Available ASI1 models: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
ASI1_MODEL = "asi1-mini"  # Use the lightest model by default

CANISTER_ID = "uxrrr-q7777-77774-qaaaq-cai"

# External API endpoints (not API Gateway)
BLOCKCHAIR_BASE_URL = "https://api.blockchair.com"
ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"
BASE_URL = "http://localhost:8083"  # Temporary - for other functions

# API Keys (add your keys here)
ETHERSCAN_API_KEY = "MIWU92VZ2HJ6M3TNZNID871477URI8PJHG"  # Get from https://etherscan.io/apis

HEADERS = {
    "Content-Type": "application/json"
}  # Simplified headers

# Wallet address memory
class WalletMemory:
    def __init__(self):
        self.user_wallets = {}  # Maps user_id to wallet address
        self.default_wallet = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"  # Default demo address
        
    def remember_wallet(self, user_id: str, address: str):
        """Store a wallet address for a user"""
        self.user_wallets[user_id] = address
        
    def get_wallet(self, user_id: str) -> str:
        """Get the most recently used wallet for a user"""
        return self.user_wallets.get(user_id, self.default_wallet)
        
    def has_wallet(self, user_id: str) -> bool:
        """Check if we have a wallet stored for this user"""
        return user_id in self.user_wallets

# Initialize wallet memory
wallet_memory = WalletMemory()

# Add a tool to specifically query ICP account transactions
tools = [
    # Bitcoin related functions
    {
        "type": "function",
        "function": {
            "name": "get_current_fee_percentiles",
            "description": "Gets the current Bitcoin fee percentiles measured in satoshi/byte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "The cryptocurrency to get fees for (BTC or ICP).",
                        "enum": ["BTC", "ICP", "btc", "icp"]
                    }
                },
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Returns the balance of a given cryptocurrency address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The cryptocurrency address to check."
                    },
                    "currency": {
                        "type": "string",
                        "description": "The cryptocurrency type (BTC or ICP).",
                        "enum": ["BTC", "ICP", "btc", "icp"]
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_utxos",
            "description": "Returns the UTXOs of a given Bitcoin address or transactions for an ICP/Ethereum address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The cryptocurrency address to fetch UTXOs or transactions for."
                    },
                    "currency": {
                        "type": "string",
                        "description": "The cryptocurrency type (BTC, ETH, or ICP).",
                        "enum": ["BTC", "ETH", "ICP", "btc", "eth", "icp"]
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_address",
            "description": "Search for comprehensive information about a cryptocurrency address including balance and recent transactions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The cryptocurrency address to search for information."
                    },
                    "currency": {
                        "type": "string",
                        "description": "The cryptocurrency type (BTC, ETH, or ICP).",
                        "enum": ["BTC", "ETH", "ICP", "btc", "eth", "icp"]
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "address_activity",
            "description": "Get recent activity and transaction history for a cryptocurrency address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The cryptocurrency address to get activity for."
                    },
                    "currency": {
                        "type": "string",
                        "description": "The cryptocurrency type (BTC, ETH, or ICP).",
                        "enum": ["BTC", "ETH", "ICP", "btc", "eth", "icp"]
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    
    # Ethereum specific functions
    {
        "type": "function",
        "function": {
            "name": "get_ethereum_account_info",
            "description": "Get detailed information about an Ethereum account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Ethereum address to get information for (starts with 0x)."
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ethereum_tokens",
            "description": "Get ERC-20 token balances for an Ethereum address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Ethereum address to get token balances for (starts with 0x)."
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ethereum_transaction",
            "description": "Get details about a specific Ethereum transaction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tx_hash": {
                        "type": "string",
                        "description": "The Ethereum transaction hash to look up (starts with 0x)."
                    }
                },
                "required": ["tx_hash"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    
    # ICP specific functions
    {
        "type": "function",
        "function": {
            "name": "get_icp_account_info",
            "description": "Get detailed information about an Internet Computer Protocol (ICP) account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The ICP account address to get information for."
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_icp_account_transactions",
            "description": "Get transactions for a specific ICP account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The ICP account address to get transactions for."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of transactions to return."
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_icp_transaction",
            "description": "Get details for a specific ICP transaction by its hash.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tx_hash": {
                        "type": "string",
                        "description": "The transaction hash to get details for."
                    }
                },
                "required": ["tx_hash"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_bitcoin_transaction",
            "description": "Get details for a specific Bitcoin transaction by its hash.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tx_hash": {
                        "type": "string",
                        "description": "The transaction hash to get details for."
                    }
                },
                "required": ["tx_hash"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_icp_blocks",
            "description": "Get recent blocks from the ICP ledger.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {
                        "type": "integer",
                        "description": "The starting block number."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of blocks to return."
                    }
                },
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_icp_fees",
            "description": "Get standard transaction fee for ICP.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_wallet",
            "description": "Generate a new wallet address for demonstration purposes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "The cryptocurrency type (BTC or ICP).",
                        "enum": ["BTC", "ICP", "ETH", "btc", "icp", "eth"]
                    }
                },
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    
    # Ethereum specific functions
    {
        "type": "function",
        "function": {
            "name": "get_ethereum_account_info",
            "description": "Get detailed information about an Ethereum account including balance and token balances.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Ethereum account address to get information for."
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ethereum_tokens",
            "description": "Get ERC20 token balances for an Ethereum address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Ethereum address to get token balances for."
                    }
                },
                "required": ["address"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ethereum_transaction",
            "description": "Get details for a specific Ethereum transaction by its hash.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tx_hash": {
                        "type": "string",
                        "description": "The transaction hash to get details for."
                    }
                },
                "required": ["tx_hash"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

async def call_icp_endpoint(func_name: str, args: dict):
    try:
        # Get the currency if provided, default to BTC
        currency = args.get("currency", "BTC").upper() if "currency" in args else "BTC"
        
        # Handle different API endpoints based on function name
        if func_name == "get_current_fee_percentiles":
            url = f"{BLOCKCHAIR_BASE_URL}/bitcoin/stats"
            response = requests.get(url, headers=HEADERS)
        elif func_name == "get_balance":
            address = args["address"]
            # Detect address type and use appropriate API
            if address.startswith("0x") and len(address) == 42:
                # Ethereum address - use Etherscan
                url = f"{ETHERSCAN_BASE_URL}"
                params = {
                    "module": "account",
                    "action": "balance",
                    "address": address,
                    "tag": "latest",
                    "apikey": 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG'
                }
                response = requests.get(url, headers=HEADERS, params=params)
            else:
                # Bitcoin address - use Blockchair
                url = f"{BLOCKCHAIR_BASE_URL}/bitcoin/dashboards/address/{address}"
                response = requests.get(url, headers=HEADERS)
        elif func_name == "get_utxos":
            address = args["address"]
            url = f"{BLOCKCHAIR_BASE_URL}/bitcoin/dashboards/address/{address}"
            response = requests.get(url, headers=HEADERS)
        elif func_name == "search_address":
            address = args['address']
            # Detect address type and use appropriate API
            if address.startswith("0x") and len(address) == 42:
                # Ethereum address
                url = f"{ETHERSCAN_BASE_URL}"
                params = {
                    "module": "account",
                    "action": "balance", 
                    "address": address,
                    "tag": "latest",
                    "apikey": 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG'
                }
                response = requests.get(url, headers=HEADERS, params=params)
            else:
                # Bitcoin address
                url = f"{BLOCKCHAIR_BASE_URL}/bitcoin/dashboards/address/{address}"
                response = requests.get(url, headers=HEADERS)
        elif func_name == "address_activity":
            address = args['address']
            if address.startswith("0x") and len(address) == 42:
                # Ethereum address
                url = f"{ETHERSCAN_BASE_URL}"
                params = {
                    "module": "account",
                    "action": "txlist",
                    "address": address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "sort": "desc",
                    "apikey": 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG'
                }
                response = requests.get(url, headers=HEADERS, params=params)
            else:
                # Bitcoin address
                url = f"{BLOCKCHAIR_BASE_URL}/bitcoin/dashboards/address/{address}"
                response = requests.get(url, headers=HEADERS)
        elif func_name == "generate_wallet":
            # For now, return a message that this needs to be implemented
            return {
                "message": "Wallet generation should be done client-side for security",
                "currency": currency
            }
        elif func_name == "get_bitcoin_transaction":
            # Handle Bitcoin transaction lookup
            tx_hash = args["tx_hash"]
            url = f"{BLOCKCHAIR_BASE_URL}/bitcoin/dashboards/transaction/{tx_hash}"
            response = requests.get(url, headers=HEADERS)
            
        # ICP specific endpoints - use the same API as api_gateway.py
        elif func_name == "get_icp_account_info":
            address = args['address']
            # Use the same ICP Ledger API as configured in api_gateway.py
            try:
                # Try the main ICP Ledger API that you have configured
                icp_ledger_url = f"https://ledger-api.internetcomputer.org/accounts/{address}"
                
                try:
                    icp_response = requests.get(icp_ledger_url, headers=HEADERS, timeout=10)
                    if icp_response.status_code == 200:
                        icp_data = icp_response.json()
                        balance_e8s = int(icp_data.get("balance", 0))
                        balance_icp = balance_e8s / 100000000  # Convert e8s to ICP
                        
                        # Try to get ICP price from CoinGecko
                        try:
                            price_response = requests.get(
                                "https://api.coingecko.com/api/v3/simple/price?ids=internet-computer&vs_currencies=usd",
                                headers=HEADERS,
                                timeout=10
                            )
                            if price_response.status_code == 200:
                                price_data = price_response.json()
                                icp_price_usd = price_data.get("internet-computer", {}).get("usd", 0)
                                balance_usd = balance_icp * icp_price_usd
                            else:
                                icp_price_usd = 0
                                balance_usd = 0
                        except:
                            icp_price_usd = 0
                            balance_usd = 0
                        
                        return {
                            "address": address,
                            "balance_e8s": balance_e8s,
                            "balance_icp": balance_icp,
                            "balance_usd": balance_usd,
                            "icp_price_usd": icp_price_usd,
                            "transaction_count": icp_data.get("transaction_count", 0),
                            "currency": "ICP",
                            "status": "success",
                            "api_source": "ICP Ledger API"
                        }
                except Exception as ledger_error:
                    print(f"ICP Ledger API failed: {ledger_error}")
                
                # Fallback: Try alternative endpoints if the main one fails
                try:
                    # Try IC Rocks API as fallback
                    ic_rocks_url = f"https://ic.rocks/api/accounts/{address}"
                    rocks_response = requests.get(ic_rocks_url, headers=HEADERS, timeout=10)
                    if rocks_response.status_code == 200:
                        rocks_data = rocks_response.json()
                        balance_e8s = int(rocks_data.get("balance", 0))
                        balance_icp = balance_e8s / 100000000
                        
                        # Try to get ICP price
                        try:
                            price_response = requests.get(
                                "https://api.coingecko.com/api/v3/simple/price?ids=internet-computer&vs_currencies=usd",
                                headers=HEADERS,
                                timeout=10
                            )
                            if price_response.status_code == 200:
                                price_data = price_response.json()
                                icp_price_usd = price_data.get("internet-computer", {}).get("usd", 0)
                                balance_usd = balance_icp * icp_price_usd
                            else:
                                icp_price_usd = 0
                                balance_usd = 0
                        except:
                            icp_price_usd = 0
                            balance_usd = 0
                        
                        return {
                            "address": address,
                            "balance_e8s": balance_e8s,
                            "balance_icp": balance_icp,
                            "balance_usd": balance_usd,
                            "icp_price_usd": icp_price_usd,
                            "transaction_count": rocks_data.get("transaction_count", 0),
                            "currency": "ICP",
                            "status": "success",
                            "api_source": "IC Rocks API (fallback)"
                        }
                except Exception as rocks_error:
                    print(f"IC Rocks API also failed: {rocks_error}")
                
                # If both APIs fail, return informational message with actual URLs
                return {
                    "address": address,
                    "balance_icp": "Unable to fetch - API unavailable",
                    "message": "ICP APIs are currently unavailable. You can check your balance at:",
                    "suggestions": [
                        f"ICP Dashboard: https://dashboard.internetcomputer.org/account/{address}",
                        f"IC Rocks Explorer: https://ic.rocks/account/{address}",
                        f"NNS Frontend: https://nns.ic0.app/",
                        "Use dfx command: dfx canister call rrkah-fqaaa-aaaaa-aaaaq-cai account_balance"
                    ],
                    "currency": "ICP",
                    "status": "api_unavailable",
                    "api_source": "Multiple ICP APIs tried"
                }
                
            except Exception as e:
                return {
                    "address": address,
                    "error": f"ICP balance lookup failed: {str(e)}",
                    "message": "ICP balance lookup encountered an error",
                    "suggestions": [
                        f"Check manually: https://dashboard.internetcomputer.org/account/{address}",
                        f"Or use: https://ic.rocks/account/{address}"
                    ],
                    "status": "error"
                }
        elif func_name == "get_icp_transaction":
            # ICP transaction lookup using the ICP Ledger API
            tx_hash = args['tx_hash']
            try:
                # Try to get transaction details from ICP Ledger API
                icp_tx_url = f"https://ledger-api.internetcomputer.org/transactions/{tx_hash}"
                tx_response = requests.get(icp_tx_url, headers=HEADERS, timeout=10)
                
                if tx_response.status_code == 200:
                    tx_data = tx_response.json()
                    return {
                        "tx_hash": tx_hash,
                        "transaction_data": tx_data,
                        "currency": "ICP",
                        "status": "success",
                        "api_source": "ICP Ledger API"
                    }
                else:
                    return {
                        "tx_hash": tx_hash,
                        "message": f"Transaction not found in ICP ledger (Status: {tx_response.status_code})",
                        "suggestions": [
                            f"Check on IC Rocks: https://ic.rocks/transaction/{tx_hash}",
                            f"Check on ICP Dashboard: https://dashboard.internetcomputer.org/"
                        ],
                        "status": "not_found"
                    }
            except Exception as e:
                return {
                    "tx_hash": tx_hash,
                    "error": f"ICP transaction lookup failed: {str(e)}",
                    "message": "Could not fetch transaction from ICP ledger",
                    "suggestions": [
                        f"Check manually: https://ic.rocks/transaction/{tx_hash}"
                    ],
                    "status": "error"
                }
        elif func_name == "get_icp_account_transactions":
            # ICP account transactions using the ICP Ledger API
            address = args["address"]
            try:
                # Get transactions for this ICP account
                icp_tx_url = f"https://ledger-api.internetcomputer.org/accounts/{address}/transactions"
                params = {
                    "limit": 10,
                    "offset": 0,
                    "sort_by": "-block_height"  # Most recent first
                }
                
                tx_response = requests.get(icp_tx_url, headers=HEADERS, params=params, timeout=10)
                
                if tx_response.status_code == 200:
                    tx_data = tx_response.json()
                    transactions = tx_data.get("blocks", [])
                    
                    # Format transactions for display
                    formatted_txs = []
                    for tx in transactions[:5]:  # Show last 5 transactions
                        formatted_tx = {
                            "tx_hash": tx.get("transaction_hash", ""),
                            "block_height": tx.get("block_height", 0),
                            "timestamp": tx.get("created_at", 0),
                            "type": tx.get("transfer_type", "TRANSFER"),
                            "amount_e8s": tx.get("amount", 0),
                            "amount_icp": tx.get("amount", 0) / 100000000,
                            "fee_e8s": tx.get("fee", 0),
                            "from": tx.get("from_account_identifier", ""),
                            "to": tx.get("to_account_identifier", "")
                        }
                        formatted_txs.append(formatted_tx)
                    
                    return {
                        "address": address,
                        "transactions": formatted_txs,
                        "total_count": tx_data.get("total", len(formatted_txs)),
                        "currency": "ICP",
                        "status": "success",
                        "api_source": "ICP Ledger API"
                    }
                else:
                    return {
                        "address": address,
                        "message": f"Could not fetch transactions (Status: {tx_response.status_code})",
                        "suggestions": [
                            f"Check manually: https://ic.rocks/account/{address}",
                            f"Or use: https://dashboard.internetcomputer.org/account/{address}"
                        ],
                        "status": "api_error"
                    }
                    
            except Exception as e:
                return {
                    "address": address,
                    "error": f"ICP transaction lookup failed: {str(e)}",
                    "message": "Could not fetch account transactions from ICP ledger",
                    "suggestions": [
                        f"Check manually: https://ic.rocks/account/{address}"
                    ],
                    "status": "error"
                }
        elif func_name == "get_icp_blocks":
            # Get ICP blocks using the ICP Ledger API
            try:
                start = args.get("start", 0)
                limit = args.get("limit", 10)
                
                icp_blocks_url = f"https://ledger-api.internetcomputer.org/blocks"
                params = {"start": start, "limit": limit}
                
                blocks_response = requests.get(icp_blocks_url, headers=HEADERS, params=params, timeout=10)
                
                if blocks_response.status_code == 200:
                    blocks_data = blocks_response.json()
                    blocks = blocks_data.get("blocks", [])
                    
                    return {
                        "blocks": blocks,
                        "start": start,
                        "limit": limit,
                        "currency": "ICP",
                        "status": "success",
                        "api_source": "ICP Ledger API"
                    }
                else:
                    return {
                        "message": f"Could not fetch ICP blocks (Status: {blocks_response.status_code})",
                        "suggestion": "Check ICP explorer for block information",
                        "status": "api_error"
                    }
                    
            except Exception as e:
                return {
                    "error": f"ICP blocks lookup failed: {str(e)}",
                    "message": "Could not fetch blocks from ICP ledger",
                    "suggestion": "Use ICP explorer for block details.",
                    "status": "error"
                }
        elif func_name == "get_icp_fees":
            # Get ICP fee information using the ICP Ledger API
            try:
                # Get general info about ICP which includes fee information
                icp_info_url = f"https://ledger-api.internetcomputer.org/info"
                
                info_response = requests.get(icp_info_url, headers=HEADERS, timeout=10)
                
                if info_response.status_code == 200:
                    info_data = info_response.json()
                    standard_fee_e8s = info_data.get("standard_fee", 10000)  # Default 10000 e8s
                    standard_fee_icp = standard_fee_e8s / 100000000
                    
                    return {
                        "standard_fee_e8s": standard_fee_e8s,
                        "standard_fee_icp": standard_fee_icp,
                        "currency": "ICP",
                        "status": "success",
                        "api_source": "ICP Ledger API"
                    }
                else:
                    return {
                        "standard_fee_e8s": 10000,  # Default fee
                        "standard_fee_icp": 0.0001,
                        "message": "Using default ICP fee (API unavailable)",
                        "currency": "ICP",
                        "status": "default_values"
                    }
                    
            except Exception as e:
                return {
                    "error": f"ICP fee lookup failed: {str(e)}",
                    "standard_fee_e8s": 10000,  # Default fee
                    "standard_fee_icp": 0.0001,
                    "message": "Using default ICP fee due to API error",
                    "currency": "ICP",
                    "status": "error"
                }
        elif func_name == "get_icp_stats":
            # Get ICP blockchain statistics using the ICP Ledger API
            try:
                icp_stats_url = f"https://ledger-api.internetcomputer.org/stats"
                
                stats_response = requests.get(icp_stats_url, headers=HEADERS, timeout=10)
                
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    
                    # Add computed metrics if possible
                    if "total_transactions" in stats_data and "total_accounts" in stats_data:
                        stats_data["avg_transactions_per_account"] = (
                            stats_data["total_transactions"] / stats_data["total_accounts"] 
                            if stats_data["total_accounts"] > 0 else 0
                        )
                    
                    return {
                        "stats": stats_data,
                        "currency": "ICP",
                        "status": "success",
                        "api_source": "ICP Ledger API"
                    }
                else:
                    return {
                        "message": f"Could not fetch ICP stats (Status: {stats_response.status_code})",
                        "suggestion": "Check ICP dashboard for blockchain statistics",
                        "status": "api_error"
                    }
                    
            except Exception as e:
                return {
                    "error": f"ICP stats lookup failed: {str(e)}",
                    "message": "Could not fetch blockchain stats from ICP ledger",
                    "suggestion": "Check ICP dashboard for statistics",
                    "status": "error"
                }
            
        # Ethereum specific endpoints
        elif func_name == "get_ethereum_account_info":
            address = args['address']
            url = f"{ETHERSCAN_BASE_URL}"
            params = {
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest",
                "apikey": 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG'
            }
            response = requests.get(url, headers=HEADERS, params=params)
        elif func_name == "get_ethereum_tokens":
            address = args['address']
            url = f"{ETHERSCAN_BASE_URL}"
            params = {
                "module": "account",
                "action": "tokentx",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "apikey": 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG'
            }
            response = requests.get(url, headers=HEADERS, params=params)
        elif func_name == "get_ethereum_transaction":
            tx_hash = args['tx_hash']
            
            # Check if we have a valid API key
            if 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG' == 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG':
                # Return mock data if no API key is configured
                return {
                    "result": {
                        "hash": tx_hash,
                        "status": "success",
                        "message": "This is mock data. Please configure ETHERSCAN_API_KEY for real data.",
                        "from": "0x...",
                        "to": "0x...",
                        "value": "0",
                        "gas": "21000",
                        "gasPrice": "20000000000",
                        "blockNumber": "0x0"
                    }
                }
            
            url = f"{ETHERSCAN_BASE_URL}"
            params = {
                "module": "proxy",
                "action": "eth_getTransactionByHash",
                "txhash": tx_hash,
                "apikey": 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG'
            }
            response = requests.get(url, headers=HEADERS, params=params)
        else:
            raise ValueError(f"Unsupported function call: {func_name}")
        
        # Handle responses that were fetched
        if 'response' in locals():
            # Print response for debugging
            print(f"Response from {url}: {response.status_code}")
            print(f"Response content: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            # Post-process Ethereum balance responses
            if func_name in ["get_balance", "search_address", "get_ethereum_account_info"] and 'result' in result:
                address = args.get('address', '')
                if address.startswith("0x") and len(address) == 42:
                    # Convert Wei to ETH for Ethereum balances
                    try:
                        wei_balance = int(result['result'])
                        eth_balance = wei_balance / 1e18  # Convert Wei to ETH
                        
                        # Get transaction count
                        try:
                            tx_count_params = {
                                "module": "proxy",
                                "action": "eth_getTransactionCount",
                                "address": address,
                                "tag": "latest",
                                "apikey": 'MIWU92VZ2HJ6M3TNZNID871477URI8PJHG'
                            }
                            tx_count_response = requests.get(f"{ETHERSCAN_BASE_URL}", params=tx_count_params)
                            tx_count_data = tx_count_response.json()
                            tx_count = int(tx_count_data.get('result', '0x0'), 16) if tx_count_data.get('result') else 0
                        except:
                            tx_count = 0
                        
                        # Get ETH price (simple approach using a free API)
                        eth_price_usd = 0
                        try:
                            price_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
                            price_data = price_response.json()
                            eth_price_usd = price_data.get('ethereum', {}).get('usd', 0)
                        except:
                            eth_price_usd = 0
                        
                        balance_usd = eth_balance * eth_price_usd if eth_price_usd > 0 else 0
                        
                        return {
                            "address": address,
                            "balance_wei": str(wei_balance),
                            "balance_eth": round(eth_balance, 6),
                            "balance_formatted": f"{eth_balance:.6f} ETH",
                            "balance_usd": round(balance_usd, 2) if balance_usd > 0 else None,
                            "balance_usd_formatted": f"${balance_usd:,.2f} USD" if balance_usd > 0 else "USD price unavailable",
                            "transaction_count": tx_count,
                            "eth_price_usd": eth_price_usd if eth_price_usd > 0 else None,
                            "currency": "ETH",
                            "status": "success",
                            "api_source": "Etherscan + CoinGecko"
                        }
                    except (ValueError, KeyError):
                        return {
                            "address": address,
                            "error": "Failed to parse balance",
                            "raw_response": result
                        }
            
            return result
        else:
            # This was a placeholder response that was already returned
            pass
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling {func_name}: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        return {
            "error": f"API error in {func_name}: {str(e)}",
            "function": func_name
        }
    except Exception as e:
        print(f"Unexpected error in {func_name}: {str(e)}")
        return {
            "error": f"Unexpected error in {func_name}: {str(e)}",
            "function": func_name
        }

async def process_query(query: str, ctx: Context, sender: str = "anonymous") -> str:
    try:
        # Check if query mentions specific blockchains first
        is_icp_query = bool(re.search(r'\b(icp|internet computer|dfinity)\b', query.lower()))
        is_eth_query = bool(re.search(r'\b(eth|ethereum|erc20|tokens)\b', query.lower()))
        is_btc_query = bool(re.search(r'\b(btc|bitcoin)\b', query.lower()))
        
        # Check for wallet references
        wallet_phrases = [
            r"\b(my|the|this|our|last|previous|saved|remembered)\s+wallet\b",
            r"\bwallet\s+(balance|info|address|utxos|details|transactions)\b",
            r"\bshow\s+(me\s+)?(the\s+)?(my\s+)?(wallet|address)\b"
        ]
        uses_generic_wallet_reference = any(re.search(pattern, query.lower()) for pattern in wallet_phrases)
        
        # Address patterns (check addresses BEFORE transaction hashes)
        bitcoin_address_pattern = r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b'
        ethereum_address_pattern = r'\b0x[a-fA-F0-9]{40}\b'
        icp_address_pattern = r'\b[a-f0-9]{64}\b'
        
        # Transaction hash patterns
        tx_hash_pattern = r'\b[a-fA-F0-9]{64}\b'
        eth_tx_pattern = r'\b0x[a-fA-F0-9]{64}\b'
        
        # Find address matches first (higher priority than transaction hashes)
        btc_address_match = re.search(bitcoin_address_pattern, query)
        eth_address_match = re.search(ethereum_address_pattern, query)
        
        # For ICP, be smarter about distinguishing addresses from transaction hashes
        icp_address_match = None
        tx_match = None
        eth_tx_match = re.search(eth_tx_pattern, query)
        
        # Check for ICP addresses with context
        if is_icp_query:
            potential_icp_matches = list(re.finditer(icp_address_pattern, query))
            for match in potential_icp_matches:
                hex_string = match.group(0)
                match_pos = match.start()
                
                # Look at surrounding context to determine if it's an address or transaction
                context_before = query.lower()[max(0, match_pos-30):match_pos]
                context_after = query.lower()[match_pos + len(hex_string):match_pos + len(hex_string) + 30]
                full_context = context_before + context_after
                
                # Address indicators
                address_indicators = ['address', 'account', 'wallet', 'balance', 'icp', 'search', 'check', 'find']
                tx_indicators = ['transaction', 'tx', 'hash', 'block']
                
                # Check if it's clearly described as an address
                address_score = sum(1 for indicator in address_indicators if indicator in full_context)
                tx_score = sum(1 for indicator in tx_indicators if indicator in full_context)
                
                # If it's an ICP query and no clear transaction indicators, treat as address
                if address_score > tx_score or (address_score >= tx_score and is_icp_query):
                    icp_address_match = match
                    break
            
            # If no clear address match but we found a hex string and it's an ICP query, treat as address
            if not icp_address_match and potential_icp_matches and is_icp_query:
                # Only consider it an address if there are no clear transaction keywords
                context = query.lower()
                if not any(keyword in context for keyword in ['transaction', 'tx', 'hash']):
                    icp_address_match = potential_icp_matches[0]
        
        # Now check for transaction hashes (lower priority)
        if not icp_address_match:  # Only look for transactions if we didn't find an ICP address
            if not eth_tx_match:  # Only look for generic tx hash if no ETH tx found
                tx_match = re.search(tx_hash_pattern, query)
                # But if this matches an ICP query context, skip it
                if tx_match and is_icp_query:
                    tx_context = query.lower()
                    if not any(keyword in tx_context for keyword in ['transaction', 'tx', 'hash', 'block']):
                        tx_match = None  # Don't treat as transaction
        # Process addresses if found (in priority order)
        if btc_address_match:
            # Remember this wallet address for future use
            detected_address = btc_address_match.group(0)
            wallet_memory.remember_wallet(sender, detected_address)
            ctx.logger.info(f"Remembered Bitcoin wallet address: {detected_address} for user: {sender}")
            
            # Get Bitcoin balance from Blockchair API
            try:
                response = await call_icp_endpoint("get_balance", {"address": detected_address, "currency": "BTC"})
                
                if isinstance(response, dict) and "data" in response:
                    # Blockchair API response structure
                    address_data = response["data"].get(detected_address, {}).get("address", {})
                    balance_satoshis = address_data.get("balance", 0)
                    balance_btc = balance_satoshis / 100000000  # Convert satoshis to BTC
                    transaction_count = address_data.get("transaction_count", 0)
                    
                    # Get BTC price from CoinGecko
                    try:
                        price_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
                        price_data = price_response.json()
                        btc_price_usd = price_data.get('bitcoin', {}).get('usd', 0)
                        balance_usd = balance_btc * btc_price_usd if btc_price_usd > 0 else 0
                    except:
                        btc_price_usd = 0
                        balance_usd = 0
                    
                    return f"💰 **Bitcoin Wallet Balance**\n\n" \
                           f"Address: `{detected_address}`\n\n" \
                           f"Balance: {balance_btc:.8f} BTC\n" \
                           f"USD Value: ${balance_usd:,.2f} USD\n" \
                           f"Transactions: {transaction_count}\n" \
                           f"BTC Price: ${btc_price_usd:,.2f} USD\n\n" \
                           f"_(Data from Blockchair API + CoinGecko)_"
                else:
                    return f"I found the Bitcoin address {detected_address}, but couldn't fetch balance data from Blockchair API."
                    
            except Exception as e:
                ctx.logger.error(f"Error getting Bitcoin balance: {str(e)}")
                return f"I found the Bitcoin address {detected_address}, but I couldn't fetch its current balance. The Blockchair API might be temporarily unavailable."
        
        elif eth_address_match:
            # Remember this Ethereum wallet address for future use
            detected_address = eth_address_match.group(0)
            wallet_memory.remember_wallet(f"{sender}_eth", detected_address)
            ctx.logger.info(f"Remembered Ethereum wallet address: {detected_address} for user: {sender}")
            
            # Get Ethereum balance from Etherscan API + USD price from CoinGecko
            try:
                response = await call_icp_endpoint("get_ethereum_account_info", {"address": detected_address})
                
                if isinstance(response, dict) and response.get("status") == "success":
                    balance_eth = response.get("balance_eth", 0)
                    transaction_count = response.get("transaction_count", 0)
                    balance_usd = response.get("balance_usd", 0)
                    eth_price_usd = response.get("eth_price_usd", 0)
                    
                    return f"💰 **Ethereum Wallet Balance**\n\n" \
                           f"Address: `{detected_address}`\n\n" \
                           f"Balance: {balance_eth:.6f} ETH\n" \
                           f"USD Value: ${balance_usd:,.2f} USD\n" \
                           f"Transactions: {transaction_count}\n" \
                           f"ETH Price: ${eth_price_usd:,.2f} USD\n\n" \
                           f"_(Data from Etherscan API + CoinGecko)_"
                else:
                    return f"I found the Ethereum address {detected_address}, but couldn't fetch balance data from Etherscan API."
                    
            except Exception as e:
                ctx.logger.error(f"Error getting Ethereum balance: {str(e)}")
                return f"I found the Ethereum address {detected_address}, but I couldn't fetch its current balance. The Etherscan API might be temporarily unavailable."
        
        elif icp_address_match and is_icp_query:
            # Remember this ICP address for future use
            detected_address = icp_address_match.group(0)
            wallet_memory.remember_wallet(f"{sender}_icp", detected_address)
            ctx.logger.info(f"Remembered ICP address: {detected_address} for user: {sender}")
            
            # Get ICP account information
            try:
                response = await call_icp_endpoint("get_icp_account_info", {"address": detected_address})
                
                if isinstance(response, dict):
                    if response.get("status") == "success":
                        # We have actual balance data
                        balance_icp = response.get("balance_icp", 0)
                        balance_usd = response.get("balance_usd", 0)
                        balance_e8s = response.get("balance_e8s", 0)
                        icp_price_usd = response.get("icp_price_usd", 0)
                        transaction_count = response.get("transaction_count", 0)
                        api_source = response.get("api_source", "Unknown")
                        
                        return f"🏛️ **ICP Wallet Balance**\n\n" \
                               f"Address: `{detected_address}`\n\n" \
                               f"Balance: {balance_icp:.6f} ICP\n" \
                               f"USD Value: ${balance_usd:,.2f} USD\n" \
                               f"Balance (e8s): {balance_e8s:,}\n" \
                               f"Transactions: {transaction_count}\n" \
                               f"ICP Price: ${icp_price_usd:,.2f} USD\n\n" \
                               f"_(Data from {api_source})_"
                               
                    elif response.get("status") == "api_unavailable":
                        suggestions_text = "\n".join([f"• {suggestion}" for suggestion in response.get("suggestions", [])])
                        
                        return f"🏛️ **ICP Address Detected**\n\n" \
                               f"Address: `{detected_address}`\n\n" \
                               f"❌ **ICP APIs are temporarily unavailable**\n\n" \
                               f"**You can check your balance at:**\n\n" \
                               f"{suggestions_text}\n\n" \
                               f"The ICP network APIs are currently not responding. Please try again later or use the links above."
                               
                    elif response.get("status") == "info_with_guidance":
                        suggestions_text = "\n".join([f"• {suggestion}" for suggestion in response.get("suggestions", [])])
                        
                        return f"🏛️ **ICP Address Detected**\n\n" \
                               f"Address: `{detected_address}`\n\n" \
                               f"I've detected this as an Internet Computer Protocol (ICP) address.\n\n" \
                               f"**To get actual ICP balance and transaction data:**\n\n" \
                               f"{suggestions_text}\n\n" \
                               f"**Why can't I show the balance directly?**\n" \
                               f"ICP uses a different protocol than Bitcoin/Ethereum and requires specialized IC agent libraries " \
                               f"for direct balance queries. Unlike Etherscan or Blockchair APIs, ICP balance queries need " \
                               f"to interact with the Internet Computer network through IC agents.\n\n" \
                               f"Would you like me to help with a Bitcoin or Ethereum address instead? " \
                               f"I can fetch real-time balances for those!"
                    else:
                        error_msg = response.get("message", "Unknown error occurred")
                        suggestions = response.get("suggestions", [])
                        suggestions_text = "\n".join([f"• {suggestion}" for suggestion in suggestions]) if suggestions else ""
                        
                        return f"🏛️ **ICP Address Detected**\n\n" \
                               f"Address: `{detected_address}`\n\n" \
                               f"❌ **Error fetching balance:** {error_msg}\n\n" \
                               f"**You can manually check at:**\n\n" \
                               f"{suggestions_text}" if suggestions_text else f"• https://dashboard.internetcomputer.org/account/{detected_address}"
                else:
                    return f"I found the ICP address {detected_address}, but the response format was unexpected."
                    
            except Exception as e:
                ctx.logger.error(f"Error getting ICP account info: {str(e)}")
                return f"I found the ICP address {detected_address}, but I couldn't fetch its information. The ICP ledger might be temporarily unavailable."
            
            # IMPORTANT: Return early to prevent further processing
            # This prevents the ICP address from being detected as a transaction hash later
        
        # Handle transaction lookup ONLY if no address was found and processed
        elif tx_match and not (btc_address_match or eth_address_match or (icp_address_match and is_icp_query)):
            # Found what looks like a transaction hash and no address was processed
            tx_hash = tx_match.group(0)
            ctx.logger.info(f"Detected transaction hash in query: {tx_hash}")
            try:
                # Determine which transaction endpoint to use
                if is_icp_query:
                    # Use ICP-specific transaction endpoint
                    url = f"{BASE_URL}/icp/transaction/{tx_hash}"
                elif is_eth_query or tx_hash.startswith("0x"):
                    # Use Ethereum-specific transaction endpoint
                    url = f"{BASE_URL}/ethereum/transaction/{tx_hash}"
                else:
                    # Use the generic transaction endpoint that tries both BTC and others
                    url = f"{BASE_URL}/transaction/{tx_hash}"
                
                response = requests.get(url, headers=HEADERS)
                response.raise_for_status()
                result = response.json()
                
                # Format the response in a user-friendly way
                currency = result.get("currency", "cryptocurrency")
                if currency.upper() == "BTC":
                    # Format Bitcoin transaction in a friendly, human-readable way
                    inputs_value = sum(inp.get("prev_out", {}).get("value", 0) for inp in result.get("inputs", []))
                    outputs_value = sum(out.get("value", 0) for out in result.get("out", []))
                    fee = inputs_value - outputs_value
                    
                    # Get confirmation status
                    status = 'Confirmed' if result.get('block_height') else 'Pending confirmation'
                    
                    formatted_result = f"📊 **Bitcoin Transaction Details**\n\n"
                    formatted_result += f"✅ Status: {status}\n"
                    
                    if result.get('block_height'):
                        formatted_result += f"🔢 Block: #{result.get('block_height', 'Pending')}\n"
                    
                    # Format time in a friendly way
                    tx_time = datetime.fromtimestamp(result.get('time', 0))
                    formatted_result += f"🕒 Time: {tx_time.strftime('%B %d, %Y at %I:%M %p')}\n\n"
                    
                    # Format amounts with proper BTC symbol and comma separators for readability
                    formatted_result += f"💰 Total Input: {inputs_value / 100000000:,.8f} BTC\n"
                    formatted_result += f"💸 Total Output: {outputs_value / 100000000:,.8f} BTC\n"
                    formatted_result += f"💵 Transaction Fee: {fee / 100000000:,.8f} BTC\n\n"
                    
                    # Add recipients in a more visually appealing format
                    formatted_result += "🔍 **Recipients**:\n"
                    for i, out in enumerate(result.get("out", [])[:5], 1):  # Show first 5 outputs
                        addr = out.get("addr", "Unknown")
                        value = out.get("value", 0) / 100000000
                        # Shorten address for readability
                        short_addr = f"{addr[:8]}...{addr[-8:]}" if len(addr) > 20 else addr
                        formatted_result += f"{i}. {short_addr}: {value:,.8f} BTC\n"
                    
                    if len(result.get("out", [])) > 5:
                        formatted_result += f"...and {len(result.get('out', [])) - 5} more recipients\n"
                        
                    formatted_result += f"\nTransaction Hash: {tx_hash}"
                    
                    return formatted_result
                elif currency.upper() == "ICP":
                    # Format ICP transaction in a more user-friendly way
                    formatted_result = f"🌐 **ICP Transaction Details**\n\n"
                    
                    # Block information with emoji
                    formatted_result += f"🔢 Block Height: {result.get('block_height', 'Genesis')}\n"
                    
                    # Get a nice description of the transaction type
                    transfer_type = result.get('transfer_type', 'Unknown').lower()
                    type_emoji = "🏭" if transfer_type == "mint" else "🔥" if transfer_type == "burn" else "💸"
                    type_description = {
                        "mint": "Token Creation (Mint)",
                        "burn": "Token Destruction (Burn)",
                        "transfer": "Standard Transfer"
                    }.get(transfer_type, transfer_type.capitalize())
                    
                    formatted_result += f"{type_emoji} Type: {type_description}\n\n"
                    
                    # Format sender/receiver with emojis and shortened addresses for readability
                    from_account = result.get('from_account_identifier')
                    to_account = result.get('to_account_identifier', 'Unknown')
                    
                    if from_account:
                        short_from = f"{from_account[:8]}...{from_account[-8:]}"
                        formatted_result += f"📤 From: {short_from}\n"
                    else:
                        formatted_result += f"📤 From: Genesis (Token Creation)\n"
                    
                    short_to = f"{to_account[:8]}...{to_account[-8:]}" if len(to_account) > 20 else to_account
                    formatted_result += f"📥 To: {short_to}\n\n"
                    
                    # Format amount with proper ICP formatting
                    amount_e8s = int(result.get('amount', 0))
                    amount_icp = amount_e8s / 100000000
                    formatted_result += f"💰 Amount: {amount_icp:,.8f} ICP\n"
                    
                    # Format fee with proper ICP formatting
                    fee_e8s = int(result.get('fee', 0))
                    fee_icp = fee_e8s / 100000000
                    formatted_result += f"💵 Fee: {fee_icp:,.8f} ICP\n\n"
                    
                    # Format time in a friendly way
                    created_at = result.get('created_at', 0)
                    if created_at:
                        tx_time = datetime.fromtimestamp(created_at)
                        formatted_result += f"🕒 Time: {tx_time.strftime('%B %d, %Y at %I:%M %p')}\n"
                    
                    # Add memo if available
                    if result.get('memo'):
                        formatted_result += f"📝 Memo: {result.get('memo')}\n"
                    
                    formatted_result += f"\nTransaction Hash: {tx_hash}"
                    
                    return formatted_result
                elif currency.upper() == "ETH":
                    # Format Ethereum transaction in a user-friendly way
                    formatted_result = f"💎 **Ethereum Transaction Details**\n\n"
                    
                    # Block information with emoji
                    formatted_result += f"🔢 Block: #{result.get('block_id', 'Pending')}\n"
                    
                    # Status information
                    status = result.get('status', 'Unknown')
                    status_emoji = "✅" if status == "success" else "❌" if status == "failed" else "⏳"
                    formatted_result += f"{status_emoji} Status: {status.capitalize()}\n"
                    
                    # Format time in a friendly way
                    if result.get('time'):
                        tx_time = datetime.fromtimestamp(result.get('time', 0))
                        formatted_result += f"🕒 Time: {tx_time.strftime('%B %d, %Y at %I:%M %p')}\n\n"
                    
                    # Format from/to addresses
                    from_addr = result.get('from', '')
                    to_addr = result.get('to', '')
                    
                    if from_addr:
                        short_from = f"{from_addr[:8]}...{from_addr[-8:]}" if len(from_addr) > 20 else from_addr
                        formatted_result += f"📤 From: {short_from}\n"
                    
                    if to_addr:
                        short_to = f"{to_addr[:8]}...{to_addr[-8:]}" if len(to_addr) > 20 else to_addr
                        formatted_result += f"📥 To: {short_to}\n\n"
                    
                    # Format value with proper ETH formatting
                    value_eth = result.get('value', 0)
                    formatted_result += f"💰 Amount: {value_eth:,.6f} ETH\n"
                    
                    # Format gas information
                    gas_used = result.get('gas_used', 0)
                    gas_limit = result.get('gas_limit', 0)
                    gas_price_gwei = result.get('gas_price', 0) / 1e9  # Convert Wei to Gwei
                    
                    formatted_result += f"⛽ Gas Used: {gas_used:,} / {gas_limit:,}\n"
                    formatted_result += f"⛽ Gas Price: {gas_price_gwei:.2f} Gwei\n"
                    
                    # Format fee
                    fee_eth = result.get('fee', 0)
                    formatted_result += f"💵 Transaction Fee: {fee_eth:,.6f} ETH\n\n"
                    
                    # Add contract interaction info if available
                    if result.get('calls') and len(result.get('calls', [])) > 0:
                        formatted_result += "📝 **Contract Interactions**:\n"
                        for i, call in enumerate(result.get('calls', [])[:3], 1):
                            call_to = call.get('to', 'Unknown')
                            short_to = f"{call_to[:8]}...{call_to[-8:]}" if len(call_to) > 20 else call_to
                            formatted_result += f"{i}. To: {short_to}\n"
                            if call.get('value', 0) > 0:
                                call_value = float(call.get('value', 0)) / 1e18
                                formatted_result += f"   Value: {call_value:,.6f} ETH\n"
                        
                        if len(result.get('calls', [])) > 3:
                            formatted_result += f"...and {len(result.get('calls', [])) - 3} more interactions\n"
                    
                    formatted_result += f"\nTransaction Hash: {tx_hash}"
                    
                    return formatted_result
                else:
                    # Generic format for other currencies
                    return f"Transaction details for {tx_hash}:\n{json.dumps(result, indent=2)}"
                    
            except Exception as e:
                ctx.logger.error(f"Error fetching transaction details: {str(e)}")
                return f"I found a transaction hash ({tx_hash}) in your query, but couldn't retrieve details: {str(e)}"
        
        # Handle cases where user refers to "my wallet" without specifying an address
        elif uses_generic_wallet_reference:
            # Determine which wallet to use based on context
            if is_icp_query and wallet_memory.has_wallet(f"{sender}_icp"):
                # Use ICP wallet
                remembered_address = wallet_memory.get_wallet(f"{sender}_icp")
                query = f"{query} for ICP address {remembered_address}"
                ctx.logger.info(f"Using remembered ICP address: {remembered_address} for user: {sender}")
                
                # Add a note about using saved address to improve transparency
                query_note = f"\n\n(Note: I'm using your saved ICP address: {remembered_address[:8]}...{remembered_address[-8:]})"
                
            elif is_eth_query and wallet_memory.has_wallet(f"{sender}_eth"):
                # Use Ethereum wallet
                remembered_address = wallet_memory.get_wallet(f"{sender}_eth")
                query = f"{query} for Ethereum address {remembered_address}"
                ctx.logger.info(f"Using remembered Ethereum address: {remembered_address} for user: {sender}")
                
                # Add a note about using saved address to improve transparency
                query_note = f"\n\n(Note: I'm using your saved Ethereum address: {remembered_address})"
                
            elif wallet_memory.has_wallet(sender):
                # Use Bitcoin wallet
                remembered_address = wallet_memory.get_wallet(sender)
                query = f"{query} for Bitcoin address {remembered_address}"
                ctx.logger.info(f"Using remembered Bitcoin address: {remembered_address} for user: {sender}")
                
                # Add a note about using saved address to improve transparency
                query_note = f"\n\n(Note: I'm using your saved Bitcoin address: {remembered_address})"
            else:
            # No wallet saved - provide helpful instructions
                if is_eth_query:
                    currency_type = "Ethereum"
                elif is_icp_query:
                    currency_type = "ICP"
                else:
                    currency_type = "Bitcoin"
                return f"I don't have a saved {currency_type} wallet address for you yet. Please provide a {currency_type} address so I can help you with your query. Once you do, I'll remember it for future conversations."        # Step 1: Initial call to ASI1 with user query and tools
        initial_system_message = {
            "role": "system",
            "content": "You are a cryptocurrency and blockchain specialist. You ONLY answer questions related to cryptocurrency, blockchain, Web3, DeFi, NFTs, and related technologies. If a user asks about a topic unrelated to cryptocurrency or blockchain, politely explain that you can only assist with cryptocurrency-related questions."
        }
        
        initial_message = {
            "role": "user",
            "content": query
        }
        
        payload = {
            "model": ASI1_MODEL,
            "messages": [initial_system_message, initial_message],
            "tools": tools,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        try:
            ctx.logger.info(f"Initial API request to {ASI1_BASE_URL}/chat/completions with model {payload['model']}")
            ctx.logger.info(f"API request payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{ASI1_BASE_URL}/chat/completions",
                headers=ASI1_HEADERS,
                json=payload
            )
            
            if response.status_code != 200:
                ctx.logger.error(f"API Error: {response.status_code} - {response.text}")
                # Try with a different model as fallback
                payload["model"] = "claude-3-haiku-20240307"
                ctx.logger.info(f"Retrying with model {payload['model']}")
                response = requests.post(
                    f"{ASI1_BASE_URL}/chat/completions",
                    headers=ASI1_HEADERS,
                    json=payload
                )
                
            response.raise_for_status()
            response_json = response.json()
        except Exception as e:
            ctx.logger.error(f"Error calling ASI1 API: {str(e)}")
            raise

        # Step 2: Parse tool calls from response
        tool_calls = response_json["choices"][0]["message"].get("tool_calls", [])
        # Store the assistant's message without the system message to avoid duplication
        messages_history = [initial_message, response_json["choices"][0]["message"]]

        # Debug information
        ctx.logger.info(f"ASI1 response: {json.dumps(response_json, indent=2)}")
        ctx.logger.info(f"Tool calls detected: {len(tool_calls)}")
        
        if not tool_calls:
           
            tx_hash_pattern = r'\b[a-fA-F0-9]{64}\b'  # Matches 64 character hex string (standard for tx hashes)
            eth_tx_pattern = r'\b0x[a-fA-F0-9]{64}\b'  # Matches Ethereum transaction format
            
            tx_match = re.search(tx_hash_pattern, query)
            eth_tx_match = re.search(eth_tx_pattern, query)
            
            if eth_tx_match:
                # Found what looks like an Ethereum transaction hash
                tx_hash = eth_tx_match.group(0)
                ctx.logger.info(f"Detected Ethereum transaction hash: {tx_hash}")
                
                try:
                    # Use the Ethereum transaction endpoint
                    url = f"{BASE_URL}/ethereum/transaction/{tx_hash}"
                    response = requests.get(url, headers=HEADERS)
                    response.raise_for_status()
                    result = response.json()
                    
                    # Add ETH currency marker
                    result["currency"] = "ETH"
                    
                    # Format Ethereum transaction in a user-friendly way
                    formatted_result = f"💎 **Ethereum Transaction Details**\n\n"
                    
                    # Block information with emoji
                    formatted_result += f"🔢 Block: #{result.get('block_id', 'Pending')}\n"
                    
                    # Status information
                    status = result.get('status', 'Unknown')
                    status_emoji = "✅" if status == "success" else "❌" if status == "failed" else "⏳"
                    formatted_result += f"{status_emoji} Status: {status.capitalize()}\n"
                    
                    # Format time in a friendly way
                    if result.get('time'):
                        tx_time = datetime.fromtimestamp(result.get('time', 0))
                        formatted_result += f"🕒 Time: {tx_time.strftime('%B %d, %Y at %I:%M %p')}\n\n"
                    
                    # Format from/to addresses
                    from_addr = result.get('from', '')
                    to_addr = result.get('to', '')
                    
                    if from_addr:
                        short_from = f"{from_addr[:8]}...{from_addr[-8:]}" if len(from_addr) > 20 else from_addr
                        formatted_result += f"📤 From: {short_from}\n"
                    
                    if to_addr:
                        short_to = f"{to_addr[:8]}...{to_addr[-8:]}" if len(to_addr) > 20 else to_addr
                        formatted_result += f"📥 To: {short_to}\n\n"
                    
                    # Format value with proper ETH formatting
                    value_eth = result.get('value', 0)
                    formatted_result += f"💰 Amount: {value_eth:,.6f} ETH\n"
                    
                    # Format gas information
                    gas_used = result.get('gas_used', 0)
                    gas_limit = result.get('gas_limit', 0)
                    gas_price_gwei = result.get('gas_price', 0) / 1e9  # Convert Wei to Gwei
                    
                    formatted_result += f"⛽ Gas Used: {gas_used:,} / {gas_limit:,}\n"
                    formatted_result += f"⛽ Gas Price: {gas_price_gwei:.2f} Gwei\n"
                    
                    # Format fee
                    fee_eth = result.get('fee', 0)
                    formatted_result += f"💵 Transaction Fee: {fee_eth:,.6f} ETH\n\n"
                    
                    formatted_result += f"\nTransaction Hash: {tx_hash}"
                    
                    return formatted_result
                except Exception as e:
                    ctx.logger.error(f"Error fetching Ethereum transaction details: {str(e)}")
                    return f"I found an Ethereum transaction hash ({tx_hash}) in your query, but couldn't retrieve details: {str(e)}"
            elif tx_match:
                # Found what looks like a transaction hash
                tx_hash = tx_match.group(0)
                ctx.logger.info(f"Detected transaction hash: {tx_hash}")
                
                try:
                    # Use the generic transaction endpoint that automatically detects BTC vs ICP
                    url = f"{BASE_URL}/transaction/{tx_hash}"
                    response = requests.get(url, headers=HEADERS)
                    response.raise_for_status()
                    result = response.json()
                    
                    formatted_result = f"Transaction details for {tx_hash}:\n{json.dumps(result, indent=2)}"
                    return formatted_result
                except Exception as e:
                    ctx.logger.error(f"Error fetching transaction details: {str(e)}")
                    # Provide a more helpful error message with suggestions
                    error_message = f"I noticed what appears to be a transaction hash ({tx_hash}) in your query, but I couldn't retrieve the details. "
                    
                    if "404" in str(e):
                        error_message += "This transaction doesn't appear to exist in the blockchain database. Please double-check the hash for accuracy."
                    elif "429" in str(e):
                        error_message += "The blockchain service is currently rate limiting requests. Please try again in a few moments."
                    elif "500" in str(e) or "502" in str(e) or "503" in str(e):
                        error_message += "The blockchain service is experiencing technical difficulties. Please try again later."
                    else:
                        error_message += f"Error details: {str(e)}"
                    
                    error_message += "\n\nYou can try:\n" + \
                                    "1. Verifying the transaction hash is correct\n" + \
                                    "2. Specifying which blockchain (Bitcoin, Ethereum, or ICP) this transaction belongs to\n" + \
                                    "3. Trying again in a few moments if this is a very recent transaction"
                    
                    return error_message
            
            # If no transaction hash or tool calls, check if the question is about cryptocurrency
            # First, query ASI1 to check if this is a cryptocurrency-related question
            check_crypto_payload = {
                "model": ASI1_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a cryptocurrency expert assistant. Your task is to analyze if the user's question is related to cryptocurrency or blockchain technology. Respond with 'YES' if the question is about cryptocurrency, blockchain, or related topics. Otherwise, respond with 'NO'. Do not explain your reasoning, just respond with YES or NO."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 5
            }
            
            # Call ASI1 API to check if it's a crypto question
            try:
                ctx.logger.info(f"Crypto check API request with model {check_crypto_payload['model']}")
                
                check_response = requests.post(
                    f"{ASI1_BASE_URL}/chat/completions",
                    headers=ASI1_HEADERS,
                    json=check_crypto_payload
                )
                # Try with a different model if the first one fails
                if check_response.status_code != 200:
                    ctx.logger.error(f"Crypto check API Error: {check_response.status_code} - {check_response.text}")
                    # Try with a different model as fallback
                    check_crypto_payload["model"] = "claude-3-haiku-20240307"
                    ctx.logger.info(f"Retrying crypto check with model {check_crypto_payload['model']}")
                    check_response = requests.post(
                        f"{ASI1_BASE_URL}/chat/completions",
                        headers=ASI1_HEADERS,
                        json=check_crypto_payload
                    )
                
                check_response.raise_for_status()
                check_result = check_response.json()
                crypto_check = check_result["choices"][0]["message"]["content"].strip().upper()
                
                ctx.logger.info(f"Crypto check result: {crypto_check}")
                
                # If ASI1 confirms this is about cryptocurrency, proceed with answering
                if crypto_check == "YES":
                    ctx.logger.info("Cryptocurrency-related question detected. Using ASI1 API response directly.")
                    return response_json["choices"][0]["message"]["content"]
                else:
                    # If not crypto-related, return a message that the assistant is for crypto only
                    return "I'm a cryptocurrency assistant and can only answer questions related to cryptocurrency and blockchain technology. Please ask me questions about:\n\n" + \
                           "• Cryptocurrencies like Bitcoin, Ethereum, ICP and others\n" + \
                           "• Blockchain technology and concepts\n" + \
                           "• Wallets, transactions, and addresses\n" + \
                           "• Crypto market information\n" + \
                           "• Smart contracts and DeFi\n\n" + \
                           "If you're looking for general information unrelated to cryptocurrency, please try a different assistant."
                           
            except Exception as e:
                ctx.logger.error(f"Error checking if query is cryptocurrency-related: {str(e)}")
                
                # Fallback to keyword-based detection
                crypto_keywords = [
                    'bitcoin', 'btc', 'ethereum', 'eth', 'cryptocurrency', 'crypto', 'blockchain', 
                    'token', 'coin', 'mining', 'wallet', 'ledger', 'transaction', 'block', 'icp', 
                    'internet computer', 'altcoin', 'defi', 'nft', 'satoshi', 'nakamoto', 'vitalik', 
                    'buterin', 'smart contract', 'gas', 'gwei', 'wei', 'satoshis', 'fork', 'halving',
                    'hash', 'address', 'private key', 'public key', 'exchange', 'binance', 'coinbase',
                    'metamask', 'dex', 'decentralized', 'consensus', 'proof of work', 'proof of stake'
                ]
                
                # Check if query contains cryptocurrency-related terms
                is_crypto_query = any(keyword in query.lower() for keyword in crypto_keywords)
                
                if is_crypto_query:
                    # If it's a crypto-related query, use the ASI1 response directly
                    ctx.logger.info("Crypto-related question detected via keywords. Using ASI1 API response directly.")
                    return response_json["choices"][0]["message"]["content"]
                else:
                    # If not crypto-related, return a helpful message
                    return "I'm a cryptocurrency assistant and can only answer questions related to cryptocurrency and blockchain technology. Please ask me questions about:\n\n" + \
                           "• Cryptocurrencies like Bitcoin, Ethereum, ICP and others\n" + \
                           "• Blockchain technology and concepts\n" + \
                           "• Wallets, transactions, and addresses\n" + \
                           "• Crypto market information\n" + \
                           "• Smart contracts and DeFi\n\n" + \
                           "If you're looking for general information unrelated to cryptocurrency, please try a different assistant."

        # Step 3: Execute tools and format results
        for tool_call in tool_calls:
            func_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])
            tool_call_id = tool_call["id"]

            ctx.logger.info(f"Executing {func_name} with arguments: {arguments}")

            try:
                result = await call_icp_endpoint(func_name, arguments)
                content_to_send = json.dumps(result)
            except Exception as e:
                error_content = {
                    "error": f"Tool execution failed: {str(e)}",
                    "status": "failed"
                }
                content_to_send = json.dumps(error_content)

            tool_result_message = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content_to_send
            }
            messages_history.append(tool_result_message)

        # Step 4: Send results back to ASI1 for final answer
        # Make sure the system message is first (remove any existing system messages)
        messages_history = [msg for msg in messages_history if msg.get("role") != "system"]
        messages_history.insert(0, {
            "role": "system",
            "content": "You are a cryptocurrency and blockchain specialist. You ONLY answer questions related to cryptocurrency, blockchain, Web3, DeFi, NFTs, and related technologies. If a user asks about a topic unrelated to cryptocurrency or blockchain, politely explain that you can only assist with cryptocurrency-related questions."
        })
        
        final_payload = {
            "model": ASI1_MODEL,
            "messages": messages_history,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        try:
            final_response = requests.post(
                f"{ASI1_BASE_URL}/chat/completions",
                headers=ASI1_HEADERS,
                json=final_payload
            )
            # Log the full request and response for debugging
            ctx.logger.info(f"Final API request: {json.dumps(final_payload, indent=2)}")
            
            # Try with a different model if the first one fails
            if final_response.status_code != 200:
                ctx.logger.error(f"Final API Error: {final_response.status_code} - {final_response.text}")
                # Try with a different model as fallback
                final_payload["model"] = "claude-3-haiku-20240307"
                # Remove tool-specific fields that might be causing issues
                if "tool_calls" in final_payload:
                    del final_payload["tool_calls"]
                
                # Make sure we're using the correct API endpoint
                final_response = requests.post(
                    f"{ASI1_BASE_URL}/chat/completions",
                    headers=ASI1_HEADERS,
                    json=final_payload
                )
                
            final_response.raise_for_status()
            final_response_json = final_response.json()
        except Exception as e:
            ctx.logger.error(f"Error in final API call: {str(e)}")
            raise

        # Step 5: Return the model's final answer
        final_answer = final_response_json["choices"][0]["message"]["content"]
        
        # If we're using a remembered address, append the query note
        if uses_generic_wallet_reference and ('query_note' in locals()):
            final_answer += query_note
            
        return final_answer

    except Exception as e:
        ctx.logger.error(f"Error processing query: {str(e)}")
        error_message = "I apologize, but I encountered an issue while processing your request. "
        
        if "connection" in str(e).lower():
            error_message += "I'm having trouble connecting to the blockchain service right now. "
            error_message += "This might be a temporary network issue. Please try again in a few moments."
        elif "timeout" in str(e).lower():
            error_message += "The request to the blockchain service timed out. "
            error_message += "This usually happens when the service is busy. Please try again shortly."
        elif "not found" in str(e).lower() or "404" in str(e):
            error_message += "I couldn't find the information you requested. "
            error_message += "Please check that any addresses or transaction hashes are correct."
        elif "400" in str(e) and "asi1.ai" in str(e):
            error_message += "There was an issue with the AI service. "
            error_message += "This could be due to an invalid API key or model name. "
            error_message += "Please contact the administrator to check the ASI1 API configuration."
        else:
            error_message += f"Error details: {str(e)}"
        
        return error_message

agent = Agent(
    name='CryptoFinder',
    port=8001,
    endpoint=["http://localhost:8001/submit"],
    # mailbox=True,
    # network = "mainnet"
)
chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    try:
        ack = ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id
        )
        await ctx.send(sender, ack)

        for item in msg.content:
            if isinstance(item, StartSessionContent):
                ctx.logger.info(f"Got a start session message from {sender}")
                continue
            elif isinstance(item, TextContent):
                ctx.logger.info(f"Got a message from {sender}: {item.text}")
                # Pass the sender ID to process_query for wallet memory
                response_text = await process_query(item.text, ctx, sender)
                ctx.logger.info(f"Response text: {response_text}")
                response = ChatMessage(
                    timestamp=datetime.now(timezone.utc),
                    msg_id=uuid4(),
                    content=[TextContent(type="text", text=response_text)]
                )
                await ctx.send(sender, response)
            else:
                ctx.logger.info(f"Got unexpected content from {sender}")
    except Exception as e:
        ctx.logger.error(f"Error handling chat message: {str(e)}")
        
        # Create a more user-friendly error message
        error_message = "I apologize, but I encountered an unexpected issue while processing your message. "
        
        if "connection" in str(e).lower():
            error_message += "I'm having trouble connecting to the blockchain service right now. "
            error_message += "This might be a temporary network issue. Please try again in a few moments."
        elif "timeout" in str(e).lower():
            error_message += "The request to the blockchain service timed out. "
            error_message += "This usually happens when the service is busy. Please try again shortly."
        else:
            error_message += "Please try again or rephrase your question."
            
        error_response = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[TextContent(type="text", text=error_message)]
        )
        await ctx.send(sender, error_response)

@chat_proto.on_message(model=ChatAcknowledgement)
async def handle_chat_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")
    if msg.metadata:
        ctx.logger.info(f"Metadata: {msg.metadata}")

agent.include(chat_proto)

if __name__ == "__main__":
    agent.run()


"""
Queries for /get-balance
What's the balance of address bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs?

Can you check how many bitcoins are in bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs?

Show me the balance of this Bitcoin wallet: bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs.

🧾 Queries for /get-utxos
What UTXOs are available for address bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs?

List unspent outputs for bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs.

Do I have any unspent transactions for bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs?

🧾 Queries for /get-current-fee-percentiles
What are the current Bitcoin fee percentiles?

Show me the latest fee percentile distribution.

How much are the Bitcoin network fees right now?

🧾 Queries for /get-p2pkh-address
What is my canister's P2PKH address?

Generate a Bitcoin address for me.

Give me a Bitcoin address I can use to receive coins.
"""

# Test section - uncomment to test directly
if __name__ == "__main__":
    import asyncio
    
    class TestCtx:
        logger = type("logger", (), {"info": print, "error": print})()
    
    async def test_query():
        # Put your test question here
        test_question = "get balance bitcoin address bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs"
        
        result = await process_query(test_question, TestCtx(), "test_user")
        print(f"Result: {result}")
    
    # Uncomment the line below to run the test
    # asyncio.run(test_query())