from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from pydantic import BaseModel
import requests
import pandas as pd
import numpy as np
import logging
import urllib3

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define message structures
class TechnicalRequest(BaseModel):
    """Request for technical analysis"""
    symbol: str  # e.g., "BTCUSDT"

class TechnicalResponse(BaseModel):
    """Response with technical analysis"""
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
    technical_score: float  # Combined technical score (-1 to 1)

# Create Technical Agent
technical_agent = Agent(
    name="technical_agent",
    port=8004,
    endpoint=["http://localhost:8004/submit"],
    seed="technical_agent_seed_phrase"
)

# Fund the agent if balance is low
fund_agent_if_low(technical_agent.wallet.address())

# Define protocol
technical_protocol = Protocol("Technical Analysis v1")

# API configuration
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
BINANCE_US_URL = "https://api.binance.us/api/v3"

def get_market_data(symbol, interval="1h", limit=200):
    """Get OHLCV data from Binance API with fallback"""
    try:
        # Try Binance US first
        url = f"{BINANCE_US_URL}/klines"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        response = requests.get(url, params=params, verify=False, timeout=10)
        
        if response.status_code != 200:
            # Fallback to main Binance
            url = f"{BINANCE_BASE_URL}/klines"
            response = requests.get(url, params=params, verify=False, timeout=10)
        
        response.raise_for_status()
        klines = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        
        # Convert numeric columns
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col])
            
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        
        return df
        
    except Exception as e:
        logging.error(f"Error fetching market data: {e}")
        return None

def calculate_rsi(df, window=14):
    """Calculate RSI indicator"""
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    ema_fast = df['close'].ewm(span=fast).mean()
    ema_slow = df['close'].ewm(span=slow).mean()
    
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal).mean()
    macd_histogram = macd - macd_signal
    
    return macd, macd_signal, macd_histogram

def calculate_bollinger_bands(df, window=20, num_std=2):
    """Calculate Bollinger Bands"""
    sma = df['close'].rolling(window=window).mean()
    std = df['close'].rolling(window=window).std()
    
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    
    return upper_band, lower_band

def calculate_atr(df, window=14):
    """Calculate Average True Range"""
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    atr = true_range.rolling(window=window).mean()
    return atr

def calculate_technical_score(rsi, macd, macd_signal, current_price, sma_20, sma_50, bb_upper, bb_lower):
    """Calculate combined technical score"""
    score = 0.0
    
    # RSI contribution (30% weight)
    if rsi < 30:
        score += 0.3  # Oversold = bullish
    elif rsi > 70:
        score -= 0.3  # Overbought = bearish
    else:
        score += 0.3 * (50 - rsi) / 20  # Neutral zone
    
    # MACD contribution (25% weight)
    if macd > macd_signal:
        score += 0.25  # MACD above signal = bullish
    else:
        score -= 0.25  # MACD below signal = bearish
    
    # Moving Average contribution (25% weight)
    if current_price > sma_50 > sma_20:
        score += 0.25  # Uptrend
    elif current_price < sma_50 < sma_20:
        score -= 0.25  # Downtrend
    
    # Bollinger Bands contribution (20% weight)
    if current_price < bb_lower:
        score += 0.2  # Oversold
    elif current_price > bb_upper:
        score -= 0.2  # Overbought
    
    return max(-1.0, min(1.0, score))  # Clamp between -1 and 1

@technical_protocol.on_message(model=TechnicalRequest)
async def handle_technical_request(ctx: Context, sender: str, msg: TechnicalRequest):
    """Handle technical analysis requests"""
    ctx.logger.info(f"Received technical analysis request for {msg.symbol} from {sender}")
    
    try:
        # Get market data
        df = get_market_data(msg.symbol)
        
        if df is None or df.empty:
            ctx.logger.error(f"Failed to get market data for {msg.symbol}")
            return
        
        # Calculate technical indicators
        df['rsi'] = calculate_rsi(df)
        macd, macd_signal, macd_histogram = calculate_macd(df)
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_histogram'] = macd_histogram
        
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        bb_upper, bb_lower = calculate_bollinger_bands(df)
        df['bb_upper'] = bb_upper
        df['bb_lower'] = bb_lower
        
        df['atr'] = calculate_atr(df)
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Calculate technical score
        technical_score = calculate_technical_score(
            latest['rsi'], latest['macd'], latest['macd_signal'],
            latest['close'], latest['sma_20'], latest['sma_50'],
            latest['bb_upper'], latest['bb_lower']
        )
        
        # Create response
        response = TechnicalResponse(
            symbol=msg.symbol,
            rsi=float(latest['rsi']),
            macd=float(latest['macd']),
            macd_signal=float(latest['macd_signal']),
            macd_histogram=float(latest['macd_histogram']),
            sma_20=float(latest['sma_20']),
            sma_50=float(latest['sma_50']),
            bollinger_upper=float(latest['bb_upper']),
            bollinger_lower=float(latest['bb_lower']),
            atr=float(latest['atr']),
            current_price=float(latest['close']),
            technical_score=technical_score
        )
        
        # Send response
        await ctx.send(sender, response)
        ctx.logger.info(f"Sent technical analysis for {msg.symbol}: Score={technical_score:.3f}, RSI={latest['rsi']:.2f}")
        
    except Exception as e:
        ctx.logger.error(f"Error in technical analysis: {e}")

# Include the protocol
technical_agent.include(technical_protocol)

if __name__ == "__main__":
    print(f"Technical Agent address: {technical_agent.address}")
    print("Technical Agent is ready to analyze market data...")
    technical_agent.run()
