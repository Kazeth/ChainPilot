import React, { useEffect, useRef, useState, useMemo } from "react";
import {
  createChart,
  IChartApi,
  CandlestickSeries,
  ISeriesApi,
} from "lightweight-charts";
import { motion, AnimatePresence } from "framer-motion";
import { Principal } from "@dfinity/principal";

// Import UI components
import Button from "../components/ui/button";
import Card from "../components/ui/card";

// Import backend declarations
import { useAuthContext } from "@/context/AuthContext";
import { trade_backend } from "@/declarations/trade_backend";
import { wallet_backend } from "@/declarations/wallet_backend";
import { user_backend } from "@/declarations/user_backend";
import { signal_backend } from "@/declarations/signal_backend";
import { marketData_backend } from "@/declarations/marketData_backend";
import { transaction_backend } from "@/declarations/transaction_backend";

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

interface Ticker {
  exchange: string;
  pair: string;
  price: number;
  volume: number;
  bid: number | null;
  spread: number | null;
  trust_score: string | null;
  last_traded: string;
  trade_url: string | null;
}

// Backend Types (matching your Motoko definitions) - Fixed
interface BackendOrderType {
  Buy?: null;
  Sell?: null;
}

interface BackendTradeStatus {
  Pending?: null;
  Completed?: null;
  Cancelled?: null;
}

interface BackendTransactionType {
  Buy?: null;
  Sell?: null;
}

interface BackendTrade {
  tradeId: string;
  user: Principal;
  asset: BackendAsset;
  orderType: BackendOrderType;
  amount: number;
  price: number;
  status: BackendTradeStatus;
  timestamp: bigint;
}

interface BackendAsset {
  assetId: string;
  symbol: string;
  name: string;
  currentPrice?: number;
  marketCap?: number;
  volume24h?: number;
  network?: string;
}

interface BackendWallet {
  walletId: string;
  walletAddress: string;
  owner: Principal;
  blockchainNetwork: string;
  balance: number;
  connectedExchange: string;
}

interface BackendSignal {
  signalId: string;
  user: Principal;
  signalMessage: string;
  signalType: string;
  confidenceScore: number;
  generatedAt: bigint;
}

// --- Analytics-style friendly wrapper ---
const wrapAnalyticsResponse = (response: string) => {
  return `📊 Trading Analytics AI:\n${response}\n\nIf you need more details or want to analyze another asset, just ask!`;
};

// --- Updated API Service for Trading Assistant using Signal Backend ---
const tradingApiService = {
  async sendMessage(message: string, principal: Principal) {
    try {
      // Create a trading signal with AI-like response
      const confidenceScore = Math.random() * 100; // 0-100
      const signalType = message.toLowerCase().includes('buy') ? 'BUY_SIGNAL' : 
                        message.toLowerCase().includes('sell') ? 'SELL_SIGNAL' : 
                        'ANALYSIS';
      
      // Generate contextual response based on message content
      let response = "";
      if (message.toLowerCase().includes('bitcoin') || message.toLowerCase().includes('btc')) {
        response = "Bitcoin is showing strong support at current levels. Technical indicators suggest potential for continued upward momentum.";
      } else if (message.toLowerCase().includes('ethereum') || message.toLowerCase().includes('eth')) {
        response = "Ethereum's network activity remains robust. Consider the upcoming upgrade impacts on price action.";
      } else if (message.toLowerCase().includes('market') || message.toLowerCase().includes('trend')) {
        response = "Current market conditions show mixed signals. Volume analysis suggests consolidation before the next major move.";
      } else if (message.toLowerCase().includes('portfolio') || message.toLowerCase().includes('diversify')) {
        response = "Portfolio diversification is key in current market conditions. Consider balancing between growth and stable assets.";
      } else {
        response = "Based on current technical analysis, I recommend monitoring key support and resistance levels before making trading decisions.";
      }

      // Store the signal in the backend
      try {
        const signal = await signal_backend.createSignal(
          principal,
          response,
          signalType,
          confidenceScore,
          BigInt(Date.now() * 1000000) // Convert to nanoseconds
        );
        console.log("Signal created:", signal);
      } catch (signalError) {
        console.error("Failed to create signal:", signalError);
      }

      return response;
    } catch (error) {
      console.error("Trading API error:", error);
      return "I'm analyzing the market data for you. What specific insights are you looking for?";
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
  const chartDataRef = useRef<any[]>([]);

  const { isAuthenticated, principal, authChecked } = useAuthContext();

  const [selectedCoin, setSelectedCoin] = useState("bitcoin");
  const [tradeType, setTradeType] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [searchTerm, setSearchTerm] = useState("");
  const [coins, setCoins] = useState<Coin[]>([]);
  const [isLoadingCoins, setIsLoadingCoins] = useState(false);
  const [isLoadingChart, setIsLoadingChart] = useState(false);

  // NEW: Trading form states
  const [tradeAmount, setTradeAmount] = useState("");
  const [limitPrice, setLimitPrice] = useState("");
  const [isSubmittingTrade, setIsSubmittingTrade] = useState(false);
  const [tradeStatus, setTradeStatus] = useState("");

  // NEW: User wallet state
  const [userWallets, setUserWallets] = useState<BackendWallet[]>([]);
  const [userTrades, setUserTrades] = useState<BackendTrade[]>([]);
  const [loadingUserData, setLoadingUserData] = useState(false);

  const [chartTimeframe, setChartTimeframe] = useState("30");
  const [marketTimeframe, setMarketTimeframe] = useState("24h");

  const [marketData, setMarketData] = useState<MarketCoin[]>([]);
  const [isLoadingMarketData, setIsLoadingMarketData] = useState(false);
  const [marketView, setMarketView] = useState<"gainers" | "losers">("gainers");

  const [tickerData, setTickerData] = useState<Ticker[]>([]);
  const [isLoadingTickers, setIsLoadingTickers] = useState(false);
  const [tickerError, setTickerError] = useState<string | null>(null);
  const [selectedExchange, setSelectedExchange] = useState('all');

  // --- NEW: State for Chatbot ---
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      text: "Hello! I'm your Trading Analytics AI assistant. I can help you with trading analysis, market insights, and strategies. How can I assist you today?",
      sender: "bot",
    },
  ]);
  const [userInput, setUserInput] = useState("");
  const [isAssistantFullScreen, setIsAssistantFullScreen] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  // Load user data when authenticated
  useEffect(() => {
    const loadUserData = async () => {
      if (!isAuthenticated || !authChecked || !principal || principal.isAnonymous()) {
        return;
      }

      setLoadingUserData(true);
      try {
        // Load user wallets
        const wallets = await wallet_backend.getWalletsByPrincipal(principal);
        setUserWallets(wallets);

        // Load user trades
        const trades = await trade_backend.getTradesByPrincipal(principal);
        setUserTrades(trades);

        console.log("Loaded user data:", { wallets, trades });
      } catch (error) {
        console.error("Failed to load user data:", error);
      } finally {
        setLoadingUserData(false);
      }
    };

    loadUserData();
  }, [isAuthenticated, authChecked, principal]);

  // NEW: Handle trade submission - Fixed type issues
  const handleTradeSubmit = async () => {
    if (!isAuthenticated || !principal || principal.isAnonymous()) {
      setTradeStatus("Please log in to place trades");
      return;
    }

    if (!tradeAmount || Number(tradeAmount) <= 0) {
      setTradeStatus("Please enter a valid amount");
      return;
    }

    if (orderType === "limit" && (!limitPrice || Number(limitPrice) <= 0)) {
      setTradeStatus("Please enter a valid limit price");
      return;
    }

    setIsSubmittingTrade(true);
    setTradeStatus("Submitting trade...");

    try {
      // Create asset object (you might want to get this from your market data)
      const asset: BackendAsset = {
        assetId: selectedCoin,
        symbol: coins.find(c => c.id === selectedCoin)?.symbol.toUpperCase() || "BTC",
        name: coins.find(c => c.id === selectedCoin)?.name || "Bitcoin",
      };

      // Determine order type - Fixed to match interface
      const orderTypeBackend: BackendOrderType = tradeType === "buy" ? { Buy: null } : { Sell: null };

      // Use market price or limit price
      const price = orderType === "market" ? 50000 : Number(limitPrice); // You'd get real market price here

      // Create trade
      const newTrade = await trade_backend.createTrade(
        principal,
        asset,
        orderTypeBackend,
        Number(tradeAmount),
        price,
        { Pending: null } as BackendTradeStatus,
        BigInt(Date.now() * 1000000) // Convert to nanoseconds
      );

      // Create transaction record
      const userWallet = userWallets[0]; // Assuming first wallet
      if (userWallet) {
        const transactionType: BackendTransactionType = tradeType === "buy" ? { Buy: null } : { Sell: null };
        
        await transaction_backend.createTransaction(
          principal,
          userWallet.walletAddress,
          "exchange_address", // This would be the exchange address
          Number(tradeAmount),
          { Pending: null }, // Assuming similar status structure
          userWallet.blockchainNetwork,
          transactionType,
          BigInt(Date.now() * 1000000)
        );
      }

      console.log("Trade created:", newTrade);
      
      // Refresh user trades
      const updatedTrades = await trade_backend.getTradesByPrincipal(principal);
      setUserTrades(updatedTrades);

      setTradeStatus(`${tradeType.charAt(0).toUpperCase() + tradeType.slice(1)} order placed successfully!`);
      setTradeAmount("");
      setLimitPrice("");
      
    } catch (error) {
      console.error("Trade submission failed:", error);
      setTradeStatus("Failed to place trade: " + (error as Error).message);
    } finally {
      setIsSubmittingTrade(false);
    }
  };

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

    const handleResize = () => {
      const chart = chartRef.current;
      const container = chartContainerRef.current;
      if (!chart || !container) return;

      const newWidth = container.clientWidth;
      chart.applyOptions({ width: newWidth });

      if (chartDataRef.current.length > 0) {
        const minBarSpacing = newWidth / (chartDataRef.current.length * 1.1);
        chart.timeScale().applyOptions({
          minBarSpacing: Math.max(0.5, minBarSpacing),
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

        chartDataRef.current = formattedData;
        candleSeriesRef.current.setData(formattedData);

        if (formattedData.length > 0) {
          const chartWidth = chartContainerRef.current.clientWidth;
          const minBarSpacing = chartWidth / (formattedData.length * 1.1);
          chartRef.current?.timeScale().applyOptions({
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

  // New ticker data useEffect - Fixed ticker parameter
  useEffect(() => {
    const fetchAndSetTickerData = async () => {
      setIsLoadingTickers(true);
      setTickerError(null);
      
      try {
        const tickers = await fetchTickerData(selectedCoin, selectedExchange);
        setTickerData(tickers);
      } catch (error) {
        console.error('Failed to fetch ticker data:', error);
        setTickerData([]);
      } finally {
        setIsLoadingTickers(false);
      }
    };
    
    fetchAndSetTickerData();
    const interval = setInterval(fetchAndSetTickerData, 30000);
    return () => clearInterval(interval);
  }, [selectedCoin, selectedExchange]);

  const fetchTickerData = async (coinId: string, exchangeId: string): Promise<Ticker[]> => {
    try {
      let url = `https://api.coingecko.com/api/v3/coins/${coinId}/tickers`;
      
      if (exchangeId && exchangeId !== 'all') {
        url += `?exchange_ids=${exchangeId}`;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      const processedTickers = data.tickers
        .filter((ticker: any) => ticker.target === 'USD' || ticker.target === 'USDT' || ticker.target === 'USDC')
        .slice(0, 15)
        .map((ticker: any) => ({
          exchange: ticker.market.name,
          pair: ticker.base + '/' + ticker.target,
          price: ticker.last,
          volume: ticker.volume,
          bid: ticker.bid_ask_spread_percentage,
          spread: ticker.bid_ask_spread_percentage,
          trust_score: ticker.trust_score,
          last_traded: ticker.last_traded_at,
          trade_url: ticker.trade_url
        }));
      
      return processedTickers;
    } catch (error) {
      console.error('Error fetching ticker data:', error);
      throw error;
    }
  };

  const getRecentTradesFromTickers = (tickers: Ticker[]) => {
    return tickers.slice(0, 10).map((ticker, index) => {
      const basePrice = ticker.price;
      const variation = (Math.random() - 0.5) * 0.002;
      const tradePrice = basePrice * (1 + variation);
      
      return {
        price: tradePrice.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }),
        size: (Math.random() * 2 + 0.01).toFixed(4),
        time: new Date(Date.now() - (index * 30000)).toLocaleTimeString(),
        side: Math.random() > 0.5 ? 'buy' : 'sell',
        exchange: ticker.exchange
      };
    });
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
      if (!isAuthenticated || !principal || principal.isAnonymous()) {
        throw new Error("Please log in to use the trading assistant");
      }

      // Get response from the trading API service using backend
      const response = await tradingApiService.sendMessage(userInput, principal);
      
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
                  {coins.find((c) => c.id === selectedCoin)?.name || "Loading..."} Chart (USD)
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
                      const sortKey = getSortKey(marketTimeframe) as keyof MarketCoin;
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
                            className={`px-4 py-2 text-right font-medium ${
                              change >= 0 ? "text-green-500" : "text-red-500"
                            }`}
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

        {/* Sidebar: Buy/Sell Widget, Market Data, Recent Market Activity, Trading Assistant */}
        <div className="space-y-4 lg:col-span-3">
          {/* Updated Buy/Sell Widget with Backend Integration */}
          <Card className="!p-4">
            <div className="grid grid-cols-2 gap-2 mb-4">
              <Button
                onClick={() => setTradeType("buy")}
                className={`w-full ${
                  tradeType === "buy" ? "bg-green-500 border-green-500 text-white" : "border-zinc-600 text-zinc-300"
                }`}
              >
                Buy
              </Button>
              <Button
                onClick={() => setTradeType("sell")}
                className={`w-full ${
                  tradeType === "sell" ? "bg-red-500 border-red-500 text-white" : "border-zinc-600 text-zinc-300"
                }`}
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
                  value={limitPrice}
                  onChange={(e) => setLimitPrice(e.target.value)}
                  className="w-full p-2 text-white border rounded-md bg-zinc-700 border-zinc-600"
                />
              )}
              <input
                type="number"
                placeholder={`Amount (${coins.find((c) => c.id === selectedCoin)?.symbol.toUpperCase() || ""})`}
                value={tradeAmount}
                onChange={(e) => setTradeAmount(e.target.value)}
                className="w-full p-2 text-white border rounded-md bg-zinc-700 border-zinc-600"
              />
              
              {/* Show wallet balance if user has wallet */}
              {userWallets.length > 0 && (
                <div className="text-xs text-zinc-400">
                  Available Balance: ${userWallets[0].balance.toLocaleString()}
                </div>
              )}
              
              {/* Authentication check */}
              {!isAuthenticated ? (
                <div className="p-2 text-xs text-center text-yellow-400 bg-yellow-400/10 rounded">
                  Please log in to place trades
                </div>
              ) : userWallets.length === 0 ? (
                <div className="p-2 text-xs text-center text-blue-400 bg-blue-400/10 rounded">
                  Please create a wallet first
                </div>
              ) : (
                <Button
                  onClick={handleTradeSubmit}
                  disabled={isSubmittingTrade || !tradeAmount}
                  className={`w-full ${
                    tradeType === "buy" ? "bg-green-500 border-green-500" : "bg-red-500 border-red-500"
                  } text-white`}
                >
                  {isSubmittingTrade 
                    ? "Submitting..." 
                    : `${tradeType === "buy" ? "Buy" : "Sell"} ${coins.find((c) => c.id === selectedCoin)?.symbol.toUpperCase() || "..."}`
                  }
                </Button>
              )}
            </div>
            
            {/* Trade status */}
            {tradeStatus && (
              <div className={`mt-2 p-2 text-xs rounded ${
                tradeStatus.includes("successfully") 
                  ? "text-green-400 bg-green-400/10" 
                  : tradeStatus.includes("Failed") || tradeStatus.includes("error")
                  ? "text-red-400 bg-red-400/10"
                  : "text-blue-400 bg-blue-400/10"
              }`}>
                {tradeStatus}
              </div>
            )}
          </Card>

          {/* User Trades History */}
          {userTrades.length > 0 && (
            <Card className="!p-0">
              <div className="p-3 border-b border-zinc-700">
                <h3 className="text-lg font-semibold text-white">Your Recent Trades</h3>
              </div>
              <div className="max-h-64 overflow-y-auto">
                <table className="w-full text-xs text-left">
                  <thead className="sticky top-0 bg-zinc-900">
                    <tr className="text-zinc-400">
                      <th className="p-2 font-normal">Asset</th>
                      <th className="p-2 font-normal text-right">Amount</th>
                      <th className="p-2 font-normal text-right">Price</th>
                      <th className="p-2 font-normal text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {userTrades.slice(0, 5).map((trade) => (
                      <tr key={trade.tradeId} className="border-t border-zinc-800">
                        <td className="p-2">
                          <div>
                            <div className="font-medium text-white text-xs">
                              {trade.asset.symbol}
                            </div>
                            <div className={`text-xs ${trade.orderType.Buy !== undefined ? "text-green-400" : "text-red-400"}`}>
                              {trade.orderType.Buy !== undefined ? "Buy" : "Sell"}
                            </div>
                          </div>
                        </td>
                        <td className="p-2 text-right text-white">
                          {trade.amount.toFixed(4)}
                        </td>
                        <td className="p-2 text-right text-white">
                          ${trade.price.toLocaleString()}
                        </td>
                        <td className="p-2 text-right">
                          <span className={`px-1 py-0.5 rounded text-xs ${
                            trade.status.Completed !== undefined
                              ? "text-green-400 bg-green-400/10" 
                              : trade.status.Pending !== undefined
                              ? "text-yellow-400 bg-yellow-400/10"
                              : "text-red-400 bg-red-400/10"
                          }`}>
                            {trade.status.Completed !== undefined ? "Done" : 
                             trade.status.Pending !== undefined ? "Pending" : "Cancelled"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          <Card className="!p-0">
            <div className="flex items-center justify-between p-3 border-b border-zinc-700">
              <h3 className="text-lg font-semibold text-white">Market Data</h3>
              <div className="flex items-center gap-2">
                {isLoadingTickers && (
                  <div className="w-4 h-4 border-2 border-blue-500 rounded-full animate-spin border-t-transparent"></div>
                )}
                <select
                  value={selectedExchange}
                  onChange={(e) => setSelectedExchange(e.target.value)}
                  className="px-2 py-1 text-xs rounded bg-zinc-700 border-zinc-600 text-white"
                >
                  <option value="all">All Exchanges</option>
                  <option value="binance">Binance</option>
                  <option value="coinbase-exchange">Coinbase</option>
                  <option value="kraken">Kraken</option>
                  <option value="kucoin">KuCoin</option>
                </select>
              </div>
            </div>

            {tickerError && (
              <div className="p-2 text-xs text-center text-red-400 bg-red-400/10">
                {tickerError}
              </div>
            )}

            <div className="max-h-96 overflow-y-auto">
              <table className="w-full text-xs text-left">
                <thead className="sticky top-0 bg-zinc-900">
                  <tr className="text-zinc-400">
                    <th className="p-2 font-normal">Exchange</th>
                    <th className="p-2 font-normal text-right">Price</th>
                    <th className="p-2 font-normal text-right">Volume</th>
                    <th className="p-2 font-normal text-right">Spread %</th>
                  </tr>
                </thead>
                <tbody>
                  {tickerData.map((ticker, index) => (
                    <tr
                      key={`${ticker.exchange}-${index}`}
                      className="border-t border-zinc-800 hover:bg-zinc-800/50 cursor-pointer"
                      onClick={() => ticker.trade_url && window.open(ticker.trade_url, '_blank')}
                    >
                      <td className="p-2">
                        <div>
                          <div className="font-medium text-white text-xs">
                            {ticker.exchange}
                          </div>
                          <div className="text-zinc-400 text-xs">
                            {ticker.pair}
                          </div>
                        </div>
                      </td>
                      <td className="p-2 text-right text-white font-medium">
                        ${ticker.price.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="p-2 text-right text-white">
                        ${ticker.volume.toLocaleString('en-US', {
                          maximumFractionDigits: 0,
                        })}
                      </td>
                      <td className="p-2 text-right">
                        <span
                          className={`${
                            ticker.spread && ticker.spread > 0.1
                              ? 'text-red-400'
                              : ticker.spread && ticker.spread > 0.05
                              ? 'text-yellow-400'
                              : 'text-green-400'
                          }`}
                        >
                          {ticker.spread?.toFixed(3) || 'N/A'}%
                        </span>
                      </td>
                    </tr>
                  ))}
                  {tickerData.length === 0 && !isLoadingTickers && (
                    <tr>
                      <td colSpan={4} className="p-4 text-center text-zinc-400">
                        No ticker data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>

          <Card className="!p-0 mt-4">
            <h3 className="p-3 text-lg font-semibold text-white border-b border-zinc-700">
              Recent Market Activity
            </h3>
            <table className="w-full text-xs text-center">
              <thead>
                <tr className="text-zinc-400">
                  <th className="p-2 font-normal">Price (USD)</th>
                  <th className="p-2 font-normal">Size</th>
                  <th className="p-2 font-normal">Exchange</th>
                </tr>
              </thead>
              <tbody>
                {getRecentTradesFromTickers(tickerData).map((trade, index) => (
                  <tr key={index}>
                    <td className={`p-1 ${trade.side === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                      {trade.price}
                    </td>
                    <td className="text-white">{trade.size}</td>
                    <td className="text-zinc-300 text-xs">{trade.exchange}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {!isAssistantFullScreen && (
            <Card className="!p-0 flex flex-col h-96">
              <div className="flex items-center justify-between border-b border-zinc-700">
                <div className="flex items-center gap-2 p-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="text-white"
                    >
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="3" y1="9" x2="21" y2="9"></line>
                      <line x1="9" y1="21" x2="9" y2="9"></line>
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-white">Trading Assistant</h3>
                </div>
                <motion.button
                  onClick={() => setIsAssistantFullScreen(true)}
                  className="mr-3 p-1.5 rounded-md hover:bg-zinc-700 transition-colors"
                  title="Expand to full screen"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="text-zinc-400 hover:text-white"
                  >
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
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="12"
                          height="12"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="text-white"
                        >
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
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="12"
                          height="12"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="text-white"
                        >
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
                    <div
                      className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"
                      style={{ animationDelay: "0.4s" }}
                    ></div>
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