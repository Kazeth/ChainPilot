#!/usr/bin/env python3
"""
Script to update all agents to use the same protocol
"""

import os
import re

def update_protocol_in_file(file_path, new_protocol_name):
    """Update protocol name in a file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Pattern to match Protocol("...") declarations
        pattern = r'Protocol\(["\'][^"\']*["\']\)'
        replacement = f'Protocol("{new_protocol_name}")'
        
        updated_content = re.sub(pattern, replacement, content)
        
        with open(file_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated {file_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to update {file_path}: {e}")
        return False

def main():
    """Update all agent files to use unified protocol"""
    
    agent_files = [
        "technical_agent.py",
        "news_agent.py", 
        "whale_agent.py",
        "enhanced_risk_manager_agent.py",
        "comprehensive_signal_agent.py",
        "comprehensive_user_agent.py"
    ]
    
    unified_protocol = "Crypto Trading v1"
    
    print("🔧 FIXING AGENT COMMUNICATION PROTOCOL")
    print("=" * 50)
    print(f"Setting all agents to use: '{unified_protocol}'")
    print()
    
    for agent_file in agent_files:
        if os.path.exists(agent_file):
            update_protocol_in_file(agent_file, unified_protocol)
        else:
            print(f"⚠️  File not found: {agent_file}")
    
    print()
    print("✅ All agents updated to use unified protocol!")
    print()
    print("📋 Next steps:")
    print("1. Restart all agents")
    print("2. Test communication")
    print("3. Verify message handlers are called")

if __name__ == "__main__":
    main()
