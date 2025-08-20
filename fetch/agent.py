import requests
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
BASE_URL = "http://localhost:8083"  # Changed to match api_gateway.py port

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
            url = f"{BASE_URL}/get-current-fee-percentiles"
            response = requests.post(url, headers=HEADERS, json={"currency": currency})
        elif func_name == "get_balance":
            url = f"{BASE_URL}/get-balance"
            response = requests.post(url, headers=HEADERS, json={"address": args["address"], "currency": currency})
        elif func_name == "get_utxos":
            url = f"{BASE_URL}/get-utxos"
            response = requests.post(url, headers=HEADERS, json={"address": args["address"], "currency": currency})
        elif func_name == "search_address":
            url = f"{BASE_URL}/search-address/{args['address']}"
            response = requests.get(url, headers=HEADERS, params={"currency": currency})
        elif func_name == "address_activity":
            url = f"{BASE_URL}/address-activity/{args['address']}"
            response = requests.get(url, headers=HEADERS, params={"currency": currency})
        elif func_name == "generate_wallet":
            url = f"{BASE_URL}/generate-wallet"
            response = requests.post(url, headers=HEADERS, json={"currency": currency})
        elif func_name == "get_bitcoin_transaction":
            # Handle Bitcoin transaction lookup
            tx_hash = args["tx_hash"]
            # Use our API gateway endpoint for Bitcoin transactions
            url = f"{BASE_URL}/transaction/{tx_hash}"  # Use the smart transaction endpoint
            response = requests.get(url, headers=HEADERS)
            
        # ICP specific endpoints
        elif func_name == "get_icp_account_info":
            url = f"{BASE_URL}/icp/account/{args['address']}"
            response = requests.get(url, headers=HEADERS)
        elif func_name == "get_icp_transaction":
            url = f"{BASE_URL}/icp/transaction/{args['tx_hash']}"
            response = requests.get(url, headers=HEADERS)
        elif func_name == "get_icp_account_transactions":
            # New function to specifically handle ICP account transactions
            address = args["address"]
            limit = args.get("limit", 10)
            url = f"{BASE_URL}/icp/account/{address}/transactions"
            params = {
                "limit": limit,
                "from_account": address,
                "to_account": address
            }
            response = requests.get(url, headers=HEADERS, params=params)
        elif func_name == "get_icp_blocks":
            start = args.get("start", 0)
            limit = args.get("limit", 10)
            url = f"{BASE_URL}/icp/blocks"
            response = requests.get(url, headers=HEADERS, params={"start": start, "limit": limit})
        elif func_name == "get_icp_fees":
            url = f"{BASE_URL}/icp/fees"
            response = requests.get(url, headers=HEADERS)
            
        # Ethereum specific endpoints
        elif func_name == "get_ethereum_account_info":
            url = f"{BASE_URL}/ethereum/account/{args['address']}"
            response = requests.get(url, headers=HEADERS)
        elif func_name == "get_ethereum_tokens":
            url = f"{BASE_URL}/ethereum/tokens/{args['address']}"
            response = requests.get(url, headers=HEADERS)
        elif func_name == "get_ethereum_transaction":
            url = f"{BASE_URL}/ethereum/transaction/{args['tx_hash']}"
            response = requests.get(url, headers=HEADERS)
        else:
            raise ValueError(f"Unsupported function call: {func_name}")
        
        # Print response for debugging
        print(f"Response from {url}: {response.status_code}")
        print(f"Response content: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling {func_name}: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        raise

async def process_query(query: str, ctx: Context, sender: str = "anonymous") -> str:
    try:
        # First, check if the query contains a transaction hash
        tx_hash_pattern = r'\b[a-fA-F0-9]{64}\b'  # Matches 64 character hex string (standard for tx hashes)
        eth_tx_pattern = r'\b0x[a-fA-F0-9]{64}\b'  # Matches Ethereum transaction hash format
        
        tx_match = re.search(tx_hash_pattern, query)
        eth_tx_match = re.search(eth_tx_pattern, query)
        
        # Check if query mentions specific blockchains
        is_icp_query = bool(re.search(r'\b(icp|internet computer|dfinity)\b', query.lower()))
        is_eth_query = bool(re.search(r'\b(eth|ethereum|erc20|tokens)\b', query.lower()))
        
        # Check for wallet references
        wallet_phrases = [
            r"\b(my|the|this|our|last|previous|saved|remembered)\s+wallet\b",
            r"\bwallet\s+(balance|info|address|utxos|details|transactions)\b",
            r"\bshow\s+(me\s+)?(the\s+)?(my\s+)?(wallet|address)\b"
        ]
        uses_generic_wallet_reference = any(re.search(pattern, query.lower()) for pattern in wallet_phrases)
        
        # Bitcoin address pattern (more specific)
        bitcoin_address_pattern = r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b'
        # ICP account identifier pattern (more specific)
        icp_address_pattern = r'\b[a-f0-9]{64}\b'  # 64-character hex string for ICP account identifiers
        # Ethereum address pattern
        ethereum_address_pattern = r'\b0x[a-fA-F0-9]{40}\b'  # 0x followed by 40 hex characters
        
        # Find address matches
        btc_address_match = re.search(bitcoin_address_pattern, query)
        eth_address_match = re.search(ethereum_address_pattern, query)
        
        # For ICP addresses, only consider hex strings that aren't transaction hashes
        # This is a heuristic since both can be 64-char hex strings
        potential_icp_addresses = re.finditer(icp_address_pattern, query)
        icp_address_match = None
        
        # If query is specifically about ICP and contains a 64-char hex that isn't clearly
        # described as a transaction, treat it as an ICP account
        if is_icp_query:
            for match in potential_icp_addresses:
                # Look for contextual clues that this is an account, not a transaction
                address_context = query.lower()
                match_pos = match.start()
                prefix_text = address_context[max(0, match_pos-20):match_pos]
                
                # If it's clearly mentioned as an account/address, use it
                account_indicators = ['account', 'address', 'wallet', 'balance']
                if any(indicator in prefix_text for indicator in account_indicators):
                    icp_address_match = match
                    break
            
            # If no match with context, and there's only one hex string and it's mentioned with ICP
            # assume it's an account if not in clear transaction context
            if not icp_address_match and tx_match:
                tx_match_pos = tx_match.start()
                surrounding_text = query.lower()[max(0, tx_match_pos-15):tx_match_pos+tx_match.end()+15]
                
                # Check if it's clearly a transaction
                tx_indicators = ['transaction', 'tx', 'hash', 'block']
                is_tx = any(indicator in surrounding_text for indicator in tx_indicators)
                
                # If not clearly a transaction, it might be an account
                if not is_tx and is_icp_query:
                    icp_address_match = tx_match
                    # Nullify the transaction match since we're treating it as an account
                    tx_match = None
        
        # Process addresses if found
        if btc_address_match:
            # Remember this wallet address for future use
            detected_address = btc_address_match.group(0)
            wallet_memory.remember_wallet(sender, detected_address)
            ctx.logger.info(f"Remembered Bitcoin wallet address: {detected_address} for user: {sender}")
            
            # If the query is looking for specific info, try to directly satisfy it
            if "balance" in query.lower():
                # Directly call the balance API
                try:
                    response = await call_icp_endpoint("get_balance", {"address": detected_address, "currency": "BTC"})
                    
                    # Format response in a user-friendly way
                    confirmed_sats = response.get("confirmed", 0)
                    unconfirmed_sats = response.get("unconfirmed", 0)
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
                           f"_(Current BTC/USD price data not available. Add a cryptocurrency price API to show USD equivalent.)_"
                except Exception as e:
                    ctx.logger.error(f"Error getting balance: {str(e)}")
                    return f"I found the Bitcoin address {detected_address}, but I couldn't fetch its current balance. The blockchain API might be temporarily unavailable."
        
        elif eth_address_match:
            # Remember this Ethereum wallet address for future use
            detected_address = eth_address_match.group(0)
            wallet_memory.remember_wallet(f"{sender}_eth", detected_address)
            ctx.logger.info(f"Remembered Ethereum wallet address: {detected_address} for user: {sender}")
            
            # If the query is looking for specific info, try to directly satisfy it
            if "balance" in query.lower():
                # Directly call the Ethereum balance API
                try:
                    response = await call_icp_endpoint("get_ethereum_account_info", {"address": detected_address})
                    
                    # Format response in a user-friendly way
                    balance_wei = response.get("balance_wei", 0)
                    balance_eth = response.get("balance_eth", 0)
                    
                    return f"💰 **Ethereum Wallet Balance**\n\n" \
                           f"Address: `{detected_address}`\n\n" \
                           f"Balance: {balance_eth:.6f} ETH\n" \
                           f"Transaction Count: {response.get('transaction_count', 0)}\n\n" \
                           f"_(Current ETH/USD price data not available. Add a cryptocurrency price API to show USD equivalent.)_"
                except Exception as e:
                    ctx.logger.error(f"Error getting Ethereum balance: {str(e)}")
                    return f"I found the Ethereum address {detected_address}, but I couldn't fetch its current balance. The blockchain API might be temporarily unavailable."
            
            # If the query is looking for tokens
            elif any(token_term in query.lower() for token_term in ["token", "erc20", "erc-20"]):
                try:
                    response = await call_icp_endpoint("get_ethereum_tokens", {"address": detected_address})
                    tokens = response.get("tokens", [])
                    
                    if not tokens:
                        return f"The Ethereum address `{detected_address}` doesn't have any ERC-20 token balances."
                    
                    # Format token balances in a readable way
                    result = f"🪙 **ERC-20 Tokens for `{detected_address}`**\n\n"
                    
                    # Sort tokens by balance value (highest first)
                    tokens.sort(key=lambda x: x.get("balance", 0), reverse=True)
                    
                    for token in tokens:
                        token_name = token.get("name", "Unknown")
                        token_symbol = token.get("symbol", "???")
                        token_balance = token.get("balance", 0)
                        
                        result += f"**{token_name} ({token_symbol})**: {token_balance:,.6f}\n"
                    
                    return result
                except Exception as e:
                    ctx.logger.error(f"Error getting Ethereum tokens: {str(e)}")
                    return f"I found the Ethereum address {detected_address}, but I couldn't fetch its token balances. The blockchain API might be temporarily unavailable."
        elif icp_address_match and is_icp_query:
            # Remember this ICP address for future use
            detected_address = icp_address_match.group(0)
            wallet_memory.remember_wallet(f"{sender}_icp", detected_address)
            ctx.logger.info(f"Remembered ICP address: {detected_address} for user: {sender}")
            
            # If this looks like both a transaction and an address, prefer treating it as an address
            # in an ICP context where the user is asking about an account
            if tx_match and tx_match.group(0) == detected_address:
                tx_match = None  # Nullify the transaction match
        
        # Explicitly handle transaction lookup if found
        if tx_match:
            # Found what looks like a transaction hash
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
            # If we have a transaction hash in the query, try to extract it and call get_transaction
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
    mailbox=True,
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