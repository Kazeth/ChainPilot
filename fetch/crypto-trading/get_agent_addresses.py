#!/usr/bin/env python3
"""
Quick script to check agent addresses
Run this to get the real agent addresses for configuration
"""

from uagents import Agent

# Create temporary agents with the same seeds to get addresses
technical_temp = Agent(name="technical_agent", seed="technical_agent_seed_phrase")
news_temp = Agent(name="news_agent", seed="news_agent_seed_phrase") 
whale_temp = Agent(name="whale_agent", seed="whale_agent_seed_phrase")
risk_temp = Agent(name="risk_manager_agent", seed="risk_manager_agent_seed_phrase")
signal_temp = Agent(name="signal_agent", seed="signal_agent_seed_phrase")
user_temp = Agent(name="user_agent", seed="user_agent_seed_phrase")

print("🔧 AGENT ADDRESSES FOR CONFIGURATION:")
print("=" * 60)
print(f"TECHNICAL_AGENT_ADDRESS = \"{technical_temp.address}\"")
print(f"NEWS_AGENT_ADDRESS = \"{news_temp.address}\"")
print(f"WHALE_AGENT_ADDRESS = \"{whale_temp.address}\"")
print(f"RISK_MANAGER_ADDRESS = \"{risk_temp.address}\"")
print(f"SIGNAL_AGENT_ADDRESS = \"{signal_temp.address}\"")
print(f"USER_AGENT_ADDRESS = \"{user_temp.address}\"")
print("=" * 60)
print("Copy these addresses to update your agent configuration files!")
