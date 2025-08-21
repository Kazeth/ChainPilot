#!/usr/bin/env python3

"""
COMPREHENSIVE SIGNAL AGENT - PURE CHAT PROTOCOL
This version uses only chat protocol for communication between agents
"""

import asyncio
import random
import logging
import json
from datetime import datetime, timedelta
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
    TECHNICAL_AGENT_ADDRESS,
    NEWS_AGENT_ADDRESS,
    WHALE_AGENT_ADDRESS,
    RISK_MANAGER_ADDRESS,
    SIGNAL_AGENT_ADDRESS
)

# Configure logging
logging.basicConfig(level=logging.INFO)

# ========================================
# COMPREHENSIVE SIGNAL AGENT - CHAT ONLY
# ========================================

# Create comprehensive signal agent using shared constants
comprehensive_signal = Agent(
    name="comprehensive_signal",
    port=8002,
    seed="comprehensive_signal_seed_fixed",
    endpoint=["http://localhost:8002/submit"],
    
)

# Fund the agent
fund_agent_if_low(comprehensive_signal.wallet.address())

# Create chat protocol
chat_protocol = Protocol(spec=chat_protocol_spec)

# ========================================
# GLOBAL STORAGE FOR AGENT RESPONSES
# ========================================

# Global variables for tracking agent responses
agent_responses = {}
agent_response_timestamps = {}

# ========================================
# CHAT MESSAGE HANDLERS
# ========================================

@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle chat messages for signal agent interaction - unified handler"""
    
    # Check if the content is TextContent
    if not msg.content or not hasattr(msg.content[0], 'text'):
        ctx.logger.warning(f"💬 Received non-text content from {sender}: {type(msg.content[0]) if msg.content else 'empty'}")
        return
    
    ctx.logger.info(f"💬 Chat message from {sender}: {msg.content[0].text}")
    
    try:
        message_text = msg.content[0].text
        current_time = datetime.now()
        
        # Check if this is a response from one of our specialized agents
        if sender in [TECHNICAL_AGENT_ADDRESS, NEWS_AGENT_ADDRESS, WHALE_AGENT_ADDRESS, RISK_MANAGER_ADDRESS]:
            ctx.logger.info(f"📨 Received agent response from {sender[:16]}...")
            
            # Handle agent responses - store them for compilation
            symbol = None
            for common_symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]:
                if common_symbol in message_text.upper():
                    symbol = common_symbol
                    break
            
            if symbol:
                # Initialize responses dict for symbol if needed
                if symbol not in agent_responses:
                    agent_responses[symbol] = {}
                    agent_response_timestamps[symbol] = {}
                
                # Store response based on sender address
                if sender == TECHNICAL_AGENT_ADDRESS:
                    agent_responses[symbol]['technical'] = message_text
                    agent_response_timestamps[symbol]['technical'] = current_time
                    ctx.logger.info(f"📊 Technical analysis stored for {symbol}")
                elif sender == NEWS_AGENT_ADDRESS:
                    agent_responses[symbol]['news'] = message_text
                    agent_response_timestamps[symbol]['news'] = current_time
                    ctx.logger.info(f"📰 News analysis stored for {symbol}")
                elif sender == WHALE_AGENT_ADDRESS:
                    agent_responses[symbol]['whale'] = message_text
                    agent_response_timestamps[symbol]['whale'] = current_time
                    ctx.logger.info(f"🐋 Whale analysis stored for {symbol}")
                elif sender == RISK_MANAGER_ADDRESS:
                    agent_responses[symbol]['risk'] = message_text
                    agent_response_timestamps[symbol]['risk'] = current_time
                    ctx.logger.info(f"⚖️ Risk analysis stored for {symbol}")
            return  # Don't send response for agent messages
        
        # Handle user messages (not from specialized agents)
        # Parse the message to extract trading symbol and request type
        message_text_lower = message_text.lower()
        
        # Default response
        response_text = "🎯 **Comprehensive Signal Agent**\n\n"
        
        # Check if user is asking for a signal
        if any(word in message_text_lower for word in ["signal", "analysis", "analyze", "buy", "sell", "trade"]):
            # Extract session ID if present
            session_id = None
            if "session:" in message_text:
                try:
                    session_part = message_text.split("session:")[1].split()[0]
                    session_id = session_part.strip()
                except:
                    ctx.logger.warning("Could not extract session ID from message")
            
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
                response_text += f"🔄 **Analyzing {', '.join(symbols)}...**\n\n"
                response_text += "I'm gathering data from:\n"
                response_text += "📊 Technical Analysis Agent (RSI, MACD, Bollinger Bands)\n"
                response_text += "📰 News Sentiment Agent\n"
                response_text += "🐋 Whale Activity Agent\n"
                response_text += "⚖️ Risk Management Agent\n\n"
                response_text += "⏰ Please wait 5-10 seconds for comprehensive analysis...\n\n"
                
                # Trigger signal analysis for the requested symbols
                for symbol in symbols[:1]:  # Limit to first symbol to avoid overload
                    await handle_chat_signal_request(ctx, symbol, sender, session_id)
                
                response_text += f"📈 Analysis in progress for {symbols[0]}! Check responses above for detailed results."
            else:
                response_text += "Please specify a trading symbol (e.g., BTC, ETH, BNB, ADA, SOL)\n\n"
                response_text += "**Available commands:**\n"
                response_text += "• 'analyze BTC' - Get comprehensive BTC analysis\n"
                response_text += "• 'signal for ETH' - Get ETH trading signal\n"
                response_text += "• 'trade analysis BNBUSDT' - Get BNB analysis\n"
        
        elif "help" in message_text_lower or "commands" in message_text_lower:
            response_text += "**Available Commands:**\n\n"
            response_text += "🎯 **Signal Analysis:**\n"
            response_text += "• 'analyze [SYMBOL]' - Get comprehensive analysis\n"
            response_text += "• 'signal for [SYMBOL]' - Get trading signal\n"
            response_text += "• 'trade [SYMBOL]' - Get full trading recommendation\n\n"
            response_text += "📊 **Supported Symbols:**\n"
            response_text += "• BTC/Bitcoin → BTCUSDT\n"
            response_text += "• ETH/Ethereum → ETHUSDT\n"
            response_text += "• BNB/Binance → BNBUSDT\n"
            response_text += "• ADA/Cardano → ADAUSDT\n"
            response_text += "• SOL/Solana → SOLUSDT\n\n"
            response_text += "🔍 **Analysis includes:**\n"
            response_text += "• Technical indicators (RSI, MACD, Bollinger Bands)\n"
            response_text += "• News sentiment analysis\n"
            response_text += "• Whale activity monitoring\n"
            response_text += "• Risk management (Stop Loss & Take Profit)\n"
        
        elif "status" in message_text_lower:
            response_text += "**Agent Status:**\n\n"
            response_text += f"🟢 Signal Agent: Active (Port 8002)\n"
            response_text += f"📊 Technical Agent: {TECHNICAL_AGENT_ADDRESS[:16]}...\n"
            response_text += f"📰 News Agent: {NEWS_AGENT_ADDRESS[:16]}...\n"
            response_text += f"🐋 Whale Agent: {WHALE_AGENT_ADDRESS[:16]}...\n"
            response_text += f"⚖️ Risk Agent: {RISK_MANAGER_ADDRESS[:16]}...\n\n"
            response_text += f"🌐 Protocol: Chat Protocol\n"
            response_text += f"💰 Wallet: {comprehensive_signal.address[:16]}...\n"
        
        else:
            response_text += "I'm your comprehensive crypto trading signal agent! 🤖\n\n"
            response_text += "I can analyze cryptocurrency markets by coordinating with:\n"
            response_text += "📊 Technical Analysis\n"
            response_text += "📰 Sentiment Analysis  \n"
            response_text += "🐋 Whale Activity\n"
            response_text += "⚖️ Risk Management\n\n"
            response_text += "Try: 'analyze BTC' or 'help' for commands"
        
        # Send response back to user
        await ctx.send(
            sender,
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
async def handle_chat_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    ctx.logger.info(f"✅ Chat acknowledgement from {sender}")

# ========================================
# CHAT-BASED SIGNAL ANALYSIS FUNCTIONS
# ========================================

async def handle_chat_signal_request(ctx: Context, symbol: str, user_address: str, session_id: str = None):
    """Handle comprehensive signal requests through chat protocol"""
    ctx.logger.info(f"🎯 Processing chat-based signal request for {symbol} (session: {session_id})")
    
    try:
        # Clear any old responses for this symbol
        if symbol not in agent_responses:
            agent_responses[symbol] = {}
            agent_response_timestamps[symbol] = {}
        
        # Send chat messages to all agents for analysis
        ctx.logger.info(f"🚀 Sending chat requests to all agents for {symbol}")
        
        # Prepare session info for messages - include user agent address for responses
        session_text = f" session:{session_id}" if session_id else ""
        user_agent_text = f" user:{user_address}"
        
        # Request technical analysis
        await ctx.send(
            TECHNICAL_AGENT_ADDRESS,
            ChatMessage(
                content=[TextContent(text=f"analyze {symbol}{session_text}{user_agent_text}")]
            )
        )
        ctx.logger.info(f"📊 Technical analysis request sent for {symbol}")
        
        # Request news sentiment analysis
        await ctx.send(
            NEWS_AGENT_ADDRESS,
            ChatMessage(
                content=[TextContent(text=f"sentiment {symbol}{session_text}{user_agent_text}")]
            )
        )
        ctx.logger.info(f"📰 News sentiment request sent for {symbol}")
        
        # Request whale activity analysis
        await ctx.send(
            WHALE_AGENT_ADDRESS,
            ChatMessage(
                content=[TextContent(text=f"whale activity {symbol}{session_text}{user_agent_text}")]
            )
        )
        ctx.logger.info(f"🐋 Whale activity request sent for {symbol}")
        
        # Request risk management analysis
        await ctx.send(
            RISK_MANAGER_ADDRESS,
            ChatMessage(
                content=[TextContent(text=f"risk analysis {symbol}{session_text}{user_agent_text}")]
            )
        )
        ctx.logger.info(f"⚖️ Risk analysis request sent for {symbol}")
        
        # Wait for responses and compile comprehensive signal
        await asyncio.sleep(5)  # Give agents time to respond
        
        # Send comprehensive analysis back to user
        await send_comprehensive_analysis(ctx, symbol, user_address, session_id)
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing chat signal request for {symbol}: {e}")
        error_msg = f"❌ **Analysis Error for {symbol}**\n\nSorry, I encountered an error while processing your signal request. Please try again."
        await ctx.send(
            user_address,
            ChatMessage(
                content=[TextContent(text=error_msg)]
            )
        )

async def send_comprehensive_analysis(ctx: Context, symbol: str, user_address: str, session_id: str = None):
    """Send comprehensive analysis results to user agent for ASI1 processing"""
    ctx.logger.info(f"📈 Compiling comprehensive analysis for {symbol} (session: {session_id})")
    
    try:
        # Build comprehensive analysis response with session ID for user agent
        session_text = f" session:{session_id}" if session_id else ""
        analysis_text = f"📊 **Signal Agent Coordination for {symbol}**{session_text}\n\n"
        
        # Check if we have responses stored (from other chat handlers)
        if symbol in agent_responses:
            responses = agent_responses[symbol]
            
            analysis_text += "🎯 **Specialist Agent Coordination Complete:**\n"
            
            if 'technical' in responses:
                analysis_text += f"✅ Technical Analysis: Received ({len(responses['technical'])} chars)\n"
            else:
                analysis_text += "⏳ Technical Analysis: Pending\n"
            
            if 'news' in responses:
                analysis_text += f"✅ News Sentiment: Received ({len(responses['news'])} chars)\n"
            else:
                analysis_text += "⏳ News Sentiment: Pending\n"
            
            if 'whale' in responses:
                analysis_text += f"✅ Whale Activity: Received ({len(responses['whale'])} chars)\n"
            else:
                analysis_text += "⏳ Whale Activity: Pending\n"
            
            if 'risk' in responses:
                analysis_text += f"✅ Risk Management: Received ({len(responses['risk'])} chars)\n"
            else:
                analysis_text += "⏳ Risk Management: Pending\n"
        
        analysis_text += "\n🤖 **Signal Agent Role:** Successfully coordinated analysis requests to all specialist agents.\n"
        analysis_text += "📊 **Data Collection:** All responses aggregated and ready for AI processing.\n"
        analysis_text += f"🕒 **Coordination Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        analysis_text += "🎯 **Status:** Analysis coordination complete - ready for ASI1 summary generation."
        
        # Send analysis to user (user agent will handle ASI1 summarization)
        await ctx.send(
            user_address,
            ChatMessage(
                content=[TextContent(text=analysis_text)]
            )
        )
        
        ctx.logger.info(f"✅ Signal agent coordination data sent for {symbol} (session: {session_id})")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error sending signal analysis for {symbol}: {str(e)}")
        error_msg = f"Error compiling signal analysis for {symbol}: {str(e)}"
        
        # Send error to user
        await ctx.send(
            user_address,
            ChatMessage(
                content=[TextContent(text=error_msg)]
            )
        )

# ========================================
# PERIODIC CLEANUP
# ========================================

@comprehensive_signal.on_interval(period=300.0)  # Clean up every 5 minutes
async def cleanup_old_responses(ctx: Context):
    """Clean up old agent responses to prevent memory leaks"""
    try:
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=10)
        
        symbols_to_remove = []
        for symbol in agent_response_timestamps:
            # Check if all timestamps for this symbol are old
            timestamps = agent_response_timestamps[symbol]
            if timestamps and all(timestamp < cutoff_time for timestamp in timestamps.values()):
                symbols_to_remove.append(symbol)
        
        for symbol in symbols_to_remove:
            del agent_responses[symbol]
            del agent_response_timestamps[symbol]
            ctx.logger.info(f"🧹 Cleaned up old responses for {symbol}")
            
    except Exception as e:
        ctx.logger.error(f"❌ Error in cleanup: {e}")

# ========================================
# PROTOCOL INCLUSION
# ========================================

# Include only chat protocol
comprehensive_signal.include(chat_protocol)

if __name__ == "__main__":
    print("=" * 70)
    print("🎯 COMPREHENSIVE SIGNAL AGENT - PURE CHAT PROTOCOL")
    print("=" * 70)
    print(f"Agent address: {comprehensive_signal.address}")
    print(f"Port: 8002")
    print()
    print("🔧 CHAT PROTOCOL FEATURES:")
    print("  ✅ Pure chat-based communication")
    print("  ✅ No legacy signal protocol dependencies")
    print("  ✅ Natural language signal requests")
    print("  ✅ Real-time agent coordination via chat")
    print("  ✅ Comprehensive analysis compilation")
    print()
    print("💬 CHAT FEATURES:")
    print("  ✅ Interactive chat protocol support")
    print("  ✅ Multi-agent response coordination")
    print("  ✅ Real-time trading analysis via chat")
    print("  ✅ Help commands and status queries")
    print("  ✅ Automatic response cleanup")
    print()
    print("📊 Expected Agent Network:")
    print(f"  Technical: {TECHNICAL_AGENT_ADDRESS}")
    print(f"  News: {NEWS_AGENT_ADDRESS}")
    print(f"  Whale: {WHALE_AGENT_ADDRESS}")
    print(f"  Risk: {RISK_MANAGER_ADDRESS}")
    print()
    print("🚀 Starting Comprehensive Signal Agent with Pure Chat...")
    print("=" * 70)
    comprehensive_signal.run()
