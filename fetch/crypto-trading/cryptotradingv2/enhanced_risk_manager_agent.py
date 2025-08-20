from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from shared_types import (
    RiskRequest, 
    RiskResponse, 
    PROTOCOL_NAME,
    RISK_MANAGER_ADDRESS
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create Risk Manager Agent
risk_manager_agent = Agent(
    name="risk_manager_agent",
    port=8001,
    endpoint=["http://localhost:8001/submit"],
    seed="risk_manager_agent_seed_phrase"
)

# Fund the agent if balance is low
fund_agent_if_low(risk_manager_agent.wallet.address())

# Define protocol using shared constant
risk_protocol = Protocol(PROTOCOL_NAME)

# Handle risk calculation requests
@risk_protocol.on_message(model=RiskRequest)
async def handle_risk_request(ctx: Context, sender: str, msg: RiskRequest):
    """Calculate stop loss and take profit with JSON logging"""
    
    ctx.logger.info(f"⚖️ RISK AGENT: Received request for {msg.symbol} from {sender}")
    ctx.logger.info(f"� Request JSON: {msg.to_json()}")
    
    try:
        # Simple risk management calculations
        if msg.signal == "BUY":
            # For BUY signals - use 5% stop loss, 10% take profit
            stop_loss = msg.current_price * 0.95
            take_profit = msg.current_price * 1.10
        elif msg.signal == "SELL":
            # For SELL signals - use 5% stop loss, 10% take profit  
            stop_loss = msg.current_price * 1.05
            take_profit = msg.current_price * 0.90
        else:
            ctx.logger.warning(f"⚠️ Unknown signal type: {msg.signal}")
            return
        
        # Calculate risk/reward ratio
        risk_pct = 5.0  # 5% risk
        reward_pct = 10.0  # 10% reward
        risk_reward_ratio = reward_pct / risk_pct  # 2:1 ratio
        
        # Position size based on confidence
        position_size = min(10.0, msg.confidence * 15.0)  # Max 10% position
        
        # Create JSON response
        response = RiskResponse(
            symbol=msg.symbol,
            signal=msg.signal,
            take_profit=take_profit,
            stop_loss=stop_loss,
            risk_reward_ratio=risk_reward_ratio,
            position_size=position_size,
            confidence=msg.confidence
        )
        
        # Send JSON response with logging
        ctx.logger.info(f"� Sending risk JSON response: {response.to_json()}")
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Risk management sent for {msg.symbol}: TP=${take_profit:.2f}, SL=${stop_loss:.2f}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error in risk calculation: {e}")
        import traceback
        traceback.print_exc()

# Include the protocol
risk_manager_agent.include(risk_protocol)

if __name__ == "__main__":
    print("=" * 60)
    print("⚖️ RISK MANAGER AGENT - JSON FORMAT")
    print("=" * 60)
    print(f"Agent address: {risk_manager_agent.address}")
    print(f"Port: 8001")
    print("=" * 60)
    print("📊 Risk Management Settings:")
    print(f"  • Stop Loss: 5% below/above entry")
    print(f"  • Take Profit: 10% above/below entry") 
    print(f"  • Risk/Reward Ratio: 2:1")
    print(f"  • Max Position Size: 10% of portfolio")
    print("=" * 60)
    print("📋 JSON Features:")
    print("  • Proper JSON request/response logging")
    print("  • Unified protocol: 'Crypto Trading v1'")
    print("  • Simple percentage-based calculations")
    print("  • Confidence-based position sizing")
    print("=" * 60)
    print("🎯 Starting Risk Manager Agent...")
    risk_manager_agent.run()
