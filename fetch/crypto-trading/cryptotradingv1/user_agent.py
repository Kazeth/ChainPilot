from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define message structures using Pydantic
class SignalRequest(BaseModel):
    """Request for trading signal"""
    symbol: str  # e.g., "BTCUSDT"

class SignalResponse(BaseModel):
    """Response with trading signal and analysis"""
    symbol: str
    signal: str  # "BUY", "SELL", "HOLD", or "ERROR"
    rsi: float
    confidence: float
    current_price: float
    timestamp: str
    take_profit: float = 0.0  # Simple default without Field
    stop_loss: float = 0.0    # Simple default without Field

# Create User Agent
user_agent = Agent(
    name="user_agent",
    port=8003,
    endpoint=["http://localhost:8003/submit"],
    seed="user_agent_seed_phrase"
)

# Fund the agent if balance is low
fund_agent_if_low(user_agent.wallet.address())

# Define protocol
user_protocol = Protocol("Signal Request v1")  # Added version to protocol name

# Signal agent address - updated with the actual address
SIGNAL_AGENT_ADDRESS = "agent1qdcny99jhna95fyt9alu6snyalkm4r69pzusg6qkatz5wplsy8vuq00fr05"

# Trading pairs to request signals for
TRADING_PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# Log received signals
@user_protocol.on_message(model=SignalResponse)
async def handle_signal_response(ctx: Context, sender: str, msg: SignalResponse):
    """Handle incoming signal responses"""
    # Format the output for better readability
    ctx.logger.info("=" * 50)
    ctx.logger.info(f"TRADING SIGNAL RECEIVED: {msg.symbol}")
    ctx.logger.info("-" * 50)
    
    # Check if it's an error response
    if msg.signal == "ERROR":
        ctx.logger.error(f"ERROR: Unable to fetch data for {msg.symbol}")
        ctx.logger.error("The service may be experiencing connectivity issues or API limitations")
        ctx.logger.info("=" * 50)
        return
    
    ctx.logger.info(f"Symbol:       {msg.symbol}")
    ctx.logger.info(f"Signal:       {msg.signal}")
    ctx.logger.info(f"RSI:          {msg.rsi:.2f}")
    ctx.logger.info(f"Confidence:   {msg.confidence:.2f}")
    ctx.logger.info(f"Price:        {msg.current_price:.2f}")
    ctx.logger.info(f"Timestamp:    {msg.timestamp}")
    
    # Check if we have valid (non-zero) take_profit and stop_loss values
    has_valid_tp_sl = msg.signal in ["BUY", "SELL"] and msg.take_profit > 0.0 and msg.stop_loss > 0.0
    
    if has_valid_tp_sl:
        ctx.logger.info(f"Take Profit:  {msg.take_profit:.2f}")
        ctx.logger.info(f"Stop Loss:    {msg.stop_loss:.2f}")
        
        # Calculate profit and risk potential
        profit_potential = abs(msg.take_profit - msg.current_price) / msg.current_price * 100
        risk_potential = abs(msg.stop_loss - msg.current_price) / msg.current_price * 100
        
        ctx.logger.info(f"Profit Potential: {profit_potential:.2f}%")
        ctx.logger.info(f"Risk Potential:   {risk_potential:.2f}%")
        ctx.logger.info(f"Risk/Reward:      {profit_potential/risk_potential:.2f}")
    
    # Print a summary with emoji
    if msg.signal == "BUY":
        signal_emoji = "🟢"
    elif msg.signal == "SELL":
        signal_emoji = "🔴"
    elif msg.signal == "HOLD":
        signal_emoji = "⚪"
    else:
        signal_emoji = "⚠️"
        
    ctx.logger.info(f"{signal_emoji} {msg.symbol} | {msg.signal} | RSI: {msg.rsi:.2f} | Confidence: {msg.confidence:.2f}")
    ctx.logger.info("=" * 50)

# Periodic task to request signals
@user_agent.on_interval(period=15.0)
async def request_signals(ctx: Context):
    """Request trading signals every 15 seconds"""
    for symbol in TRADING_PAIRS:
        ctx.logger.info(f"Requesting signal for {symbol}")
        
        # Create signal request
        request = SignalRequest(symbol=symbol)
        
        # Send request to signal agent
        await ctx.send(SIGNAL_AGENT_ADDRESS, request)

# Include the protocol
user_agent.include(user_protocol)

# Create a generic model for fallback message handling
class GenericMessage(BaseModel):
    """Generic message model to catch all unknown messages"""
    # This class can be empty as it's just used as a fallback
    pass

# Add a generic message handler to catch messages that don't match SignalResponse
@user_agent.on_message(model=GenericMessage)
async def handle_generic_message(ctx: Context, sender: str, message):
    """Handle any message that doesn't match our known schemas"""
    ctx.logger.info("=" * 50)
    ctx.logger.info(f"RECEIVED TRADING SIGNAL FROM: {sender}")
    ctx.logger.info("-" * 50)
    
    # Try to interpret the message as a trading signal
    try:
        # Check if it's a dict-like object
        if hasattr(message, '__getitem__') or isinstance(message, dict):
            # Try to extract common fields
            symbol = message.get('symbol', 'UNKNOWN') if isinstance(message, dict) else getattr(message, 'symbol', 'UNKNOWN')
            signal = message.get('signal', 'UNKNOWN') if isinstance(message, dict) else getattr(message, 'signal', 'UNKNOWN')
            rsi = message.get('rsi', 0.0) if isinstance(message, dict) else getattr(message, 'rsi', 0.0)
            confidence = message.get('confidence', 0.0) if isinstance(message, dict) else getattr(message, 'confidence', 0.0)
            price = message.get('current_price', 0.0) if isinstance(message, dict) else getattr(message, 'current_price', 0.0)
            timestamp = message.get('timestamp', '') if isinstance(message, dict) else getattr(message, 'timestamp', '')
            
            # Display the trading signal information
            ctx.logger.info(f"Symbol:       {symbol}")
            ctx.logger.info(f"Signal:       {signal}")
            ctx.logger.info(f"RSI:          {rsi}")
            ctx.logger.info(f"Confidence:   {confidence}")
            ctx.logger.info(f"Price:        {price}")
            ctx.logger.info(f"Timestamp:    {timestamp}")
            
            # Try to get TP/SL if available
            take_profit = message.get('take_profit', 0.0) if isinstance(message, dict) else getattr(message, 'take_profit', 0.0)
            stop_loss = message.get('stop_loss', 0.0) if isinstance(message, dict) else getattr(message, 'stop_loss', 0.0)
            
            if take_profit and stop_loss and take_profit > 0 and stop_loss > 0:
                ctx.logger.info(f"Take Profit:  {take_profit}")
                ctx.logger.info(f"Stop Loss:    {stop_loss}")
                
                # Calculate profit and risk potential
                profit_potential = abs(take_profit - price) / price * 100
                risk_potential = abs(stop_loss - price) / price * 100
                
                ctx.logger.info(f"Profit Potential: {profit_potential:.2f}%")
                ctx.logger.info(f"Risk Potential:   {risk_potential:.2f}%")
                try:
                    ctx.logger.info(f"Risk/Reward:      {profit_potential/risk_potential:.2f}")
                except:
                    ctx.logger.info(f"Risk/Reward:      N/A")
            
            # Print a summary with emoji
            if signal == "BUY":
                signal_emoji = "🟢"
            elif signal == "SELL":
                signal_emoji = "🔴"
            elif signal == "HOLD":
                signal_emoji = "⚪"
            else:
                signal_emoji = "⚠️"
                
            ctx.logger.info(f"{signal_emoji} {symbol} | {signal} | RSI: {rsi} | Confidence: {confidence}")
        else:
            # If we can't parse it as expected, just print the raw message
            ctx.logger.info(f"Received raw message: {message}")
    except Exception as e:
        ctx.logger.error(f"Error parsing message: {e}")
        ctx.logger.info(f"Raw message: {message}")
        
    ctx.logger.info("=" * 50)

if __name__ == "__main__":
    # Print schema info for debugging
    print(f"User Agent's SignalResponse schema: {SignalResponse.schema()}")
    
    # Clear any cached protocol schemas
    print("Starting User Agent with address:", user_agent.address)
    print("Configured to request signals for:", TRADING_PAIRS)
    print("Will request signals every 15 seconds")
    
    # Run the agent
    user_agent.run()
