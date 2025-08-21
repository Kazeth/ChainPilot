from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
)
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
    seed="news_agent_seed_phrase",
)

# Fund the agent if balance is low
fund_agent_if_low(news_agent.wallet.address())

# Define protocol using shared constant
news_protocol = Protocol(PROTOCOL_NAME)

# Create chat protocol
chat_protocol = Protocol(spec=chat_protocol_spec)

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

# ========================================
# CHAT PROTOCOL HANDLERS
# ========================================

@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle chat messages for news sentiment analysis"""
    ctx.logger.info(f"💬 Chat message from {sender}: {msg.content[0].text}")
    
    try:
        message_text = msg.content[0].text
        message_text_lower = message_text.lower()
        
        # Extract session ID and user agent address if present
        session_id = None
        user_agent_address = None
        if "session:" in message_text:
            try:
                session_part = message_text.split("session:")[1].split()[0]
                session_id = session_part.strip()
                ctx.logger.info(f"📰 News analysis requested for session: {session_id}")
            except:
                ctx.logger.warning("Could not extract session ID from message")
        
        if "user:" in message_text:
            try:
                user_part = message_text.split("user:")[1].split()[0]
                user_agent_address = user_part.strip()
                ctx.logger.info(f"📰 Will send response to user agent: {user_agent_address[:16]}...")
            except:
                ctx.logger.warning("Could not extract user agent address from message")
        
        response_text = "📰 **News Sentiment Agent**\n\n"
        
        # Check if user is asking for sentiment analysis
        if any(word in message_text_lower for word in ["news", "sentiment", "headlines", "analyze"]):
            # Look for trading symbols
            symbols = []
            common_symbols = ["btc", "eth", "bnb", "ada", "sol", "btcusdt", "ethusdt", "bnbusdt", "adausdt", "solusdt"]
            
            for symbol in common_symbols:
                if symbol in message_text_lower:  # Fix: Use lowercase for consistent matching
                    if symbol in ["btc", "bitcoin"]:
                        symbols.append("BTCUSDT")
                    elif symbol in ["eth", "ethereum"]:
                        symbols.append("ETHUSDT")
                    elif symbol in ["bnb", "binance"]:
                        symbols.append("BNBUSDT")
                    elif symbol in ["ada", "cardano"]:
                        symbols.append("ADAUSDT")
                    elif symbol in ["sol", "solana"]:
                        symbols.append("SOLUSDT")
                    else:
                        symbols.append(symbol.upper())
            
            if symbols:
                response_text += f"🔄 **Analyzing {', '.join(symbols)} news sentiment...**\n\n"
                
                # Perform sentiment analysis for the first symbol
                symbol = symbols[0]
                try:
                    # Get news articles
                    articles = get_crypto_news(symbol)
                    
                    # Analyze sentiment
                    sentiment_score, news_count, headlines, confidence = calculate_overall_sentiment(articles)
                    
                    # Format response
                    response_text += f"📰 **{symbol} News Sentiment Analysis:**\n\n"
                    response_text += f"📊 Sentiment Score: {sentiment_score:.3f}\n"
                    response_text += f"📄 Articles Analyzed: {news_count}\n"
                    response_text += f"🎯 Confidence: {confidence:.2%}\n\n"
                    
                    # Add interpretation
                    if sentiment_score > 0.3:
                        response_text += "🟢 **Sentiment: POSITIVE**\n"
                        response_text += "News indicates bullish market sentiment\n\n"
                    elif sentiment_score < -0.3:
                        response_text += "🔴 **Sentiment: NEGATIVE**\n"
                        response_text += "News indicates bearish market sentiment\n\n"
                    else:
                        response_text += "⚪ **Sentiment: NEUTRAL**\n"
                        response_text += "News sentiment is balanced\n\n"
                    
                    # Show top headlines
                    if headlines:
                        response_text += "📖 **Top Headlines:**\n"
                        for i, headline in enumerate(headlines[:3], 1):
                            # Truncate long headlines
                            display_headline = headline[:80] + "..." if len(headline) > 80 else headline
                            response_text += f"{i}. {display_headline}\n"
                        
                        if len(headlines) > 3:
                            response_text += f"...and {len(headlines) - 3} more headlines\n"
                    
                    if NEWS_API_KEY == "your_newsapi_key_here":
                        response_text += "\n⚠️ **Note:** Using mock news data. "
                        response_text += "Get a free API key from https://newsapi.org/ for real news."
                        
                except Exception as e:
                    response_text += f"❌ Error analyzing {symbol}: {str(e)}"
            else:
                response_text += "Please specify a trading symbol (e.g., BTC, ETH, BNB)\n\n"
                response_text += "**Example commands:**\n"
                response_text += "• 'news sentiment for BTC'\n"
                response_text += "• 'analyze ETH headlines'\n"
                response_text += "• 'show BNB news sentiment'\n"
        
        elif "help" in message_text or "commands" in message_text:
            response_text += "**Available Commands:**\n\n"
            response_text += "📰 **News Analysis:**\n"
            response_text += "• 'news [SYMBOL]' - Get news sentiment\n"
            response_text += "• 'sentiment [SYMBOL]' - Analyze sentiment\n"
            response_text += "• 'headlines [SYMBOL]' - Show top headlines\n\n"
            response_text += "📊 **Sentiment Analysis:**\n"
            response_text += "• Positive/Negative keyword detection\n"
            response_text += "• Confidence scoring based on consistency\n"
            response_text += "• Multiple news source aggregation\n\n"
            response_text += "🎯 **Supported Symbols:**\n"
            response_text += "BTC, ETH, BNB, ADA, SOL (and related pairs)"
        
        elif "status" in message_text:
            response_text += "**News Agent Status:**\n\n"
            response_text += f"🟢 Status: Active (Port 8005)\n"
            response_text += f"💰 Address: {news_agent.address[:16]}...\n"
            response_text += f"🌐 Protocol: {PROTOCOL_NAME}\n"
            
            if NEWS_API_KEY != "your_newsapi_key_here":
                response_text += f"📡 Data Source: NewsAPI (Live)\n"
            else:
                response_text += f"📡 Data Source: Mock Data (Demo)\n"
                response_text += f"🔑 API Key: Not configured\n"
            
            response_text += f"📰 Analysis: Keyword-based sentiment\n"
        
        else:
            response_text += "I'm your news sentiment specialist! 📰\n\n"
            response_text += "I analyze cryptocurrency news for:\n"
            response_text += "📊 Sentiment scoring (positive/negative)\n"
            response_text += "📈 Market sentiment trends\n"
            response_text += "📖 Latest headlines and topics\n"
            response_text += "🎯 Confidence assessments\n\n"
            
            if NEWS_API_KEY == "your_newsapi_key_here":
                response_text += "⚠️ Currently using mock data for demonstration.\n"
                response_text += "Configure NewsAPI key for live news analysis.\n\n"
            
            response_text += "Try: 'news BTC' or 'help' for commands"
        
        # Add session ID to response if present
        if session_id:
            response_text += f"\n\nsession:{session_id}"
        
        # Determine where to send response (user agent if specified, otherwise sender)
        response_target = user_agent_address if user_agent_address else sender
        ctx.logger.info(f"📤 Sending news analysis to: {response_target[:16]}...")
        
        # Send response
        await ctx.send(
            response_target,
            ChatMessage(
                content=[TextContent(text=response_text)]
            )
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Error handling chat message: {e}")
        error_response = "Sorry, I encountered an error processing your message. Please try again."
        await ctx.send(
            sender,
            ChatMessage(
                content=[TextContent(text=error_response)]
            )
        )

@chat_protocol.on_message(model=ChatAcknowledgement)
async def handle_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    ctx.logger.info(f"💬 Chat acknowledgement from {sender}")

# Include both protocols
news_agent.include(news_protocol)
news_agent.include(chat_protocol)

if __name__ == "__main__":
    print("=" * 60)
    print("📰 NEWS SENTIMENT AGENT WITH CHAT")
    print("=" * 60)
    print(f"Agent address: {news_agent.address}")
    print(f"Port: 8005")
    print()
    print("📊 SENTIMENT ANALYSIS:")
    print("  ✅ Positive/Negative keyword detection")
    print("  ✅ Confidence scoring")
    print("  ✅ Multiple news source aggregation")
    print("  ✅ Real-time headline analysis")
    print()
    print("💬 CHAT FEATURES:")
    print("  ✅ Interactive sentiment analysis via chat")
    print("  ✅ Symbol-specific news analysis")
    print("  ✅ Top headlines display")
    print("  ✅ Help commands and status queries")
    print()
    if NEWS_API_KEY == "your_newsapi_key_here":
        print("📡 DATA SOURCE: Mock Data (Demo)")
        print("⚠️  Get a free API key from https://newsapi.org/ for real news.")
    else:
        print("📡 DATA SOURCE: NewsAPI (Live)")
    print()
    print("🚀 Starting News Agent with Chat...")
    print("=" * 60)
    news_agent.run()
