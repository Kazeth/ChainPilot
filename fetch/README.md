# ChainPilot Cryptocurrency Agent

ChainPilot is an AI agent designed to answer cryptocurrency-related questions and fetch blockchain data for both Bitcoin and Internet Computer Protocol (ICP).

## Features

- Answer general cryptocurrency questions
- Fetch real-time Bitcoin blockchain data using Blockchair and MemPool.space APIs
- Fetch Internet Computer Protocol (ICP) blockchain data using the ICP Ledger API
- Remember user wallet addresses for both Bitcoin and ICP
- Support for querying account balances, transaction history, and blockchain information

## Components

### Agent (agent.py)

The main agent file handles:
- User query processing
- Wallet address detection and memory
- Tool definitions for interacting with blockchain APIs
- ASI-1 API integration for AI responses

### API Gateway (api_gateway.py)

The API gateway serves as an interface between the agent and external blockchain APIs:
- Bitcoin data through MemPool.space and Blockchair APIs
- ICP data through the ICP Ledger API
- Endpoints for querying account balances, transactions, and blockchain information

## Usage

1. Start the API gateway:
```bash
uvicorn api_gateway:app --reload
```

2. Run the agent:
```bash
python agent.py
```

3. Sample queries:
   - "What is Bitcoin?"
   - "Show the balance for bc1q...." (Bitcoin address)
   - "Show the balance for rrkah-fqaaa-aaaaa-aaaaq-cai" (ICP address)
   - "What's the current ICP price?"
   - "Show my wallet balance" (after previously using a wallet address)

## Testing

To test the ICP integration:
```bash
python test_icp_integration.py
```

## Adding More Cryptocurrencies

To add support for additional cryptocurrencies:
1. Create a new API service class in api_gateway.py
2. Add new endpoints for the cryptocurrency
3. Update the process_query function in agent.py to detect and handle the new cryptocurrency addresses
4. Add new tool definitions for the cryptocurrency

## Dependencies

See requirements.txt for a full list of dependencies.
