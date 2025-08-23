# ChainPilot: Your Intelligent Crypto Co-Pilot 🚀

Tired of guessing which crypto to buy? Worried about market volatility? 🤔 Ever wondered what happens to your digital assets if you're no longer around?

ChainPilot is a cutting-edge Web3 application designed to be your ultimate partner in the crypto world. We combine artificial intelligence, automated safety nets, and a revolutionary inheritance system to give you total peace of mind and control over your digital wealth. 💸

## ✨ Features

### 🤖 AI-Powered Analytical Chatbot
Stop staring at confusing charts! Our friendly AI assistant is here to help with:

- "What are the top 3 coins to watch this week?"
- "What's the market sentiment for Ethereum?"
- "Show me the technical analysis for Solana."

Get clear, data-driven insights and suggestions in a simple, conversational way. It's like having a professional crypto analyst on call 24/7! 💡

### 🛡️ Automated Portfolio Protection
Set your strategy and relax! For every asset you own, you can easily define your Take Profit and Stop Loss levels:

- **Secure Your Gains**: Automatically sell when your price target is hit 💰
- **Minimize Your Losses**: Automatically sell if the market turns against you

ChainPilot acts as your disciplined trading partner, executing your plan without emotion, even while you sleep. 😴

### 🔑 Secure Wallet & Inheritance Protocol
Your crypto is a vital part of your legacy. Our groundbreaking Inheritance Protocol ensures it's never lost:

- **Designate a Beneficiary**: Securely choose a wallet to receive your assets
- **Set an Inactivity Timer**: Define a period (e.g., 1 year). If your account is inactive for that long, the protocol kicks in
- **Safe & Secure Transfer**: After a verification process, your assets are automatically transferred to your loved ones 👨‍👩‍👧‍👦

This is your digital "dead man's switch," giving you the ultimate peace of mind that your legacy is protected. 🕊️

## 🏗️ Architecture

The ChainPilot architecture follows a modern, distributed design:

### 1. User Interaction (Frontend)
- **TypeScript/React**: Modern user interface for portfolio management and trading
- **Real-time Dashboard**: View data, manage portfolio, and initiate trades

### 2. Central Router (API Gateway)
- **Python API Gateway**: Security checkpoint and traffic director
- **Request Routing**: Routes incoming requests to appropriate services

### 3. Core Logic Layer
- **AI Agent Layer**: Fetch.ai agent for complex computations and trading strategies
- **Smart Contracts**: Motoko canisters on Internet Computer for decentralized logic

### 4. External Integration
- **Crypto-Exchange APIs**: Real-time market data and trade execution
- **Blockchain Networks**: Final settlement on public networks (Ethereum, ICP)

## 📊 User Flows

### Trading Flow
1. **Login & Dashboard**: Access portfolio and AI suggestions
2. **Choose Action**: Buy, Sell, or enable Auto-Trade
3. **Order Processing**: Backend verification and smart contract execution
4. **Exchange Integration**: Order sent to external exchange APIs

### Inheritance Flow
1. **Configuration**: Set inactivity timer and beneficiary wallet
2. **Monitoring**: Continuous activity monitoring
3. **Warning System**: Email notifications before inheritance activation
4. **Secure Transfer**: Automatic asset transfer to designated beneficiary

## ⚙️ Tech Stack

- **Frontend**: React, TypeScript
- **Backend**: Python (API Gateway)
- **AI Agent**: Fetch.ai (Python)
- **Smart Contracts**: Motoko (Internet Computer)
- **Blockchain**: Internet Computer Protocol (ICP)
- **External APIs**: Crypto exchange integrations

## 🤖 Fetch.ai Agents

### ChainPilot Crypto Analyze
- **Agent Address**: `agent1qvwrg7d7fy27xsnd5sc82cm84ljn96cvzf8p0p9j8ltf6l2gcz7zj2rcwty`
- **Function**: Market analysis and trading recommendations

### ChainPilot Legacy Checker  
- **Agent Address**: `agent1q09ymw547qkluxf7h33vuv39zclmsl745x575jr82g72c0vza222z49q7ta`
- **Function**: Inheritance protocol monitoring and execution

## 🚀 Getting Started

### Prerequisites
- [DFINITY Canister SDK](https://internetcomputer.org/docs/current/developer-docs/setup/install/)
- Node.js (v14 or higher)
- Python 3.8+
- Fetch.ai development environment

### 1. Clone Repository
```bash
git clone https://github.com/Kazeth/ChainPilot.git
cd ChainPilot
```

### 2. Setup ICP Canisters (Backend)
```bash
# Start the local replica in the background
dfx start --clean --background

# Deploy the canisters
dfx deploy
```

### 3. Setup React App (Frontend)
```bash
cd frontend
npm install
npm run dev
```

### 4. Setup Python Agent (Fetch.ai)
```bash
cd fetch
python3 -m venv .venv

# Activate the virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run the Agent
```bash
python main.py  # or your main agent script
```

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
FETCHAI_API_KEY=your_fetchai_api_key
AGENT_SEED_PHRASE=your_agent_seed_phrase
```

**⚠️ Security Note**: Ensure your agent's private keys or seed phrases are handled securely and are not committed to version control.

## 📂 Project Structure

```
CHAINPILOT/
│
├── backend/                 # Motoko smart contracts
│   ├── AuditLog.mo
│   ├── Insurance.mo
│   ├── MarketData.mo
│   ├── Signal.mo
│   ├── Trade.mo
│   ├── Transaction.mo
│   ├── User.mo
│   ├── Wallet.mo
│   ├── main.mo
│   └── Types.mo
│
├── fetch/                   # Fetch.ai agents
│   ├── venv/
│   ├── agent.py
│   ├── api_gateway.py
│   └── ...
│
├── frontend/                # React application
│   ├── node_modules/
│   ├── public/
│   └── src/
│       ├── App.css
│       ├── App.tsx
│       └── ...
│
├── node_modules/
├── dfx.json 
└── ...
```

## 🎬 Demo & Presentation

- **Demo Video**: [Link to Demo Video - TBD]
- **Presentation Video**: [Link to Presentation Video - TBD]  
- **Presentation Material**: [Canva Presentation](link-to-canva)

## 📄 Usage Examples

### AI Chatbot Queries
- "What's the current sentiment for Bitcoin?"
- "Should I buy Ethereum now?"
- "What are the top performing altcoins this week?"
- "Set a stop loss at $30,000 for my Bitcoin holdings"

### Portfolio Management
- Configure automated take-profit levels
- Set stop-loss orders for risk management
- Monitor portfolio performance in real-time
- Receive AI-powered trading recommendations

### Inheritance Setup
- Designate beneficiary wallet addresses
- Configure inactivity periods
- Test notification systems
- Monitor inheritance protocol status

## 🤝 Contributing

We welcome contributions to ChainPilot! Please read our contributing guidelines and feel free to submit pull requests.

## 📜 License

MIT License © 2025 ChainPilot Team

## 📞 Support

For support and questions, please reach out to our team or open an issue in this repository.

---

**Powered by Fetch.ai and Internet Computer | Built for the Future of Crypto**