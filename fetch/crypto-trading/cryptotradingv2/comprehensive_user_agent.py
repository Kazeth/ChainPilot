from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
)
import logging
import asyncio
import requests
import json
import uuid
import datetime
import re
from shared_types import (
    SIGNAL_AGENT_ADDRESS,
    TECHNICAL_AGENT_ADDRESS,
    NEWS_AGENT_ADDRESS,
    WHALE_AGENT_ADDRESS,
    RISK_MANAGER_ADDRESS
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ASI1 API Configuration
ASI1_API_KEY = "sk_f31d6a0de98f412b91427e2ee7e8dc2957a8bd305a1146869d500252c187a224"
ASI1_BASE_URL = "https://api.asi1.ai/v1"
ASI1_HEADERS = {
    "Authorization": f"Bearer {ASI1_API_KEY}",
    "Content-Type": "application/json"
}
ASI1_MODEL = "asi1-mini"  # Use the lightest model by default

# Create User Agent with mailbox for chat
user_agent = Agent(
    name="user_agent",
    port=8008,  # Changed from 8007 to avoid conflict
    seed="user_agent_seed_phrase",
    endpoint=["http://localhost:8008/submit"],
    mailbox=True
)

# Fund the agent if balance is low
fund_agent_if_low(user_agent.wallet.address())

# Create chat protocol for interactive communication
chat_protocol = Protocol(spec=chat_protocol_spec)

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

# Analysis data storage for collecting responses from all agents
class AnalysisCollector:
    def __init__(self):
        self.sessions = {}  # Store analysis data by session_id
    
    def create_session(self, session_id: str, symbol: str, user_sender: str):
        """Create a new analysis session"""
        self.sessions[session_id] = {
            "symbol": symbol,
            "user_sender": user_sender,
            "technical_data": None,
            "news_data": None,
            "whale_data": None,
            "risk_data": None,
            "signal_data": None,
            "completed_agents": set(),
            "start_time": asyncio.get_event_loop().time()
        }
    
    def add_agent_response(self, session_id: str, agent_type: str, data: str):
        """Add response from specific agent"""
        if session_id in self.sessions:
            self.sessions[session_id][f"{agent_type}_data"] = data
            self.sessions[session_id]["completed_agents"].add(agent_type)
    
    def is_analysis_complete(self, session_id: str) -> bool:
        """Check if all agents have responded"""
        if session_id not in self.sessions:
            return False
        expected_agents = {"technical", "news", "whale", "risk", "signal"}
        completed = self.sessions[session_id]["completed_agents"]
        return expected_agents.issubset(completed)
    
    def get_analysis_data(self, session_id: str):
        """Get all collected analysis data"""
        return self.sessions.get(session_id, {})
    
    def cleanup_old_sessions(self, max_age_seconds=300):  # 5 minutes
        """Remove old analysis sessions"""
        current_time = asyncio.get_event_loop().time()
        expired_sessions = [
            sid for sid, data in self.sessions.items()
            if current_time - data["start_time"] > max_age_seconds
        ]
        for sid in expired_sessions:
            del self.sessions[sid]

# Global analysis collector
analysis_collector = AnalysisCollector()

# First-time user tracker
first_time_users = set()

def create_welcome_message() -> str:
    """Create comprehensive welcome message with all available commands"""
    welcome = """🤖 **Welcome to ChainPilot Crypto Trading Bot!** 

🚀 **This bot uses ASI1 AI to analyze cryptocurrency with 5 specialist agents:**
• 📊 Technical Analysis (RSI, MACD, Bollinger Bands)
• 📰 News Sentiment Analysis 
• 🐋 Whale Activity Monitoring
• ⚖️ Risk Management
• 🎯 Signal Coordination

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 **MAIN COMMANDS - Start here:**

💰 **COMPREHENSIVE ANALYSIS (Automatic ASI1 Summary)**
• `analyze BTC` - Complete Bitcoin analysis
• `analyze ETH` - Complete Ethereum analysis  
• `analyze SOL` - Complete Solana analysis
• `analyze [SYMBOL]` - Analyze other coins

📊 **SPECIFIC ANALYSIS**
• `technical BTC` - Technical analysis only
• `news ETH` - News sentiment only
• `whale SOL` - Whale activity only
• `risk BNB` - Risk analysis only

🛠️ **UTILITY COMMANDS**
• `help` - Show all commands
• `status` - System agents status
• `pairs` - Available trading pairs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **HOW TO USE:**

1️⃣ **For complete analysis:** Type `analyze BTC`
   ⏰ Wait 15-20 seconds for ASI1 AI summary

2️⃣ **For quick analysis:** Type `technical ETH` 
   ⚡ Get instant technical results

3️⃣ **Use natural language:** "How is Ethereum looking today?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **USAGE EXAMPLE:**
```
👤 User: analyze BTC
🤖 Bot:  ⏰ Please wait 15-20 seconds...
🤖 Bot:  🎯 AI-Powered Analysis Summary for BTCUSDT
         📈 RECOMMENDATION: BUY
         💰 Technical signals show bullish trend...
         📰 News sentiment positive at 75%...
         🐋 Large whale accumulation detected...
         ⚖️ Risk level: MODERATE (3/10)
         📊 Confidence: HIGH (8.5/10)
```

🚀 **QUICK START:**
• Type `analyze BTC` to begin
• Type `help` for complete assistance
• Type `status` to check system

⚠️ **DISCLAIMER:** This is not financial advice. Always DYOR!
� **Support:** Ketik `help` jika butuh bantuan

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 **Ready to analyze crypto? Type `analyze BTC` now!**"""
    
    return welcome

async def generate_asi1_summary(analysis_data: dict, ctx: Context) -> str:
    """Use ASI1 to generate a friendly summary of all analysis data"""
    try:
        symbol = analysis_data.get("symbol", "Unknown")
        technical_data = analysis_data.get("technical_data", "No technical analysis available")
        news_data = analysis_data.get("news_data", "No news analysis available")
        whale_data = analysis_data.get("whale_data", "No whale analysis available")
        risk_data = analysis_data.get("risk_data", "No risk analysis available")
        signal_data = analysis_data.get("signal_data", "No signal analysis available")
        
        # Create comprehensive prompt for ASI1
        system_prompt = """You are a friendly cryptocurrency trading assistant. Your job is to analyze comprehensive trading data and provide a clear, actionable summary for retail traders. 

Key guidelines:
1. Start with a clear overall recommendation (BUY/SELL/HOLD)
2. Explain the reasoning in simple terms
3. Highlight the most important factors
4. Use emojis to make it engaging
5. Include risk warnings when appropriate
6. Keep it concise but comprehensive
7. Use friendly, conversational tone
8. Avoid jargon - explain technical terms simply"""

        user_prompt = f"""Please analyze this comprehensive trading data for {symbol} and provide a friendly summary:

**TECHNICAL ANALYSIS:**
{technical_data}

**NEWS SENTIMENT:**
{news_data}

**WHALE ACTIVITY:**
{whale_data}

**RISK MANAGEMENT:**
{risk_data}

**SIGNAL COORDINATION:**
{signal_data}

Please provide a comprehensive but easy-to-understand summary that includes:
1. Overall trading recommendation
2. Key supporting factors
3. Main risks to consider
4. Suggested action plan
5. Confidence level

Make it friendly and accessible for both beginners and experienced traders."""

        # Prepare ASI1 API request
        payload = {
            "model": ASI1_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }

        # Call ASI1 API
        ctx.logger.info(f"🤖 Calling ASI1 API for {symbol} analysis summary...")
        response = requests.post(
            f"{ASI1_BASE_URL}/chat/completions",
            headers=ASI1_HEADERS,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            ctx.logger.error(f"ASI1 API Error: {response.status_code} - {response.text}")
            # Fallback to simple summary
            return f"⚠️ **Analysis Summary for {symbol}**\n\nI collected data from all agents but couldn't generate an AI summary. Here's the raw data:\n\n📊 Technical: {technical_data[:200]}...\n📰 News: {news_data[:200]}...\n🐋 Whale: {whale_data[:200]}...\n⚖️ Risk: {risk_data[:200]}..."
        
        response.raise_for_status()
        result = response.json()
        
        ai_summary = result["choices"][0]["message"]["content"]
        
        # Add header and metadata
        final_summary = f"🎯 **AI-Powered Analysis Summary for {symbol}**\n"
        final_summary += f"📅 Generated: {asyncio.get_event_loop().time()}\n"
        final_summary += f"🤖 Powered by ASI1 AI\n\n"
        final_summary += ai_summary
        final_summary += f"\n\n---\n*This analysis combines technical indicators, news sentiment, whale activity, and risk management. Always do your own research before trading.*"
        
        ctx.logger.info(f"✅ ASI1 summary generated successfully for {symbol}")
        return final_summary
        
    except Exception as e:
        ctx.logger.error(f"❌ Error generating ASI1 summary: {str(e)}")
        # Fallback summary
        return f"⚠️ **Analysis Summary for {symbol}**\n\nI collected comprehensive analysis data but encountered an error generating the AI summary. All agent responses were received successfully. Please try again or contact support if the issue persists.\n\nError: {str(e)}"

async def generate_specific_asi1_summary(analysis_type: str, symbol: str, data: str, ctx: Context) -> str:
    """Use ASI1 to generate a friendly summary for specific analysis type"""
    try:
        # Create specific prompt based on analysis type
        if analysis_type == "technical":
            system_prompt = """You are a cryptocurrency technical analysis expert. Analyze the technical data and provide clear, actionable insights for traders.

Focus on:
1. Key technical indicators (RSI, MACD, Bollinger Bands, SMA, ATR)
2. Support and resistance levels
3. Trend direction and strength
4. Entry/exit points
5. Risk levels

Make it friendly and accessible, use emojis, and provide clear buy/sell/hold recommendation."""
            
        elif analysis_type == "news":
            system_prompt = """You are a cryptocurrency news sentiment analyst. Analyze the news sentiment data and provide clear insights about market mood and potential impact.

Focus on:
1. Overall sentiment score
2. Key news themes affecting price
3. Market mood and investor confidence
4. Potential catalysts or risks
5. Short-term sentiment outlook

Make it engaging with emojis and provide sentiment-based trading insights."""
            
        elif analysis_type == "whale":
            system_prompt = """You are a whale activity analyst for cryptocurrency markets. Analyze the whale transaction data and provide insights about large holder behavior.

Focus on:
1. Large transaction patterns
2. Whale accumulation or distribution
3. Market impact of whale movements
4. Liquidity and volume analysis
5. Whale behavior implications for price

Make it clear and engaging with emojis, explaining what whale activity means for regular traders."""
            
        elif analysis_type == "risk":
            system_prompt = """You are a cryptocurrency risk management expert. Analyze the risk data and provide clear risk assessment and management recommendations.

Focus on:
1. Current risk level assessment
2. Stop loss recommendations
3. Position sizing suggestions
4. Risk/reward ratios
5. Portfolio protection strategies

Make it practical and actionable with emojis, helping traders manage their risk effectively."""
            
        else:
            system_prompt = "You are a cryptocurrency analysis expert. Provide clear, actionable insights based on the provided data."

        user_prompt = f"Analyze this {analysis_type} data for {symbol}:\n\n{data}\n\nProvide a clear, friendly summary with actionable insights and recommendations."

        # Prepare ASI1 API request
        payload = {
            "model": ASI1_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        # Call ASI1 API
        ctx.logger.info(f"🤖 Calling ASI1 API for {symbol} {analysis_type} summary...")
        response = requests.post(
            f"{ASI1_BASE_URL}/chat/completions",
            headers=ASI1_HEADERS,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            ctx.logger.error(f"ASI1 API Error: {response.status_code} - {response.text}")
            return f"⚠️ **{analysis_type.title()} Analysis for {symbol}**\n\n{data[:500]}...\n\n*ASI1 summary temporarily unavailable. Raw data shown above.*"
        
        response.raise_for_status()
        result = response.json()
        
        ai_summary = result["choices"][0]["message"]["content"]
        
        # Add header and metadata
        analysis_emoji = {"technical": "📊", "news": "📰", "whale": "🐋", "risk": "⚖️"}
        emoji = analysis_emoji.get(analysis_type, "📈")
        
        final_summary = f"{emoji} **AI-Powered {analysis_type.title()} Analysis for {symbol}**\n"
        final_summary += f"📅 Generated: {datetime.datetime.now().strftime('%H:%M:%S')}\n"
        final_summary += f"🤖 Powered by ASI1 AI\n\n"
        final_summary += ai_summary
        final_summary += f"\n\n---\n*This {analysis_type} analysis is AI-generated. Always do your own research before trading.*"
        
        ctx.logger.info(f"✅ ASI1 {analysis_type} summary generated successfully for {symbol}")
        return final_summary
        
    except Exception as e:
        ctx.logger.error(f"❌ Error generating ASI1 {analysis_type} summary: {str(e)}")
        return f"⚠️ **{analysis_type.title()} Analysis for {symbol}**\n\n{data[:500]}...\n\nError generating AI summary: {str(e)}"

# ========================================
# CHAT PROTOCOL HANDLERS
# ========================================

@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle chat messages for comprehensive user interaction"""
    
    # Check if the content is TextContent
    if not msg.content or not hasattr(msg.content[0], 'text'):
        ctx.logger.warning(f"💬 Received non-text content from {sender}: {type(msg.content[0]) if msg.content else 'empty'}")
        return
    
    ctx.logger.info(f"💬 Chat message from {sender}: {msg.content[0].text}")
    
    # Check if this is a response from one of our specialist agents
    agent_responses = {
        TECHNICAL_AGENT_ADDRESS: "technical",
        NEWS_AGENT_ADDRESS: "news", 
        WHALE_AGENT_ADDRESS: "whale",
        RISK_MANAGER_ADDRESS: "risk",
        SIGNAL_AGENT_ADDRESS: "signal"
    }
    
    # If this is from a specialist agent, handle as agent response
    if sender in agent_responses:
        agent_type = agent_responses[sender]
        message_content = msg.content[0].text
        
        # Look for session ID in the message
        session_id = None
        if "session:" in message_content:
            try:
                session_part = message_content.split("session:")[1].split()[0]
                session_id = session_part.strip()
            except:
                ctx.logger.warning(f"Could not extract session ID from {agent_type} response")
        
        # If we have a session ID, add this response to the collection
        if session_id and session_id in analysis_collector.sessions:
            ctx.logger.info(f"📊 Received {agent_type} analysis for session {session_id}")
            analysis_collector.add_agent_response(session_id, agent_type, message_content)
            
            # Check if this is a specific analysis type (single agent response expected)
            session_data = analysis_collector.sessions[session_id]
            analysis_type = session_data.get("analysis_type")
            
            if analysis_type and analysis_type == agent_type:
                # This is a specific analysis session, generate immediate ASI1 summary
                ctx.logger.info(f"✅ {analysis_type.title()} analysis completed for session {session_id}! Generating ASI1 summary...")
                
                user_sender = session_data.get("user_sender")
                symbol = session_data.get("symbol")
                
                if user_sender:
                    # Generate specific AI summary using ASI1
                    ai_summary = await generate_specific_asi1_summary(analysis_type, symbol, message_content, ctx)
                    
                    # Send the summary back to the user
                    await ctx.send(
                        user_sender,
                        ChatMessage(
                            content=[TextContent(text=ai_summary)]
                        )
                    )
                    
                    # Clean up the session
                    del analysis_collector.sessions[session_id]
                    ctx.logger.info(f"🧹 Cleaned up {analysis_type} session {session_id}")
                else:
                    ctx.logger.error(f"No user_sender found for {analysis_type} session {session_id}")
                    
            # Check if all agents have responded for comprehensive analysis
            elif analysis_collector.is_analysis_complete(session_id):
                ctx.logger.info(f"✅ All agents completed for session {session_id}! Generating ASI1 summary...")
                
                # Get all analysis data
                analysis_data = analysis_collector.get_analysis_data(session_id)
                user_sender = analysis_data.get("user_sender")
                
                if user_sender:
                    # Generate comprehensive AI summary using ASI1
                    ai_summary = await generate_asi1_summary(analysis_data, ctx)
                    
                    # Send the summary back to the user
                    await ctx.send(
                        user_sender,
                        ChatMessage(
                            content=[TextContent(text=ai_summary)]
                        )
                    )
                    
                    # Clean up the session
                    del analysis_collector.sessions[session_id]
                    ctx.logger.info(f"🧹 Cleaned up session {session_id}")
                else:
                    ctx.logger.error(f"No user_sender found for session {session_id}")
            else:
                completed = analysis_collector.sessions[session_id]["completed_agents"]
                ctx.logger.info(f"⏳ Session {session_id} waiting for: {set(['technical', 'news', 'whale', 'risk', 'signal']) - completed}")
        
        # Don't process agent responses as user commands
        return
    
    try:
        message_text = msg.content[0].text.lower()
        
        # Check if this is a first-time user and send welcome message
        if sender not in first_time_users:
            ctx.logger.info(f"🆕 First-time user detected: {sender[:16]}...")
            first_time_users.add(sender)
            
            # Send welcome message
            welcome_msg = create_welcome_message()
            await ctx.send(
                sender,
                ChatMessage(
                    content=[TextContent(text=welcome_msg)]
                )
            )
            ctx.logger.info(f"✅ Welcome message sent to {sender[:16]}...")
            
            # If user just sent a greeting, don't process further
            if any(greeting in message_text for greeting in ["hi", "hello", "hey", "start"]):
                return
        
        response_text = "🚀 **Comprehensive Crypto Trading System**\n\n"
        
        # Parse different types of requests
        if any(word in message_text for word in ["signal", "analyze", "analysis", "trade"]):
            # Look for trading symbols
            symbols = []
            common_symbols = ["btc", "eth", "bnb", "ada", "sol", "btcusdt", "ethusdt", "bnbusdt", "adausdt", "solusdt"]
            
            for symbol in common_symbols:
                if symbol in message_text:
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
                symbol = symbols[0]  # Use first symbol found
                response_text += f"🔄 **Requesting comprehensive analysis for {symbol}...**\n\n"
                
                # Create unique analysis session
                session_id = str(uuid.uuid4())
                analysis_collector.create_session(session_id, symbol, sender)
                ctx.logger.info(f"🆕 Created analysis session {session_id} for {symbol}")
                
                # Send analysis request to signal agent (orchestrator)
                try:
                    chat_message = ChatMessage(
                        content=[TextContent(text=f"analyze {symbol} for trading signal session:{session_id}")]
                    )
                    await ctx.send(SIGNAL_AGENT_ADDRESS, chat_message)
                    
                    response_text += f"📊 **Analysis requested from:**\n"
                    response_text += f"🎯 Signal Agent (Orchestrator)\n"
                    response_text += f"📈 Technical Analysis Agent\n"
                    response_text += f"📰 News Sentiment Agent\n"
                    response_text += f"🐋 Whale Activity Agent\n"
                    response_text += f"⚖️ Risk Management Agent\n\n"
                    response_text += f"⏰ **Please wait 15-20 seconds for complete analysis...**\n"
                    response_text += f"🤖 **ASI1 AI will generate a comprehensive summary!**\n"
                    response_text += f"📊 Session ID: `{session_id}`"
                    
                except Exception as e:
                    response_text += f"❌ Error requesting analysis: {str(e)}"
            else:
                response_text += "Please specify a trading symbol (e.g., BTC, ETH, BNB, ADA, SOL)\n\n"
                response_text += "**Example commands:**\n"
                response_text += "• 'analyze BTC' - Get comprehensive BTC analysis\n"
                response_text += "• 'signal for ETH' - Get ETH trading signal\n"
                response_text += "• 'trade analysis BNBUSDT' - Get BNB trading analysis\n"
        
        elif any(word in message_text for word in ["technical", "rsi", "macd", "bollinger"]):
            response_text += "📊 **Technical Analysis Request with ASI1 Summary**\n\n"
            
            # Look for symbols
            symbols = []
            common_symbols = ["btc", "eth", "bnb", "ada", "sol", "bitcoin", "ethereum", "binance"]
            
            for word in message_text.split():
                if word in common_symbols:
                    if word in ["btc", "bitcoin"]:
                        symbols.append("BTCUSDT")
                    elif word in ["eth", "ethereum"]:
                        symbols.append("ETHUSDT")
                    elif word in ["bnb", "binance"]:
                        symbols.append("BNBUSDT")
                    elif word in ["ada", "cardano"]:
                        symbols.append("ADAUSDT")
                    elif word in ["sol", "solana"]:
                        symbols.append("SOLUSDT")
                    else:
                        symbols.append(f"{word.upper()}USDT")
            
            if symbols:
                symbol = symbols[0]
                response_text += f"🔄 **Requesting technical analysis for {symbol}...**\n\n"
                
                # Create unique session for this specific analysis
                session_id = str(uuid.uuid4())
                analysis_collector.create_session(session_id, symbol, sender)
                analysis_collector.sessions[session_id]["analysis_type"] = "technical"  # Mark as technical-only
                ctx.logger.info(f"🆕 Created technical analysis session {session_id} for {symbol}")
                
                # Send request directly to technical agent with session ID
                try:
                    chat_message = ChatMessage(
                        content=[TextContent(text=f"analyze {symbol} session:{session_id} user:{sender}")]
                    )
                    await ctx.send(TECHNICAL_AGENT_ADDRESS, chat_message)
                    
                    response_text += f"📈 **Technical Analysis Agent contacted**\n"
                    response_text += f"⏰ **Please wait 5-10 seconds...**\n"
                    response_text += f"🤖 **ASI1 AI will summarize the technical data!**\n"
                    response_text += f"📊 Session ID: `{session_id}`"
                    
                except Exception as e:
                    response_text += f"❌ Error requesting technical analysis: {str(e)}"
            else:
                response_text += "Please specify a symbol (e.g., 'technical BTC', 'technical analysis for ETH')\n\n"
                response_text += "**Supported symbols:** BTC, ETH, BNB, ADA, SOL"
        
        elif any(word in message_text for word in ["news", "sentiment", "headlines"]):
            response_text += "📰 **News Sentiment Analysis with ASI1 Summary**\n\n"
            
            # Look for symbols
            symbols = []
            common_symbols = ["btc", "eth", "bnb", "ada", "sol", "bitcoin", "ethereum", "binance"]
            
            for word in message_text.split():
                if word in common_symbols:
                    if word in ["btc", "bitcoin"]:
                        symbols.append("BTCUSDT")
                    elif word in ["eth", "ethereum"]:
                        symbols.append("ETHUSDT")
                    elif word in ["bnb", "binance"]:
                        symbols.append("BNBUSDT")
                    elif word in ["ada", "cardano"]:
                        symbols.append("ADAUSDT")
                    elif word in ["sol", "solana"]:
                        symbols.append("SOLUSDT")
                    else:
                        symbols.append(f"{word.upper()}USDT")
            
            if symbols:
                symbol = symbols[0]
                response_text += f"🔄 **Requesting news sentiment for {symbol}...**\n\n"
                
                # Create unique session for this specific analysis
                session_id = str(uuid.uuid4())
                analysis_collector.create_session(session_id, symbol, sender)
                analysis_collector.sessions[session_id]["analysis_type"] = "news"  # Mark as news-only
                ctx.logger.info(f"🆕 Created news analysis session {session_id} for {symbol}")
                
                # Send request directly to news agent with session ID
                try:
                    chat_message = ChatMessage(
                        content=[TextContent(text=f"analyze {symbol} session:{session_id} user:{sender}")]
                    )
                    await ctx.send(NEWS_AGENT_ADDRESS, chat_message)
                    
                    response_text += f"📰 **News Sentiment Agent contacted**\n"
                    response_text += f"⏰ **Please wait 5-10 seconds...**\n"
                    response_text += f"🤖 **ASI1 AI will summarize the news sentiment!**\n"
                    response_text += f"📊 Session ID: `{session_id}`"
                    
                except Exception as e:
                    response_text += f"❌ Error requesting news analysis: {str(e)}"
            else:
                response_text += "Please specify a symbol (e.g., 'news BTC', 'sentiment for ETH')\n\n"
                response_text += "**Supported symbols:** BTC, ETH, BNB, ADA, SOL"
        
        elif any(word in message_text for word in ["whale", "transactions", "flow"]):
            response_text += "🐋 **Whale Activity Analysis with ASI1 Summary**\n\n"
            
            # Look for symbols
            symbols = []
            common_symbols = ["btc", "eth", "bnb", "ada", "sol", "bitcoin", "ethereum", "binance"]
            
            for word in message_text.split():
                if word in common_symbols:
                    if word in ["btc", "bitcoin"]:
                        symbols.append("BTCUSDT")
                    elif word in ["eth", "ethereum"]:
                        symbols.append("ETHUSDT")
                    elif word in ["bnb", "binance"]:
                        symbols.append("BNBUSDT")
                    elif word in ["ada", "cardano"]:
                        symbols.append("ADAUSDT")
                    elif word in ["sol", "solana"]:
                        symbols.append("SOLUSDT")
                    else:
                        symbols.append(f"{word.upper()}USDT")
            
            if symbols:
                symbol = symbols[0]
                response_text += f"🔄 **Requesting whale activity for {symbol}...**\n\n"
                
                # Create unique session for this specific analysis
                session_id = str(uuid.uuid4())
                analysis_collector.create_session(session_id, symbol, sender)
                analysis_collector.sessions[session_id]["analysis_type"] = "whale"  # Mark as whale-only
                ctx.logger.info(f"🆕 Created whale analysis session {session_id} for {symbol}")
                
                # Send request directly to whale agent with session ID
                try:
                    chat_message = ChatMessage(
                        content=[TextContent(text=f"analyze {symbol} session:{session_id} user:{sender}")]
                    )
                    await ctx.send(WHALE_AGENT_ADDRESS, chat_message)
                    
                    response_text += f"🐋 **Whale Activity Agent contacted**\n"
                    response_text += f"⏰ **Please wait 5-10 seconds...**\n"
                    response_text += f"🤖 **ASI1 AI will summarize the whale data!**\n"
                    response_text += f"📊 Session ID: `{session_id}`"
                    
                except Exception as e:
                    response_text += f"❌ Error requesting whale analysis: {str(e)}"
            else:
                response_text += "Please specify a symbol (e.g., 'whale BTC', 'whale activity for ETH')\n\n"
                response_text += "**Supported symbols:** BTC, ETH, BNB, ADA, SOL"
        
        elif any(word in message_text for word in ["risk", "management", "stop", "loss"]):
            response_text += "⚖️ **Risk Management Analysis with ASI1 Summary**\n\n"
            
            # Look for symbols
            symbols = []
            common_symbols = ["btc", "eth", "bnb", "ada", "sol", "bitcoin", "ethereum", "binance"]
            
            for word in message_text.split():
                if word in common_symbols:
                    if word in ["btc", "bitcoin"]:
                        symbols.append("BTCUSDT")
                    elif word in ["eth", "ethereum"]:
                        symbols.append("ETHUSDT")
                    elif word in ["bnb", "binance"]:
                        symbols.append("BNBUSDT")
                    elif word in ["ada", "cardano"]:
                        symbols.append("ADAUSDT")
                    elif word in ["sol", "solana"]:
                        symbols.append("SOLUSDT")
                    else:
                        symbols.append(f"{word.upper()}USDT")
            
            if symbols:
                symbol = symbols[0]
                response_text += f"🔄 **Requesting risk analysis for {symbol}...**\n\n"
                
                # Create unique session for this specific analysis
                session_id = str(uuid.uuid4())
                analysis_collector.create_session(session_id, symbol, sender)
                analysis_collector.sessions[session_id]["analysis_type"] = "risk"  # Mark as risk-only
                ctx.logger.info(f"🆕 Created risk analysis session {session_id} for {symbol}")
                
                # Send request directly to risk agent with session ID
                try:
                    chat_message = ChatMessage(
                        content=[TextContent(text=f"analyze {symbol} session:{session_id} user:{sender}")]
                    )
                    await ctx.send(RISK_MANAGER_ADDRESS, chat_message)
                    
                    response_text += f"⚖️ **Risk Management Agent contacted**\n"
                    response_text += f"⏰ **Please wait 5-10 seconds...**\n"
                    response_text += f"🤖 **ASI1 AI will summarize the risk analysis!**\n"
                    response_text += f"📊 Session ID: `{session_id}`"
                    
                except Exception as e:
                    response_text += f"❌ Error requesting risk analysis: {str(e)}"
            else:
                response_text += "Please specify a symbol (e.g., 'risk BTC', 'risk management for ETH')\n\n"
                response_text += "**Supported symbols:** BTC, ETH, BNB, ADA, SOL"
        
        elif any(word in message_text for word in ["session", "summary"]) and any(char.isdigit() or char in "abcdef-" for char in message_text):
            # Session ID retrieval - look for UUID pattern
            import re
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            session_match = re.search(uuid_pattern, message_text)
            
            if session_match:
                session_id = session_match.group()
                ctx.logger.info(f"🔍 User requested session: {session_id}")
                
                if session_id in analysis_collector.sessions:
                    session_data = analysis_collector.sessions[session_id]
                    completed_agents = session_data["completed_agents"]
                    
                    response_text += f"📊 **Session Status: {session_id}**\n\n"
                    response_text += f"🎯 Symbol: {session_data['symbol']}\n"
                    response_text += f"⏰ Created: {session_data['start_time']:.0f} seconds ago\n\n"
                    
                    # Show which agents have responded
                    expected_agents = {"technical", "news", "whale", "risk", "signal"}
                    response_text += "**📋 Agent Response Status:**\n"
                    for agent in expected_agents:
                        status = "✅" if agent in completed_agents else "⏳"
                        response_text += f"{status} {agent.title()} Agent\n"
                    
                    # Check if ready for ASI1 summary
                    if analysis_collector.is_analysis_complete(session_id):
                        response_text += f"\n🤖 **Ready for ASI1 Summary!**\n"
                        response_text += f"All agents have responded. Generating summary...\n\n"
                        
                        # Generate ASI1 summary manually
                        try:
                            analysis_data = analysis_collector.get_analysis_data(session_id)
                            ai_summary = await generate_asi1_summary(analysis_data, ctx)
                            
                            # Send the summary
                            await ctx.send(
                                sender,
                                ChatMessage(
                                    content=[TextContent(text=ai_summary)]
                                )
                            )
                            
                            # Clean up the session
                            del analysis_collector.sessions[session_id]
                            ctx.logger.info(f"🧹 Session {session_id} completed and cleaned up")
                            return
                            
                        except Exception as e:
                            response_text += f"❌ Error generating summary: {str(e)}"
                    else:
                        missing = expected_agents - completed_agents
                        response_text += f"\n⏳ **Waiting for:** {', '.join(missing)}\n"
                        response_text += f"📊 Progress: {len(completed_agents)}/5 agents completed\n"
                else:
                    response_text += f"❌ **Session Not Found: {session_id}**\n\n"
                    response_text += "This session may have:\n"
                    response_text += "• Already been completed and cleaned up\n"
                    response_text += "• Expired (sessions last 5 minutes)\n"
                    response_text += "• Never existed\n\n"
                    response_text += "💡 **Try starting a new analysis:**\n"
                    response_text += "• 'analyze BTC' - New comprehensive analysis\n"
            else:
                response_text += "Please include a valid session ID (UUID format)\n"
                response_text += "Example: 'session 1335a807-4c3f-4cc4-8dcc-c2ee8ac46a08'"
        
        elif "help" in message_text or "commands" in message_text:
            response_text += "**📚 ChainPilot Commands Guide:**\n\n"
            response_text += "🔥 **MAIN COMMANDS (with ASI1 AI Summary):**\n"
            response_text += "• `analyze BTC` - Full comprehensive analysis\n"
            response_text += "• `analyze ETH` - Complete Ethereum analysis\n"
            response_text += "• `analyze SOL` - Full Solana analysis\n\n"
            response_text += "📊 **SPECIFIC ANALYSIS (with ASI1 Summary):**\n"
            response_text += "• `technical BTC` - Technical indicators only\n"
            response_text += "• `news ETH` - News sentiment only\n"
            response_text += "• `whale SOL` - Whale activity only\n"
            response_text += "• `risk BNB` - Risk management only\n\n"
            response_text += "�️ **UTILITY COMMANDS:**\n"
            response_text += "• `help` - Show this command guide\n"
            response_text += "• `status` - System and agents status\n"
            response_text += "• `pairs` - Supported trading pairs\n\n"
            response_text += "🔍 **SESSION MANAGEMENT:**\n"
            response_text += "• `session [ID]` - Check session status\n"
            response_text += "• `summary [ID]` - Get ASI1 summary\n\n"
            response_text += "🎯 **SUPPORTED SYMBOLS:**\n"
            response_text += "BTC, ETH, BNB, ADA, SOL\n\n"
            response_text += "⚡ **QUICK EXAMPLES:**\n"
            response_text += "• `analyze BTC` → Full AI analysis\n"
            response_text += "• `technical ETH` → Technical AI summary\n"
            response_text += "• `news SOL` → News AI summary\n\n"
            response_text += "🤖 **All analyses use ASI1 AI for intelligent summaries!**\n"
            response_text += "⏰ **Wait 5-20 seconds for ASI1 to generate results**"
        
        elif "status" in message_text:
            response_text += "**🔍 System Status:**\n\n"
            response_text += f"🚀 User Agent: Active (Port 8008)\n"
            response_text += f"💰 Address: {user_agent.address[:16]}...\n"
            response_text += f"📬 Mailbox: Enabled\n"
            response_text += f"🌐 Protocol: Chat Protocol\n"
            response_text += f"🤖 ASI1 Integration: Active\n\n"
            response_text += f"**📡 Connected Agents:**\n"
            response_text += f"🎯 Signal Agent (Port 8002)\n"
            response_text += f"📊 Technical Agent (Port 8004)\n"
            response_text += f"📰 News Agent (Port 8005)\n"
            response_text += f"🐋 Whale Agent (Port 8006)\n"
            response_text += f"⚖️ Risk Agent (Port 8001)\n\n"
            response_text += f"**⏰ Current Sessions:**\n"
            active_sessions = len(analysis_collector.sessions)
            response_text += f"Active Analysis Sessions: {active_sessions}\n"
            response_text += f"Trading Pairs Supported: {len(TRADING_PAIRS)}\n\n"
            response_text += f"**💡 Quick Commands:**\n"
            response_text += f"• Type 'analyze BTC' for comprehensive analysis\n"
            response_text += f"• Type 'pairs' to see supported trading pairs\n"
            response_text += f"• Type 'help' for full command list"
        
        elif "pairs" in message_text or "symbols" in message_text:
            response_text += "**💰 Supported Trading Pairs:**\n\n"
            response_text += "**🔥 Main Cryptocurrencies:**\n"
            response_text += "• 🟠 **BTC** (Bitcoin) - BTCUSDT\n"
            response_text += "• 🔷 **ETH** (Ethereum) - ETHUSDT\n"
            response_text += "• 🟡 **BNB** (Binance Coin) - BNBUSDT\n"
            response_text += "• 🔵 **ADA** (Cardano) - ADAUSDT\n"
            response_text += "• 🟣 **SOL** (Solana) - SOLUSDT\n\n"
            response_text += "**📈 Usage Examples:**\n"
            response_text += "• `analyze BTC` - Full Bitcoin analysis\n"
            response_text += "• `technical ETH` - Ethereum technical only\n"
            response_text += "• `news SOL` - Solana news sentiment\n"
            response_text += "• `whale BNB` - Binance whale activity\n"
            response_text += "• `risk ADA` - Cardano risk analysis\n\n"
            response_text += "**🎯 Commands work with:**\n"
            response_text += "• Symbol names: BTC, ETH, BNB, ADA, SOL\n"
            response_text += "• Full names: Bitcoin, Ethereum, Solana\n"
            response_text += "• Trading pairs: BTCUSDT, ETHUSDT, etc.\n\n"
            response_text += "**💡 Tip:** Use `analyze [SYMBOL]` for best results!"
        
        elif any(word in message_text for word in ["agents", "list", "network"]):
            response_text += "**🤖 Agent Network:**\n\n"
            response_text += f"🎯 **Signal Agent** (Port 8002)\n"
            response_text += f"   Main orchestrator for comprehensive analysis\n"
            response_text += f"   Address: {SIGNAL_AGENT_ADDRESS[:16]}...\n\n"
            response_text += f"📊 **Technical Agent** (Port 8004)\n"
            response_text += f"   RSI, MACD, Bollinger Bands, SMA, ATR\n"
            response_text += f"   Address: {TECHNICAL_AGENT_ADDRESS[:16]}...\n\n"
            response_text += f"📰 **News Agent** (Port 8005)\n"
            response_text += f"   News sentiment analysis and headlines\n"
            response_text += f"   Address: {NEWS_AGENT_ADDRESS[:16]}...\n\n"
            response_text += f"🐋 **Whale Agent** (Port 8006)\n"
            response_text += f"   Large transaction monitoring (>$1M)\n"
            response_text += f"   Address: {WHALE_AGENT_ADDRESS[:16]}...\n\n"
            response_text += f"⚖️ **Risk Agent** (Port 8001)\n"
            response_text += f"   Stop loss, take profit, position sizing\n"
            response_text += f"   Address: {RISK_MANAGER_ADDRESS[:16]}...\n"
        
        else:
            response_text += "Welcome to the **Comprehensive Crypto Trading System**! 🎯\n\n"
            response_text += "I can help you analyze cryptocurrency markets using:\n"
            response_text += "📊 Technical Analysis (RSI, MACD, Bollinger Bands)\n"
            response_text += "📰 News Sentiment Analysis\n"
            response_text += "🐋 Whale Activity Monitoring\n"
            response_text += "⚖️ Risk Management\n\n"
            response_text += "**Quick Start:**\n"
            response_text += "• Try: 'analyze BTC' for comprehensive analysis\n"
            response_text += "• Try: 'help' for all available commands\n"
            response_text += "• Try: 'status' to check system status\n\n"
            response_text += "**Direct Agent Chat:**\n"
            response_text += "• 'technical BTC' - Chat with Technical Agent\n"
            response_text += "• 'news ETH' - Chat with News Agent\n"
            response_text += "• 'whale BNB' - Chat with Whale Agent\n"
        
        # Send response
        await ctx.send(
            sender,
            ChatMessage(
                content=[TextContent(text=response_text)]
            )
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Error handling chat message: {e}")
        error_response = "Sorry, I encountered an error processing your message. Please try again or type 'help' for available commands."
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

# Periodic task to request signals
# @user_agent.on_interval(period=30.0)  # Increased to 30 seconds for comprehensive analysis
# async def request_signals(ctx: Context):
#     """Request comprehensive trading signals every 30 seconds"""
#     for symbol in TRADING_PAIRS:
#         ctx.logger.info(f"🔄 Requesting comprehensive analysis for {symbol}...")
        
#         # Create chat message for analysis request
#         chat_message = ChatMessage(
#             content=[TextContent(text=f"analyze {symbol} for trading signal")]
#         )
        
#         # Send chat message to comprehensive signal agent
#         await ctx.send(SIGNAL_AGENT_ADDRESS, chat_message)

# Periodic cleanup task for old analysis sessions
@user_agent.on_interval(period=60.0)  # Run every minute
async def cleanup_old_sessions(ctx: Context):
    """Clean up old analysis sessions to prevent memory leaks"""
    analysis_collector.cleanup_old_sessions()
    ctx.logger.info(f"🧹 Session cleanup completed. Active sessions: {len(analysis_collector.sessions)}")

# Include chat protocol only
user_agent.include(chat_protocol)

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 COMPREHENSIVE CRYPTO TRADING SYSTEM WITH CHAT")
    print("=" * 70)
    print(f"User Agent address: {user_agent.address}")
    print(f"Port: 8008")
    print(f"Monitoring pairs: {', '.join(TRADING_PAIRS)}")
    print(f"Analysis interval: 30 seconds")
    print()
    print("💬 CHAT FEATURES:")
    print("  ✅ Interactive trading analysis via chat")
    print("  ✅ Direct communication with all agents")
    print("  ✅ Natural language commands")
    print("  ✅ Real-time market analysis")
    print("  ✅ Comprehensive signal coordination")
    print()
    print("📊 Analysis includes:")
    print("  • Technical Analysis (RSI, MACD, Bollinger Bands)")
    print("  • Sentiment Analysis (News & Social Media)")
    print("  • Whale Activity (On-chain transactions)")
    print("  • Risk Management (Stop Loss & Take Profit)")
    print("=" * 70)
    print("🤖 AGENT NETWORK:")
    print(f"  🎯 Signal Agent (Port 8002): {SIGNAL_AGENT_ADDRESS[:16]}...")
    print(f"  📊 Technical Agent (Port 8004): {TECHNICAL_AGENT_ADDRESS[:16]}...")
    print(f"  📰 News Agent (Port 8005): {NEWS_AGENT_ADDRESS[:16]}...")
    print(f"  🐋 Whale Agent (Port 8006): {WHALE_AGENT_ADDRESS[:16]}...")
    print(f"  ⚖️ Risk Agent (Port 8001): {RISK_MANAGER_ADDRESS[:16]}...")
    print("=" * 70)
    print("📱 CHAT COMMANDS:")
    print("  • 'analyze BTC' - Comprehensive analysis")
    print("  • 'technical ETH' - Technical analysis only") 
    print("  • 'news BNB' - News sentiment only")
    print("  • 'whale SOL' - Whale activity only")
    print("  • 'help' - Show all commands")
    print("  • 'status' - System status")
    print("=" * 70)
    print("💡 USAGE TIPS:")
    print("  • Connect via Agentverse mailbox for chat interface")
    print("  • Use natural language commands")
    print("  • Check logs for detailed analysis results")
    print("  • Try 'help' command for complete command list")
    print("=" * 70)
    
    if SIGNAL_AGENT_ADDRESS == "agent1qdcny99jhna95fyt9alu6snyalkm4r69pzusg6qkatz5wplsy8vuq00fr05":
        print("🔧 Remember to update agent addresses with actual deployed addresses!")
        print("=" * 70)
    
    print("🚀 Starting Comprehensive User Agent with Chat...")
    print("📬 Mailbox enabled - Connect via Agentverse for chat interface!")
    print("=" * 70)
    user_agent.run()
