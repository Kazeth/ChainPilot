from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from pydantic import BaseModel
import logging
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define message structures using Pydantic
class SignalRequest(BaseModel):
    """Request for trading signal"""
    symbol: str  # e.g., "BTCUSDT"

class TechnicalRequest(BaseModel):
    """Request for technical analysis"""
    symbol: str

class NewsRequest(BaseModel):
    """Request for news sentiment analysis"""
    symbol: str

class WhaleRequest(BaseModel):
    """Request for whale activity analysis"""
    symbol: str

class RiskRequest(BaseModel):
    """Request for TP/SL calculation based on ATR"""
    signal: str  # "BUY" or "SELL"
    symbol: str  # e.g., "BTCUSDT"
    current_price: float
    atr_value: float

class TechnicalResponse(BaseModel):
    """Response with technical analysis"""
    symbol: str
    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    sma_20: float
    sma_50: float
    bollinger_upper: float
    bollinger_lower: float
    atr: float
    current_price: float
    technical_score: float

class NewsResponse(BaseModel):
    """Response with news sentiment analysis"""
    symbol: str
    sentiment_score: float
    news_count: int
    headlines: list[str]
    confidence: float

class WhaleResponse(BaseModel):
    """Response with whale activity analysis"""
    symbol: str
    whale_score: float
    large_transactions: int
    exchange_inflow: float
    exchange_outflow: float
    net_flow: float
    confidence: float

class RiskResponse(BaseModel):
    """Response with TP/SL calculation"""
    signal: str
    symbol: str
    take_profit: float
    stop_loss: float

class SignalResponse(BaseModel):
    """Response with comprehensive trading signal"""
    symbol: str
    final_signal: str  # "BUY", "SELL", "HOLD", or "ERROR"
    confidence: float
    
    # Technical Analysis
    rsi: float
    technical_score: float
    current_price: float
    
    # Sentiment Analysis
    sentiment_score: float
    news_count: int
    top_headlines: list[str]
    
    # Whale Analysis
    whale_score: float
    whale_transactions: int
    net_whale_flow: float
    
    # Risk Management
    take_profit: float = 0.0
    stop_loss: float = 0.0
    atr: float = 0.0
    
    # Metadata
    timestamp: str
    analysis_summary: str

# Create Signal Agent
signal_agent = Agent(
    name="signal_agent",
    port=8002,
    endpoint=["http://localhost:8002/submit"],
    seed="signal_agent_seed_phrase"
)



# Fund the agent if balance is low
fund_agent_if_low(signal_agent.wallet.address())

# Define protocol - Use universal protocol for all agents
signal_protocol = Protocol("Crypto Trading v1")

# Agent addresses - These should match the seeds used in other agents
TECHNICAL_AGENT_ADDRESS = "agent1qgn5e6pqta60x79jrlmhlqcajxykagyuzvsw28j25u3y7jpp3estktf0uy3"  # technical_agent_seed_phrase
NEWS_AGENT_ADDRESS = "agent1qtt84hk6njyd07z5t8xrhc076wjsd3x3mlqd9qaem8hjnkrg6enpz8h2gfq"      # news_agent_seed_phrase  
WHALE_AGENT_ADDRESS = "agent1qvqth3lnn5tw2dl3xsk60lvp0aeah65uyvscqg7l43pth4lytay6sd30fly"    # whale_agent_seed_phrase
RISK_MANAGER_ADDRESS = "agent1qg9j3gx650julrvspcfsv3fhdcqlfjthf48tf0ljj7wpyzw29jwpgda2y0c"   # risk_manager_agent_seed_phrase

# Enable real agent communication instead of mock data
USE_REAL_AGENTS = True  # Set to False to use mock data

# Global storage for pending requests and responses
pending_requests = {}
agent_responses = {}
import uuid
import asyncio

def calculate_final_signal(technical_score, sentiment_score, whale_score, technical_confidence, sentiment_confidence, whale_confidence):
    """Calculate final trading signal based on all inputs"""
    
    # Weighted scores based on confidence
    total_confidence = technical_confidence + sentiment_confidence + whale_confidence
    
    if total_confidence == 0:
        return "HOLD", 0.0, "Insufficient data for analysis"
    
    # Weight each score by its confidence and predefined importance
    # Technical: 40%, Sentiment: 30%, Whale: 30%
    weights = {
        'technical': 0.3,
        'sentiment': 0.4,
        'whale': 0.3
    }
    
    weighted_score = (
        technical_score * weights['technical'] * technical_confidence +
        sentiment_score * weights['sentiment'] * sentiment_confidence +
        whale_score * weights['whale'] * whale_confidence
    ) / total_confidence
    
    # Calculate overall confidence
    overall_confidence = min(0.75, total_confidence / 3.0)
    
    # Determine signal based on weighted score
    if weighted_score > 0.3:
        signal = "BUY"
        summary = f"Bullish signal (Score: {weighted_score:.2f}). "
    elif weighted_score < -0.3:
        signal = "SELL" 
        summary = f"Bearish signal (Score: {weighted_score:.2f}). "
    else:
        signal = "HOLD"
        summary = f"Neutral signal (Score: {weighted_score:.2f}). "
    
    # Add contributing factors to summary
    factors = []
    if abs(technical_score) > 0.2:
        factors.append(f"Technical: {'Bullish' if technical_score > 0 else 'Bearish'}")
    if abs(sentiment_score) > 0.2:
        factors.append(f"Sentiment: {'Positive' if sentiment_score > 0 else 'Negative'}")
    if abs(whale_score) > 0.2:
        factors.append(f"Whales: {'Accumulating' if whale_score > 0 else 'Distributing'}")
    
    if factors:
        summary += "Key factors: " + ", ".join(factors)
    else:
        summary += "All indicators showing neutral trends"
    
    return signal, overall_confidence, summary

@signal_protocol.on_message(model=SignalRequest)
async def handle_signal_request(ctx: Context, sender: str, msg: SignalRequest):
    """Handle comprehensive signal requests - Choose between real agents or mock data"""
    ctx.logger.info(f"Received comprehensive signal request for {msg.symbol} from {sender}")
    
    if USE_REAL_AGENTS:
        # Use real agents 
        ctx.logger.info("🔄 Using REAL AGENTS for comprehensive analysis...")
        try:
            # Clear any old responses for this symbol
            if msg.symbol in agent_responses:
                agent_responses[msg.symbol] = {}
            else:
                agent_responses[msg.symbol] = {}
            
            # Send requests to all analysis agents
            ctx.logger.info(f"Requesting analysis from all agents for {msg.symbol}...")
            
            # Request technical analysis
            await ctx.send(TECHNICAL_AGENT_ADDRESS, TechnicalRequest(symbol=msg.symbol))
            ctx.logger.info("✓ Technical analysis request sent")
            
            # Request news sentiment analysis
            await ctx.send(NEWS_AGENT_ADDRESS, NewsRequest(symbol=msg.symbol))
            ctx.logger.info("✓ News analysis request sent")
            
            # Request whale activity analysis
            await ctx.send(WHALE_AGENT_ADDRESS, WhaleRequest(symbol=msg.symbol))
            ctx.logger.info("✓ Whale analysis request sent")
            
            # Wait for responses with polling approach
            max_wait_time = 15  # Total wait time in seconds
            check_interval = 1   # Check every 1 second
            waited_time = 0
            
            ctx.logger.info(f"🔍 DEBUG: agent_responses before polling: {list(agent_responses.keys())}")
            
            while waited_time < max_wait_time:
                await asyncio.sleep(check_interval)
                waited_time += check_interval
                
                # Check if we received responses
                responses = agent_responses.get(msg.symbol, {})
                technical_data = responses.get('technical')
                news_data = responses.get('news')
                whale_data = responses.get('whale')
                
                # Debug: Show actual stored data
                ctx.logger.info(f"🔍 DEBUG: agent_responses has symbols: {list(agent_responses.keys())}")
                ctx.logger.info(f"🔍 DEBUG: responses for {msg.symbol}: {list(responses.keys()) if responses else 'None'}")
                
                # Log current status
                ctx.logger.info(f"⏱️  Waiting {waited_time}s: Technical={bool(technical_data)}, News={bool(news_data)}, Whale={bool(whale_data)}")
                
                # If we have all responses, process immediately
                if technical_data and news_data and whale_data:
                    ctx.logger.info("✅ All responses received! Processing...")
                    break
                
                # If we have at least 2 responses after 8 seconds, proceed
                elif waited_time >= 8 and sum([bool(technical_data), bool(news_data), bool(whale_data)]) >= 2:
                    ctx.logger.info("✅ Sufficient responses received! Processing...")
                    break
            
            # Final check for any responses
            responses = agent_responses.get(msg.symbol, {})
            technical_data = responses.get('technical')
            news_data = responses.get('news')
            whale_data = responses.get('whale')
            
            ctx.logger.info(f"Received responses: Technical={bool(technical_data)}, News={bool(news_data)}, Whale={bool(whale_data)}")
            
            # If we have at least some data, process it
            if technical_data or news_data or whale_data:
                await process_and_send_final_signal(ctx, sender, msg.symbol, technical_data, news_data, whale_data)
                return
            else:
                # Fall back to mock data if no responses
                ctx.logger.warning("No responses received from agents, falling back to mock data")
                
        except Exception as e:
            ctx.logger.warning(f"Real agents failed: {e}, falling back to mock data")
    
    # Fall back to mock data (original implementation)
    ctx.logger.info("🎭 Using MOCK DATA for comprehensive analysis...")
    
    try:
        # Generate mock data that simulates the comprehensive analysis
        import random
        import math
        
        # Base prices for different symbols
        price_bases = {
            "BTCUSDT": 43250.0,
            "ETHUSDT": 2680.0,
            "BNBUSDT": 315.0
        }
        
        current_price = price_bases.get(msg.symbol, 1000.0)
        
        # Generate realistic RSI (30-70 range mostly)
        rsi = random.uniform(25, 75)
        
        # Technical score based on RSI and some randomness
        if rsi > 70:
            technical_score = random.uniform(0.3, 0.8)  # Overbought but could be strong
        elif rsi < 30:
            technical_score = random.uniform(-0.8, -0.3)  # Oversold
        else:
            technical_score = random.uniform(-0.4, 0.4)  # Neutral zone
        
        # ATR calculation (2% of price)
        atr = current_price * 0.02
        
        # Generate sentiment analysis
        sentiment_keywords = ["bullish", "moon", "breakout", "rally", "dump", "bearish", "correction"]
        sentiment_score = random.uniform(-0.6, 0.6)
        news_count = random.randint(5, 12)
        
        # Generate headlines based on sentiment
        if sentiment_score > 0.2:
            headlines = [
                f"{msg.symbol} shows strong bullish momentum",
                f"Institutional investors accumulating {msg.symbol}",
                f"Technical breakout anticipated for {msg.symbol}"
            ]
        elif sentiment_score < -0.2:
            headlines = [
                f"{msg.symbol} faces selling pressure",
                f"Market correction affects {msg.symbol}",
                f"Bearish sentiment around {msg.symbol}"
            ]
        else:
            headlines = [
                f"{msg.symbol} trading in consolidation phase",
                f"Mixed signals for {msg.symbol}",
                f"Neutral sentiment prevails for {msg.symbol}"
            ]
        
        # Generate whale analysis
        whale_score = random.uniform(-0.7, 0.7)
        whale_transactions = random.randint(8, 18)
        
        # Net flow based on whale score
        if whale_score > 0.3:
            net_whale_flow = random.uniform(20000000, 80000000)  # Accumulation
        elif whale_score < -0.3:
            net_whale_flow = random.uniform(-80000000, -20000000)  # Distribution
        else:
            net_whale_flow = random.uniform(-15000000, 15000000)  # Neutral
        
        # Calculate final signal using the existing function
        final_signal, overall_confidence, analysis_summary = calculate_final_signal(
            technical_score, sentiment_score, whale_score,
            0.85, 0.75, 0.65  # Mock confidence values
        )
        
        # Calculate risk management if signal is actionable
        take_profit = 0.0
        stop_loss = 0.0
        
        if final_signal in ["BUY", "SELL"]:
            # ATR-based risk management
            atr_multiplier_tp = 3.0  # Take profit at 3x ATR
            atr_multiplier_sl = 2.0  # Stop loss at 2x ATR
            
            if final_signal == "BUY":
                take_profit = current_price + (atr * atr_multiplier_tp)
                stop_loss = current_price - (atr * atr_multiplier_sl)
            else:  # SELL
                take_profit = current_price - (atr * atr_multiplier_tp)
                stop_loss = current_price + (atr * atr_multiplier_sl)
        
        # Create comprehensive response
        response = SignalResponse(
            symbol=msg.symbol,
            final_signal=final_signal,
            confidence=overall_confidence,
            
            # Technical Analysis
            rsi=rsi,
            technical_score=technical_score,
            current_price=current_price,
            
            # Sentiment Analysis
            sentiment_score=sentiment_score,
            news_count=news_count,
            top_headlines=headlines,
            
            # Whale Analysis
            whale_score=whale_score,
            whale_transactions=whale_transactions,
            net_whale_flow=net_whale_flow,
            
            # Risk Management
            take_profit=take_profit,
            stop_loss=stop_loss,
            atr=atr,
            
            # Metadata
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            analysis_summary=analysis_summary
        )
        
        # Log the generated signal
        ctx.logger.info(f"Generated comprehensive signal for {msg.symbol}:")
        ctx.logger.info(f"  🎯 Signal: {final_signal} (Confidence: {overall_confidence:.1%})")
        ctx.logger.info(f"  📈 Technical: {technical_score:.2f} (RSI: {rsi:.1f})")
        ctx.logger.info(f"  📰 Sentiment: {sentiment_score:.2f} ({news_count} articles)")
        ctx.logger.info(f"  🐋 Whale: {whale_score:.2f} (${net_whale_flow:,.0f} flow)")
        
        if final_signal in ["BUY", "SELL"]:
            ctx.logger.info(f"  💰 TP: ${take_profit:.2f} | SL: ${stop_loss:.2f}")
        
        # Send response back to requester
        await ctx.send(sender, response)
        
    except Exception as e:
        ctx.logger.error(f"Error processing comprehensive signal request: {e}")
        
        # Send error response
        error_response = SignalResponse(
            symbol=msg.symbol,
            final_signal="ERROR",
            confidence=0.0,
            rsi=0.0,
            technical_score=0.0,
            current_price=0.0,
            sentiment_score=0.0,
            news_count=0,
            top_headlines=[f"Error: {str(e)}"],
            whale_score=0.0,
            whale_transactions=0,
            net_whale_flow=0.0,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            analysis_summary=f"Failed to process request: {str(e)}"
        )
        await ctx.send(sender, error_response)

# Message handlers to receive responses from other agents
@signal_protocol.on_message(model=TechnicalResponse)
async def handle_technical_response(ctx: Context, sender: str, msg: TechnicalResponse):
    """Handle technical analysis responses"""
    ctx.logger.info(f"🔥 HANDLER CALLED: Received technical analysis for {msg.symbol}: Score={msg.technical_score:.3f}")
    
    # Store the response using symbol as key
    if msg.symbol not in agent_responses:
        agent_responses[msg.symbol] = {}
    agent_responses[msg.symbol]['technical'] = msg
    ctx.logger.info(f"🔥 STORED: Technical data for {msg.symbol} stored successfully")

@signal_protocol.on_message(model=NewsResponse)
async def handle_news_response(ctx: Context, sender: str, msg: NewsResponse):
    """Handle news sentiment responses"""
    ctx.logger.info(f"🔥 HANDLER CALLED: Received news analysis for {msg.symbol}: Score={msg.sentiment_score:.3f}")
    
    # Store the response using symbol as key
    if msg.symbol not in agent_responses:
        agent_responses[msg.symbol] = {}
    agent_responses[msg.symbol]['news'] = msg
    ctx.logger.info(f"🔥 STORED: News data for {msg.symbol} stored successfully")

@signal_protocol.on_message(model=WhaleResponse)
async def handle_whale_response(ctx: Context, sender: str, msg: WhaleResponse):
    """Handle whale activity responses"""
    ctx.logger.info(f"🔥 HANDLER CALLED: Received whale analysis for {msg.symbol}: Score={msg.whale_score:.3f}")
    
    # Store the response using symbol as key
    if msg.symbol not in agent_responses:
        agent_responses[msg.symbol] = {}
    agent_responses[msg.symbol]['whale'] = msg
    ctx.logger.info(f"🔥 STORED: Whale data for {msg.symbol} stored successfully")

@signal_protocol.on_message(model=RiskResponse)
async def handle_risk_response(ctx: Context, sender: str, msg: RiskResponse):
    """Handle risk management responses"""
    ctx.logger.info(f"Received risk analysis for {msg.symbol}: TP=${msg.take_profit:.2f}, SL=${msg.stop_loss:.2f}")
    
    # Store the response using symbol as key
    if msg.symbol not in agent_responses:
        agent_responses[msg.symbol] = {}
    agent_responses[msg.symbol]['risk'] = msg

# Process and send final signal function
async def process_and_send_final_signal(ctx: Context, sender: str, symbol: str, technical_data, news_data, whale_data):
    """Process received data and send final comprehensive signal"""
    
    # Extract data with defaults
    if technical_data:
        technical_score = technical_data.technical_score
        current_price = technical_data.current_price
        rsi = technical_data.rsi
        atr = technical_data.atr
        technical_confidence = 0.9
    else:
        technical_score = 0.0
        current_price = 43250.0  # Default BTC price
        rsi = 50.0
        atr = current_price * 0.02
        technical_confidence = 0.0
    
    if news_data:
        sentiment_score = news_data.sentiment_score
        news_count = news_data.news_count
        headlines = news_data.headlines
        sentiment_confidence = news_data.confidence
    else:
        sentiment_score = 0.0
        news_count = 0
        headlines = ["No news data available"]
        sentiment_confidence = 0.0
    
    if whale_data:
        whale_score = whale_data.whale_score
        whale_transactions = whale_data.large_transactions
        net_whale_flow = whale_data.net_flow
        whale_confidence = whale_data.confidence
    else:
        whale_score = 0.0
        whale_transactions = 0
        net_whale_flow = 0.0
        whale_confidence = 0.0
    
    # Calculate final signal
    final_signal, overall_confidence, analysis_summary = calculate_final_signal(
        technical_score, sentiment_score, whale_score,
        technical_confidence, sentiment_confidence, whale_confidence
    )
    
    # Calculate risk management if we have technical data and a trading signal
    take_profit = 0.0
    stop_loss = 0.0
    
    if final_signal in ["BUY", "SELL"] and technical_data:
        # Request risk management
        ctx.logger.info(f"Requesting risk management for {final_signal} signal...")
        await ctx.send(RISK_MANAGER_ADDRESS, RiskRequest(
            symbol=symbol,
            current_price=current_price,
            atr=atr,
            signal=final_signal
        ))
        
        # Wait briefly for risk response
        await asyncio.sleep(2)
        
        # Check if we got risk response
        risk_data = agent_responses.get(symbol, {}).get('risk')
        if risk_data:
            take_profit = risk_data.take_profit
            stop_loss = risk_data.stop_loss
            ctx.logger.info(f"✓ Risk management received: TP=${take_profit:.2f}, SL=${stop_loss:.2f}")
        else:
            # Calculate basic risk management
            atr_multiplier_tp = 3.0
            atr_multiplier_sl = 2.0
            
            if final_signal == "BUY":
                take_profit = current_price + (atr * atr_multiplier_tp)
                stop_loss = current_price - (atr * atr_multiplier_sl)
            else:  # SELL
                take_profit = current_price - (atr * atr_multiplier_tp)
                stop_loss = current_price + (atr * atr_multiplier_sl)
    
    # Create comprehensive response
    response = SignalResponse(
        symbol=symbol,
        final_signal=final_signal,
        confidence=overall_confidence,
        
        # Technical Analysis
        rsi=rsi,
        technical_score=technical_score,
        current_price=current_price,
        
        # Sentiment Analysis
        sentiment_score=sentiment_score,
        news_count=news_count,
        top_headlines=headlines,
        
        # Whale Analysis
        whale_score=whale_score,
        whale_transactions=whale_transactions,
        net_whale_flow=net_whale_flow,
        
        # Risk Management
        take_profit=take_profit,
        stop_loss=stop_loss,
        atr=atr,
        
        # Metadata
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        analysis_summary=analysis_summary
    )
    
    # Send final response
    await ctx.send(sender, response)
    ctx.logger.info(f"✅ Sent comprehensive signal for {symbol}: {final_signal} (Confidence: {overall_confidence:.1%})")
    
    # Clean up responses
    if symbol in agent_responses:
        del agent_responses[symbol]

# Include the protocol
signal_agent.include(signal_protocol)

if __name__ == "__main__":
    print("=" * 70)
    print("🎯 COMPREHENSIVE SIGNAL AGENT")
    print("=" * 70)
    print(f"Agent address: {signal_agent.address}")
    print(f"Port: 8002")
    print()
    print("🤖 OPERATING MODE:")
    if USE_REAL_AGENTS:
        print("  ✅ REAL AGENTS MODE - Will communicate with actual agents")
        print("  📊 Technical Agent:", TECHNICAL_AGENT_ADDRESS)
        print("  📰 News Agent:", NEWS_AGENT_ADDRESS) 
        print("  🐋 Whale Agent:", WHALE_AGENT_ADDRESS)
        print("  ⚖️  Risk Manager:", RISK_MANAGER_ADDRESS)
        print()
        print("  🔄 Process Flow:")
        print("    1. Receive signal request")
        print("    2. Send requests to technical, news, whale agents")
        print("    3. Wait for responses (5 seconds)")
        print("    4. Request risk management")
        print("    5. Compile and send comprehensive signal")
        print("    6. Fall back to mock data if agents don't respond")
    else:
        print("  🎭 MOCK DATA MODE - Using simulated analysis")
        print("  📊 Generates realistic technical indicators")
        print("  📰 Creates sample news sentiment")
        print("  🐋 Simulates whale activity")
        print("  ⚖️  Calculates risk management")
    print()
    print("💡 To switch modes, change USE_REAL_AGENTS in the code")
    print("=" * 70)
    print("🚀 Starting Signal Agent...")
    signal_agent.run()
