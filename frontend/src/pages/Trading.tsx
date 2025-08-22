import React, { useEffect, useRef, useState, useMemo } from "react";
import {
  createChart,
  IChartApi,
  CandlestickSeries,
  ISeriesApi,
} from "lightweight-charts";

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
      text: "Hello! How can I help you with your trading today?",
      sender: "bot",
    },
  ]);
  const [userInput, setUserInput] = useState("");

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
  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const newUserMessage: ChatMessage = {
      id: Date.now(),
      text: userInput,
      sender: "user",
    };

    setChatMessages((prev) => [...prev, newUserMessage]);
    setUserInput("");

    // Mock bot response after 1 second
    setTimeout(() => {
      const botResponse: ChatMessage = {
        id: Date.now() + 1,
        text: "Thanks for your message! I'm a demo assistant and my responses are pre-programmed for this frontend mockup.",
        sender: "bot",
      };
      setChatMessages((prev) => [...prev, botResponse]);
    }, 1000);
  };

  return (
    <div
      className="container mx-auto p-4"
      style={{ fontFamily: "'Creati Display', sans-serif" }}
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
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
                  className="w-full bg-zinc-700 text-white border border-zinc-600 rounded-lg px-4 py-2 focus:outline-none"
                />
                {isLoadingCoins && (
                  <div className="absolute right-2 top-2">...</div>
                )}
                {searchTerm && !isLoadingCoins && filteredCoins.length > 0 && (
                  <ul className="absolute z-10 w-full bg-zinc-800 border border-zinc-700 rounded-lg mt-1 max-h-40 overflow-y-auto">
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
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <h2 className="text-xl font-bold text-white">
                  {coins.find((c) => c.id === selectedCoin)?.name ||
                    "Loading..."}{" "}
                  Chart (USD)
                </h2>
                <div className="flex items-center gap-1 bg-zinc-800 p-1 rounded-md">
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
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-zinc-700 p-3 gap-2">
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
              <div className="flex items-center gap-1 bg-zinc-800 p-1 rounded-md">
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
                  <thead className="text-xs text-zinc-400 uppercase">
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
                          className="border-t border-zinc-800 hover:bg-zinc-800 cursor-pointer"
                          onClick={() => setSelectedCoin(coin.id)}
                        >
                          <td className="px-4 py-2 flex items-center gap-2">
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
        <div className="lg:col-span-3 space-y-4">
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
            <div className="flex text-xs mb-4">
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
                  className="w-full bg-zinc-700 border border-zinc-600 rounded-md p-2 text-white"
                />
              )}
              <input
                type="number"
                placeholder={`Amount (${coins.find((c) => c.id === selectedCoin)?.symbol.toUpperCase() || ""})`}
                className="w-full bg-zinc-700 border border-zinc-600 rounded-md p-2 text-white"
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
            <h3 className="text-lg font-semibold text-white p-3 border-b border-zinc-700">
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
            <h3 className="text-lg font-semibold text-white p-3 border-b border-zinc-700">
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

          {/* --- NEW SECTION: Mockup Chatbot --- */}
          <Card className="!p-0 flex flex-col h-96">
            <h3 className="text-lg font-semibold text-white p-3 border-b border-zinc-700">
              Trading Assistant
            </h3>
            <div
              ref={chatContainerRef}
              className="flex-1 overflow-y-auto p-3 space-y-4"
            >
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex items-end ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-3 py-2 ${msg.sender === "user" ? "bg-blue-600 text-white" : "bg-zinc-700 text-zinc-200"}`}
                  >
                    <p className="text-sm">{msg.text}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-2 border-t border-zinc-700">
              <form onSubmit={handleChatSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Ask something..."
                  className="flex-1 bg-zinc-700 border border-zinc-600 rounded-md p-2 text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  autoComplete="off"
                />
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 rounded-md text-sm font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
                  disabled={!userInput.trim()}
                >
                  Send
                </button>
              </form>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
