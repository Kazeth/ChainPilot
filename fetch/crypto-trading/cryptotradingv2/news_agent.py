from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from shared_types import (
    NewsRequest, 
    NewsResponse, 
    PROTOCOL_NAME,
    NEWS_AGENT_ADDRESS
)
import requests
import logging
from datetime import datetime, timedelta
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create News Agent
news_agent = Agent(
    name="news_agent",
    port=8005,
    endpoint=["http://localhost:8005/submit"],
    seed="news_agent_seed_phrase"
)

# Fund the agent if balance is low
fund_agent_if_low(news_agent.wallet.address())

# Define protocol using shared constant
news_protocol = Protocol(PROTOCOL_NAME)

# API configuration - You need to get your own API key from NewsAPI
NEWS_API_KEY = "your_newsapi_key_here"  # Replace with your actual API key
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Sentiment word lists (simple rule-based sentiment analysis)
POSITIVE_WORDS = {
    'bullish', 'bull', 'rise', 'surge', 'pump', 'moon', 'rocket', 'gain', 'profit',
    'buy', 'long', 'up', 'high', 'increase', 'growth', 'positive', 'good', 'great',
    'excellent', 'strong', 'support', 'breakthrough', 'rally', 'momentum', 'upgrade',
    'adoption', 'partnership', 'success', 'winner', 'boom', 'soar', 'climb'
}

NEGATIVE_WORDS = {
    'bearish', 'bear', 'fall', 'crash', 'dump', 'drop', 'sell', 'short', 'down',
    'low', 'decrease', 'decline', 'negative', 'bad', 'terrible', 'weak', 'resistance',
    'breakdown', 'correction', 'recession', 'loss', 'risk', 'fear', 'panic', 'concern',
    'warning', 'alert', 'banned', 'regulation', 'scam', 'hack', 'exploit', 'plunge'
}

def get_crypto_news(symbol):
    """Get crypto news from NewsAPI"""
    try:
        # Extract base currency (e.g., BTC from BTCUSDT)
        base_currency = symbol.replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        
        # Map common symbols to full names
        currency_map = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'BNB': 'Binance',
            'ADA': 'Cardano',
            'DOT': 'Polkadot',
            'LINK': 'Chainlink',
            'SOL': 'Solana',
            'MATIC': 'Polygon'
        }
        
        currency_name = currency_map.get(base_currency, base_currency)
        
        # Search query
        query = f"{currency_name} OR {base_currency} AND (crypto OR cryptocurrency OR bitcoin)"
        
        # Use alternative free news sources if NewsAPI key is not available
        if NEWS_API_KEY == "your_newsapi_key_here":
            # Fallback to mock news for demonstration
            return get_mock_news(currency_name)
        
        params = {
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'pageSize': 20,
            'apiKey': NEWS_API_KEY
        }
        
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('articles', [])
        
        return articles
        
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return get_mock_news(symbol)

def get_mock_news(symbol):
    """Generate mock news for demonstration when API is not available"""
    mock_articles = [
        {
            'title': f'{symbol} shows strong technical indicators amid market uncertainty',
            'description': f'Technical analysis suggests {symbol} may be poised for a breakout as trading volume increases.',
            'publishedAt': datetime.now().isoformat()
        },
        {
            'title': f'Institutional interest in {symbol} continues to grow',
            'description': f'Major investment firms are reportedly increasing their {symbol} holdings despite market volatility.',
            'publishedAt': (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            'title': f'Market analysts remain cautiously optimistic about {symbol}',
            'description': f'While short-term volatility persists, long-term outlook for {symbol} remains positive according to experts.',
            'publishedAt': (datetime.now() - timedelta(hours=4)).isoformat()
        }
    ]
    
    return mock_articles

def analyze_sentiment(text):
    """Simple rule-based sentiment analysis"""
    if not text:
        return 0.0
    
    # Clean and tokenize text
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    
    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)
    
    total_sentiment_words = positive_count + negative_count
    
    if total_sentiment_words == 0:
        return 0.0
    
    # Calculate sentiment score
    sentiment_score = (positive_count - negative_count) / total_sentiment_words
    
    # Apply word count weighting (more sentiment words = higher confidence)
    weight = min(total_sentiment_words / 10, 1.0)
    
    return sentiment_score * weight

def calculate_overall_sentiment(articles):
    """Calculate overall sentiment from multiple articles"""
    if not articles:
        return 0.0, 0, [], 0.0
    
    sentiments = []
    headlines = []
    
    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '')
        
        # Combine title and description for sentiment analysis
        text = f"{title} {description}"
        sentiment = analyze_sentiment(text)
        
        sentiments.append(sentiment)
        headlines.append(title[:100])  # Limit headline length
    
    # Calculate weighted average sentiment
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Calculate confidence based on consistency of sentiments
        if len(sentiments) > 1:
            sentiment_std = (sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)) ** 0.5
            confidence = max(0.1, 1.0 - sentiment_std)
        else:
            confidence = 0.5
    else:
        avg_sentiment = 0.0
        confidence = 0.0
    
    return avg_sentiment, len(articles), headlines[:5], confidence

@news_protocol.on_message(model=NewsRequest)
async def handle_news_request(ctx: Context, sender: str, msg: NewsRequest):
    """Handle news sentiment analysis requests with JSON logging"""
    ctx.logger.info(f"📰 NEWS AGENT: Received request for {msg.symbol} from {sender}")
    ctx.logger.info(f"📄 Request JSON: {msg.to_json()}")
    
    try:
        # Get news articles
        articles = get_crypto_news(msg.symbol)
        
        # Analyze sentiment
        sentiment_score, news_count, headlines, confidence = calculate_overall_sentiment(articles)
        
        # Create JSON response
        response = NewsResponse(
            symbol=msg.symbol,
            sentiment_score=sentiment_score,
            news_count=news_count,
            headlines=headlines,
            confidence=confidence
        )
        
        # Send JSON response with logging
        ctx.logger.info(f"📤 Sending news JSON response: {response.to_json()}")
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ News analysis sent for {msg.symbol}: Sentiment={sentiment_score:.3f}, Articles={news_count}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error in news analysis: {e}")
        import traceback
        traceback.print_exc()
        
        # Send neutral response on error
        error_response = NewsResponse(
            symbol=msg.symbol,
            sentiment_score=0.0,
            news_count=0,
            headlines=["Error fetching news"],
            confidence=0.0
        )
        ctx.logger.info(f"📤 Sending error JSON response: {error_response.to_json()}")
        await ctx.send(sender, error_response)

# Include the protocol
news_agent.include(news_protocol)

if __name__ == "__main__":
    print(f"News Agent address: {news_agent.address}")
    print("News Agent is ready to analyze sentiment...")
    if NEWS_API_KEY == "your_newsapi_key_here":
        print("⚠️  Using mock news data. Get a free API key from https://newsapi.org/ for real news.")
    news_agent.run()
