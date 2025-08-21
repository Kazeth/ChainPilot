#!/usr/bin/env python3

"""
AGENT STATUS CHECKER
Quick verification of all agent configurations and their chat protocol status
"""

import os
import re

def check_agent_status():
    """Check the status and configuration of all agents"""
    
    print("=" * 70)
    print("🔍 CRYPTOTRADINGV2 AGENT STATUS VERIFICATION")
    print("=" * 70)
    print()
    
    agents = {
        "comprehensive_user_agent.py": {
            "name": "User Agent",
            "port": "8008",
            "icon": "👤",
            "description": "Human interface and interaction"
        },
        "fixed_comprehensive_signal_agent.py": {
            "name": "Signal Agent", 
            "port": "8002",
            "icon": "🎯",
            "description": "Central coordination hub"
        },
        "technical_agent.py": {
            "name": "Technical Agent",
            "port": "8004", 
            "icon": "📊",
            "description": "RSI, MACD, Bollinger Bands analysis"
        },
        "news_agent.py": {
            "name": "News Agent",
            "port": "8005",
            "icon": "📰", 
            "description": "Sentiment analysis"
        },
        "whale_agent.py": {
            "name": "Whale Agent",
            "port": "8006",
            "icon": "🐋",
            "description": "Large transaction monitoring"
        },
        "enhanced_risk_manager_agent.py": {
            "name": "Risk Manager",
            "port": "8001",
            "icon": "⚖️",
            "description": "Stop loss & take profit"
        }
    }
    
    for filename, info in agents.items():
        if os.path.exists(filename):
            print(f"{info['icon']} {info['name']} (Port {info['port']}):")
            print(f"   📁 File: {filename}")
            print(f"   📝 Description: {info['description']}")
            
            # Check file content for protocol usage
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                    
                # Count protocol references
                chat_protocol_count = len(re.findall(r'chat_protocol', content))
                signal_protocol_count = len(re.findall(r'signal_protocol', content))
                signal_request_count = len(re.findall(r'SignalRequest|SignalResponse', content))
                
                print(f"   📡 Chat Protocol: {chat_protocol_count} references")
                
                if signal_protocol_count > 0 or signal_request_count > 0:
                    print(f"   ⚠️  Legacy Protocol: {signal_protocol_count + signal_request_count} references")
                    status = "🟡 HYBRID"
                else:
                    status = "🟢 PURE CHAT"
                    
                print(f"   🔄 Status: {status}")
                
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
                
            print()
        else:
            print(f"❌ {info['icon']} {info['name']}: FILE NOT FOUND - {filename}")
            print()
    
    print("📋 SUMMARY:")
    print("   ✅ All agents should show 'PURE CHAT' or 'HYBRID' status")
    print("   ✅ User and Signal agents should be 'PURE CHAT'")
    print("   ✅ Specialized agents can be 'HYBRID' (keeps internal protocols)")
    print()
    
    print("🚀 TO START THE SYSTEM:")
    print("   1. Terminal 1: python fixed_comprehensive_signal_agent.py")
    print("   2. Terminal 2: python comprehensive_user_agent.py") 
    print("   3. Terminal 3: python technical_agent.py")
    print("   4. Terminal 4: python news_agent.py")
    print("   5. Terminal 5: python whale_agent.py")
    print("   6. Terminal 6: python enhanced_risk_manager_agent.py")
    print()
    
    print("💬 CHAT INTERFACE:")
    print("   • Connect to User Agent via Agentverse mailbox")
    print("   • Use natural language commands like 'analyze BTC'")
    print("   • System will coordinate all agents via chat protocol")
    print()
    
    print("=" * 70)
    print("🎉 TRANSFORMATION VERIFICATION COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir("/home/andrew/code/chainpilot3/ChainPilot/fetch/crypto-trading/cryptotradingv2")
    check_agent_status()
