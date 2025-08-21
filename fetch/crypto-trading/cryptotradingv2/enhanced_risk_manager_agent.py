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
    seed="risk_manager_agent_seed_phrase",
)

# Fund the agent if balance is low
fund_agent_if_low(risk_manager_agent.wallet.address())

# Define protocol using shared constant
risk_protocol = Protocol(PROTOCOL_NAME)

# Create chat protocol
chat_protocol = Protocol(spec=chat_protocol_spec)

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

# ========================================
# CHAT PROTOCOL HANDLERS
# ========================================

@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle chat messages for risk management"""
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
                ctx.logger.info(f"⚖️ Risk analysis requested for session: {session_id}")
            except:
                ctx.logger.warning("Could not extract session ID from message")
        
        if "user:" in message_text:
            try:
                user_part = message_text.split("user:")[1].split()[0]
                user_agent_address = user_part.strip()
                ctx.logger.info(f"⚖️ Will send response to user agent: {user_agent_address[:16]}...")
            except:
                ctx.logger.warning("Could not extract user agent address from message")
        
        response_text = "⚖️ **Risk Management Agent**\n\n"
        
        if "help" in message_text or "commands" in message_text:
            response_text += "**Available Commands:**\n\n"
            response_text += "⚖️ **Risk Management:**\n"
            response_text += "• 'calculate risk BUY BTC 45000 0.8' - Calculate risk for BUY signal\n"
            response_text += "• 'risk SELL ETH 3000 0.7' - Calculate risk for SELL signal\n"
            response_text += "• 'status' - Show risk settings\n\n"
            response_text += "📊 **Risk Parameters:**\n"
            response_text += "• Stop Loss: 5% from entry price\n"
            response_text += "• Take Profit: 10% from entry price\n"
            response_text += "• Risk/Reward Ratio: 2:1\n"
            response_text += "• Position Size: Based on confidence (max 10%)\n\n"
            response_text += "📝 **Format:** risk [SIGNAL] [SYMBOL] [PRICE] [CONFIDENCE]\n"
            response_text += "Example: risk BUY BTC 45000 0.85"
        
        elif "status" in message_text or "settings" in message_text:
            response_text += "**Risk Management Settings:**\n\n"
            response_text += f"🟢 Status: Active (Port 8001)\n"
            response_text += f"💰 Address: {risk_manager_agent.address[:16]}...\n"
            response_text += f"🌐 Protocol: {PROTOCOL_NAME}\n\n"
            response_text += "📊 **Current Risk Parameters:**\n"
            response_text += "• Stop Loss: 5% below/above entry\n"
            response_text += "• Take Profit: 10% above/below entry\n"
            response_text += "• Risk/Reward Ratio: 2:1\n"
            response_text += "• Max Position Size: 10% of portfolio\n"
            response_text += "• Position Sizing: Confidence-based\n\n"
            response_text += "⚖️ **Risk Calculation Method:**\n"
            response_text += "• BUY: SL = Price × 0.95, TP = Price × 1.10\n"
            response_text += "• SELL: SL = Price × 1.05, TP = Price × 0.90\n"
            response_text += "• Position Size = min(10%, Confidence × 15%)"
        
        elif any(word in message_text for word in ["calculate", "risk", "buy", "sell"]):
            # Try to parse risk calculation request
            words = message_text.split()
            
            try:
                # Look for signal, symbol, price, and confidence in the message
                signal = None
                symbol = None
                price = None
                confidence = None
                
                for i, word in enumerate(words):
                    if word.upper() in ["BUY", "SELL"]:
                        signal = word.upper()
                    elif word.upper() in ["BTC", "ETH", "BNB", "ADA", "SOL", "BTCUSDT", "ETHUSDT"]:
                        symbol = word.upper()
                        if symbol in ["BTC"]: symbol = "BTCUSDT"
                        elif symbol in ["ETH"]: symbol = "ETHUSDT"
                    elif word.replace(".", "").replace(",", "").isdigit():
                        if price is None:
                            price = float(word.replace(",", ""))
                        elif confidence is None and 0 <= float(word) <= 1:
                            confidence = float(word)
                
                if signal and symbol and price and confidence:
                    # Perform risk calculation
                    if signal == "BUY":
                        stop_loss = price * 0.95
                        take_profit = price * 1.10
                    else:  # SELL
                        stop_loss = price * 1.05
                        take_profit = price * 0.90
                    
                    risk_pct = 5.0
                    reward_pct = 10.0
                    risk_reward_ratio = reward_pct / risk_pct
                    position_size = min(10.0, confidence * 15.0)
                    
                    response_text += f"📊 **Risk Calculation for {symbol}**\n\n"
                    response_text += f"🎯 Signal: {signal}\n"
                    response_text += f"💰 Entry Price: ${price:,.2f}\n"
                    response_text += f"🎲 Confidence: {confidence:.1%}\n\n"
                    response_text += f"⚖️ **Risk Management:**\n"
                    response_text += f"🛑 Stop Loss: ${stop_loss:,.2f}\n"
                    response_text += f"🎯 Take Profit: ${take_profit:,.2f}\n"
                    response_text += f"📊 Risk/Reward: {risk_reward_ratio:.1f}:1\n"
                    response_text += f"📈 Position Size: {position_size:.1f}%\n\n"
                    
                    if signal == "BUY":
                        risk_amount = price - stop_loss
                        profit_amount = take_profit - price
                    else:
                        risk_amount = stop_loss - price
                        profit_amount = price - take_profit
                    
                    response_text += f"💸 Risk per unit: ${risk_amount:,.2f}\n"
                    response_text += f"💰 Profit per unit: ${profit_amount:,.2f}\n"
                else:
                    response_text += "Please provide: signal (BUY/SELL), symbol, price, and confidence\n\n"
                    response_text += "**Example:** calculate risk BUY BTC 45000 0.8\n"
                    response_text += "This means: BUY signal for BTC at $45,000 with 80% confidence"
                    
            except Exception as e:
                response_text += f"Error parsing risk calculation request: {str(e)}\n"
                response_text += "Please use format: risk [SIGNAL] [SYMBOL] [PRICE] [CONFIDENCE]"
        
        else:
            response_text += "I'm your risk management specialist! ⚖️\n\n"
            response_text += "I calculate:\n"
            response_text += "🛑 Stop Loss levels (5% from entry)\n"
            response_text += "🎯 Take Profit levels (10% from entry)\n"
            response_text += "📊 Risk/Reward ratios (2:1)\n"
            response_text += "📈 Position sizing (confidence-based)\n\n"
            response_text += "Try: 'calculate risk BUY BTC 45000 0.8' or 'help'"
        
        # Include session ID in response if it was in the request
        if session_id:
            response_text += f"\n\nsession:{session_id}"
        
        # Determine where to send response (user agent if specified, otherwise sender)
        response_target = user_agent_address if user_agent_address else sender
        ctx.logger.info(f"📤 Sending risk analysis to: {response_target[:16]}...")
        
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
risk_manager_agent.include(risk_protocol)
risk_manager_agent.include(chat_protocol)

if __name__ == "__main__":
    print("=" * 60)
    print("⚖️ RISK MANAGER AGENT WITH CHAT - JSON FORMAT")
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
    print("� CHAT FEATURES:")
    print("  ✅ Interactive risk calculations via chat")
    print("  ✅ Real-time stop loss and take profit")
    print("  ✅ Position sizing recommendations")
    print("  ✅ Help commands and status queries")
    print("=" * 60)
    print("�📋 JSON Features:")
    print("  • Proper JSON request/response logging")
    print("  • Unified protocol: 'Crypto Trading v1'")
    print("  • Simple percentage-based calculations")
    print("  • Confidence-based position sizing")
    print("=" * 60)
    print("🎯 Starting Risk Manager Agent with Chat...")
    risk_manager_agent.run()
