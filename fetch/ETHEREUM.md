# Ethereum Support

ChainPilot has been extended to support Ethereum blockchain queries and operations. This allows users to check balances, view token holdings, and explore transaction details for Ethereum addresses.

## Ethereum Features

- **Address Detection**: The agent automatically detects Ethereum addresses (0x format) in user queries
- **Account Information**: Get balance and transaction count for any Ethereum address
- **Token Support**: View ERC-20 token balances for Ethereum addresses
- **Transaction Details**: Examine the details of any Ethereum transaction

## Ethereum API Endpoints

The following API endpoints are available for Ethereum operations:

- `/ethereum/account/{address}` - Get basic account information for an Ethereum address
- `/ethereum/tokens/{address}` - Get ERC-20 token balances for an Ethereum address
- `/ethereum/transaction/{tx_hash}` - Get details about a specific Ethereum transaction
- `/ethereum/transactions/{address}` - Get recent transactions for an Ethereum address

## Testing Ethereum Support

A test script is provided to verify Ethereum integration:

```bash
# Run the API server
./run_server.sh

# In another terminal, run the test script
./test_ethereum.py --all

# Test specific functionality
./test_ethereum.py --account
./test_ethereum.py --tokens
./test_ethereum.py --transaction
./test_ethereum.py --agent

# Test with a custom address
./test_ethereum.py --address 0xYourEthereumAddress
```

## Example Agent Queries

ChainPilot can now understand and respond to Ethereum-related questions:

- "What's the balance of 0x9af2911f9f15202042378e1576e1fae7f2223251?"
- "What ERC-20 tokens does 0x9af2911f9f15202042378e1576e1fae7f2223251 have?"
- "Tell me about this Ethereum address 0x9af2911f9f15202042378e1576e1fae7f2223251"
- "Show me the details of this Ethereum transaction: 0x4a9a049253964ae756bc8c18a85d3c1f1018b558a56458427b10ccc6f78a036d"

## Implementation Details

The Ethereum support is implemented through:

1. **BlockchairAPI Class**: Extended to detect and handle Ethereum addresses and queries
2. **Ethereum Endpoints**: FastAPI router with specific Ethereum endpoints
3. **Agent Detection**: Enhanced query processing to recognize Ethereum addresses and transactions
4. **Wallet Memory**: Support for remembering Ethereum addresses across sessions
