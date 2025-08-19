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
ASI1_API_KEY = "sk_fd6898249273444cbf358b150ee8e57373152e1bae7847a1a8f5b3523ea59697"
ASI1_BASE_URL = "https://api.asi1.ai/v1"
ASI1_HEADERS = {
    "Authorization": f"Bearer {ASI1_API_KEY}",
    "Content-Type": "application/json"
}

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

# Function definitions for ASI1 function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_fee_percentiles",
            "description": "Gets the current Bitcoin fee percentiles measured in satoshi/byte.",
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
            "name": "get_balance",
            "description": "Returns the balance of a given Bitcoin address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Bitcoin address to check."
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
            "description": "Returns the UTXOs of a given Bitcoin address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Bitcoin address to fetch UTXOs for."
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
            "description": "Search for comprehensive information about a Bitcoin address including balance and recent transactions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Bitcoin address to search for information."
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
            "description": "Get recent activity and transaction history for a Bitcoin address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Bitcoin address to get activity for."
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
            "name": "generate_wallet",
            "description": "Generate a new Bitcoin wallet address for demonstration purposes.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

async def call_icp_endpoint(func_name: str, args: dict):
    try:
        if func_name == "get_current_fee_percentiles":
            url = f"{BASE_URL}/get-current-fee-percentiles"
            response = requests.post(url, headers=HEADERS, json={})
        elif func_name == "get_balance":
            url = f"{BASE_URL}/get-balance"
            response = requests.post(url, headers=HEADERS, json={"address": args["address"]})
        elif func_name == "get_utxos":
            url = f"{BASE_URL}/get-utxos"
            response = requests.post(url, headers=HEADERS, json={"address": args["address"]})
        elif func_name == "search_address":
            url = f"{BASE_URL}/search-address/{args['address']}"
            response = requests.get(url, headers=HEADERS)
        elif func_name == "address_activity":
            url = f"{BASE_URL}/address-activity/{args['address']}"
            response = requests.get(url, headers=HEADERS)
        elif func_name == "generate_wallet":
            url = f"{BASE_URL}/generate-wallet"
            response = requests.post(url, headers=HEADERS, json={})
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
        # First, check if the query is about "my wallet" or "the wallet" without specifying an address
        wallet_phrases = [
            r"\b(my|the|this|our|last|previous|saved|remembered)\s+wallet\b",
            r"\bwallet\s+(balance|info|address|utxos|details|transactions)\b",
            r"\bshow\s+(me\s+)?(the\s+)?(my\s+)?(wallet|address)\b"
        ]
        
        uses_generic_wallet_reference = any(re.search(pattern, query.lower()) for pattern in wallet_phrases)
        
        # Check if the query contains a Bitcoin address (simple regex for demo)
        bitcoin_address_pattern = r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b'
        address_match = re.search(bitcoin_address_pattern, query)
        
        if address_match:
            # Remember this wallet address for future use
            detected_address = address_match.group(0)
            wallet_memory.remember_wallet(sender, detected_address)
            ctx.logger.info(f"Remembered wallet address: {detected_address} for user: {sender}")
        elif uses_generic_wallet_reference and wallet_memory.has_wallet(sender):
            # Replace generic wallet references with the actual address
            remembered_address = wallet_memory.get_wallet(sender)
            query = f"{query} for address {remembered_address}"
            ctx.logger.info(f"Using remembered wallet address: {remembered_address} for user: {sender}")
        
        # Step 1: Initial call to ASI1 with user query and tools
        initial_message = {
            "role": "user",
            "content": query
        }
        payload = {
            "model": "asi1-mini",
            "messages": [initial_message],
            "tools": tools,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        response = requests.post(
            f"{ASI1_BASE_URL}/chat/completions",
            headers=ASI1_HEADERS,
            json=payload
        )
        response.raise_for_status()
        response_json = response.json()

        # Step 2: Parse tool calls from response
        tool_calls = response_json["choices"][0]["message"].get("tool_calls", [])
        messages_history = [initial_message, response_json["choices"][0]["message"]]

        if not tool_calls:
            return "I couldn't determine what Bitcoin information you're looking for. Please try rephrasing your question."

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
        final_payload = {
            "model": "asi1-mini",
            "messages": messages_history,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        final_response = requests.post(
            f"{ASI1_BASE_URL}/chat/completions",
            headers=ASI1_HEADERS,
            json=final_payload
        )
        final_response.raise_for_status()
        final_response_json = final_response.json()

        # Step 5: Return the model's final answer
        return final_response_json["choices"][0]["message"]["content"]

    except Exception as e:
        ctx.logger.error(f"Error processing query: {str(e)}")
        return f"An error occurred while processing your request: {str(e)}"

agent = Agent(
    name='test-ICP-agent',
    port=8001,
    mailbox=True
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
        error_response = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[TextContent(type="text", text=f"An error occurred: {str(e)}")]
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