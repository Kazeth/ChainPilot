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
    TechnicalRequest, 
    TechnicalResponse, 
    PROTOCOL_NAME,
    TECHNICAL_AGENT_ADDRESS
)
import requests
import pandas as pd
import numpy as np
import logging
import urllib3

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create Technical Agent
technical_agent = Agent(
    name="technical_agent",
    port=8004,
    endpoint=["http://localhost:8004/submit"],
    seed="technical_agent_seed_phrase",
        # Enable mailbox for chat functionality
)

# Fund the agent if balance is low
fund_agent_if_low(technical_agent.wallet.address())

# Define protocol using shared constant
technical_protocol = Protocol(PROTOCOL_NAME)

# Create chat protocol
chat_protocol = Protocol(spec=chat_protocol_spec)

# API configuration
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
BINANCE_US_URL = "https://api.binance.us/api/v3"

def get_market_data(symbol, interval="1h", limit=200):
    """Get OHLCV data from Binance API with fallback"""
    try:
        # Try Binance US first
        url = f"{BINANCE_US_URL}/klines"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        response = requests.get(url, params=params, verify=False, timeout=10)
        
        if response.status_code != 200:
            # Fallback to main Binance
            url = f"{BINANCE_BASE_URL}/klines"
            response = requests.get(url, params=params, verify=False, timeout=10)
        
        response.raise_for_status()
        klines = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        
        # Convert numeric columns
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col])
            
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        
        return df
        
    except Exception as e:
        logging.error(f"Error fetching market data: {e}")
        return None

def calculate_rsi(df, window=14):
    """Calculate RSI indicator"""
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    ema_fast = df['close'].ewm(span=fast).mean()
    ema_slow = df['close'].ewm(span=slow).mean()
    
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal).mean()
    macd_histogram = macd - macd_signal
    
    return macd, macd_signal, macd_histogram

def calculate_bollinger_bands(df, window=20, num_std=2):
    """Calculate Bollinger Bands"""
    sma = df['close'].rolling(window=window).mean()
    std = df['close'].rolling(window=window).std()
    
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    
    return upper_band, lower_band

def calculate_atr(df, window=14):
    """Calculate Average True Range"""
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    atr = true_range.rolling(window=window).mean()
    return atr

def calculate_technical_score(rsi, macd, macd_signal, current_price, sma_20, sma_50, bb_upper, bb_lower):
    """Calculate combined technical score"""
    score = 0.0
    
    # RSI contribution (30% weight)
    if rsi < 30:
        score += 0.3  # Oversold = bullish
    elif rsi > 70:
        score -= 0.3  # Overbought = bearish
    else:
        score += 0.3 * (50 - rsi) / 20  # Neutral zone
    
    # MACD contribution (25% weight)
    if macd > macd_signal:
        score += 0.25  # MACD above signal = bullish
    else:
        score -= 0.25  # MACD below signal = bearish
    
    # Moving Average contribution (25% weight)
    if current_price > sma_50 > sma_20:
        score += 0.25  # Uptrend
    elif current_price < sma_50 < sma_20:
        score -= 0.25  # Downtrend
    
    # Bollinger Bands contribution (20% weight)
    if current_price < bb_lower:
        score += 0.2  # Oversold
    elif current_price > bb_upper:
        score -= 0.2  # Overbought
    
    return max(-1.0, min(1.0, score))  # Clamp between -1 and 1

@technical_protocol.on_message(model=TechnicalRequest)
async def handle_technical_request(ctx: Context, sender: str, msg: TechnicalRequest):
    """Handle technical analysis requests with JSON logging"""
    ctx.logger.info(f"📊 TECHNICAL AGENT: Received request for {msg.symbol} from {sender}")
    ctx.logger.info(f"📄 Request JSON: {msg.to_json()}")
    
    try:
        # Get market data
        df = get_market_data(msg.symbol)
        
        if df is None or df.empty:
            ctx.logger.error(f"Failed to get market data for {msg.symbol}")
            return
        
        # Calculate technical indicators
        df['rsi'] = calculate_rsi(df)
        macd, macd_signal, macd_histogram = calculate_macd(df)
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_histogram'] = macd_histogram
        
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        bb_upper, bb_lower = calculate_bollinger_bands(df)
        df['bb_upper'] = bb_upper
        df['bb_lower'] = bb_lower
        
        df['atr'] = calculate_atr(df)
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Calculate technical score
        technical_score = calculate_technical_score(
            latest['rsi'], latest['macd'], latest['macd_signal'],
            latest['close'], latest['sma_20'], latest['sma_50'],
            latest['bb_upper'], latest['bb_lower']
        )
        
        # Create JSON response
        response = TechnicalResponse(
            symbol=msg.symbol,
            rsi=float(latest['rsi']),
            macd=float(latest['macd']),
            macd_signal=float(latest['macd_signal']),
            macd_histogram=float(latest['macd_histogram']),
            sma_20=float(latest['sma_20']),
            sma_50=float(latest['sma_50']),
            bollinger_upper=float(latest['bb_upper']),
            bollinger_lower=float(latest['bb_lower']),
            atr=float(latest['atr']),
            current_price=float(latest['close']),
            technical_score=technical_score
        )
        
        # Send JSON response with logging
        ctx.logger.info(f"📤 Sending technical JSON response: {response.to_json()}")
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Technical analysis sent for {msg.symbol}: Score={technical_score:.3f}, RSI={latest['rsi']:.2f}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error in technical analysis: {e}")
        import traceback
        traceback.print_exc()

# ========================================
# CHAT PROTOCOL HANDLERS
# ========================================

@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle chat messages for technical analysis"""
    ctx.logger.info(f"💬 Chat message from {sender}: {msg.content[0].text}")
    
    try:
        message_text = msg.content[0].text
        message_text_lower = message_text.lower()
        
        # Extract session ID and user agent address if present
        session_id = None
        user_agent_address = None
        if "session:" in message_text:
            try:
                session_part = message_text.split("session:")[1].split()[0]
                session_id = session_part.strip()
                ctx.logger.info(f"📊 Technical analysis requested for session: {session_id}")
            except:
                ctx.logger.warning("Could not extract session ID from message")
        
        if "user:" in message_text:
            try:
                user_part = message_text.split("user:")[1].split()[0]
                user_agent_address = user_part.strip()
                ctx.logger.info(f"📊 Will send response to user agent: {user_agent_address[:16]}...")
            except:
                ctx.logger.warning("Could not extract user agent address from message")
        
        response_text = "📊 **Technical Analysis Agent**\n\n"
        
        # Check if user is asking for technical analysis
        if any(word in message_text_lower for word in ["analyze", "technical", "rsi", "macd", "bollinger", "indicators"]):
            # Look for trading symbols
            symbols = []
            common_symbols = ["btc", "eth", "bnb", "ada", "sol", "btcusdt", "ethusdt", "bnbusdt", "adausdt", "solusdt"]
            
            for symbol in common_symbols:
                if symbol in message_text_lower:
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
                response_text += f"🔄 **Analyzing {', '.join(symbols)} technical indicators...**\n\n"
                
                # Perform technical analysis for the first symbol
                symbol = symbols[0]
                try:
                    # Get market data
                    df = get_market_data(symbol)
                    
                    if df is not None and not df.empty:
                        # Calculate indicators
                        df['rsi'] = calculate_rsi(df)
                        macd, macd_signal, macd_histogram = calculate_macd(df)
                        df['macd'] = macd
                        df['macd_signal'] = macd_signal
                        df['macd_histogram'] = macd_histogram
                        
                        df['sma_20'] = df['close'].rolling(window=20).mean()
                        df['sma_50'] = df['close'].rolling(window=50).mean()
                        
                        bb_upper, bb_lower = calculate_bollinger_bands(df)
                        df['bb_upper'] = bb_upper
                        df['bb_lower'] = bb_lower
                        
                        df['atr'] = calculate_atr(df)
                        
                        # Get latest values
                        latest = df.iloc[-1]
                        
                        # Calculate technical score
                        technical_score = calculate_technical_score(
                            latest['rsi'], latest['macd'], latest['macd_signal'],
                            latest['close'], latest['sma_20'], latest['sma_50'],
                            latest['bb_upper'], latest['bb_lower']
                        )
                        
                        # Format response
                        response_text += f"📈 **{symbol} Technical Analysis:**\n\n"
                        response_text += f"💰 Current Price: ${latest['close']:,.2f}\n"
                        response_text += f"📊 Technical Score: {technical_score:.3f}\n\n"
                        response_text += f"**Key Indicators:**\n"
                        response_text += f"• RSI (14): {latest['rsi']:.2f}\n"
                        response_text += f"• MACD: {latest['macd']:.4f}\n"
                        response_text += f"• MACD Signal: {latest['macd_signal']:.4f}\n"
                        response_text += f"• SMA 20: ${latest['sma_20']:,.2f}\n"
                        response_text += f"• SMA 50: ${latest['sma_50']:,.2f}\n"
                        response_text += f"• Bollinger Upper: ${latest['bb_upper']:,.2f}\n"
                        response_text += f"• Bollinger Lower: ${latest['bb_lower']:,.2f}\n"
                        response_text += f"• ATR: {latest['atr']:.4f}\n\n"
                        
                        # Add interpretation
                        if technical_score > 0.3:
                            response_text += "🟢 **Technical Outlook: BULLISH**\n"
                        elif technical_score < -0.3:
                            response_text += "🔴 **Technical Outlook: BEARISH**\n"
                        else:
                            response_text += "⚪ **Technical Outlook: NEUTRAL**\n"
                        
                        # RSI interpretation
                        if latest['rsi'] > 70:
                            response_text += "⚠️ RSI indicates overbought conditions\n"
                        elif latest['rsi'] < 30:
                            response_text += "⚠️ RSI indicates oversold conditions\n"
                        
                    else:
                        response_text += f"❌ Unable to fetch market data for {symbol}\n"
                        response_text += "The API might be temporarily unavailable."
                        
                except Exception as e:
                    response_text += f"❌ Error analyzing {symbol}: {str(e)}"
            else:
                response_text += "Please specify a trading symbol (e.g., BTC, ETH, BNB)\n\n"
                response_text += "**Example commands:**\n"
                response_text += "• 'analyze BTC technical indicators'\n"
                response_text += "• 'show ETH RSI and MACD'\n"
                response_text += "• 'technical analysis for BNBUSDT'\n"
        
        elif "help" in message_text or "commands" in message_text:
            response_text += "**Available Commands:**\n\n"
            response_text += "📊 **Technical Analysis:**\n"
            response_text += "• 'analyze [SYMBOL]' - Full technical analysis\n"
            response_text += "• 'technical [SYMBOL]' - Get indicators\n"
            response_text += "• 'RSI [SYMBOL]' - Get RSI value\n"
            response_text += "• 'MACD [SYMBOL]' - Get MACD analysis\n\n"
            response_text += "📈 **Supported Indicators:**\n"
            response_text += "• RSI (Relative Strength Index)\n"
            response_text += "• MACD (Moving Average Convergence Divergence)\n"
            response_text += "• Bollinger Bands\n"
            response_text += "• Simple Moving Averages (20, 50)\n"
            response_text += "• ATR (Average True Range)\n\n"
            response_text += "🎯 **Supported Symbols:**\n"
            response_text += "BTC, ETH, BNB, ADA, SOL (and USDT pairs)"
        
        elif "status" in message_text:
            response_text += "**Technical Agent Status:**\n\n"
            response_text += f"🟢 Status: Active (Port 8004)\n"
            response_text += f"💰 Address: {technical_agent.address[:16]}...\n"
            response_text += f"🌐 Protocol: {PROTOCOL_NAME}\n"
            response_text += f"📊 Data Source: Binance API\n"
            response_text += f"⚡ Indicators: RSI, MACD, Bollinger, SMA, ATR\n"
        
        else:
            response_text += "I'm your technical analysis specialist! 📊\n\n"
            response_text += "I analyze market data using:\n"
            response_text += "📈 RSI (Relative Strength Index)\n"
            response_text += "📊 MACD (Moving Average Convergence Divergence)\n"
            response_text += "📉 Bollinger Bands\n"
            response_text += "📋 Simple Moving Averages\n"
            response_text += "⚡ ATR (Average True Range)\n\n"
            response_text += "Try: 'analyze BTC' or 'help' for commands"
        
        # Add session ID to response if present
        if session_id:
            response_text += f"\n\nsession:{session_id}"
        
        # Determine where to send response (user agent if specified, otherwise sender)
        response_target = user_agent_address if user_agent_address else sender
        ctx.logger.info(f"📤 Sending technical analysis to: {response_target[:16]}...")
        
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
technical_agent.include(technical_protocol)
technical_agent.include(chat_protocol)

if __name__ == "__main__":
    print("=" * 60)
    print("📊 TECHNICAL ANALYSIS AGENT WITH CHAT")
    print("=" * 60)
    print(f"Agent address: {technical_agent.address}")
    print(f"Port: 8004")
    print()
    print("📈 TECHNICAL INDICATORS:")
    print("  ✅ RSI (Relative Strength Index)")
    print("  ✅ MACD (Moving Average Convergence Divergence)")
    print("  ✅ Bollinger Bands")
    print("  ✅ Simple Moving Averages (20, 50)")
    print("  ✅ ATR (Average True Range)")
    print()
    print("💬 CHAT FEATURES:")
    print("  ✅ Interactive technical analysis via chat")
    print("  ✅ Real-time indicator calculations")
    print("  ✅ Symbol-specific analysis")
    print("  ✅ Help commands and status queries")
    print()
    print("📊 DATA SOURCE: Binance API")
    print("🚀 Starting Technical Agent with Chat...")
    print("=" * 60)
    technical_agent.run()
