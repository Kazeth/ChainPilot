// src/pages/AIAnalyticsPage.tsx

import React, { useState } from "react";
import { Send, TrendingUp, BarChart, Newspaper } from "lucide-react";
import Button from "../components/ui/button";
import Card from "../components/ui/card";

// --- Main AI Analytics Page Component ---
export default function AIAnalyticsPage() {
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! I'm your ChainPilot AI assistant. How can I help you analyze the market today? You can ask me about top coins, market sentiment, or specific asset analysis.",
    },
    {
      sender: "user",
      text: "What are the top 3 high-potential coins right now?",
    },
    {
      sender: "ai",
      type: "structured",
      content: {
        intro:
          "Based on current on-chain data, market sentiment, and technical analysis, here are three coins showing high potential:",
        coins: [
          {
            name: "Bitcoin (BTC)",
            sentiment: "Positive",
            keyMetric: "Strong institutional inflow",
            icon: <TrendingUp size={20} />,
          },
          {
            name: "Ethereum (ETH)",
            sentiment: "Neutral",
            keyMetric: "Upcoming network upgrade",
            icon: <BarChart size={20} />,
          },
          {
            name: "Solana (SOL)",
            sentiment: "Very Positive",
            keyMetric: "High developer activity",
            icon: <Newspaper size={20} />,
          },
        ],
        suggestions: [
          "Tell me more about BTC",
          "Show technical analysis for SOL",
          "What is the market sentiment?",
        ],
      },
    },
  ]);
  const [inputValue, setInputValue] = useState("");

  const handleSendMessage = () => {
    if (inputValue.trim() === "") return;
    // In a real app, you'd send the message to the backend and get an AI response.
    // Here, we'll just add the user's message for demonstration.
    setMessages([...messages, { sender: "user", text: inputValue }]);
    setInputValue("");
  };

  return (
    <div
      className="flex flex-col h-[calc(100vh-5rem)] container mx-auto"
      style={{ fontFamily: "'Creati Display', sans-serif" }}
    >
      {/* Chat Messages Area */}
      <div className="flex-grow overflow-y-auto p-4 md:p-6 space-y-6">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex items-end gap-3 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            {/* AI Avatar */}
            {msg.sender === "ai" && (
              <div className="w-8 h-8 rounded-full bg-[#87efff] flex-shrink-0"></div>
            )}

            {/* Message Bubble */}
            <div
              className={`max-w-lg rounded-2xl p-4 ${msg.sender === "user" ? "bg-zinc-700 text-white rounded-br-none" : "bg-zinc-800 text-zinc-300 rounded-bl-none"}`}
            >
              {msg.type === "structured" ? (
                <div className="space-y-4">
                  <p>{msg.content.intro}</p>
                  <div className="space-y-3">
                    {msg.content.coins.map((coin) => (
                      <Card
                        key={coin.name}
                        className="flex items-center gap-4 !p-3"
                      >
                        <div className="text-[#87efff]">{coin.icon}</div>
                        <div>
                          <p className="font-semibold text-white">
                            {coin.name}
                          </p>
                          <p className="text-sm">
                            Sentiment:{" "}
                            <span className="font-medium text-white">
                              {coin.sentiment}
                            </span>
                          </p>
                          <p className="text-sm">{coin.keyMetric}</p>
                        </div>
                      </Card>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-2 pt-2">
                    {msg.content.suggestions.map((suggestion) => (
                      <Button
                        key={suggestion}
                        className="text-xs !px-3 !py-1.5 border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white hover:border-zinc-500"
                      >
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                </div>
              ) : (
                <p>{msg.text}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Chat Input Area */}
      <div className="p-4 md:p-6 border-t border-zinc-800 bg-zinc-900">
        <div className="relative">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Ask about a coin or market trend..."
            className="w-full bg-zinc-800 border-2 border-zinc-700 text-white rounded-xl py-3 pl-4 pr-12 focus:outline-none focus:border-[#87efff] transition-colors"
          />
          <button
            onClick={handleSendMessage}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-[#87efff] transition-colors"
          >
            <Send size={22} />
          </button>
        </div>
      </div>
    </div>
  );
}
