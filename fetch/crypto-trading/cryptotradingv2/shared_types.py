#!/usr/bin/env python3

"""
SHARED AGENT TYPES - Ensures identical JSON schemas across all agents
This is the KEY to fixing the schema digest mismatch issue
"""

from pydantic import BaseModel
import json

# ========================================
# SHARED REQUEST MODELS - IDENTICAL SCHEMAS
# ========================================

class SignalRequest(BaseModel):
    """Request for comprehensive signal analysis"""
    symbol: str
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

class TechnicalRequest(BaseModel):
    """Request for technical analysis"""
    symbol: str
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

class NewsRequest(BaseModel):
    """Request for news sentiment analysis"""
    symbol: str
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

class WhaleRequest(BaseModel):
    """Request for whale activity analysis"""
    symbol: str
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

class RiskRequest(BaseModel):
    """Request for risk management"""
    symbol: str
    signal: str
    current_price: float
    confidence: float
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

# ========================================
# SHARED RESPONSE MODELS - IDENTICAL SCHEMAS  
# ========================================

class TechnicalResponse(BaseModel):
    """Technical analysis response - SHARED SCHEMA"""
    symbol: str
    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    sma_20: float
    sma_50: float
    bollinger_upper: float
    bollinger_lower: float
    atr: float
    current_price: float
    technical_score: float
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

class NewsResponse(BaseModel):
    """News sentiment response - SHARED SCHEMA"""
    symbol: str
    sentiment_score: float
    news_count: int
    headlines: list[str]
    confidence: float
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

class WhaleResponse(BaseModel):
    """Whale activity response - SHARED SCHEMA"""
    symbol: str
    whale_score: float
    whale_transactions: int
    net_whale_flow: float
    large_transactions: int
    average_transaction_size: float
    confidence: float
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

class RiskResponse(BaseModel):
    """Risk management response - SHARED SCHEMA"""
    symbol: str
    signal: str
    take_profit: float
    stop_loss: float
    risk_reward_ratio: float
    position_size: float
    confidence: float
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

class SignalResponse(BaseModel):
    """Comprehensive signal response - SHARED SCHEMA"""
    symbol: str
    signal: str  # BUY, SELL, HOLD
    confidence: float
    current_price: float
    
    # Technical data
    technical_score: float
    rsi: float
    macd: float
    atr: float = 0.0  # Add missing ATR field
    
    # Sentiment data
    sentiment_score: float
    news_count: int
    top_headlines: list[str] = []  # Add missing headlines field
    
    # Whale data
    whale_score: float
    net_whale_flow: float
    whale_transactions: int = 0  # Add missing whale transactions field
    
    # Risk management
    take_profit: float
    stop_loss: float
    risk_reward_ratio: float
    
    # Metadata
    timestamp: str
    analysis_summary: str
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

# ========================================
# SHARED PROTOCOL DEFINITION
# ========================================

PROTOCOL_NAME = "Crypto Trading v1"

# ========================================
# AGENT ADDRESSES - SHARED CONSTANTS
# ========================================

TECHNICAL_AGENT_ADDRESS = "agent1qgn5e6pqta60x79jrlmhlqcajxykagyuzvsw28j25u3y7jpp3estktf0uy3" # Update after run the agent
NEWS_AGENT_ADDRESS = "agent1qtt84hk6njyd07z5t8xrhc076wjsd3x3mlqd9qaem8hjnkrg6enpz8h2gfq" # Update after run the agent
WHALE_AGENT_ADDRESS = "agent1qvqth3lnn5tw2dl3xsk60lvp0aeah65uyvscqg7l43pth4lytay6sd30fly" # Update after run the agent
RISK_MANAGER_ADDRESS = "agent1qg9j3gx650julrvspcfsv3fhdcqlfjthf48tf0ljj7wpyzw29jwpgda2y0c" # Update after run the agent
SIGNAL_AGENT_ADDRESS = "agent1qgszqd3n6evuxmdlalvv6t6693sphg5nd0xvf8em74kpyjqfg8t3s48nqz7" # Update after run the agent

if __name__ == "__main__":
    print("🔧 SHARED AGENT TYPES")
    print("=" * 50)
    print("This module ensures all agents use identical JSON schemas")
    print()
    print("📄 Available Models:")
    print(f"  • SignalRequest: {SignalRequest.model_fields}")
    print(f"  • TechnicalRequest: {TechnicalRequest.model_fields}")
    print(f"  • NewsRequest: {NewsRequest.model_fields}")
    print(f"  • WhaleRequest: {WhaleRequest.model_fields}")
    print(f"  • RiskRequest: {RiskRequest.model_fields}")
    print()
    print("📤 Response Models:")
    print(f"  • TechnicalResponse: {len(TechnicalResponse.model_fields)} fields")
    print(f"  • NewsResponse: {len(NewsResponse.model_fields)} fields") 
    print(f"  • WhaleResponse: {len(WhaleResponse.model_fields)} fields")
    print(f"  • RiskResponse: {len(RiskResponse.model_fields)} fields")
    print(f"  • SignalResponse: {len(SignalResponse.model_fields)} fields")
    print()
    print(f"🌐 Protocol: {PROTOCOL_NAME}")
    print("=" * 50)
