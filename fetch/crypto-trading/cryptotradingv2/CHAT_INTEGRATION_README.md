# 💬 Chat-Enabled Crypto Trading Agents

This document explains how to use the chat functionality integrated into the cryptotradingv2 agents.

## 🚀 Overview

All agents in the cryptotradingv2 system now support **interactive chat** using the uAgents chat protocol. You can communicate with each agent using natural language to request analysis, get status updates, and receive help.

## 🤖 Chat-Enabled Agents

### 🚀 **Comprehensive User Agent** (Port 8007) - **MAIN CHAT INTERFACE**
**Your primary chat interface that coordinates all other agents**

**Chat Commands:**
- `analyze BTC` - Full comprehensive analysis (coordinates all agents)
- `signal for ETH` - Complete trading signal with risk management
- `technical BNB` - Direct chat with Technical Agent
- `news SOL` - Direct chat with News Agent  
- `whale ADA` - Direct chat with Whale Agent
- `help` - Show all available commands
- `status` - System and agent network status
- `agents` - List all connected agents

**Special Features:**
- 🎯 **Smart Routing**: Automatically sends requests to appropriate agents
- 📊 **Result Aggregation**: Displays comprehensive analysis from all agents
- 💬 **Direct Agent Chat**: Can relay messages to specific agents
- 🔄 **Real-time Monitoring**: Continues automated signal monitoring
- 📱 **User-Friendly**: Natural language command processing

**Example Chat Session:**
```
User: analyze BTC
Agent: 🚀 Comprehensive Crypto Trading System
       🔄 Requesting comprehensive analysis for BTCUSDT...
       📊 Analysis requested from:
       🎯 Signal Agent (Orchestrator)
       📈 Technical Analysis Agent
       📰 News Sentiment Agent
       🐋 Whale Activity Agent
       ⚖️ Risk Management Agent
       ⏰ Please wait 10-15 seconds for complete analysis...
       Results will appear in the logs above! 📈

User: technical ETH
Agent: Sending technical analysis request for ETHUSDT to Technical Agent...
       Agent Address: agent1qgn5e6pqta60x79...
       ✅ Request sent! Check the technical agent's response.

User: status
Agent: 🔍 System Status:
       🚀 User Agent: Active (Port 8007)
       💰 Address: agent1qvwrg7d7fy27...
       📬 Mailbox: Enabled
       🌐 Protocol: Crypto Trading v1
       
       📡 Connected Agents:
       🎯 Signal Agent (Port 8002)
       📊 Technical Agent (Port 8004)
       📰 News Agent (Port 8005)
       🐋 Whale Agent (Port 8006)
       ⚖️ Risk Agent (Port 8001)
```

### 2. 🎯 **Comprehensive Signal Agent** (Port 8002)
**Main orchestrator that coordinates all other agents**

**Chat Commands:**
- `analyze BTC` - Get comprehensive analysis for Bitcoin
- `signal for ETH` - Request trading signal for Ethereum  
- `trade analysis BNBUSDT` - Full trading recommendation
- `help` - Show available commands
- `status` - Check agent and network status

**Example Chat:**
```
User: analyze BTC
Agent: 🎯 Comprehensive Signal Agent
       🔄 Analyzing BTCUSDT...
       I'm gathering data from:
       📊 Technical Analysis Agent (RSI, MACD, Bollinger Bands)
       📰 News Sentiment Agent
       🐋 Whale Activity Agent
       ⚖️ Risk Management Agent
       ⏰ Please wait 5-10 seconds for comprehensive analysis...
```

### 3. 📊 **Technical Analysis Agent** (Port 8004)
**Provides technical indicators and market analysis**

**Chat Commands:**
- `analyze BTC technical indicators` - Full technical analysis
- `show ETH RSI and MACD` - Specific indicators
- `technical analysis for BNBUSDT` - Complete technical overview
- `help` - Show technical analysis commands
- `status` - Check technical agent status

**Example Chat:**
```
User: analyze BTC technical indicators
Agent: 📊 Technical Analysis Agent
       📈 BTCUSDT Technical Analysis:
       💰 Current Price: $45,123.45
       📊 Technical Score: 0.456
       
       Key Indicators:
       • RSI (14): 62.5
       • MACD: 0.0234
       • SMA 20: $44,890.12
       • Bollinger Upper: $46,234.56
       🟢 Technical Outlook: BULLISH
```

### 4. 📰 **News Sentiment Agent** (Port 8005)
**Analyzes cryptocurrency news sentiment**

**Chat Commands:**
- `news sentiment for BTC` - Get news sentiment analysis
- `analyze ETH headlines` - Analyze recent headlines
- `show BNB news sentiment` - News sentiment overview
- `help` - Show news analysis commands
- `status` - Check news agent status

**Example Chat:**
```
User: news sentiment for BTC
Agent: 📰 News Sentiment Agent
       📰 BTCUSDT News Sentiment Analysis:
       📊 Sentiment Score: 0.678
       📄 Articles Analyzed: 12
       🎯 Confidence: 85%
       🟢 Sentiment: POSITIVE
       News indicates bullish market sentiment
       
       📖 Top Headlines:
       1. Bitcoin Reaches New All-Time High Amid Institutional Adoption...
       2. Major Corporation Adds Bitcoin to Treasury Reserves...
       3. Regulatory Clarity Boosts Cryptocurrency Market Confidence...
```

### 5. 🐋 **Whale Activity Agent** (Port 8006)
**Monitors large cryptocurrency transactions**

**Chat Commands:**
- `whale activity for BTC` - Get whale activity analysis
- `analyze ETH whale transactions` - Whale transaction analysis
- `show BNB whale flow` - Exchange flow analysis
- `help` - Show whale analysis commands
- `status` - Check whale agent status

**Example Chat:**
```
User: whale activity for BTC
Agent: 🐋 Whale Activity Agent
       🐋 BTCUSDT Whale Activity Analysis:
       📊 Whale Score: 0.234
       📈 Large Transactions: 8
       💰 Net Flow: $12,450,000
       🎯 Confidence: 78%
       🟢 Whale Activity: ACCUMULATION
       Whales are likely buying/accumulating
       
       💹 Exchange Flows:
       📥 Inflow: $25,000,000
       📤 Outflow: $37,450,000
       ⚖️ Net Flow: -$12,450,000
       📉 Net negative flow (potential buying pressure)
```

### 6. ⚖️ **Risk Manager Agent** (Port 8001)
**Calculates risk management parameters**

**Chat Commands:**
- `calculate risk BUY BTC 45000 0.8` - Calculate risk for trade
- `risk SELL ETH 3000 0.7` - Risk calculation for sell signal
- `status` - Show risk management settings
- `help` - Show risk calculation commands

**Example Chat:**
```
User: calculate risk BUY BTC 45000 0.8
Agent: ⚖️ Risk Management Agent
       📊 Risk Calculation for BTCUSDT
       🎯 Signal: BUY
       💰 Entry Price: $45,000.00
       🎲 Confidence: 80%
       
       ⚖️ Risk Management:
       🛑 Stop Loss: $42,750.00
       🎯 Take Profit: $49,500.00
       📊 Risk/Reward: 2.0:1
       📈 Position Size: 10.0%
       
       💸 Risk per unit: $2,250.00
       💰 Profit per unit: $4,500.00
```

## 🔗 How to Connect and Chat

### 1. **Start the Agents**
```bash
# Navigate to cryptotradingv2 directory
cd ChainPilot/fetch/crypto-trading/cryptotradingv2/

# Start each agent in separate terminals
python enhanced_risk_manager_agent.py        # Port 8001
python fixed_comprehensive_signal_agent.py   # Port 8002
python technical_agent.py                    # Port 8004
python news_agent.py                         # Port 8005  
python whale_agent.py                        # Port 8006

# Start the main chat interface (User Agent)
python comprehensive_user_agent.py           # Port 8007
```

### 2. **Using the Comprehensive User Agent for Chat**
The **`comprehensive_user_agent.py`** is your main chat interface! It can:
- 💬 **Accept chat messages** via mailbox
- 🎯 **Coordinate comprehensive analysis** by talking to all agents
- 📊 **Relay specific requests** to individual agents
- 🔄 **Display formatted results** in real-time

**Key Features:**
- **Natural Language Commands**: Just type "analyze BTC" or "news ETH"
- **Agent Coordination**: Automatically sends requests to appropriate agents
- **Real-time Results**: See analysis results in the logs immediately
- **Help System**: Type "help" for all available commands

### 3. **Connect via Agentverse Mailbox**
1. **Start the User Agent**: `python comprehensive_user_agent.py`
2. **Copy the Agent Address**: Look for the address in the startup logs
3. **Visit Agentverse**: Go to https://agentverse.ai
4. **Start Chat**: Use the agent address to begin a chat session

### 4. **Test Chat with Test Client**
```bash
# Use the provided test client
python test_chat_client.py --address <user_agent_address>

# Or use the default address
python test_chat_client.py
```

### 3. **Example Integration Code**
```python
from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    TextContent,
)

# Your chat client agent
chat_client = Agent(name="chat_client", mailbox=True)
chat_protocol = Protocol(spec=chat_protocol_spec)

@chat_protocol.on_message(model=ChatMessage)
async def handle_response(ctx: Context, sender: str, msg: ChatMessage):
    print(f"Response from {sender}: {msg.content.text}")

# Send message to signal agent
async def send_chat_message(agent_address: str, message: str):
    await ctx.send(
        agent_address,
        ChatMessage(
            content=TextContent(text=message),
            session_id="chat_session_123"
        )
    )

chat_client.include(chat_protocol)
```

## 📱 Chat Features

### ✅ **Available Features**
- **Natural Language Processing** - Understand trading commands
- **Symbol Recognition** - Automatic detection of crypto symbols
- **Real-time Analysis** - Live data processing and responses
- **Help Commands** - Built-in help for each agent
- **Status Queries** - Check agent health and configuration
- **Error Handling** - Graceful error responses
- **Session Management** - Persistent chat sessions

### 🎯 **Supported Symbols**
- **BTC/Bitcoin** → BTCUSDT
- **ETH/Ethereum** → ETHUSDT  
- **BNB/Binance** → BNBUSDT
- **ADA/Cardano** → ADAUSDT
- **SOL/Solana** → SOLUSDT

## 🛠️ Technical Implementation

### **Chat Protocol Integration**
```python
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
)

# Create chat protocol
chat_protocol = Protocol(spec=chat_protocol_spec)

# Handle incoming chat messages
@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    # Process message and generate response
    response_text = process_chat_request(msg.content.text)
    
    # Send response
    await ctx.send(
        sender,
        ChatMessage(
            content=TextContent(text=response_text),
            session_id=msg.session_id
        )
    )

# Include chat protocol in agent
agent.include(chat_protocol)
```

### **Agent Configuration**
```python
# Enable mailbox for chat functionality
agent = Agent(
    name="agent_name",
    port=8001,
    mailbox=True,  # Required for chat
    seed="agent_seed"
)
```

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirementsv2.txt
   ```

2. **Start All Agents**
   ```bash
   python run_all_agents.py
   ```

3. **Connect via Agentverse**
   - Visit https://agentverse.ai
   - Use agent addresses to start chat sessions

4. **Try Sample Commands**
   ```
   analyze BTC
   news sentiment for ETH
   whale activity for BNB
   calculate risk BUY BTC 45000 0.8
   help
   status
   ```

## 💡 Tips for Best Results

- **Be Specific** - Include symbol names in your requests
- **Use Keywords** - Words like "analyze", "show", "calculate" help the agents understand
- **Check Status** - Use "status" command to verify agents are working properly
- **Ask for Help** - Each agent has a "help" command showing all available options
- **Wait for Responses** - Some analysis takes a few seconds to complete

## 🔧 Troubleshooting

### **Agent Not Responding**
- Check if agent is running on correct port
- Verify mailbox is enabled (`mailbox=True`)
- Ensure agent has sufficient funds

### **Chat Messages Not Working**
- Verify chat protocol is included: `agent.include(chat_protocol)`
- Check agent address is correct
- Ensure proper session ID in messages

### **Analysis Errors**
- Check API keys are configured (NewsAPI, Whale Alert)
- Verify internet connection for market data
- Try "status" command to check agent health

## 📚 Additional Resources

- **uAgents Documentation**: https://docs.fetch.ai/uAgents
- **Chat Protocol Guide**: Check uAgents contrib documentation
- **Agentverse Platform**: https://agentverse.ai
- **API Keys**: 
  - NewsAPI: https://newsapi.org/
  - Whale Alert: https://whale-alert.io/

---

**Happy Trading with Chat-Enabled Agents! 🚀💬**
