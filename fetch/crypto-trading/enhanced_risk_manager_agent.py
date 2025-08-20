from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define message structures using Pydantic
class RiskRequest(BaseModel):
    """Request for risk management calculations"""
    symbol: str  # e.g., "BTCUSDT"
    current_price: float
    atr: float  # Average True Range from technical analysis
    signal: str  # "BUY" or "SELL"

class RiskResponse(BaseModel):
    """Response with risk management calculations"""
    symbol: str
    signal: str
    current_price: float
    atr: float
    
    # ATR-based calculations
    take_profit: float
    stop_loss: float
    
    # Risk metrics
    risk_percentage: float
    reward_percentage: float
    risk_reward_ratio: float
    
    # Additional info
    atr_multiplier_tp: float
    atr_multiplier_sl: float
    position_size_suggestion: float  # Based on risk percentage
    timestamp: str

# Create Risk Manager Agent
risk_manager_agent = Agent(
    name="risk_manager_agent",
    port=8001,
    endpoint=["http://localhost:8001/submit"],
    seed="risk_manager_agent_seed_phrase"
)

# Fund the agent if balance is low
fund_agent_if_low(risk_manager_agent.wallet.address())

# Define protocol
risk_protocol = Protocol("Risk Management v1")

# Risk parameters (can be adjusted based on trading strategy)
RISK_SETTINGS = {
    "atr_multiplier_stop_loss": 2.0,      # Stop loss at 2x ATR
    "atr_multiplier_take_profit": 3.0,    # Take profit at 3x ATR
    "max_risk_percentage": 2.0,           # Maximum 2% risk per trade
    "min_risk_reward_ratio": 1.5,         # Minimum 1.5:1 risk/reward
}

# Handle risk calculation requests
@risk_protocol.on_message(model=RiskRequest)
async def handle_risk_request(ctx: Context, sender: str, msg: RiskRequest):
    """Calculate stop loss and take profit based on ATR"""
    
    ctx.logger.info(f"⚖️  Calculating risk management for {msg.symbol}")
    ctx.logger.info(f"📍 Current Price: ${msg.current_price:.2f}")
    ctx.logger.info(f"📊 ATR: {msg.atr:.4f}")
    ctx.logger.info(f"🎯 Signal: {msg.signal}")
    
    try:
        # Calculate ATR-based stop loss and take profit
        atr_sl_multiplier = RISK_SETTINGS["atr_multiplier_stop_loss"]
        atr_tp_multiplier = RISK_SETTINGS["atr_multiplier_take_profit"]
        
        if msg.signal == "BUY":
            # For BUY signals
            stop_loss = msg.current_price - (msg.atr * atr_sl_multiplier)
            take_profit = msg.current_price + (msg.atr * atr_tp_multiplier)
            
        elif msg.signal == "SELL":
            # For SELL signals
            stop_loss = msg.current_price + (msg.atr * atr_sl_multiplier)
            take_profit = msg.current_price - (msg.atr * atr_tp_multiplier)
            
        else:
            ctx.logger.warning(f"⚠️  Unknown signal type: {msg.signal}")
            return
        
        # Calculate risk and reward percentages
        risk_percentage = abs(stop_loss - msg.current_price) / msg.current_price * 100
        reward_percentage = abs(take_profit - msg.current_price) / msg.current_price * 100
        
        # Calculate risk/reward ratio
        risk_reward_ratio = reward_percentage / risk_percentage if risk_percentage > 0 else 0
        
        # Calculate suggested position size based on maximum risk
        max_risk_pct = RISK_SETTINGS["max_risk_percentage"]
        position_size_suggestion = max_risk_pct / risk_percentage if risk_percentage > 0 else 0
        
        # Validate risk/reward ratio
        min_ratio = RISK_SETTINGS["min_risk_reward_ratio"]
        if risk_reward_ratio < min_ratio:
            ctx.logger.warning(f"⚠️  Risk/Reward ratio {risk_reward_ratio:.2f} is below minimum {min_ratio}")
        
        # Create response
        response = RiskResponse(
            symbol=msg.symbol,
            signal=msg.signal,
            current_price=msg.current_price,
            atr=msg.atr,
            take_profit=take_profit,
            stop_loss=stop_loss,
            risk_percentage=risk_percentage,
            reward_percentage=reward_percentage,
            risk_reward_ratio=risk_reward_ratio,
            atr_multiplier_tp=atr_tp_multiplier,
            atr_multiplier_sl=atr_sl_multiplier,
            position_size_suggestion=position_size_suggestion,
            timestamp=ctx.get_timestamp()
        )
        
        # Log calculations
        ctx.logger.info(f"💰 Take Profit: ${take_profit:.2f} ({reward_percentage:.2f}%)")
        ctx.logger.info(f"🛡️  Stop Loss:   ${stop_loss:.2f} ({risk_percentage:.2f}%)")
        ctx.logger.info(f"📈 Risk/Reward:  {risk_reward_ratio:.2f}:1")
        ctx.logger.info(f"💼 Position Size: {position_size_suggestion:.2f}% of portfolio")
        
        # Send response back
        await ctx.send(sender, response)
        
        ctx.logger.info(f"✅ Risk management calculations sent back to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error calculating risk management: {str(e)}")

# Include the protocol
risk_manager_agent.include(risk_protocol)

if __name__ == "__main__":
    print("=" * 60)
    print("⚖️  RISK MANAGER AGENT")
    print("=" * 60)
    print(f"Agent address: {risk_manager_agent.address}")
    print(f"Port: 8001")
    print("=" * 60)
    print("📊 Risk Management Settings:")
    print(f"  • Stop Loss ATR Multiplier:   {RISK_SETTINGS['atr_multiplier_stop_loss']}x")
    print(f"  • Take Profit ATR Multiplier: {RISK_SETTINGS['atr_multiplier_take_profit']}x")
    print(f"  • Maximum Risk per Trade:     {RISK_SETTINGS['max_risk_percentage']}%")
    print(f"  • Minimum Risk/Reward Ratio:  {RISK_SETTINGS['min_risk_reward_ratio']}:1")
    print("=" * 60)
    print("📋 Calculation Methods:")
    print("  • ATR-based Stop Loss & Take Profit")
    print("  • Position Size based on risk percentage")
    print("  • Risk/Reward ratio validation")
    print("  • Dynamic calculations for BUY/SELL signals")
    print("=" * 60)
    print("🎯 Starting Risk Manager Agent...")
    risk_manager_agent.run()
