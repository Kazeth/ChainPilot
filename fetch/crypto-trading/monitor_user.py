#!/usr/bin/env python3
"""
User Activity Monitor for Crypto Trading System
Monitor real-time user agent activity and trading signals

Usage:
    python monitor_user.py [options]
    
Options:
    --live          Show live user agent output
    --status        Show system status
    --logs          Show recent logs
    --signals       Show recent signals only
"""

import subprocess
import time
import sys
import argparse
from datetime import datetime
import os

def get_agent_status():
    """Check which agents are running"""
    print("🔍 CHECKING AGENT STATUS...")
    print("=" * 60)
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        agents = {
            "technical_agent.py": {"name": "Technical Agent", "port": 8004, "status": "🔴 STOPPED"},
            "news_agent.py": {"name": "News Agent", "port": 8005, "status": "🔴 STOPPED"},
            "whale_agent.py": {"name": "Whale Agent", "port": 8006, "status": "🔴 STOPPED"},
            "enhanced_risk_manager_agent.py": {"name": "Risk Manager", "port": 8001, "status": "🔴 STOPPED"},
            "comprehensive_signal_agent.py": {"name": "Signal Agent", "port": 8002, "status": "🔴 STOPPED"},
            "comprehensive_user_agent.py": {"name": "User Agent", "port": 8003, "status": "🔴 STOPPED"},
        }
        
        for agent_file, info in agents.items():
            if agent_file in processes:
                info["status"] = "🟢 RUNNING"
                # Extract PID
                lines = processes.split('\n')
                for line in lines:
                    if agent_file in line and 'python' in line:
                        parts = line.split()
                        if len(parts) > 1:
                            pid = parts[1]
                            info["pid"] = pid
                            break
        
        # Display status
        for agent_file, info in agents.items():
            pid_info = f" (PID: {info.get('pid', 'N/A')})" if info["status"] == "🟢 RUNNING" else ""
            print(f"{info['name']:>15} | Port {info['port']} | {info['status']}{pid_info}")
    
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    
    print("=" * 60)

def monitor_user_live():
    """Monitor user agent output in real-time"""
    print("📺 LIVE USER AGENT MONITORING")
    print("=" * 60)
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)
    
    try:
        # Find the user agent process
        result = subprocess.run(['pgrep', '-f', 'comprehensive_user_agent.py'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("❌ User Agent is not running!")
            print("💡 Start it with: python comprehensive_user_agent.py")
            return
        
        pid = result.stdout.strip().split('\n')[0]
        print(f"🎯 Monitoring User Agent (PID: {pid})")
        print("-" * 60)
        
        # Monitor the process output - this is a simplified approach
        # In a real scenario, you'd want to monitor log files or use a proper logging system
        print("🔴 Note: Direct process output monitoring requires log files.")
        print("💡 To see live output, check the terminal where comprehensive_user_agent.py is running")
        print("💡 Or redirect agent output to log files for monitoring")
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error monitoring: {e}")

def show_recent_logs():
    """Show recent system logs if available"""
    print("📋 RECENT SYSTEM LOGS")
    print("=" * 60)
    
    log_files = [
        "trading_system.log",
        "user_agent.log",
        "system.log"
    ]
    
    found_logs = False
    for log_file in log_files:
        if os.path.exists(log_file):
            found_logs = True
            print(f"📄 {log_file}:")
            print("-" * 40)
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Show last 10 lines
                    for line in lines[-10:]:
                        print(line.strip())
            except Exception as e:
                print(f"❌ Error reading {log_file}: {e}")
            print()
    
    if not found_logs:
        print("📝 No log files found in current directory")
        print("💡 Logs are currently printed to console/terminal")
        print("💡 To enable file logging, modify the logging configuration in agents")

def show_network_connections():
    """Show network connections for agent ports"""
    print("🌐 AGENT NETWORK CONNECTIONS")
    print("=" * 60)
    
    ports = [8001, 8002, 8003, 8004, 8005, 8006]
    
    for port in ports:
        try:
            result = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True)
            connections = result.stdout
            
            port_info = f":{port}"
            if port_info in connections:
                for line in connections.split('\n'):
                    if port_info in line and 'LISTEN' in line:
                        print(f"✅ Port {port}: {line.strip()}")
                        break
            else:
                print(f"❌ Port {port}: Not listening")
                
        except Exception as e:
            print(f"❌ Error checking port {port}: {e}")

def create_monitoring_dashboard():
    """Create a simple monitoring dashboard"""
    while True:
        os.system('clear')  # Clear screen
        
        print("🤖 CRYPTO TRADING SYSTEM MONITOR")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Show agent status
        get_agent_status()
        print()
        
        # Show network connections
        show_network_connections()
        print()
        
        print("🔄 Refreshing in 10 seconds... (Press Ctrl+C to stop)")
        
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped")
            break

def main():
    parser = argparse.ArgumentParser(description='Monitor Crypto Trading System User Activity')
    parser.add_argument('--live', action='store_true', help='Show live user agent output')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--logs', action='store_true', help='Show recent logs')
    parser.add_argument('--dashboard', action='store_true', help='Show live dashboard')
    parser.add_argument('--network', action='store_true', help='Show network connections')
    
    args = parser.parse_args()
    
    if args.live:
        monitor_user_live()
    elif args.status:
        get_agent_status()
    elif args.logs:
        show_recent_logs()
    elif args.dashboard:
        create_monitoring_dashboard()
    elif args.network:
        show_network_connections()
    else:
        # Default: show status and recent activity
        print("🤖 CRYPTO TRADING SYSTEM - USER MONITORING")
        print("=" * 60)
        get_agent_status()
        print()
        show_network_connections()
        print()
        show_recent_logs()
        print()
        print("💡 Available monitoring options:")
        print("   python monitor_user.py --live       # Live user output")
        print("   python monitor_user.py --status     # Agent status")
        print("   python monitor_user.py --logs       # Recent logs")
        print("   python monitor_user.py --dashboard  # Live dashboard")
        print("   python monitor_user.py --network    # Network status")

if __name__ == "__main__":
    main()
