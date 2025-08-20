import requests
import pandas as pd
import numpy as np
from datetime import datetime
from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from pydantic import BaseModel
import logging
import urllib3

# Suppress insecure request warnings when verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define message structures using Pydantic
class RiskRequest(BaseModel):
    """Request for TP/SL calculation based on ATR"""
    signal: str  # "BUY" or "SELL"
    symbol: str  # e.g., "BTCUSDT"
    current_price: float
    atr_value: float

class RiskResponse(BaseModel):
    """Response with TP/SL calculation"""
    signal: str  # "BUY" or "SELL"
    symbol: str  # e.g., "BTCUSDT"
    take_profit: float
    stop_loss: float

class SignalRequest(BaseModel):
    """Request for trading signal"""
    symbol: str  # e.g., "BTCUSDT"

class SignalResponse(BaseModel):
    """Response with trading signal and analysis"""
    symbol: str
    signal: str  # "BUY", "SELL", "HOLD", or "ERROR"
    rsi: float
    confidence: float
    current_price: float
    timestamp: str
    take_profit: float = 0.0  # Simple default without Field
    stop_loss: float = 0.0    # Simple default without Field

# Create Signal Agent
signal_agent = Agent(
    name="signal_agent",
    port=8002,
    endpoint=["http://localhost:8002/submit"],
    seed="signal_agent_seed_phrase"
)

# Fund the agent if balance is low
fund_agent_if_low(signal_agent.wallet.address())

# Define protocol
signal_protocol = Protocol("Signal Request v1")  # Added version to protocol name

# Define API URLs - using multiple sources for redundancy
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
BINANCE_US_URL = "https://api.binance.us/api/v3"
KUCOIN_BASE_URL = "https://api.kucoin.com/api/v1"
CURRENT_API = "BINANCE_US"  # Can be "BINANCE", "BINANCE_US", or "KUCOIN"

# Risk manager address - updated with the actual address
RISK_MANAGER_ADDRESS = "agent1q2pp6mj3z87fde22ce5pf2tue027zaks6ezyw0wu3lhjnt8n3ll9c3wva7w"

def get_klines_data(symbol, interval="1h", limit=100):
    """Get OHLCV data from multiple crypto exchange APIs with fallback options"""
    # First, try the current configured API
    data = _try_get_klines(symbol, interval, limit, CURRENT_API)
    
    # If the primary API fails, try fallbacks in sequence
    if data is None and CURRENT_API != "BINANCE_US":
        logging.info("Primary API failed, trying Binance US...")
        data = _try_get_klines(symbol, interval, limit, "BINANCE_US")
    
    if data is None and CURRENT_API != "KUCOIN":
        logging.info("Trying KuCoin API...")
        data = _try_get_klines(symbol, interval, limit, "KUCOIN")
    
    # If all APIs fail, log the error and return None
    if data is None:
        logging.error(f"Failed to fetch market data for {symbol} from all API sources")
    
    return data

def _try_get_klines(symbol, interval="1h", limit=100, api_source="BINANCE_US"):
    """Internal helper to attempt getting klines data from a specific API source"""
    try:
        if api_source == "BINANCE":
            url = f"{BINANCE_BASE_URL}/klines"
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit
            }
            # Using verify=False for SSL issues
            response = requests.get(url, params=params, verify=False, timeout=10)
            
        elif api_source == "BINANCE_US":
            url = f"{BINANCE_US_URL}/klines"
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit
            }
            response = requests.get(url, params=params, verify=False, timeout=10)
            
        elif api_source == "KUCOIN":
            # Convert symbol format (e.g., BTCUSDT -> BTC-USDT for KuCoin)
            kucoin_symbol = f"{symbol[:-4]}-{symbol[-4:]}" if symbol.endswith("USDT") else symbol
            # Convert interval format (e.g., 1h -> 1hour for KuCoin)
            kucoin_interval = interval.replace("h", "hour").replace("d", "day").replace("m", "min")
            
            url = f"{KUCOIN_BASE_URL}/market/candles"
            params = {
                "symbol": kucoin_symbol,
                "type": kucoin_interval,
                "startAt": int((datetime.now() - pd.Timedelta(days=7)).timestamp()),  # Last 7 days
                "endAt": int(datetime.now().timestamp())
            }
            response = requests.get(url, params=params, verify=False, timeout=10)
        else:
            logging.error(f"Unknown API source: {api_source}")
            return None
            
        response.raise_for_status()
        
        # Parse klines data based on the API source
        if api_source in ["BINANCE", "BINANCE_US"]:
            klines = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])
            
        elif api_source == "KUCOIN":
            data = response.json()
            if data["code"] != "200000":
                logging.error(f"KuCoin API error: {data['msg']}")
                return None
                
            # KuCoin returns data in a different format
            klines = data["data"]
            
            # KuCoin columns: [timestamp, open, close, high, low, volume, turnover]
            df = pd.DataFrame(klines, columns=[
                "open_time", "open", "close", "high", "low", "volume", "turnover"
            ])
        
        # Convert numeric columns
        numeric_columns = ["open", "high", "low", "close", "volume"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col])
            
        # Convert timestamps for Binance
        if api_source in ["BINANCE", "BINANCE_US"]:
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
        # Convert timestamps for KuCoin
        elif api_source == "KUCOIN":
            df["open_time"] = pd.to_datetime(df["open_time"], unit="s")
            # Create a close_time column (not provided by KuCoin)
            df["close_time"] = df["open_time"] + pd.Timedelta(interval)
        
        logging.info(f"Successfully fetched data from {api_source} API")
        return df
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {api_source} API: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error with {api_source} API: {e}")
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

def calculate_atr(df, window=14):
    """Calculate Average True Range (ATR)"""
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    atr = true_range.rolling(window=window).mean()
    return atr

def analyze_signal(df):
    """Analyze price data and determine trading signal based on RSI"""
    # Calculate RSI
    df['rsi'] = calculate_rsi(df)
    
    # Calculate ATR
    df['atr'] = calculate_atr(df)
    
    # Get the latest values
    latest_rsi = df['rsi'].iloc[-1]
    latest_price = df['close'].iloc[-1]
    latest_atr = df['atr'].iloc[-1]
    
    # Determine signal based on RSI
    # Using more aggressive thresholds for testing (35/65 instead of 30/70)
    if latest_rsi < 35:
        signal = "BUY"
        # Confidence calculation: Higher confidence when RSI is lower
        confidence = 0.5 + ((35 - latest_rsi) / 70)  # Maps RSI 0-35 to confidence 0.5-0.8
    elif latest_rsi > 65:
        signal = "SELL"
        # Confidence calculation: Higher confidence when RSI is higher
        confidence = 0.5 + ((latest_rsi - 65) / 70)  # Maps RSI 65-100 to confidence 0.5-0.8
    else:
        signal = "HOLD"
        # Confidence is lower in HOLD zone, highest at mid-range (RSI=50)
        confidence = 0.5 - (abs(50 - latest_rsi) / 40)  # Highest at RSI=50
    
    # Ensure confidence is within bounds
    confidence = min(max(confidence, 0.5), 0.8)
    
    logging.info(f"Analysis result: Signal={signal}, RSI={latest_rsi:.2f}, Price={latest_price:.2f}, ATR={latest_atr:.2f}")
    
    return {
        "signal": signal,
        "rsi": latest_rsi,
        "confidence": confidence,
        "price": latest_price,
        "atr": latest_atr
    }

@signal_protocol.on_message(model=SignalRequest)
async def handle_signal_request(ctx: Context, sender: str, msg: SignalRequest):
    """Handle incoming signal requests"""
    ctx.logger.info(f"Received signal request for {msg.symbol} from {sender}")
    
    try:
        # Get OHLCV data
        df = get_klines_data(msg.symbol)
        
        if df is None or df.empty:
            ctx.logger.error(f"Failed to get data for {msg.symbol} from all API sources")
            # Send a simple response back indicating the service is unavailable
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_response = SignalResponse(
                symbol=msg.symbol,
                signal="ERROR",
                rsi=0.0,
                confidence=0.0,
                current_price=0.0,
                timestamp=timestamp,
                take_profit=0.0,  # Using 0.0 instead of None
                stop_loss=0.0     # Using 0.0 instead of None
            )
            await ctx.send(sender, error_response)
            ctx.logger.info(f"Sent error response for {msg.symbol} back to {sender}")
            return
        
        # Analyze data
        analysis = analyze_signal(df)
        
        # If BUY or SELL, request TP/SL from Risk Manager
        take_profit = None
        stop_loss = None
        
        if analysis["signal"] in ["BUY", "SELL"]:
            ctx.logger.info(f"Requesting risk management for {analysis['signal']} signal on {msg.symbol}")
            ctx.logger.info(f"Current price: {analysis['price']}, ATR: {analysis['atr']}")
            ctx.logger.info(f"Sending request to Risk Manager at address: {RISK_MANAGER_ADDRESS}")
            
            # Create risk request
            risk_request = RiskRequest(
                signal=analysis["signal"],
                symbol=msg.symbol,
                current_price=analysis["price"],
                atr_value=analysis["atr"]
            )
            
            # Send to risk manager and wait for response
            try:
                ctx.logger.info("Sending request to risk manager...")
                risk_response = await ctx.request(
                    destination=RISK_MANAGER_ADDRESS,  # Risk manager address
                    message=risk_request,
                    timeout=15.0  # Increased timeout
                )
                
                if risk_response:
                    take_profit = risk_response.take_profit
                    stop_loss = risk_response.stop_loss
                    ctx.logger.info(f"Received risk management response: TP={take_profit:.2f}, SL={stop_loss:.2f}")
                else:
                    ctx.logger.warning("No response from risk manager, proceeding without TP/SL")
            except Exception as e:
                ctx.logger.error(f"Error communicating with risk manager: {e}")
                ctx.logger.warning("Proceeding without TP/SL due to error")
        
        # Current time for timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Set default values for take_profit and stop_loss if they're None
        if take_profit is None:
            take_profit = 0.0
        if stop_loss is None:
            stop_loss = 0.0
            
        # Create signal response
        signal_response = SignalResponse(
            symbol=msg.symbol,
            signal=analysis["signal"],
            rsi=round(analysis["rsi"], 2),
            confidence=round(analysis["confidence"], 2),
            current_price=analysis["price"],
            timestamp=timestamp,
            take_profit=take_profit,
            stop_loss=stop_loss
        )
        
        # Send response back to sender
        await ctx.send(sender, signal_response)
        ctx.logger.info(f"Sent signal response for {msg.symbol} back to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"Error processing signal request: {e}")

# Include the protocol
signal_agent.include(signal_protocol)

if __name__ == "__main__":
    # Print schema info for debugging
    print(f"Signal Agent's SignalResponse schema: {SignalResponse.schema()}")
    
    # Clear any cached protocol schemas
    print("Starting Signal Agent with address:", signal_agent.address)
    print(f"Primary API source: {CURRENT_API}")
    print(f"Using fallback APIs if primary fails: Binance US, KuCoin")
    print(f"Starting signal agent service...")
    
    # Run the agent
    signal_agent.run()
