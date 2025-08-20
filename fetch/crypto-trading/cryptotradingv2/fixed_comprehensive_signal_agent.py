#!/usr/bin/env python3

"""
FIXED COMPREHENSIVE SIGNAL AGENT - JSON FORMAT SOLUTION
This addresses the core issue: proper JSON serialization and message handling
"""

import asyncio
import random
import logging
from datetime import datetime, timedelta
from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from shared_types import (
    SignalRequest,
    TechnicalRequest,
    NewsRequest, 
    WhaleRequest,
    RiskRequest,
    TechnicalResponse,
    NewsResponse,
    WhaleResponse,
    RiskResponse,
    SignalResponse,
    PROTOCOL_NAME,
    TECHNICAL_AGENT_ADDRESS,
    NEWS_AGENT_ADDRESS,
    WHALE_AGENT_ADDRESS,
    RISK_MANAGER_ADDRESS,
    SIGNAL_AGENT_ADDRESS
)

# Configure logging
logging.basicConfig(level=logging.INFO)

# ========================================
# FIXED COMPREHENSIVE SIGNAL AGENT
# ========================================

# Create comprehensive signal agent using shared constants
comprehensive_signal = Agent(
    name="comprehensive_signal",
    port=8002,
    seed="comprehensive_signal_seed_fixed",
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Fund the agent
fund_agent_if_low(comprehensive_signal.wallet.address())

# Create protocol using shared constant
signal_protocol = Protocol(PROTOCOL_NAME)

# Global storage for JSON responses
agent_responses = {}
pending_requests = {}

def calculate_final_signal(technical_score, sentiment_score, whale_score, technical_confidence, sentiment_confidence, whale_confidence):
    """Calculate final trading signal based on all inputs"""
    
    # Validate confidence values
    if technical_confidence == 0 and sentiment_confidence == 0 and whale_confidence == 0:
        return "HOLD", 0.0, "Insufficient data for analysis"
    
    # Weight each score by its predefined importance (not by confidence twice)
    weights = {
        'technical': 0.4,
        'sentiment': 0.3,
        'whale': 0.3
    }
    
    # Calculate weighted average of scores, using confidence as reliability weighting
    total_weighted_confidence = (
        weights['technical'] * technical_confidence +
        weights['sentiment'] * sentiment_confidence +
        weights['whale'] * whale_confidence
    )
    
    if total_weighted_confidence == 0:
        return "HOLD", 0.0, "No reliable data for analysis"
    
    weighted_score = (
        technical_score * weights['technical'] * technical_confidence +
        sentiment_score * weights['sentiment'] * sentiment_confidence +
        whale_score * weights['whale'] * whale_confidence
    ) / total_weighted_confidence
    
    # Calculate overall confidence (average of available confidences)
    available_confidences = [c for c in [technical_confidence, sentiment_confidence, whale_confidence] if c > 0]
    overall_confidence = min(0.95, sum(available_confidences) / len(available_confidences) if available_confidences else 0.5)
    
    # Determine signal based on weighted score - MADE MORE SENSITIVE FOR TESTING
    if weighted_score > 0.1:  # Lowered from 0.3 to 0.1
        signal = "BUY"
        summary = f"Bullish signal (Score: {weighted_score:.2f}). "
    elif weighted_score < -0.1:  # Lowered from -0.3 to -0.1
        signal = "SELL" 
        summary = f"Bearish signal (Score: {weighted_score:.2f}). "
    else:
        signal = "HOLD"
        summary = f"Neutral signal (Score: {weighted_score:.2f}). "
    
    # Add contributing factors to summary
    factors = []
    if abs(technical_score) > 0.2:
        factors.append(f"Technical: {'Bullish' if technical_score > 0 else 'Bearish'}")
    if abs(sentiment_score) > 0.2:
        factors.append(f"Sentiment: {'Positive' if sentiment_score > 0 else 'Negative'}")
    if abs(whale_score) > 0.2:
        factors.append(f"Whales: {'Accumulating' if whale_score > 0 else 'Distributing'}")
    
    if factors:
        summary += "Key factors: " + ", ".join(factors)
    else:
        summary += "All indicators showing neutral trends"
    
    return signal, overall_confidence, summary

# ========================================
# MAIN SIGNAL REQUEST HANDLER - FIXED JSON
# ========================================

@signal_protocol.on_message(model=SignalRequest)
async def handle_signal_request(ctx: Context, sender: str, msg: SignalRequest):
    """Handle comprehensive signal requests with proper JSON handling"""
    ctx.logger.info(f"🎯 Received comprehensive signal request for {msg.symbol} from {sender}")
    ctx.logger.info(f"📄 Request JSON: {msg.to_json()}")
    
    try:
        # Clear any old responses for this symbol
        if msg.symbol not in agent_responses:
            agent_responses[msg.symbol] = {}
        
        ctx.logger.info(f"🔄 Requesting analysis from all agents for {msg.symbol}...")
        
        # Send requests to all agents with proper JSON models
        technical_request = TechnicalRequest(symbol=msg.symbol)
        news_request = NewsRequest(symbol=msg.symbol)  
        whale_request = WhaleRequest(symbol=msg.symbol)
        
        ctx.logger.info(f"📊 Sending technical request: {technical_request.to_json()}")
        await ctx.send(TECHNICAL_AGENT_ADDRESS, technical_request)
        
        ctx.logger.info(f"📰 Sending news request: {news_request.to_json()}")
        await ctx.send(NEWS_AGENT_ADDRESS, news_request)
        
        ctx.logger.info(f"🐋 Sending whale request: {whale_request.to_json()}")
        await ctx.send(WHALE_AGENT_ADDRESS, whale_request)
        
        # Wait for responses from all agents
        wait_time = 5.0
        ctx.logger.info(f"⏰ Waiting {wait_time} seconds for agent responses...")
        await asyncio.sleep(wait_time)
        
        # Process received JSON responses
        responses = agent_responses.get(msg.symbol, {})
        ctx.logger.info(f"📥 Received {len(responses)} responses: {list(responses.keys())}")
        
        if len(responses) >= 3:
            ctx.logger.info("✅ All agents responded! Processing comprehensive signal...")
            
            # Extract data from JSON responses
            technical_data = responses.get('technical')
            news_data = responses.get('news')
            whale_data = responses.get('whale')
            
            if technical_data and news_data and whale_data:
                # Log received JSON data
                ctx.logger.info(f"📊 Technical JSON: {technical_data.to_json()}")
                ctx.logger.info(f"📰 News JSON: {news_data.to_json()}")  
                ctx.logger.info(f"🐋 Whale JSON: {whale_data.to_json()}")
                
                # Calculate final signal
                final_signal, overall_confidence, analysis_summary = calculate_final_signal(
                    technical_data.technical_score, news_data.sentiment_score, whale_data.whale_score,
                    0.85, news_data.confidence, whale_data.confidence
                )
                
                # Request risk management if signal is actionable
                if final_signal in ["BUY", "SELL"]:
                    risk_request = RiskRequest(
                        symbol=msg.symbol,
                        signal=final_signal,
                        current_price=technical_data.current_price,
                        confidence=overall_confidence
                    )
                    ctx.logger.info(f"⚖️ Sending risk request: {risk_request.to_json()}")
                    await ctx.send(RISK_MANAGER_ADDRESS, risk_request)
                    
                    # Wait for risk response
                    await asyncio.sleep(3.0)
                    risk_data = agent_responses.get(msg.symbol, {}).get('risk')
                    
                    if risk_data:
                        ctx.logger.info(f"⚖️ Risk JSON: {risk_data.to_json()}")
                        take_profit = risk_data.take_profit
                        stop_loss = risk_data.stop_loss
                        risk_reward_ratio = risk_data.risk_reward_ratio
                    else:
                        ctx.logger.warning("⚠️ No risk management response, using defaults")
                        take_profit = technical_data.current_price * 1.05
                        stop_loss = technical_data.current_price * 0.95
                        risk_reward_ratio = 2.0
                else:
                    take_profit = 0.0
                    stop_loss = 0.0
                    risk_reward_ratio = 0.0
                
                # Create comprehensive JSON response
                response = SignalResponse(
                    symbol=msg.symbol,
                    signal=final_signal,
                    confidence=overall_confidence,
                    current_price=technical_data.current_price,
                    technical_score=technical_data.technical_score,
                    rsi=technical_data.rsi,
                    macd=technical_data.macd,
                    atr=technical_data.atr,  # Add missing ATR field
                    sentiment_score=news_data.sentiment_score,
                    news_count=news_data.news_count,
                    top_headlines=news_data.headlines,  # Add missing headlines field
                    whale_score=whale_data.whale_score,
                    net_whale_flow=whale_data.net_whale_flow,
                    whale_transactions=whale_data.whale_transactions,  # Add missing field
                    take_profit=take_profit,
                    stop_loss=stop_loss,
                    risk_reward_ratio=risk_reward_ratio,
                    timestamp=datetime.now().isoformat(),
                    analysis_summary=analysis_summary
                )
                
                # Send JSON response
                ctx.logger.info(f"🎯 Sending comprehensive JSON response: {response.to_json()}")
                await ctx.send(sender, response)
                ctx.logger.info(f"✅ Comprehensive analysis complete for {msg.symbol}")
                
            else:
                ctx.logger.error("❌ Missing required response data")
        else:
            ctx.logger.warning(f"⚠️ Only received {len(responses)} responses, attempting retry...")
            
            # Identify which agents didn't respond
            missing_agents = []
            if 'technical' not in responses:
                missing_agents.append(('technical', TECHNICAL_AGENT_ADDRESS, technical_request))
            if 'news' not in responses:
                missing_agents.append(('news', NEWS_AGENT_ADDRESS, news_request))
            if 'whale' not in responses:
                missing_agents.append(('whale', WHALE_AGENT_ADDRESS, whale_request))
            
            ctx.logger.info(f"🔄 Retrying requests to {len(missing_agents)} agents: {[agent[0] for agent in missing_agents]}")
            
            # Retry requests to missing agents
            for agent_name, agent_address, request in missing_agents:
                ctx.logger.info(f"🔄 Retrying {agent_name} agent request...")
                await ctx.send(agent_address, request)
            
            # Wait shorter time for retry responses
            retry_wait_time = 3.0
            ctx.logger.info(f"⏰ Waiting {retry_wait_time} seconds for retry responses...")
            await asyncio.sleep(retry_wait_time)
            
            # Check responses again after retry
            responses = agent_responses.get(msg.symbol, {})
            ctx.logger.info(f"📥 After retry: received {len(responses)} responses: {list(responses.keys())}")
            
            if len(responses) >= 3:
                ctx.logger.info("✅ Retry successful! Processing comprehensive signal...")
                # Process the responses (same logic as above)
                technical_data = responses.get('technical')
                news_data = responses.get('news')
                whale_data = responses.get('whale')
                
                if technical_data and news_data and whale_data:
                    # Calculate final signal
                    final_signal, overall_confidence, analysis_summary = calculate_final_signal(
                        technical_data.technical_score, news_data.sentiment_score, whale_data.whale_score,
                        0.85, news_data.confidence, whale_data.confidence
                    )
                    
                    # Create comprehensive response
                    response = SignalResponse(
                        symbol=msg.symbol,
                        signal=final_signal,
                        confidence=overall_confidence,
                        current_price=technical_data.current_price,
                        technical_score=technical_data.technical_score,
                        rsi=technical_data.rsi,
                        macd=technical_data.macd,
                        atr=technical_data.atr,
                        sentiment_score=news_data.sentiment_score,
                        news_count=news_data.news_count,
                        top_headlines=news_data.headlines,
                        whale_score=whale_data.whale_score,
                        net_whale_flow=whale_data.net_whale_flow,
                        whale_transactions=whale_data.whale_transactions,
                        take_profit=0.0,  # Will be calculated if needed
                        stop_loss=0.0,
                        risk_reward_ratio=0.0,
                        timestamp=datetime.now().isoformat(),
                        analysis_summary=analysis_summary
                    )
                    
                    ctx.logger.info(f"🎯 Sending retry-successful response: {response.to_json()}")
                    await ctx.send(sender, response)
                    ctx.logger.info(f"✅ Retry analysis complete for {msg.symbol}")
                else:
                    ctx.logger.error("❌ Retry failed: Missing required response data")
                    # Send error response instead of mock data
                    error_response = SignalResponse(
                        symbol=msg.symbol,
                        signal="ERROR",
                        confidence=0.0,
                        current_price=0.0,
                        technical_score=0.0,
                        rsi=0.0,
                        macd=0.0,
                        atr=0.0,
                        sentiment_score=0.0,
                        news_count=0,
                        top_headlines=["Analysis failed"],
                        whale_score=0.0,
                        net_whale_flow=0.0,
                        whale_transactions=0,
                        take_profit=0.0,
                        stop_loss=0.0,
                        risk_reward_ratio=0.0,
                        timestamp=datetime.now().isoformat(),
                        analysis_summary="Analysis failed - agents not responding after retry"
                    )
                    await ctx.send(sender, error_response)
            else:
                ctx.logger.error(f"❌ Retry failed: Still only {len(responses)} responses after retry")
                # Send error response instead of mock data
                error_response = SignalResponse(
                    symbol=msg.symbol,
                    signal="ERROR",
                    confidence=0.0,
                    current_price=0.0,
                    technical_score=0.0,
                    rsi=0.0,
                    macd=0.0,
                    atr=0.0,
                    sentiment_score=0.0,
                    news_count=0,
                    top_headlines=["Analysis failed"],
                    whale_score=0.0,
                    net_whale_flow=0.0,
                    whale_transactions=0,
                    take_profit=0.0,
                    stop_loss=0.0,
                    risk_reward_ratio=0.0,
                    timestamp=datetime.now().isoformat(),
                    analysis_summary="Analysis failed - insufficient agent responses after retry"
                )
                await ctx.send(sender, error_response)
        
    except Exception as e:
        ctx.logger.error(f"❌ Error in signal processing: {e}")
        import traceback
        traceback.print_exc()

# ========================================
# JSON RESPONSE HANDLERS - FIXED FORMAT
# ========================================

@signal_protocol.on_message(model=TechnicalResponse)
async def handle_technical_response(ctx: Context, sender: str, msg: TechnicalResponse):
    """Handle technical analysis JSON responses"""
    ctx.logger.info(f"🔥 TECHNICAL RESPONSE: Received for {msg.symbol}: Score={msg.technical_score:.3f}")
    ctx.logger.info(f"📄 Technical JSON: {msg.to_json()}")
    
    # Store the JSON-serializable response
    if msg.symbol not in agent_responses:
        agent_responses[msg.symbol] = {}
    agent_responses[msg.symbol]['technical'] = msg
    ctx.logger.info(f"✅ Technical JSON data stored for {msg.symbol}")

@signal_protocol.on_message(model=NewsResponse)
async def handle_news_response(ctx: Context, sender: str, msg: NewsResponse):
    """Handle news sentiment JSON responses"""
    ctx.logger.info(f"🔥 NEWS RESPONSE: Received for {msg.symbol}: Score={msg.sentiment_score:.3f}")
    ctx.logger.info(f"📄 News JSON: {msg.to_json()}")
    
    # Store the JSON-serializable response
    if msg.symbol not in agent_responses:
        agent_responses[msg.symbol] = {}
    agent_responses[msg.symbol]['news'] = msg
    ctx.logger.info(f"✅ News JSON data stored for {msg.symbol}")

@signal_protocol.on_message(model=WhaleResponse)
async def handle_whale_response(ctx: Context, sender: str, msg: WhaleResponse):
    """Handle whale activity JSON responses"""
    ctx.logger.info(f"🔥 WHALE RESPONSE: Received for {msg.symbol}: Score={msg.whale_score:.3f}")
    ctx.logger.info(f"📄 Whale JSON: {msg.to_json()}")
    
    # Store the JSON-serializable response
    if msg.symbol not in agent_responses:
        agent_responses[msg.symbol] = {}
    agent_responses[msg.symbol]['whale'] = msg
    ctx.logger.info(f"✅ Whale JSON data stored for {msg.symbol}")

@signal_protocol.on_message(model=RiskResponse)
async def handle_risk_response(ctx: Context, sender: str, msg: RiskResponse):
    """Handle risk management JSON responses"""
    ctx.logger.info(f"🔥 RISK RESPONSE: Received for {msg.symbol}: TP=${msg.take_profit:.2f}, SL=${msg.stop_loss:.2f}")
    ctx.logger.info(f"📄 Risk JSON: {msg.to_json()}")
    
    # Store the JSON-serializable response
    if msg.symbol not in agent_responses:
        agent_responses[msg.symbol] = {}
    agent_responses[msg.symbol]['risk'] = msg
    ctx.logger.info(f"✅ Risk JSON data stored for {msg.symbol}")

# Include the protocol
comprehensive_signal.include(signal_protocol)

if __name__ == "__main__":
    print("=" * 70)
    print("🎯 FIXED COMPREHENSIVE SIGNAL AGENT - JSON FORMAT")
    print("=" * 70)
    print(f"Agent address: {comprehensive_signal.address}")
    print(f"Port: 8002")
    print()
    print("🔧 JSON FORMAT FIXES:")
    print("  ✅ All messages use shared Pydantic models")
    print("  ✅ Automatic JSON serialization with .to_json() methods")
    print("  ✅ Unified protocol: CryptoTradingProtocol")
    print("  ✅ Enhanced logging for JSON data flow")
    print("  ✅ Proper response storage and processing")
    print()
    print("📊 Expected Agent Network:")
    print(f"  Technical: {TECHNICAL_AGENT_ADDRESS}")
    print(f"  News: {NEWS_AGENT_ADDRESS}")
    print(f"  Whale: {WHALE_AGENT_ADDRESS}")
    print(f"  Risk: {RISK_MANAGER_ADDRESS}")
    print()
    print("🚀 Starting Fixed Signal Agent...")
    print("=" * 70)
    comprehensive_signal.run()
