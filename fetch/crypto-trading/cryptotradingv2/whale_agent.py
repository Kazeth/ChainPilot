from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from shared_types import (
    WhaleRequest, 
    WhaleResponse, 
    PROTOCOL_NAME,
    WHALE_AGENT_ADDRESS
)
import requests
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create Whale Agent
whale_agent = Agent(
    name="whale_agent",
    port=8006,
    endpoint=["http://localhost:8006/submit"],
    seed="whale_agent_seed_phrase"
)

# Fund the agent if balance is low
fund_agent_if_low(whale_agent.wallet.address())

# Define protocol using shared constant
whale_protocol = Protocol(PROTOCOL_NAME)

# API configuration
WHALE_ALERT_API_KEY = "your_whale_alert_api_key"  # Get from https://whale-alert.io/
WHALE_ALERT_URL = "https://api.whale-alert.io/v1/transactions"

def get_whale_transactions(symbol):
    """Get whale transactions from Whale Alert API"""
    try:
        # Extract base currency
        base_currency = symbol.replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        
        # Map symbols to whale alert currency codes
        currency_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binance-coin',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'SOL': 'solana',
            'MATIC': 'polygon'
        }
        
        currency = currency_map.get(base_currency, base_currency.lower())
        
        # If no API key, return mock data
        if WHALE_ALERT_API_KEY == "your_whale_alert_api_key":
            return get_mock_whale_data(base_currency)
        
        # Get transactions from last 24 hours
        start_time = int((datetime.now() - timedelta(hours=24)).timestamp())
        end_time = int(datetime.now().timestamp())
        
        params = {
            'api_key': WHALE_ALERT_API_KEY,
            'start': start_time,
            'end': end_time,
            'currency': currency,
            'min_value': 1000000  # Minimum $1M transactions
        }
        
        response = requests.get(WHALE_ALERT_URL, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        return data.get('transactions', [])
        
    except Exception as e:
        logging.error(f"Error fetching whale data: {e}")
        return get_mock_whale_data(symbol)

def get_mock_whale_data(symbol):
    """Generate mock whale data for demonstration"""
    # Generate realistic-looking whale transactions
    transactions = []
    
    for i in range(random.randint(5, 15)):
        # Random transaction type
        transaction_types = [
            {'from': 'unknown', 'to': 'binance', 'type': 'exchange_inflow'},
            {'from': 'binance', 'to': 'unknown', 'type': 'exchange_outflow'},
            {'from': 'unknown', 'to': 'coinbase', 'type': 'exchange_inflow'},
            {'from': 'coinbase', 'to': 'unknown', 'type': 'exchange_outflow'},
            {'from': 'unknown', 'to': 'unknown', 'type': 'transfer'}
        ]
        
        tx_type = random.choice(transaction_types)
        
        transaction = {
            'id': f"mock_{i}",
            'blockchain': 'bitcoin' if symbol.startswith('BTC') else 'ethereum',
            'symbol': symbol.replace('USDT', '').lower(),
            'amount': random.uniform(50, 500),
            'amount_usd': random.uniform(1000000, 50000000),
            'from': {'address': tx_type['from']},
            'to': {'address': tx_type['to']},
            'timestamp': int((datetime.now() - timedelta(hours=random.randint(0, 24))).timestamp()),
            'transaction_type': tx_type['type']
        }
        
        transactions.append(transaction)
    
    return transactions

def analyze_whale_activity(transactions):
    """Analyze whale transactions to determine market sentiment"""
    if not transactions:
        return 0.0, 0, 0.0, 0.0, 0.0, 0.0
    
    exchange_inflow = 0.0  # Money going TO exchanges (bearish)
    exchange_outflow = 0.0  # Money leaving exchanges (bullish)
    large_transactions = len(transactions)
    
    exchange_addresses = {
        'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okex',
        'kucoin', 'gate.io', 'crypto.com', 'gemini', 'bitstamp'
    }
    
    for tx in transactions:
        amount_usd = tx.get('amount_usd', 0)
        from_addr = tx.get('from', {}).get('address', '').lower()
        to_addr = tx.get('to', {}).get('address', '').lower()
        
        # Check if transaction involves exchanges
        if from_addr in exchange_addresses and to_addr not in exchange_addresses:
            # Outflow from exchange (bullish)
            exchange_outflow += amount_usd
        elif to_addr in exchange_addresses and from_addr not in exchange_addresses:
            # Inflow to exchange (bearish)
            exchange_inflow += amount_usd
    
    # Calculate net flow (positive = more outflow = bullish)
    net_flow = exchange_outflow - exchange_inflow
    
    # Calculate whale score
    total_flow = exchange_inflow + exchange_outflow
    
    if total_flow > 0:
        # Normalize by total flow
        whale_score = net_flow / total_flow
        # Apply logarithmic scaling for large amounts
        if abs(net_flow) > 10000000:  # $10M+
            whale_score *= 1.5
        elif abs(net_flow) > 50000000:  # $50M+
            whale_score *= 2.0
    else:
        whale_score = 0.0
    
    # Clamp score between -1 and 1
    whale_score = max(-1.0, min(1.0, whale_score))
    
    # Calculate confidence based on transaction volume and count
    if large_transactions > 0 and total_flow > 5000000:  # $5M+ total
        confidence = min(0.9, 0.3 + (large_transactions / 20) + (total_flow / 100000000))
    else:
        confidence = 0.1
    
    return whale_score, large_transactions, exchange_inflow, exchange_outflow, net_flow, confidence

@whale_protocol.on_message(model=WhaleRequest)
async def handle_whale_request(ctx: Context, sender: str, msg: WhaleRequest):
    """Handle whale activity analysis requests with JSON logging"""
    ctx.logger.info(f"🐋 WHALE AGENT: Received request for {msg.symbol} from {sender}")
    ctx.logger.info(f"📄 Request JSON: {msg.to_json()}")
    
    try:
        # Get whale transactions
        transactions = get_whale_transactions(msg.symbol)
        
        # Analyze whale activity
        whale_score, large_transactions, exchange_inflow, exchange_outflow, net_flow, confidence = analyze_whale_activity(transactions)
        
        # Create JSON response (updated format)
        response = WhaleResponse(
            symbol=msg.symbol,
            whale_score=whale_score,
            whale_transactions=large_transactions,
            net_whale_flow=net_flow,
            large_transactions=large_transactions,
            average_transaction_size=abs(net_flow / max(large_transactions, 1)),
            confidence=confidence
        )
        
        # Send JSON response with logging
        ctx.logger.info(f"📤 Sending whale JSON response: {response.to_json()}")
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Whale analysis sent for {msg.symbol}: Score={whale_score:.3f}, Transactions={large_transactions}, Net Flow=${net_flow:,.0f}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error in whale analysis: {e}")
        import traceback
        traceback.print_exc()
        
        # Send neutral JSON response on error
        error_response = WhaleResponse(
            symbol=msg.symbol,
            whale_score=0.0,
            whale_transactions=0,
            net_whale_flow=0.0,
            large_transactions=0,
            average_transaction_size=0.0,
            confidence=0.0
        )
        ctx.logger.info(f"📤 Sending error JSON response: {error_response.to_json()}")
        await ctx.send(sender, error_response)

# Include the protocol
whale_agent.include(whale_protocol)

if __name__ == "__main__":
    print(f"Whale Agent address: {whale_agent.address}")
    print("Whale Agent is ready to analyze on-chain activity...")
    if WHALE_ALERT_API_KEY == "your_whale_alert_api_key":
        print("⚠️  Using mock whale data. Get a free API key from https://whale-alert.io/ for real data.")
    whale_agent.run()
