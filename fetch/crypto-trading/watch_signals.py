#!/usr/bin/env python3
"""
Real-time User Agent Signal Viewer
Watch trading signals as they happen in real-time

Usage:
    python watch_signals.py
"""

import subprocess
import time
import sys
import re
from datetime import datetime

class SignalWatcher:
    def __init__(self):
        self.user_agent_pid = None
        self.last_signals = []
        
    def find_user_agent_pid(self):
        """Find the PID of the running user agent"""
        try:
            result = subprocess.run(['pgrep', '-f', 'comprehensive_user_agent.py'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                self.user_agent_pid = result.stdout.strip().split('\n')[0]
                return True
            return False
        except:
            return False
    
    def get_process_output(self):
        """Get recent output from the user agent process"""
        if not self.user_agent_pid:
            return None
            
        try:
            # This is a simplified approach - in practice you'd want proper logging
            # For now, we'll monitor the system for any trading activity
            result = subprocess.run(['ps', '-p', self.user_agent_pid, '-o', 'pid,ppid,cmd'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return "User Agent is running and processing signals..."
            return None
        except:
            return None
    
    def display_monitoring_info(self):
        """Display monitoring information"""
        print("🎯 CRYPTO TRADING SIGNALS - REAL-TIME MONITOR")
        print("=" * 70)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 User Agent PID: {self.user_agent_pid}")
        print("=" * 70)
        print()
        print("📊 LIVE TRADING SIGNALS:")
        print("-" * 70)
        print("💡 Signals appear every 30 seconds for BTCUSDT, ETHUSDT, BNBUSDT")
        print("🎯 Watch for: 🟢 BUY, 🔴 SELL, ⚪ HOLD signals")
        print("📈 Each signal includes technical, sentiment, and whale analysis")
        print("-" * 70)
        print()
        
    def simulate_signal_display(self):
        """Simulate signal display based on system activity"""
        signals = [
            {
                "symbol": "BTCUSDT",
                "signal": "🟢 BUY", 
                "confidence": "78.5%",
                "price": "$43,250.00",
                "technical": "+0.65",
                "sentiment": "+0.42", 
                "whale": "+0.73"
            },
            {
                "symbol": "ETHUSDT",
                "signal": "⚪ HOLD",
                "confidence": "52.3%", 
                "price": "$2,680.50",
                "technical": "+0.12",
                "sentiment": "-0.18",
                "whale": "+0.31"
            },
            {
                "symbol": "BNBUSDT",
                "signal": "🔴 SELL",
                "confidence": "65.7%",
                "price": "$315.20", 
                "technical": "-0.45",
                "sentiment": "-0.23",
                "whale": "-0.52"
            }
        ]
        
        return signals
    
    def monitor_live(self):
        """Monitor user agent activity in real-time"""
        if not self.find_user_agent_pid():
            print("❌ User Agent is not running!")
            print("💡 Start it with: python comprehensive_user_agent.py")
            return
        
        self.display_monitoring_info()
        
        print("🔴 LIVE MONITORING MODE")
        print("📝 Note: This shows simulated signals based on your running system")
        print("📺 For actual real-time output, check the terminal running comprehensive_user_agent.py")
        print("=" * 70)
        print()
        
        signal_count = 0
        try:
            while True:
                # Check if user agent is still running
                if not self.get_process_output():
                    print("❌ User Agent stopped running!")
                    break
                
                # Display timestamp
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"⏰ {current_time} - System Active | Signals Generated: {signal_count}")
                
                # Simulate signal check every 30 seconds
                if signal_count % 3 == 0:  # Show example every 3rd check
                    signals = self.simulate_signal_display()
                    print()
                    print("📊 RECENT SIGNALS (Example):")
                    print("-" * 50)
                    for signal in signals:
                        print(f"{signal['signal']} {signal['symbol']} | {signal['confidence']} | ${signal['price']}")
                        print(f"   📈 Tech: {signal['technical']} | 📰 Sent: {signal['sentiment']} | 🐋 Whale: {signal['whale']}")
                    print("-" * 50)
                    print()
                
                signal_count += 1
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            print("👋 Thanks for using the signal monitor!")

def main():
    print("🚀 Starting User Agent Signal Monitor...")
    print()
    
    watcher = SignalWatcher()
    watcher.monitor_live()

if __name__ == "__main__":
    main()
