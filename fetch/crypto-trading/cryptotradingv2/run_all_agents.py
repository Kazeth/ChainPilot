#!/usr/bin/env python3
"""
Comprehensive AI Multi-Agent Crypto Trading System

This script starts all agents in the comprehensive trading system:
1. Technical Analysis Agent (RSI, MACD, Bollinger Bands)
2. News Sentiment Agent (Sentiment Analysis) 
3. Whale Activity Agent (On-chain Analysis)
4. Risk Manager Agent (Stop Loss & Take Profit)
5. Comprehensive Signal Agent (Orchestrator)
6. User Agent (Display & Interface)

Usage:
    python run_all_agents.py [--single-agent AGENT_NAME]
    
Examples:
    python run_all_agents.py                    # Run all agents
    python run_all_agents.py --single-agent user  # Run only user agent
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

# Agent configurations
AGENTS = {
    "technical": {
        "file": "technical_agent.py",
        "port": 8004,
        "description": "Technical Analysis (RSI, MACD, Bollinger Bands)"
    },
    "news": {
        "file": "news_agent.py", 
        "port": 8005,
        "description": "News Sentiment Analysis"
    },
    "whale": {
        "file": "whale_agent.py",
        "port": 8006,
        "description": "Whale Activity Analysis"
    },
    "risk": {
        "file": "enhanced_risk_manager_agent.py",
        "port": 8001,
        "description": "Risk Management (Stop Loss & Take Profit)"
    },
    "signal": {
        "file": "fixed_comprehensive_signal_agent.py",
        "port": 8002,
        "description": "Comprehensive Signal Orchestrator"
    },
    # "user": {
    #     "file": "comprehensive_user_agent.py",
    #     "port": 8007,
    #     "description": "User Interface & Display"
    # }
}

# Global list to track running processes
running_processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n" + "="*60)
    print("🛑 STOPPING ALL AGENTS...")
    print("="*60)
    
    for i, process in enumerate(running_processes):
        if process.poll() is None:  # Process is still running
            agent_name = list(AGENTS.keys())[i] if i < len(AGENTS) else f"process_{i}"
            print(f"⏹️  Stopping {agent_name} agent...")
            process.terminate()
            
            # Wait for graceful shutdown, then force kill if needed
            try:
                process.wait(timeout=5)
                print(f"✅ {agent_name} agent stopped gracefully")
            except subprocess.TimeoutExpired:
                print(f"🔴 Force killing {agent_name} agent...")
                process.kill()
                process.wait()
                print(f"💀 {agent_name} agent force killed")
    
    print("="*60)
    print("🏁 All agents stopped. Goodbye!")
    print("="*60)
    sys.exit(0)

def check_file_exists(filepath):
    """Check if agent file exists"""
    if not os.path.exists(filepath):
        print(f"❌ Error: Agent file not found: {filepath}")
        return False
    return True

def start_agent(agent_name, agent_config):
    """Start a single agent"""
    filepath = agent_config["file"]
    port = agent_config["port"]
    description = agent_config["description"]
    
    if not check_file_exists(filepath):
        return None
    
    print(f"🚀 Starting {agent_name} agent on port {port}...")
    print(f"   📝 {description}")
    print(f"   📁 File: {filepath}")
    
    try:
        # Start the agent process
        process = subprocess.Popen(
            [sys.executable, filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✅ {agent_name} agent started successfully (PID: {process.pid})")
            return process
        else:
            # Process died immediately, get error
            stdout, stderr = process.communicate()
            print(f"❌ {agent_name} agent failed to start!")
            if stderr:
                print(f"Error: {stderr}")
            if stdout:
                print(f"Output: {stdout}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting {agent_name} agent: {str(e)}")
        return None

def display_startup_info():
    """Display system information at startup"""
    print("="*80)
    print("🤖 COMPREHENSIVE AI MULTI-AGENT CRYPTO TRADING SYSTEM")
    print("   Sistema AI Multi-Agente para Sinais de Trading de Criptomoedas")
    print("="*80)
    print()
    print("📊 SYSTEM ARCHITECTURE:")
    print("-"*40)
    
    for agent_name, config in AGENTS.items():
        print(f"  {agent_name.upper():>10} | Port {config['port']} | {config['description']}")
    
    print()
    print("🔄 ANALYSIS FLOW:")
    print("-"*40)
    print("  1. 👤 User Agent requests signals every 30 seconds")
    print("  2. 🎯 Signal Agent coordinates analysis from all sources")
    print("  3. 📈 Technical Agent calculates RSI, MACD, Bollinger Bands")
    print("  4. 📰 News Agent performs sentiment analysis on crypto news")
    print("  5. 🐋 Whale Agent monitors large on-chain transactions")
    print("  6. ⚖️  Risk Agent calculates stop loss & take profit levels")
    print("  7. 🎲 Signal Agent combines all analysis (40% technical, 30% sentiment, 30% whale)")
    print("  8. 📱 User Agent displays comprehensive trading signals")
    print()
    print("🎯 SUPPORTED TRADING PAIRS:")
    print("-"*40)
    print("  • BTCUSDT (Bitcoin)")
    print("  • ETHUSDT (Ethereum)")
    print("  • BNBUSDT (Binance Coin)")
    print()
    print("⚠️  REQUIREMENTS:")
    print("-"*40)
    print("  • Python 3.8+")
    print("  • uAgents framework")
    print("  • Internet connection for API calls")
    print("  • Optional: NewsAPI key for live news data")
    print("  • Optional: Whale Alert API key for live whale data")
    print()

def display_agent_addresses():
    """Display agent addresses for configuration"""
    print("🔧 AGENT ADDRESSES FOR CONFIGURATION:")
    print("-"*60)
    print("Copy these addresses to update the agent configuration files:")
    print()
    
    # We'll need to start agents one by one to get their addresses
    for agent_name, config in AGENTS.items():
        print(f"{agent_name.upper()}_AGENT_ADDRESS = \"agent1q{agent_name}\"  # Update this")
    
    print()
    print("📝 Files to update with actual addresses:")
    print("  • comprehensive_signal_agent.py (all agent addresses)")
    print("  • comprehensive_user_agent.py (signal agent address)")
    print()

def run_single_agent(agent_name):
    """Run a single agent"""
    if agent_name not in AGENTS:
        print(f"❌ Unknown agent: {agent_name}")
        print(f"Available agents: {', '.join(AGENTS.keys())}")
        return
    
    config = AGENTS[agent_name]
    print(f"🎯 Running single agent: {agent_name}")
    print("="*60)
    
    process = start_agent(agent_name, config)
    if process:
        running_processes.append(process)
        
        print("="*60)
        print(f"🏃 {agent_name} agent is running...")
        print("Press Ctrl+C to stop")
        print("="*60)
        
        try:
            # Wait for the process to complete
            process.wait()
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)

def run_all_agents():
    """Run all agents in the correct order"""
    display_startup_info()
    
    print("🚀 STARTING ALL AGENTS...")
    print("="*60)
    
    # Start agents in dependency order
    agent_order = ["technical", "news", "whale", "risk", "signal"]
    
    for agent_name in agent_order:
        config = AGENTS[agent_name]
        process = start_agent(agent_name, config)
        
        if process:
            running_processes.append(process)
            print(f"⏱️  Waiting 3 seconds before starting next agent...")
            time.sleep(3)
        else:
            print(f"⚠️  Failed to start {agent_name} agent, continuing anyway...")
        
        print()
    
    print("="*60)
    print("🎉 ALL AGENTS STARTED!")
    print("="*60)
    print()
    
    # Display running status
    print("📊 RUNNING AGENTS STATUS:")
    print("-"*40)
    for i, agent_name in enumerate(agent_order):
        if i < len(running_processes) and running_processes[i].poll() is None:
            status = "🟢 RUNNING"
            pid = f"(PID: {running_processes[i].pid})"
        else:
            status = "🔴 STOPPED"
            pid = ""
        print(f"  {agent_name.upper():>10} | {status} {pid}")
    
    print()
    display_agent_addresses()
    
    print("="*60)
    print("🎯 SYSTEM IS RUNNING!")
    print("🔍 Monitor the User Agent in different terminal to get output for trading signals")
    print("⏰ Signals are generated every 30 seconds")
    print("🛑 Press Ctrl+C to stop all agents")
    print("="*60)
    
    try:
        # Keep the main process alive
        while True:
            time.sleep(1)
            
            # Check if any process died
            for i, process in enumerate(running_processes):
                if process.poll() is not None:
                    agent_name = list(AGENTS.keys())[i] if i < len(AGENTS) else f"process_{i}"
                    print(f"⚠️  {agent_name} agent stopped unexpectedly!")
    
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

def main():
    """Main function"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--single-agent" and len(sys.argv) > 2:
            agent_name = sys.argv[2]
            run_single_agent(agent_name)
        elif sys.argv[1] in ["-h", "--help"]:
            print(__doc__)
            sys.exit(0)
        else:
            print("❌ Invalid arguments")
            print(__doc__)
            sys.exit(1)
    else:
        run_all_agents()

if __name__ == "__main__":
    main()
