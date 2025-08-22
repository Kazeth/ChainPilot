import React, { useEffect, useRef, useState, useMemo } from "react";
import {
  createChart,
  IChartApi,
  CandlestickSeries,
  ISeriesApi,
} from "lightweight-charts";
import { motion, AnimatePresence } from "framer-motion";

// Import UI components
import Button from "../components/ui/button";
import Card from "../components/ui/card";

// --- Mock Data (for Order Book and Trade History) ---
const mockOrderBook = {
  bids: [
    { price: "60,500.10", size: "0.75", total: "0.75" },
    { price: "60,499.50", size: "1.20", total: "1.95" },
    { price: "60,498.00", size: "0.50", total: "2.45" },
  ],
  asks: [
    { price: "60,501.80", size: "0.80", total: "0.80" },
    { price: "60,502.30", size: "1.50", total: "2.30" },
    { price: "60,503.90", size: "0.60", total: "2.90" },
  ],
};

const mockTradeHistory = [
  { price: "60,501.80", size: "0.15", time: "10:30:05" },
  { price: "60,501.80", size: "0.05", time: "10:30:02" },
  { price: "60,500.10", size: "0.20", time: "10:29:59" },
];

// --- Interfaces ---
interface Coin {
  id: string;
  name: string;
  symbol: string;
}

interface MarketCoin {
  id: string;
  name: string;
  symbol: string;
  image: string;
  current_price: number;
  price_change_percentage_24h: number;
  price_change_percentage_7d_in_currency?: number;
  price_change_percentage_30d_in_currency?: number;
  price_change_percentage_1y_in_currency?: number;
}

// --- NEW: Interface for Chat Messages ---
interface ChatMessage {
  id: number;
  text: string;
  sender: "user" | "bot";
}

// --- Analytics-style friendly wrapper ---
const wrapAnalyticsResponse = (response: string) => {
  return `📊 Trading Analytics AI:\n${response}\n\nIf you need more details or want to analyze another asset, just ask!`;
};

// --- API Service for Trading Assistant ---
const TRADING_API_URL = "http://localhost:8082";

const tradingApiService = {
  async sendMessage(message: string, sessionId: string) {
    try {
      // Add fallback responses in case the API is not available
      const fallbackResponses = [
        "Based on current market trends, this asset shows potential for growth.",
        "I notice some volatility in this market. Consider diversifying your portfolio.",
        "Technical indicators suggest a bullish pattern forming.",
        "Looking at the chart, there appears to be support at the current price level.",
        "This asset has shown resilience during recent market fluctuations."
      ];

      try {
        const response = await fetch(`${TRADING_API_URL}/ask`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: message,
            session_id: sessionId
          })
        });
        
        if (!response.ok) {
          throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        return data.answer || "I'm analyzing the market data for you. What specific insights are you looking for?";
      } catch (error) {
        console.error("API Error:", error);
        // Use a fallback response if the API is not available
        const randomIndex = Math.floor(Math.random() * fallbackResponses.length);
        return fallbackResponses[randomIndex];
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      console.error(`Failed to get AI response: ${errorMessage}`);
      return "I'm experiencing some technical difficulties. Please try again later.";
    }
  }
};

// --- NEW: Interface for Trading Assistant Modal ---
interface TradingAssistantModalProps {
  chatMessages: ChatMessage[];
  userInput: string;
  setUserInput: (input: string) => void;
  handleChatSubmit: (e: React.FormEvent) => void;
  onClose: () => void;
}

// --- Trading Assistant Modal Component ---
const TradingAssistantModal: React.FC<TradingAssistantModalProps> = ({
  chatMessages,
  userInput,
  setUserInput,
  handleChatSubmit,
  onClose
}) => {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      onClick={onClose}
    >
      <motion.div
        className="relative w-full max-w-5xl h-[85vh] bg-zinc-800 rounded-lg overflow-hidden shadow-2xl"
        initial={{ scale: 0.8, y: 50 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.8, y: 50, opacity: 0 }}
        transition={{ 
          type: "spring", 
          damping: 20, 
          stiffness: 300,
          duration: 0.4
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <motion.div 
          className="flex items-center justify-between p-4 border-b border-zinc-700"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="3" y1="9" x2="21" y2="9"></line>
                <line x1="9" y1="21" x2="9" y2="9"></line>
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Trading Assistant</h3>
              <p className="text-xs text-zinc-400">Powered by ChainPilot AI</p>
            </div>
          </div>
          <motion.button
            onClick={onClose}
            className="p-2 transition-colors rounded-full hover:bg-zinc-700"
            title="Close"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-400 hover:text-white">
              <path d="M18 6L6 18"></path>
              <path d="M6 6l12 12"></path>
            </svg>
          </motion.button>
        </motion.div>
        
        <div className="h-[calc(85vh-140px)] overflow-y-auto p-6 space-y-5">
          {chatMessages.map((msg, index) => (
            <motion.div
              key={msg.id}
              className={`flex items-end ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ 
                duration: 0.4,
                delay: 0.1 + (index % 3) * 0.05,
                type: "spring",
                damping: 25
              }}
            >
              {msg.sender === "bot" && (
                <motion.div 
                  className="flex items-center justify-center flex-shrink-0 w-10 h-10 mr-3 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500"
                  whileHover={{ scale: 1.1 }}
                  transition={{ duration: 0.2 }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="3" y1="9" x2="21" y2="9"></line>
                    <line x1="9" y1="21" x2="9" y2="9"></line>
                  </svg>
                </motion.div>
              )}
              
              <motion.div
                className={`max-w-[75%] rounded-2xl px-5 py-3 shadow-lg ${
                  msg.sender === "user" 
                    ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-br-md" 
                    : "bg-zinc-700 text-zinc-100 rounded-bl-md border border-zinc-600/50"
                }`}
                whileHover={{ scale: 1.01 }}
                transition={{ duration: 0.2 }}
              >
                <p className="text-base whitespace-pre-wrap">{msg.text}</p>
              </motion.div>

              {msg.sender === "user" && (
                <motion.div 
                  className="flex items-center justify-center flex-shrink-0 w-10 h-10 ml-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500"
                  whileHover={{ scale: 1.1 }}
                  transition={{ duration: 0.2 }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
        
        <motion.div 
          className="absolute bottom-0 left-0 right-0 p-5 border-t border-zinc-700 bg-zinc-800"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <form onSubmit={handleChatSubmit} className="flex gap-3">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Ask about trading, analysis, or strategies..."
              className="flex-1 p-3 text-base text-white border rounded-md bg-zinc-700 border-zinc-600 focus:outline-none focus:ring-1 focus:ring-blue-500"
              autoComplete="off"
            />
            <motion.button
              type="submit"
              className="px-6 text-base font-semibold text-white transition-colors rounded-md bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:opacity-50 disabled:hover:from-blue-500 disabled:hover:to-cyan-500"
              disabled={!userInput.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Send
            </motion.button>
          </form>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

// --- Timeframe Options ---
const chartTimeframeOptions = [
  { label: "24h", days: "1" },
  { label: "7d", days: "7" },
  { label: "1m", days: "30" },
  { label: "1y", days: "365" },
];

const marketTimeframeOptions = [
  { label: "24h", key: "24h" },
  { label: "7d", key: "7d" },
  { label: "30d", key: "30d" },
  { label: "1y", key: "1y" },
];

// --- Main Trading Page Component ---
export default function TradingPage() {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const chartDataRef = useRef([]);

  const [selectedCoin, setSelectedCoin] = useState("bitcoin");
  const [tradeType, setTradeType] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [searchTerm, setSearchTerm] = useState("");
  const [coins, setCoins] = useState<Coin[]>([]);
  const [isLoadingCoins, setIsLoadingCoins] = useState(false);
  const [isLoadingChart, setIsLoadingChart] = useState(false);

  const [chartTimeframe, setChartTimeframe] = useState("30");
  const [marketTimeframe, setMarketTimeframe] = useState("24h");

  const [marketData, setMarketData] = useState<MarketCoin[]>([]);
  const [isLoadingMarketData, setIsLoadingMarketData] = useState(false);
  const [marketView, setMarketView] = useState<"gainers" | "losers">("gainers");

  // --- NEW: State for Chatbot ---
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      text: "Hello! I'm your Trading Analytics AI assistant. I can help you with trading analysis, market insights, and strategies. How can I assist you today?",
      sender: "bot",
    },
  ]);
  const [userInput, setUserInput] = useState("");
  const [isAssistantFullScreen, setIsAssistantFullScreen] = useState(false); // New state for full-screen mode
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [chatSessionId, setChatSessionId] = useState<string>("");

  // Generate session ID on mount
  useEffect(() => {
    setChatSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  // Fetch initial list of coins for search
  useEffect(() => {
    const fetchCoins = async () => {
      setIsLoadingCoins(true);
      try {
        const res = await fetch("https://api.coingecko.com/api/v3/coins/list");
        const data = await res.json();
        setCoins(data);
      } catch (err) {
        console.error("Error fetching coin list:", err);
      } finally {
        setIsLoadingCoins(false);
      }
    };
    fetchCoins();
  }, []);

  // Fetch market data for Top Gainers/Losers
  useEffect(() => {
    const fetchMarketData = async () => {
      setIsLoadingMarketData(true);
      try {
        const res = await fetch(
          "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=24h,7d,30d,1y"
        );
        const data = await res.json();
        setMarketData(data);
      } catch (err) {
        console.error("Error fetching market data:", err);
      } finally {
        setIsLoadingMarketData(false);
      }
    };
    fetchMarketData();
  }, []);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;
    chartRef.current = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 500,
      layout: { background: { color: "#18181b" }, textColor: "#d4d4d8" },
      grid: {
        vertLines: { color: "#27272a" },
        horzLines: { color: "#27272a" },
      },
    });
    candleSeriesRef.current = chartRef.current.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderUpColor: "#22c55e",
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    // --- UPDATED: Resize handler now also recalculates zoom limit ---
    const handleResize = () => {
      const chart = chartRef.current;
      const container = chartContainerRef.current;
      if (!chart || !container) return;

      const newWidth = container.clientWidth;
      chart.applyOptions({ width: newWidth });

      // If we have data, recalculate minBarSpacing to constrain zoom
      if (chartDataRef.current.length > 0) {
        const minBarSpacing = newWidth / (chartDataRef.current.length * 1.1); // Add 10% buffer
        chart.timeScale().applyOptions({
          minBarSpacing: Math.max(0.5, minBarSpacing), // Prevent it from being too small
        });
      }
    };

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chartRef.current?.remove();
    };
  }, []);

  // Fetch chart data when selectedCoin OR chartTimeframe changes
  useEffect(() => {
    const fetchData = async () => {
      if (!candleSeriesRef.current || !chartContainerRef.current) return;
      setIsLoadingChart(true);
      try {
        const res = await fetch(
          `https://api.coingecko.com/api/v3/coins/${selectedCoin}/ohlc?vs_currency=usd&days=${chartTimeframe}`
        );
        const data = await res.json();
        const formattedData = data.map(
          (d: [number, number, number, number, number]) => ({
            time: Math.floor(d[0] / 1000),
            open: d[1],
            high: d[2],
            low: d[3],
            close: d[4],
          })
        );

        // --- NEW: Update ref with new data ---
        chartDataRef.current = formattedData;

        candleSeriesRef.current.setData(formattedData);

        // --- NEW: Calculate and apply zoom constraint ---
        if (formattedData.length > 0) {
          const chartWidth = chartContainerRef.current.clientWidth;
          // Calculate the minimum bar spacing to fit all data points within the view
          const minBarSpacing = chartWidth / (formattedData.length * 1.1); // Add a small 10% buffer for padding
          chartRef.current?.timeScale().applyOptions({
            // Use Math.max to ensure bar spacing is not less than the library's default minimum (0.5)
            minBarSpacing: Math.max(0.5, minBarSpacing),
          });
        }

        chartRef.current?.timeScale().fitContent();
      } catch (err) {
        console.error("Error fetching OHLC data:", err);
      } finally {
        setIsLoadingChart(false);
      }
    };
    fetchData();
  }, [selectedCoin, chartTimeframe]);

  // Filter coins for the search bar
  const filteredCoins = useMemo(() => {
    return coins.filter(
      (coin) =>
        coin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        coin.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm, coins]);

  const getSortKey = (timeframe: string) => {
    if (timeframe === "24h") return "price_change_percentage_24h";
    return `price_change_percentage_${timeframe}_in_currency`;
  };

  const topGainers = useMemo(() => {
    const sortKey = getSortKey(marketTimeframe);
    return [...marketData]
      .filter((coin) => coin[sortKey as keyof MarketCoin] != null)
      .sort(
        (a, b) =>
          (b[sortKey as keyof MarketCoin] as number) -
          (a[sortKey as keyof MarketCoin] as number)
      )
      .slice(0, 10);
  }, [marketData, marketTimeframe]);

  const topLosers = useMemo(() => {
    const sortKey = getSortKey(marketTimeframe);
    return [...marketData]
      .filter((coin) => coin[sortKey as keyof MarketCoin] != null)
      .sort(
        (a, b) =>
          (a[sortKey as keyof MarketCoin] as number) -
          (b[sortKey as keyof MarketCoin] as number)
      )
      .slice(0, 10);
  }, [marketData, marketTimeframe]);

  const coinsToDisplay = marketView === "gainers" ? topGainers : topLosers;

  // --- NEW: Function to handle chatbot submission ---
  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const newUserMessage: ChatMessage = {
      id: Date.now(),
      text: userInput,
      sender: "user",
    };
    setChatMessages((prev) => [...prev, newUserMessage]);
    setUserInput("");
    setIsChatLoading(true);
    setChatError(null);
    
    try {
      // Get response from the trading API service
      const response = await tradingApiService.sendMessage(userInput, chatSessionId);
      
      // Format the response in an analytics-friendly way
      const friendlyResponse = wrapAnalyticsResponse(response);
      
      const botResponse: ChatMessage = {
        id: Date.now() + 1,
        text: friendlyResponse,
        sender: "bot",
      };
      
      setChatMessages((prev) => [...prev, botResponse]);
    } catch (err) {
      console.error("Chat error:", err);
      setChatError("There was an error processing your request");
      
      const errorResponse: ChatMessage = {
        id: Date.now() + 1,
        text: "I'm currently experiencing some technical difficulties. Please try again later or try a different query.",
        sender: "bot",
      };
      
      setChatMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <div
      className="container p-4 mx-auto"
      style={{ fontFamily: "'Creati Display', sans-serif" }}
    >
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        {/* Main Content: Chart and Gainers/Losers */}
        <div className="lg:col-span-9">
          <Card className="!p-4">
            <div className="flex flex-col gap-4 mb-4">
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search for a coin..."
                  className="w-full px-4 py-2 text-white border rounded-lg bg-zinc-700 border-zinc-600 focus:outline-none"
                />
                {isLoadingCoins && (
                  <div className="absolute right-2 top-2">...</div>
                )}
                {searchTerm && !isLoadingCoins && filteredCoins.length > 0 && (
                  <ul className="absolute z-10 w-full mt-1 overflow-y-auto border rounded-lg bg-zinc-800 border-zinc-700 max-h-40">
                    {filteredCoins.slice(0, 100).map((coin) => (
                      <li
                        key={coin.id}
                        onClick={() => {
                          setSelectedCoin(coin.id);
                          setSearchTerm("");
                        }}
                        className="px-4 py-2 cursor-pointer hover:bg-zinc-700"
                      >
                        {coin.name} ({coin.symbol.toUpperCase()})
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <h2 className="text-xl font-bold text-white">
                  {coins.find((c) => c.id === selectedCoin)?.name ||
                    "Loading..."}{" "}
                  Chart (USD)
                </h2>
                <div className="flex items-center gap-1 p-1 rounded-md bg-zinc-800">
                  {chartTimeframeOptions.map((tf) => (
                    <button
                      key={tf.label}
                      onClick={() => setChartTimeframe(tf.days)}
                      className={`px-3 py-1 text-xs font-semibold rounded ${
                        chartTimeframe === tf.days
                          ? "bg-zinc-600 text-white"
                          : "text-zinc-400 hover:bg-zinc-700"
                      }`}
                    >
                      {tf.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div
              ref={chartContainerRef}
              className={`w-full h-[500px] ${isLoadingChart ? "flex items-center justify-center" : ""}`}
            >
              {isLoadingChart && <span>Loading chart...</span>}
            </div>
          </Card>

          {/* Top Gainers & Losers Section */}
          <Card className="!p-0 mt-4">
            <div className="flex flex-col gap-2 p-3 border-b sm:flex-row sm:items-center sm:justify-between border-zinc-700">
              <div className="flex">
                <button
                  onClick={() => setMarketView("gainers")}
                  className={`flex-1 p-1 px-3 font-semibold transition-colors duration-200 ${
                    marketView === "gainers"
                      ? "text-green-500"
                      : "text-zinc-400 hover:text-white"
                  }`}
                >
                  Top Gainers
                </button>
                <button
                  onClick={() => setMarketView("losers")}
                  className={`flex-1 p-1 px-3 font-semibold transition-colors duration-200 ${
                    marketView === "losers"
                      ? "text-red-500"
                      : "text-zinc-400 hover:text-white"
                  }`}
                >
                  Top Losers
                </button>
              </div>
              <div className="flex items-center gap-1 p-1 rounded-md bg-zinc-800">
                {marketTimeframeOptions.map((tf) => (
                  <button
                    key={tf.label}
                    onClick={() => setMarketTimeframe(tf.key)}
                    className={`px-3 py-1 text-xs font-semibold rounded ${
                      marketTimeframe === tf.key
                        ? "bg-zinc-600 text-white"
                        : "text-zinc-400 hover:bg-zinc-700"
                    }`}
                  >
                    {tf.label}
                  </button>
                ))}
              </div>
            </div>
            {isLoadingMarketData ? (
              <div className="p-4 text-center text-zinc-400">
                Loading market data...
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs uppercase text-zinc-400">
                    <tr>
                      <th scope="col" className="px-4 py-2">
                        Name
                      </th>
                      <th scope="col" className="px-4 py-2 text-right">
                        Price
                      </th>
                      <th scope="col" className="px-4 py-2 text-right">
                        Change ({marketTimeframe})
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {coinsToDisplay.map((coin) => {
                      const sortKey = getSortKey(
                        marketTimeframe
                      ) as keyof MarketCoin;
                      const change = (coin[sortKey] as number) ?? 0;
                      return (
                        <tr
                          key={coin.id}
                          className="border-t cursor-pointer border-zinc-800 hover:bg-zinc-800"
                          onClick={() => setSelectedCoin(coin.id)}
                        >
                          <td className="flex items-center gap-2 px-4 py-2">
                            <img
                              src={coin.image}
                              alt={coin.name}
                              className="w-6 h-6"
                            />
                            <div>
                              <span className="font-medium text-white">
                                {coin.name}
                              </span>
                              <span className="text-zinc-400 ml-1.5">
                                {coin.symbol.toUpperCase()}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-2 text-right text-white">
                            ${coin.current_price.toLocaleString()}
                          </td>
                          <td
                            className={`px-4 py-2 text-right font-medium ${change >= 0 ? "text-green-500" : "text-red-500"}`}
                          >
                            {change.toFixed(2)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        {/* Sidebar: Buy/Sell Widget and Order Book */}
        <div className="space-y-4 lg:col-span-3">
          <Card className="!p-4">
            <div className="grid grid-cols-2 gap-2 mb-4">
              <Button
                onClick={() => setTradeType("buy")}
                className={`w-full ${tradeType === "buy" ? "bg-green-500 border-green-500 text-white" : "border-zinc-600 text-zinc-300"}`}
              >
                Buy
              </Button>
              <Button
                onClick={() => setTradeType("sell")}
                className={`w-full ${tradeType === "sell" ? "bg-red-500 border-red-500 text-white" : "border-zinc-600 text-zinc-300"}`}
              >
                Sell
              </Button>
            </div>
            <div className="flex mb-4 text-xs">
              <button
                onClick={() => setOrderType("market")}
                className={`flex-1 py-1 ${orderType === "market" ? "text-white" : "text-zinc-400"}`}
              >
                Market
              </button>
              <button
                onClick={() => setOrderType("limit")}
                className={`flex-1 py-1 ${orderType === "limit" ? "text-white" : "text-zinc-400"}`}
              >
                Limit
              </button>
            </div>
            <div className="space-y-3">
              {orderType === "limit" && (
                <input
                  type="number"
                  placeholder="Price (USD)"
                  className="w-full p-2 text-white border rounded-md bg-zinc-700 border-zinc-600"
                />
              )}
              <input
                type="number"
                placeholder={`Amount (${coins.find((c) => c.id === selectedCoin)?.symbol.toUpperCase() || ""})`}
                className="w-full p-2 text-white border rounded-md bg-zinc-700 border-zinc-600"
              />
              <Button
                className={`w-full ${tradeType === "buy" ? "bg-green-500 border-green-500" : "bg-red-500 border-red-500"} text-white`}
              >
                {tradeType === "buy" ? "Buy" : "Sell"}{" "}
                {coins
                  .find((c) => c.id === selectedCoin)
                  ?.symbol.toUpperCase() || "..."}
              </Button>
            </div>
          </Card>

          <Card className="!p-0">
            <h3 className="p-3 text-lg font-semibold text-white border-b border-zinc-700">
              Order Book
            </h3>
            <table className="w-full text-xs text-center">
              <thead>
                <tr className="text-zinc-400">
                  <th className="p-2 font-normal">Price (USD)</th>
                  <th className="p-2 font-normal">Size</th>
                  <th className="p-2 font-normal">Total</th>
                </tr>
              </thead>
              <tbody>
                {mockOrderBook.asks.map((ask) => (
                  <tr key={ask.price}>
                    <td className="p-1 text-red-400">{ask.price}</td>
                    <td className="text-white">{ask.size}</td>
                    <td className="text-white">{ask.total}</td>
                  </tr>
                ))}
                <tr>
                  <td
                    colSpan={3}
                    className="p-2 text-lg font-bold text-center text-white"
                  >
                    60,501.15
                  </td>
                </tr>
                {mockOrderBook.bids.map((bid) => (
                  <tr key={bid.price}>
                    <td className="p-1 text-green-400">{bid.price}</td>
                    <td className="text-white">{bid.size}</td>
                    <td className="text-white">{bid.total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <Card className="!p-0">
            <h3 className="p-3 text-lg font-semibold text-white border-b border-zinc-700">
              Trade History
            </h3>
            <table className="w-full text-xs text-center">
              <thead>
                <tr className="text-zinc-400">
                  <th className="p-2 font-normal">Price (USD)</th>
                  <th className="p-2 font-normal">Size</th>
                  <th className="p-2 font-normal">Time</th>
                </tr>
              </thead>
              <tbody>
                {mockTradeHistory.map((trade, index) => (
                  <tr key={index}>
                    <td className="p-1 text-red-400">{trade.price}</td>
                    <td className="text-white">{trade.size}</td>
                    <td className="text-white">{trade.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* --- NEW SECTION: Trading Assistant --- */}
          {!isAssistantFullScreen && (
            <Card className="!p-0 flex flex-col h-96">
              <div className="flex items-center justify-between border-b border-zinc-700">
                <div className="flex items-center gap-2 p-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="3" y1="9" x2="21" y2="9"></line>
                      <line x1="9" y1="21" x2="9" y2="9"></line>
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-white">
                    Trading Assistant
                  </h3>
                </div>
                <motion.button 
                  onClick={() => setIsAssistantFullScreen(true)}
                  className="mr-3 p-1.5 rounded-md hover:bg-zinc-700 transition-colors"
                  title="Expand to full screen"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-400 hover:text-white">
                    <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
                  </svg>
                </motion.button>
              </div>
              <div
                ref={chatContainerRef}
                className="flex-1 p-3 space-y-4 overflow-y-auto"
              >
                {chatMessages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    className={`flex items-end ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {msg.sender === "bot" && (
                      <div className="flex items-center justify-center flex-shrink-0 w-6 h-6 mr-2 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                          <line x1="3" y1="9" x2="21" y2="9"></line>
                          <line x1="9" y1="21" x2="9" y2="9"></line>
                        </svg>
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-lg px-3 py-2 ${
                        msg.sender === "user" 
                          ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-br-md" 
                          : "bg-zinc-700 text-zinc-200 rounded-bl-md border border-zinc-600/50"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                    </div>
                    {msg.sender === "user" && (
                      <div className="flex items-center justify-center flex-shrink-0 w-6 h-6 ml-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                          <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                      </div>
                    )}
                  </motion.div>
                ))}
                {isChatLoading && (
                  <div className="flex items-center gap-2 pl-2 text-blue-400">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "0.2s" }}></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "0.4s" }}></div>
                  </div>
                )}
                {chatError && (
                  <div className="p-2 text-sm text-center text-red-400 rounded-md bg-red-400/10">
                    {chatError}
                  </div>
                )}
              </div>
              <div className="p-2 border-t border-zinc-700">
                <form onSubmit={handleChatSubmit} className="flex gap-2">
                  <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="Ask about trading..."
                    className="flex-1 p-2 text-sm text-white border rounded-md bg-zinc-700 border-zinc-600 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    autoComplete="off"
                    disabled={isChatLoading}
                  />
                  <motion.button
                    type="submit"
                    className="px-4 text-sm font-semibold text-white transition-colors rounded-md bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:opacity-50"
                    disabled={!userInput.trim() || isChatLoading}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Send
                  </motion.button>
                </form>
              </div>
            </Card>
          )}

          {/* Trading Assistant Full Screen Modal */}
          <AnimatePresence>
            {isAssistantFullScreen && (
              <TradingAssistantModal 
                chatMessages={chatMessages}
                userInput={userInput}
                setUserInput={setUserInput}
                handleChatSubmit={handleChatSubmit}
                onClose={() => setIsAssistantFullScreen(false)}
              />
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
