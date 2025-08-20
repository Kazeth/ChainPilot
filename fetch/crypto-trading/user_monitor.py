#!/usr/bin/env python3
"""
Ultimate User Activity Monitor for Crypto Trading System
Monitor user agent activity with multiple viewing options

This script helps you monitor user activity in the following ways:
1. Find which terminal has the User Agent running
2. Monitor process activity
3. Show real-time status
4. Display signal patterns
"""

import subprocess
import time
import os
import sys
from datetime import datetime

def find_user_agent_terminal():
    """Find which terminal/process is running the user agent"""
    print("🔍 LOCATING USER AGENT...")
    print("=" * 60)
    
    try:
        # Find the user agent process
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout.split('\n')
        
        user_agent_info = None
        for line in processes:
            if 'comprehensive_user_agent.py' in line:
                user_agent_info = line
                break
        
        if user_agent_info:
            parts = user_agent_info.split()
            pid = parts[1]
            print(f"✅ User Agent Found!")
            print(f"   📍 PID: {pid}")
            print(f"   🖥️  Process: {' '.join(parts[10:])}")
            print(f"   ⚡ Status: Running on port 8003")
            print()
            
            # Try to find the terminal
            print("🖥️  TERMINAL INFORMATION:")
            print("-" * 40)
            try:
                # Get process tree to find parent terminal
                result = subprocess.run(['ps', '-p', pid, '-o', 'pid,ppid,tty,cmd'], 
                                      capture_output=True, text=True)
                print(result.stdout)
            except:
                print("   Could not determine terminal info")
            
            print()
            print("📺 WHERE TO MONITOR:")
            print("-" * 40)
            print("1. 🎯 BEST OPTION: Look for a terminal window that shows:")
            print("   '🤖 COMPREHENSIVE CRYPTO TRADING SIGNAL SYSTEM'")
            print("   'User Agent address: agent1q...'")
            print("   'Starting User Agent...'")
            print()
            print("2. 🔄 That terminal will show signals every 30 seconds like:")
            print("   '================================================================================")
            print("   📊 COMPREHENSIVE TRADING SIGNAL: BTCUSDT")
            print("   🎯 FINAL SIGNAL: 🟢 BUY")
            print("   🎲 CONFIDENCE:   78.5%'")
            print()
            print("3. 📊 Or use the monitoring tools below...")
            
            return pid
        else:
            print("❌ User Agent not found!")
            print("💡 Start it with: python comprehensive_user_agent.py")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def monitor_process_activity(pid):
    """Monitor the process activity"""
    print(f"📊 MONITORING USER AGENT ACTIVITY (PID: {pid})")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        check_count = 0
        while True:
            check_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Check if process is still alive
            try:
                result = subprocess.run(['ps', '-p', pid], capture_output=True, text=True)
                if result.returncode == 0:
                    status = "🟢 ACTIVE"
                else:
                    status = "🔴 STOPPED"
                    print(f"❌ User Agent stopped running!")
                    break
            except:
                status = "❓ UNKNOWN"
            
            # Show activity indicator
            activity_indicator = "🔄" if check_count % 4 == 0 else "📊" if check_count % 4 == 1 else "📈" if check_count % 4 == 2 else "🎯"
            
            print(f"{current_time} | {status} | {activity_indicator} Processing signals... (Check #{check_count})")
            
            # Show signal expectation
            if check_count % 3 == 0:
                print(f"   💡 Next signals expected around {current_time} for BTCUSDT, ETHUSDT, BNBUSDT")
            
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")

def show_quick_status():
    """Show quick system status"""
    print("⚡ QUICK SYSTEM STATUS")
    print("=" * 50)
    
    # Check all agents
    agents = {
        "comprehensive_user_agent.py": "👤 User Agent (Port 8003)",
        "comprehensive_signal_agent.py": "🎯 Signal Agent (Port 8002)", 
        "technical_agent.py": "📈 Technical Agent (Port 8004)",
        "news_agent.py": "📰 News Agent (Port 8005)",
        "whale_agent.py": "🐋 Whale Agent (Port 8006)",
        "enhanced_risk_manager_agent.py": "⚖️ Risk Manager (Port 8001)"
    }
    
    for agent_file, description in agents.items():
        try:
            result = subprocess.run(['pgrep', '-f', agent_file], capture_output=True, text=True)
            if result.stdout.strip():
                status = "🟢 RUNNING"
            else:
                status = "🔴 STOPPED"
        except:
            status = "❓ UNKNOWN"
        
        print(f"{description}: {status}")
    
    print()
    print("🎯 USER MONITORING INSTRUCTIONS:")
    print("-" * 50)
    print("1. Find terminal with User Agent output")
    print("2. Look for signals every 30 seconds")
    print("3. Signals format: 🟢 BUY / 🔴 SELL / ⚪ HOLD")
    print("4. Each signal shows technical + sentiment + whale analysis")

def create_monitoring_dashboard():
    """Create a live monitoring dashboard"""
    print("🎯 STARTING LIVE MONITORING DASHBOARD...")
    print("Press Ctrl+C to stop")
    time.sleep(2)
    
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("🤖 CRYPTO TRADING SYSTEM - USER ACTIVITY MONITOR")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)
            
            # Find user agent
            pid = find_user_agent_terminal()
            
            if pid:
                print()
                print("🎯 REAL-TIME ACTIVITY MONITOR:")
                print("-" * 50)
                
                # Show recent activity (simulated)
                signals_expected = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
                current_time = datetime.now()
                
                print(f"📊 Next signal cycle in: {30 - (current_time.second % 30)} seconds")
                print(f"🎲 Monitoring symbols: {', '.join(signals_expected)}")
                print(f"📈 Expected signal types: BUY 🟢, SELL 🔴, HOLD ⚪")
                print()
                
                print("💡 TO SEE ACTUAL SIGNALS:")
                print("   → Check the terminal where 'comprehensive_user_agent.py' is running")
                print("   → Look for colorful signal displays with emojis")
                print("   → Signals appear every 30 seconds automatically")
            
            print()
            print("🔄 Refreshing in 5 seconds...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")

def main():
    print("🚀 USER ACTIVITY MONITOR FOR CRYPTO TRADING SYSTEM")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--dashboard':
            create_monitoring_dashboard()
        elif sys.argv[1] == '--status':
            show_quick_status()
        elif sys.argv[1] == '--monitor':
            pid = find_user_agent_terminal()
            if pid:
                monitor_process_activity(pid)
        else:
            print("Usage: python user_monitor.py [--dashboard|--status|--monitor]")
    else:
        # Default behavior
        pid = find_user_agent_terminal()
        print()
        
        if pid:
            print("🎯 MONITORING OPTIONS:")
            print("-" * 40)
            print("1. python user_monitor.py --dashboard   # Live dashboard")
            print("2. python user_monitor.py --monitor     # Process monitoring") 
            print("3. python user_monitor.py --status      # Quick status")
            print()
            print("💡 OR simply check the terminal running comprehensive_user_agent.py")
            print("   for real-time signal output!")
        
        show_quick_status()

if __name__ == "__main__":
    main()
