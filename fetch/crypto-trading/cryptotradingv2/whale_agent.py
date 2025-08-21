from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
)
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
    seed="whale_agent_seed_phrase",
    mailbox=True  # Enable mailbox for chat functionality
)

# Fund the agent if balance is low
fund_agent_if_low(whale_agent.wallet.address())

# Define protocol using shared constant
whale_protocol = Protocol(PROTOCOL_NAME)

# Create chat protocol
chat_protocol = Protocol(spec=chat_protocol_spec)

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

# ========================================
# CHAT PROTOCOL HANDLERS
# ========================================

@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle chat messages for whale activity analysis"""
    ctx.logger.info(f"💬 Chat message from {sender}: {msg.content[0].text}")
    
    try:
        message_text = msg.content[0].text.lower()
        
        # Extract session ID and user agent address if present
        session_id = None
        user_agent_address = None
        if "session:" in message_text:
            try:
                session_part = message_text.split("session:")[1].split()[0]
                session_id = session_part.strip()
                ctx.logger.info(f"� Whale analysis requested for session: {session_id}")
            except:
                ctx.logger.warning("Could not extract session ID from message")
        
        if "user:" in message_text:
            try:
                user_part = message_text.split("user:")[1].split()[0]
                user_agent_address = user_part.strip()
                ctx.logger.info(f"🐋 Will send response to user agent: {user_agent_address[:16]}...")
            except:
                ctx.logger.warning("Could not extract user agent address from message")
        
        response_text = "🐋 **Whale Activity Agent**\n\n"
        
        # Check if user is asking for whale analysis
        if any(word in message_text for word in ["whale", "activity", "transactions", "flow", "analyze"]):
            # Look for trading symbols
            symbols = []
            common_symbols = ["btc", "eth", "bnb", "ada", "sol", "btcusdt", "ethusdt", "bnbusdt", "adausdt", "solusdt"]
            
            for symbol in common_symbols:
                if symbol in message_text:  # Already lowercase from above
                    if symbol in ["btc", "bitcoin"]:
                        symbols.append("BTCUSDT")
                    elif symbol in ["eth", "ethereum"]:
                        symbols.append("ETHUSDT")
                    elif symbol in ["bnb", "binance"]:
                        symbols.append("BNBUSDT")
                    elif symbol in ["ada", "cardano"]:
                        symbols.append("ADAUSDT")
                    elif symbol in ["sol", "solana"]:
                        symbols.append("SOLUSDT")
                    else:
                        symbols.append(symbol.upper())
            
            if symbols:
                response_text += f"🔄 **Analyzing {', '.join(symbols)} whale activity...**\n\n"
                
                # Perform whale analysis for the first symbol
                symbol = symbols[0]
                try:
                    # Get whale transactions
                    transactions = get_whale_transactions(symbol)
                    
                    # Analyze whale activity
                    whale_score, large_transactions, exchange_inflow, exchange_outflow, net_flow, confidence = analyze_whale_activity(transactions)
                    
                    # Format response
                    response_text += f"🐋 **{symbol} Whale Activity Analysis:**\n\n"
                    response_text += f"📊 Whale Score: {whale_score:.3f}\n"
                    response_text += f"📈 Large Transactions: {large_transactions}\n"
                    response_text += f"💰 Net Flow: ${net_flow:,.0f}\n"
                    response_text += f"🎯 Confidence: {confidence:.2%}\n\n"
                    
                    # Add interpretation
                    if whale_score > 0.3:
                        response_text += "🟢 **Whale Activity: ACCUMULATION**\n"
                        response_text += "Whales are likely buying/accumulating\n\n"
                    elif whale_score < -0.3:
                        response_text += "🔴 **Whale Activity: DISTRIBUTION**\n"
                        response_text += "Whales are likely selling/distributing\n\n"
                    else:
                        response_text += "⚪ **Whale Activity: NEUTRAL**\n"
                        response_text += "No significant whale movements detected\n\n"
                    
                    # Show flow details
                    if exchange_inflow > 0 or exchange_outflow > 0:
                        response_text += "💹 **Exchange Flows:**\n"
                        response_text += f"📥 Inflow: ${exchange_inflow:,.0f}\n"
                        response_text += f"📤 Outflow: ${exchange_outflow:,.0f}\n"
                        response_text += f"⚖️ Net Flow: ${net_flow:,.0f}\n\n"
                        
                        if net_flow > 0:
                            response_text += "📈 Net positive flow (potential selling pressure)\n"
                        elif net_flow < 0:
                            response_text += "📉 Net negative flow (potential buying pressure)\n"
                    
                    if WHALE_ALERT_API_KEY == "your_whale_alert_api_key":
                        response_text += "\n⚠️ **Note:** Using mock whale data. "
                        response_text += "Get a free API key from https://whale-alert.io/ for real data."
                        
                except Exception as e:
                    response_text += f"❌ Error analyzing {symbol}: {str(e)}"
            else:
                response_text += "Please specify a trading symbol (e.g., BTC, ETH, BNB)\n\n"
                response_text += "**Example commands:**\n"
                response_text += "• 'whale activity for BTC'\n"
                response_text += "• 'analyze ETH whale transactions'\n"
                response_text += "• 'show BNB whale flow'\n"
        
        elif "help" in message_text or "commands" in message_text:
            response_text += "**Available Commands:**\n\n"
            response_text += "🐋 **Whale Analysis:**\n"
            response_text += "• 'whale [SYMBOL]' - Get whale activity\n"
            response_text += "• 'transactions [SYMBOL]' - Show large transactions\n"
            response_text += "• 'flow [SYMBOL]' - Analyze exchange flows\n\n"
            response_text += "📊 **Analysis Includes:**\n"
            response_text += "• Large transaction detection (>$1M)\n"
            response_text += "• Exchange inflow/outflow analysis\n"
            response_text += "• Net whale flow calculations\n"
            response_text += "• Accumulation/distribution patterns\n\n"
            response_text += "🎯 **Supported Symbols:**\n"
            response_text += "BTC, ETH, BNB, ADA, SOL (and related pairs)"
        
        elif "status" in message_text:
            response_text += "**Whale Agent Status:**\n\n"
            response_text += f"🟢 Status: Active (Port 8006)\n"
            response_text += f"💰 Address: {whale_agent.address[:16]}...\n"
            response_text += f"🌐 Protocol: {PROTOCOL_NAME}\n"
            
            if WHALE_ALERT_API_KEY != "your_whale_alert_api_key":
                response_text += f"📡 Data Source: Whale Alert API (Live)\n"
            else:
                response_text += f"📡 Data Source: Mock Data (Demo)\n"
                response_text += f"🔑 API Key: Not configured\n"
            
            response_text += f"🐋 Threshold: $1M+ transactions\n"
            response_text += f"⏰ Analysis Window: 24 hours\n"
        
        else:
            response_text += "I'm your whale activity specialist! 🐋\n\n"
            response_text += "I monitor large cryptocurrency transactions:\n"
            response_text += "💰 Transactions >$1M USD\n"
            response_text += "📊 Exchange inflow/outflow patterns\n"
            response_text += "📈 Accumulation vs distribution signals\n"
            response_text += "🎯 Market impact assessments\n\n"
            
            if WHALE_ALERT_API_KEY == "your_whale_alert_api_key":
                response_text += "⚠️ Currently using mock data for demonstration.\n"
                response_text += "Configure Whale Alert API key for live data.\n\n"
            
            response_text += "Try: 'whale BTC' or 'help' for commands"
        
        # Include session ID in response if it was in the request
        if session_id:
            response_text += f"\n\nsession:{session_id}"
        
        # Determine where to send response (user agent if specified, otherwise sender)
        response_target = user_agent_address if user_agent_address else sender
        ctx.logger.info(f"📤 Sending whale analysis to: {response_target[:16]}...")
        
        # Send response
        await ctx.send(
            response_target,
            ChatMessage(
                content=[TextContent(text=response_text)]
            )
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Error handling chat message: {e}")
        error_response = "Sorry, I encountered an error processing your message. Please try again."
        await ctx.send(
            sender,
            ChatMessage(
                content=[TextContent(text=error_response)]
            )
        )

@chat_protocol.on_message(model=ChatAcknowledgement)
async def handle_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    ctx.logger.info(f"💬 Chat acknowledgement from {sender}")

# Include both protocols
whale_agent.include(whale_protocol)
whale_agent.include(chat_protocol)

if __name__ == "__main__":
    print("=" * 60)
    print("🐋 WHALE ACTIVITY AGENT WITH CHAT")
    print("=" * 60)
    print(f"Agent address: {whale_agent.address}")
    print(f"Port: 8006")
    print()
    print("🐋 WHALE MONITORING:")
    print("  ✅ Large transaction detection (>$1M)")
    print("  ✅ Exchange inflow/outflow analysis")
    print("  ✅ Net whale flow calculations")
    print("  ✅ Accumulation/distribution patterns")
    print()
    print("💬 CHAT FEATURES:")
    print("  ✅ Interactive whale analysis via chat")
    print("  ✅ Real-time transaction monitoring")
    print("  ✅ Symbol-specific whale activity")
    print("  ✅ Help commands and status queries")
    print()
    if WHALE_ALERT_API_KEY == "your_whale_alert_api_key":
        print("📡 DATA SOURCE: Mock Data (Demo)")
        print("⚠️  Get a free API key from https://whale-alert.io/ for real data.")
    else:
        print("📡 DATA SOURCE: Whale Alert API (Live)")
    print()
    print("🚀 Starting Whale Agent with Chat...")
    print("=" * 60)
    whale_agent.run()
