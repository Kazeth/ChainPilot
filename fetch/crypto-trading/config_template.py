"""
Configuration Template for Comprehensive AI Multi-Agent Trading System
Template Konfigurasi untuk Sistem AI Multi-Agent Trading

Copy this file to 'config.py' and update with your settings.
Salin file ini ke 'config.py' dan perbarui dengan pengaturan Anda.
"""

# =============================================================================
# API CONFIGURATION / KONFIGURASI API
# =============================================================================

# NewsAPI Configuration (Optional - for live news data)
# Konfigurasi NewsAPI (Opsional - untuk data berita langsung)
NEWSAPI_CONFIG = {
    "api_key": "ea95d2a81cae42b38aabc1f0547df0a7",  # Get from: https://newsapi.org
    "enabled": True,  # Set to True when you have API key
}

# Whale Alert API Configuration (Optional - for live whale data)
# Konfigurasi Whale Alert API (Opsional - untuk data whale langsung)
WHALE_ALERT_CONFIG = {
    "api_key": "YOUR_WHALE_ALERT_KEY_HERE",  # Get from: https://whale-alert.io
    "enabled": False,  # Set to True when you have API key
}

# =============================================================================
# TRADING CONFIGURATION / KONFIGURASI TRADING
# =============================================================================

# Trading pairs to monitor
# Pasangan trading yang akan dimonitor
TRADING_PAIRS = [
    "BTCUSDT",   # Bitcoin
    "ETHUSDT",   # Ethereum
    "BNBUSDT",   # Binance Coin
    "ADAUSDT",   # Cardano
    "SOLUSDT",   # Solana
]

# Signal generation interval (seconds)
# Interval generasi sinyal (detik)
SIGNAL_INTERVAL = 30  # 30 seconds

# =============================================================================
# TECHNICAL ANALYSIS SETTINGS / PENGATURAN ANALISIS TEKNIKAL
# =============================================================================

TECHNICAL_SETTINGS = {
    # RSI Settings
    "rsi_period": 14,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    
    # MACD Settings  
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    
    # Bollinger Bands Settings
    "bb_period": 20,
    "bb_std": 2,
    
    # Moving Average Settings
    "sma_short": 10,
    "sma_long": 50,
    
    # ATR Settings (for risk management)
    "atr_period": 14,
}

# =============================================================================
# RISK MANAGEMENT SETTINGS / PENGATURAN MANAJEMEN RISIKO
# =============================================================================

RISK_SETTINGS = {
    # ATR Multipliers for Stop Loss and Take Profit
    "atr_multiplier_stop_loss": 2.0,      # Stop loss at 2x ATR
    "atr_multiplier_take_profit": 3.0,    # Take profit at 3x ATR
    
    # Maximum risk per trade (percentage of portfolio)
    "max_risk_percentage": 2.0,           # 2% maximum risk
    
    # Minimum risk/reward ratio
    "min_risk_reward_ratio": 1.5,         # 1.5:1 minimum
}

# =============================================================================
# SENTIMENT ANALYSIS SETTINGS / PENGATURAN ANALISIS SENTIMEN
# =============================================================================

SENTIMENT_SETTINGS = {
    # Keywords for positive sentiment
    "positive_keywords": [
        "bullish", "moon", "pump", "breakout", "rally", "surge", "gains",
        "profit", "buy", "long", "uptend", "bullrun", "green", "rocket"
    ],
    
    # Keywords for negative sentiment  
    "negative_keywords": [
        "bearish", "dump", "crash", "fall", "drop", "sell", "short",
        "decline", "red", "fear", "panic", "correction", "dip", "loss"
    ],
    
    # Number of news articles to analyze
    "max_articles": 10,
}

# =============================================================================
# WHALE ANALYSIS SETTINGS / PENGATURAN ANALISIS WHALE
# =============================================================================

WHALE_SETTINGS = {
    # Minimum transaction amount to consider as "whale activity" (USD)
    "min_whale_amount": 1000000,  # $1M USD
    
    # Time window for whale analysis (hours)
    "analysis_window_hours": 24,
    
    # Exchange addresses for flow analysis (simplified list)
    "exchange_addresses": {
        "binance": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"],  # Example addresses
        "coinbase": ["3Qd8ZV4PdYRhhtN4dGdGT8t2qfpjW8QcHK"],
        "kraken": ["1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"],
    },
}

# =============================================================================
# SIGNAL WEIGHTING / BOBOT SINYAL
# =============================================================================

SIGNAL_WEIGHTS = {
    "technical_weight": 0.40,    # 40% weight for technical analysis
    "sentiment_weight": 0.30,    # 30% weight for sentiment analysis
    "whale_weight": 0.30,        # 30% weight for whale activity
}

# Signal confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high_confidence": 0.8,      # 80%+ = High confidence
    "medium_confidence": 0.6,    # 60-80% = Medium confidence
    "low_confidence": 0.4,       # 40-60% = Low confidence
}

# =============================================================================
# LOGGING CONFIGURATION / KONFIGURASI LOGGING
# =============================================================================

LOGGING_CONFIG = {
    "level": "INFO",             # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_enabled": False,       # Set to True to log to file
    "log_file": "trading_system.log",
}

# =============================================================================
# AGENT NETWORK CONFIGURATION / KONFIGURASI JARINGAN AGENT
# =============================================================================

# Agent addresses - UPDATE THESE WITH ACTUAL ADDRESSES AFTER DEPLOYMENT
# Alamat agent - PERBARUI INI DENGAN ALAMAT SEBENARNYA SETELAH DEPLOYMENT
AGENT_ADDRESSES = {
    "technical_agent": "agent1qtech",      # Update after deployment
    "news_agent": "agent1qnews",          # Update after deployment
    "whale_agent": "agent1qwhale",        # Update after deployment
    "risk_manager": "agent1qrisk",        # Update after deployment
    "signal_agent": "agent1qsignal",      # Update after deployment
    "user_agent": "agent1quser",          # Update after deployment
}

# Agent ports
AGENT_PORTS = {
    "risk_manager": 8001,
    "signal_agent": 8002,
    "user_agent": 8003,
    "technical_agent": 8004,
    "news_agent": 8005,
    "whale_agent": 8006,
}

# =============================================================================
# MOCK DATA SETTINGS / PENGATURAN DATA MOCK
# =============================================================================

# Enable mock data when APIs are not available
# Aktifkan data mock ketika API tidak tersedia
MOCK_DATA_ENABLED = True

# Mock data settings
MOCK_SETTINGS = {
    "price_volatility": 0.02,    # 2% price volatility for mock data
    "news_count": 5,             # Number of mock news articles
    "whale_transactions": 3,     # Number of mock whale transactions
}

# =============================================================================
# EXAMPLE USAGE / CONTOH PENGGUNAAN
# =============================================================================

"""
# Copy this file to config.py and customize:
cp config_template.py config.py

# Then import in your agents:
from config import (
    TRADING_PAIRS, 
    TECHNICAL_SETTINGS, 
    RISK_SETTINGS,
    AGENT_ADDRESSES
)

# Example usage in agent:
for symbol in TRADING_PAIRS:
    rsi_period = TECHNICAL_SETTINGS["rsi_period"]
    # ... your code here
"""
