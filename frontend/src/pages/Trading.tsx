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
    { price: "60,497.20", size: "2.50", total: "4.95" },
  ],
  asks: [
    { price: "60,501.80", size: "0.80", total: "0.80" },
    { price: "60,502.30", size: "1.50", total: "2.30" },
    { price: "60,503.90", size: "0.60", total: "2.90" },
    { price: "60,504.10", size: "3.10", total: "6.00" },
  ],
};

const mockTradeHistory = [
  { price: "60,501.80", size: "0.15", time: "10:30:05" },
  { price: "60,501.80", size: "0.05", time: "10:30:02" },
  { price: "60,500.10", size: "0.20", time: "10:29:59" },
  { price: "60,500.10", size: "0.10", time: "10:29:55" },
];

// --- Main Trading Page Component ---

interface Coin {
  id: string;
  name: string;
  symbol: string;
}

export default function TradingPage() {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  const [selectedCoin, setSelectedCoin] = useState("bitcoin");
  const [tradeType, setTradeType] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [searchTerm, setSearchTerm] = useState("");
  const [coins, setCoins] = useState<Coin[]>([]);
  const [isLoadingCoins, setIsLoadingCoins] = useState(false);
  const [isLoadingChart, setIsLoadingChart] = useState(false);

  // Fetch initial list of coins
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
      chartRef.current?.applyOptions({
        width: chartContainerRef.current?.clientWidth,
      });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chartRef.current?.remove();
    };
  }, []);

  // Fetch data when selectedCoin changes
  useEffect(() => {
    const fetchData = async () => {
      if (!candleSeriesRef.current) return;
      setIsLoadingChart(true);
      try {
        const res = await fetch(
          `https://api.coingecko.com/api/v3/coins/${selectedCoin}/ohlc?vs_currency=usd&days=30`
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
        candleSeriesRef.current.setData(formattedData);
      } catch (err) {
        console.error("Error fetching OHLC data:", err);
      } finally {
        setIsLoadingChart(false);
      }
    };

    fetchData();
  }, [selectedCoin]);

  // Filter coins based on search term
  const filteredCoins = useMemo(() => {
    return coins.filter((coin) =>
      coin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm, coins]);

  return (
    <div
      className="container mx-auto p-4"
      style={{ fontFamily: "'Creati Display', sans-serif" }}
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Main Content: Chart and Order History */}
        <div className="lg:col-span-9">
          <Card className="!p-4">
            <div className="flex flex-col gap-2 mb-4">
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search for a coin..."
                  className="w-full bg-zinc-700 text-white border border-zinc-600 rounded-lg px-4 py-2 focus:outline-none"
                />
                {isLoadingCoins && (
                  <div className="absolute right-2 top-2">Loading...</div>
                )}
                {searchTerm && !isLoadingCoins && filteredCoins.length > 0 && (
                  <ul className="absolute z-10 w-full bg-zinc-800 border border-zinc-700 rounded-lg mt-1 max-h-40 overflow-y-auto">
                    {filteredCoins.map((coin) => (
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
              <h2 className="text-xl font-bold text-white">
                {coins.find((c) => c.id === selectedCoin)?.name || "Loading..."} Chart (USD)
              </h2>
            </div>
            <div
              ref={chartContainerRef}
              className={`w-full h-[500px] ${isLoadingChart ? "flex items-center justify-center" : ""}`}
            >
              {isLoadingChart && <span>Loading chart...</span>}
            </div>
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
                placeholder="Amount (BTC)"
                className="w-full bg-zinc-700 border border-zinc-600 rounded-md p-2 text-white"
              />
              <Button
                className={`w-full ${tradeType === "buy" ? "bg-green-500 border-green-500" : "bg-red-500 border-red-500"} text-white`}
              >
                {tradeType === "buy" ? "Buy" : "Sell"}{" "}
                {coins.find((c) => c.id === selectedCoin)?.name || "Loading..."}
              </Button>
            </div>
          </Card>

          <Card className="!p-0">
            <h3 className="text-lg font-semibold text-white p-3 border-b border-zinc-700">
              Order Book
            </h3>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-zinc-400">
                  <th className="p-2">Price (USD)</th>
                  <th className="p-2">Size</th>
                  <th className="p-2">Total</th>
                </tr>
              </thead>
              <tbody>
                {mockOrderBook.asks.map((ask) => (
                  <tr key={ask.price}>
                    <td className="p-1 text-red-400">{ask.price}</td>
                    <td>{ask.size}</td>
                    <td>{ask.total}</td>
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
                    <td>{bid.size}</td>
                    <td>{bid.total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <Card className="!p-0">
            <h3 className="text-lg font-semibold text-white p-3 border-b border-zinc-700">
              Trade History
            </h3>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-zinc-400">
                  <th className="p-2">Price (USD)</th>
                  <th className="p-2">Size</th>
                  <th className="p-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {mockTradeHistory.map((trade) => (
                  <tr key={trade.time}>
                    <td className="p-1 text-red-400">{trade.price}</td>
                    <td>{trade.size}</td>
                    <td>{trade.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      </div>
    </div>
  );
}