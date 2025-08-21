#!/usr/bin/env python3
"""
Kill All Agents Script
Skrip untuk menghentikan semua agent trading yang berjalan
"""

import subprocess
import sys
import time

def kill_all_agents():
    """Kill all crypto trading agents"""
    
    print("🛑 STOPPING ALL CRYPTO TRADING AGENTS")
    print("="*60)
    
    # List of agent processes to kill
    agent_processes = [
        "technical_agent.py",
        "news_agent.py", 
        "whale_agent.py",
        "enhanced_risk_manager_agent.py",
        "risk_manager_agent.py",
        "comprehensive_signal_agent.py",
        "fixed_comprehensive_signal_agent.py",
        "signal_agent.py",
        "comprehensive_user_agent.py",
        "user_agent.py",
        "run_all_agents.py",
        "user_monitor.py"
    ]
    
    killed_count = 0
    
    for process_name in agent_processes:
        try:
            # Find and kill processes by name
            result = subprocess.run(
                ["pkill", "-f", process_name], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Stopped: {process_name}")
                killed_count += 1
            else:
                print(f"ℹ️  Not running: {process_name}")
                
        except Exception as e:
            print(f"❌ Error stopping {process_name}: {e}")
    
    # Also kill by port (backup method)
    ports = [8001, 8002, 8003, 8004, 8005, 8006, 8007]
    
    print("\n🔍 Checking ports...")
    for port in ports:
        try:
            # Find process using port
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], 
                capture_output=True, 
                text=True
            )
            
            if result.stdout.strip():
                pid = result.stdout.strip()
                # Kill the process
                subprocess.run(["kill", "-9", pid], capture_output=True)
                print(f"✅ Killed process on port {port} (PID: {pid})")
                killed_count += 1
            else:
                print(f"ℹ️  Port {port} is free")
                
        except Exception as e:
            print(f"❌ Error checking port {port}: {e}")
    
    print("\n" + "="*60)
    print(f"🎯 SUMMARY: Stopped {killed_count} processes")
    print("✅ All crypto trading agents have been stopped")
    print("="*60)

if __name__ == "__main__":
    try:
        kill_all_agents()
    except KeyboardInterrupt:
        print("\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
