from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define message structures using Pydantic
class RiskRequest(BaseModel):
    """Request for TP/SL calculation based on ATR"""
    signal: str  # "BUY" or "SELL"
    symbol: str  # e.g., "BTCUSDT"
    current_price: float
    atr_value: float

class RiskResponse(BaseModel):
    """Response with TP/SL calculation"""
    signal: str  # "BUY" or "SELL"
    symbol: str  # e.g., "BTCUSDT"
    take_profit: float
    stop_loss: float

# Create Risk Manager Agent
risk_manager = Agent(
    name="risk_manager",
    port=8001,
    endpoint=["http://localhost:8001/submit"],
    seed="risk_manager_seed_phrase",
    mailbox=True
)

# Fund the agent if balance is low
fund_agent_if_low(risk_manager.wallet.address())

# Create protocol for handling risk management requests
risk_protocol = Protocol("Risk Management v1")  # Added version to protocol name

@risk_protocol.on_message(model=RiskRequest)
async def handle_risk_request(ctx: Context, sender: str, msg: RiskRequest):
    """Calculate TP/SL based on ATR value"""
    ctx.logger.info(f"Received risk calculation request for {msg.symbol} with signal {msg.signal}")
    
    # Calculate TP/SL based on ATR
    if msg.signal == "BUY":
        take_profit = msg.current_price + (2 * msg.atr_value)
        stop_loss = msg.current_price - (1 * msg.atr_value)
        ctx.logger.info(f"BUY Signal for {msg.symbol}: TP={take_profit:.2f}, SL={stop_loss:.2f}")
    elif msg.signal == "SELL":
        take_profit = msg.current_price - (2 * msg.atr_value)
        stop_loss = msg.current_price + (1 * msg.atr_value)
        ctx.logger.info(f"SELL Signal for {msg.symbol}: TP={take_profit:.2f}, SL={stop_loss:.2f}")
    else:
        ctx.logger.info(f"Invalid signal: {msg.signal}. Must be 'BUY' or 'SELL'")
        return
    
    # Create response
    response = RiskResponse(
        signal=msg.signal,
        symbol=msg.symbol,
        take_profit=take_profit,
        stop_loss=stop_loss
    )
    
    # Send response back to sender
    await ctx.send(sender, response)
    ctx.logger.info(f"Sent risk management response for {msg.symbol} back to {sender}")

# Include the protocol in the agent
risk_manager.include(risk_protocol)

if __name__ == "__main__":
    # Print schema info for debugging
    print(f"Risk Manager Agent's RiskRequest schema: {RiskRequest.schema()}")
    print(f"Risk Manager Agent's RiskResponse schema: {RiskResponse.schema()}")
    
    print(f"Risk Manager Agent address: {risk_manager.address}")
    print(f"Risk Manager is running and waiting for requests...")
    
    # Enable more verbose logging
    logging.getLogger('uagents').setLevel(logging.DEBUG)
    
    # Run the agent
    risk_manager.run()
