from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
import logging
from shared_types import (
    SignalRequest,
    SignalResponse,
    PROTOCOL_NAME,
    SIGNAL_AGENT_ADDRESS
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create User Agent
user_agent = Agent(
    name="user_agent",
    port=8007,
    endpoint=["http://127.0.0.1:8007/submit"],
    seed="user_agent_seed_phrase"
)

# Fund the agent if balance is low
fund_agent_if_low(user_agent.wallet.address())

# Create protocol using shared constant
user_protocol = Protocol(PROTOCOL_NAME)

# Trading pairs to request signals for
TRADING_PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

def format_signal_emoji(signal):
    """Get emoji for signal type"""
    emoji_map = {
        "BUY": "🟢",
        "SELL": "🔴", 
        "HOLD": "⚪",
        "ERROR": "⚠️"
    }
    return emoji_map.get(signal, "❓")

def format_score_bar(score, width=10):
    """Create a visual score bar"""
    # Normalize score from -1,1 to 0,1 range
    normalized = (score + 1) / 2
    filled = int(normalized * width)
    empty = width - filled
    
    if score > 0.3:
        bar_char = "█"
        color = "🟢"
    elif score < -0.3:
        bar_char = "█" 
        color = "🔴"
    else:
        bar_char = "█"
        color = "⚪"
    
    return f"{color} [{'█' * filled}{'░' * empty}] {score:+.2f}"

# Log received signals
@user_protocol.on_message(model=SignalResponse)
async def handle_signal_response(ctx: Context, sender: str, msg: SignalResponse):
    """Handle incoming comprehensive signal responses"""
    
    # Header
    ctx.logger.info("=" * 80)
    ctx.logger.info(f"📊 COMPREHENSIVE TRADING SIGNAL: {msg.symbol}")
    ctx.logger.info("=" * 80)
    
    # Check if it's an error response
    if msg.signal == "ERROR":
        ctx.logger.error(f"❌ ERROR: Unable to fetch analysis data for {msg.symbol}")
        ctx.logger.error(f"📝 Summary: {msg.analysis_summary}")
        ctx.logger.info("=" * 80)
        return
    
    # Main Signal Information
    signal_emoji = format_signal_emoji(msg.signal)
    ctx.logger.info(f"🎯 FINAL SIGNAL: {signal_emoji} {msg.signal}")
    ctx.logger.info(f"🎲 CONFIDENCE:   {msg.confidence:.2%}")
    ctx.logger.info(f"💰 PRICE:        ${msg.current_price:,.2f}")
    ctx.logger.info(f"⏰ TIMESTAMP:    {msg.timestamp}")
    ctx.logger.info("")
    
    # Technical Analysis Section
    ctx.logger.info("📈 TECHNICAL ANALYSIS")
    ctx.logger.info("-" * 40)
    ctx.logger.info(f"RSI:              {msg.rsi:.1f}")
    ctx.logger.info(f"Technical Score:  {format_score_bar(msg.technical_score)}")
    ctx.logger.info(f"ATR:              {msg.atr:.4f}")
    ctx.logger.info("")
    
    # Sentiment Analysis Section
    ctx.logger.info("📰 SENTIMENT ANALYSIS")
    ctx.logger.info("-" * 40)
    ctx.logger.info(f"Sentiment Score:  {format_score_bar(msg.sentiment_score)}")
    ctx.logger.info(f"News Articles:    {msg.news_count}")
    
    if msg.top_headlines:
        ctx.logger.info("Top Headlines:")
        for i, headline in enumerate(msg.top_headlines[:3], 1):
            ctx.logger.info(f"  {i}. {headline[:60]}...")
    ctx.logger.info("")
    
    # Whale Analysis Section
    ctx.logger.info("🐋 WHALE ANALYSIS")
    ctx.logger.info("-" * 40)
    ctx.logger.info(f"Whale Score:      {format_score_bar(msg.whale_score)}")
    ctx.logger.info(f"Large Transactions: {msg.whale_transactions}")
    ctx.logger.info(f"Net Whale Flow:   ${msg.net_whale_flow:,.0f}")
    
    flow_direction = "📈 Accumulating" if msg.net_whale_flow > 0 else "📉 Distributing" if msg.net_whale_flow < 0 else "➡️ Neutral"
    ctx.logger.info(f"Flow Direction:   {flow_direction}")
    ctx.logger.info("")
    
    
    # Risk Management Section
    # print(msg.signal,msg.take_profit, msg.stop_loss)
    if msg.signal in ["BUY", "SELL"] and msg.take_profit > 0 and msg.stop_loss > 0:
        ctx.logger.info("⚖️ RISK MANAGEMENT")
        ctx.logger.info("-" * 40)
        ctx.logger.info(f"Take Profit:      ${msg.take_profit:,.2f}")
        ctx.logger.info(f"Stop Loss:        ${msg.stop_loss:,.2f}")
        
        # Calculate profit and risk potential
        if msg.current_price > 0:
            profit_potential = abs(msg.take_profit - msg.current_price) / msg.current_price * 100
            risk_potential = abs(msg.stop_loss - msg.current_price) / msg.current_price * 100
            
            ctx.logger.info(f"Profit Potential: {profit_potential:.2f}%")
            ctx.logger.info(f"Risk Potential:   {risk_potential:.2f}%")
            
            if risk_potential > 0:
                risk_reward = profit_potential / risk_potential
                ctx.logger.info(f"Risk/Reward:      {risk_reward:.2f}:1")
        ctx.logger.info("")
    
    # Analysis Summary
    ctx.logger.info("📋 ANALYSIS SUMMARY")
    ctx.logger.info("-" * 40)
    ctx.logger.info(f"{msg.analysis_summary}")
    ctx.logger.info("")
    
        
    # Quick Summary Line
    confidence_emoji = "🔥" if msg.confidence > 0.8 else "✅" if msg.confidence > 0.6 else "⚠️"
    ctx.logger.info(f"📊 SUMMARY: {signal_emoji} {msg.symbol} | {msg.signal} | {confidence_emoji} {msg.confidence:.1%} confidence")
    ctx.logger.info("=" * 80)

# Periodic task to request signals
@user_agent.on_interval(period=30.0)  # Increased to 30 seconds for comprehensive analysis
async def request_signals(ctx: Context):
    """Request comprehensive trading signals every 30 seconds"""
    for symbol in TRADING_PAIRS:
        ctx.logger.info(f"🔄 Requesting comprehensive analysis for {symbol}...")
        
        # Create signal request
        request = SignalRequest(symbol=symbol)
        
        # Send request to comprehensive signal agent
        await ctx.send(SIGNAL_AGENT_ADDRESS, request)

# Include the protocol
user_agent.include(user_protocol)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 COMPREHENSIVE CRYPTO TRADING SIGNAL SYSTEM")
    print("=" * 60)
    print(f"User Agent address: {user_agent.address}")
    print(f"Monitoring pairs: {', '.join(TRADING_PAIRS)}")
    print(f"Analysis interval: 30 seconds")
    print("=" * 60)
    print("📊 Analysis includes:")
    print("  • Technical Analysis (RSI, MACD, Bollinger Bands)")
    print("  • Sentiment Analysis (News & Social Media)")
    print("  • Whale Activity (On-chain transactions)")
    print("  • Risk Management (Stop Loss & Take Profit)")
    print("=" * 60)
    print("⚠️  Make sure all agents are running:")
    print("  1. Technical Agent (port 8004)")
    print("  2. News Agent (port 8005)")
    print("  3. Whale Agent (port 8006)")
    print("  4. Risk Manager Agent (port 8001)")
    print("  5. Comprehensive Signal Agent (port 8002)")
    print("=" * 60)
    
    if SIGNAL_AGENT_ADDRESS == "agent1qdcny99jhna95fyt9alu6snyalkm4r69pzusg6qkatz5wplsy8vuq00fr05":
        print("🔧 Remember to update SIGNAL_AGENT_ADDRESS with the actual address!")
        print("=" * 60)
    
    print("🎯 Starting User Agent...")
    user_agent.run()
