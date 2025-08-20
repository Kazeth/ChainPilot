import React, { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Settings,
  PlusCircle,
  Search,
} from "lucide-react";
import Button from "../components/ui/button";
import Card from "../components/ui/card";

// --- Mock Data ---
const portfolioAssets = [
  {
    name: "Bitcoin",
    symbol: "BTC",
    balance: "0.501",
    avgBuyPrice: "58,500.00",
    currentValue: "30,060.00",
    pnl: "+1,560.00",
    pnlPercent: "+5.45%",
    "24hChange": "+2.5%",
    iconUrl: "https://placehold.co/40x40/F7931A/FFFFFF?text=B",
    takeProfit: "65,000",
    stopLoss: "55,000",
  },
  {
    name: "Ethereum",
    symbol: "ETH",
    balance: "3.120",
    avgBuyPrice: "1,850.00",
    currentValue: "5,928.00",
    pnl: "+156.00",
    pnlPercent: "+2.71%",
    "24hChange": "-1.2%",
    iconUrl: "https://placehold.co/40x40/627EEA/FFFFFF?text=E",
    takeProfit: null,
    stopLoss: "1,700",
  },
  {
    name: "Solana",
    symbol: "SOL",
    balance: "15.80",
    avgBuyPrice: "45.00",
    currentValue: "632.00",
    pnl: "-79.00",
    pnlPercent: "-11.11%",
    "24hChange": "+7.8%",
    iconUrl: "https://placehold.co/40x40/9945FF/FFFFFF?text=S",
    takeProfit: null,
    stopLoss: null,
  },
];

const openOrders = [
  {
    symbol: "BTC",
    action: "SELL",
    amount: "0.1",
    price: "65,000.00",
    status: "Active",
  },
  {
    symbol: "ETH",
    action: "BUY",
    amount: "2.0",
    price: "1,800.00",
    status: "Active",
  },
];

const tradeHistory = [
  {
    symbol: "BTC",
    action: "BUY",
    amount: "0.2",
    price: "58,000.00",
    date: "2023-10-26",
  },
  {
    symbol: "ETH",
    action: "SELL",
    amount: "1.0",
    price: "1,950.00",
    date: "2023-10-25",
  },
  {
    symbol: "SOL",
    action: "BUY",
    amount: "10.0",
    price: "42.00",
    date: "2023-10-24",
  },
];

// --- Main Portfolio Page Component ---
export default function PortfolioPage() {
  const [activeTab, setActiveTab] = useState("coins");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredHistory = tradeHistory.filter(
    (trade) =>
      trade.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      trade.action.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const TabButton = ({
    tabName,
    label,
  }: {
    tabName: string;
    label: string;
  }) => (
    <button
      onClick={() => setActiveTab(tabName)}
      className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
        activeTab === tabName
          ? "bg-zinc-700 text-white"
          : "text-zinc-400 hover:bg-zinc-800"
      }`}
      style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
      aria-label={`Switch to ${label} tab`}
    >
      {label}
    </button>
  );

  return (
    <div
      className="container mx-auto py-8 px-4"
      style={{ fontFamily: "'Creati Display', sans-serif" }}
    >
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <h1
          className="text-4xl font-bold text-white"
          style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
        >
          My Portfolio
        </h1>
        <Button
          className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff] mt-4 md:mt-0"
          aria-label="Add new transaction"
        >
          <PlusCircle size={16} className="mr-2" /> Add Transaction
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 border-b border-zinc-800 mb-6">
        <TabButton tabName="coins" label="Coins" />
        <TabButton tabName="orders" label="Orders" />
        <TabButton tabName="history" label="History" />
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === "coins" && (
          <div>
            {/* Portfolio Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card className="!p-5">
                <p className="text-zinc-400 text-sm">Total Profit / Loss</p>
                <p className="text-2xl font-bold text-green-400 mt-1">
                  +$1,637.00
                </p>
                <p className="text-zinc-400 text-sm mt-1">+4.68% all time</p>
              </Card>
              <Card className="!p-5">
                <p className="text-zinc-400 text-sm">Best Performer (24h)</p>
                <p className="text-2xl font-bold text-white mt-1">Solana</p>
                <p className="text-green-400 text-sm mt-1">+7.8%</p>
              </Card>
              <Card className="!p-5">
                <p className="text-zinc-400 text-sm">Worst Performer (24h)</p>
                <p className="text-2xl font-bold text-white mt-1">Ethereum</p>
                <p className="text-red-400 text-sm mt-1">-1.2%</p>
              </Card>
            </div>
            {/* Assets List */}
            <div className="space-y-4">
              <h2
                className="text-2xl font-semibold text-white"
                style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
              >
                Asset Details
              </h2>
              {portfolioAssets.map((asset) => (
                <Card key={asset.symbol} className="!p-0 overflow-hidden">
                  <div className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-4">
                      <img
                        src={asset.iconUrl}
                        alt={asset.name}
                        className="w-10 h-10 rounded-full"
                      />
                      <div>
                        <p className="font-semibold text-white text-lg">
                          {asset.name}
                        </p>
                        <p className="text-zinc-400 text-sm">
                          {asset.balance} {asset.symbol}
                        </p>
                      </div>
                    </div>
                    <div className="hidden md:block text-right">
                      <p className="font-semibold text-white text-lg">
                        ${asset.currentValue}
                      </p>
                      <p
                        className={`text-sm ${
                          asset["24hChange"].startsWith("+")
                            ? "text-green-400"
                            : "text-red-400"
                        }`}
                      >
                        {asset["24hChange"]}
                      </p>
                    </div>
                    <div className="hidden lg:block text-right">
                      <p
                        className={`font-semibold text-lg ${
                          asset.pnl.startsWith("+")
                            ? "text-green-400"
                            : "text-red-400"
                        }`}
                      >
                        {asset.pnl}
                      </p>
                      <p className="text-zinc-400 text-sm">
                        {asset.pnlPercent}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        className="!px-3 !py-2 border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white hover:border-zinc-500"
                        aria-label={`Edit settings for ${asset.name}`}
                      >
                        <Settings size={16} />
                      </Button>
                    </div>
                  </div>
                  {(asset.takeProfit || asset.stopLoss) && (
                    <div className="bg-zinc-900/50 px-4 py-3 border-t border-zinc-700 flex flex-wrap gap-x-6 gap-y-2">
                      {asset.takeProfit && (
                        <div className="flex items-center gap-2 text-sm">
                          <TrendingUp size={16} className="text-green-400" />
                          <span className="text-zinc-400">Take Profit:</span>
                          <span className="font-mono text-white">
                            ${asset.takeProfit}
                          </span>
                        </div>
                      )}
                      {asset.stopLoss && (
                        <div className="flex items-center gap-2 text-sm">
                          <TrendingDown size={16} className="text-red-400" />
                          <span className="text-zinc-400">Stop Loss:</span>
                          <span className="font-mono text-white">
                            ${asset.stopLoss}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeTab === "orders" && (
          <Card>
            <h2
              className="text-2xl font-semibold text-white mb-4"
              style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
            >
              Open Orders
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-zinc-700">
                    <th className="p-2 text-zinc-400">Coin</th>
                    <th className="p-2 text-zinc-400">Action</th>
                    <th className="p-2 text-zinc-400">Amount</th>
                    <th className="p-2 text-zinc-400">Price</th>
                    <th className="p-2 text-zinc-400">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {openOrders.map((order) => (
                    <tr key={order.symbol} className="border-b border-zinc-800">
                      <td className="p-2">{order.symbol}</td>
                      <td
                        className={`p-2 ${
                          order.action === "BUY"
                            ? "text-green-400"
                            : "text-red-400"
                        }`}
                      >
                        {order.action}
                      </td>
                      <td className="p-2">{order.amount}</td>
                      <td className="p-2">${order.price}</td>
                      <td className="p-2 text-yellow-400">{order.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {activeTab === "history" && (
          <Card>
            <div className="flex justify-between items-center mb-4">
              <h2
                className="text-2xl font-semibold text-white"
                style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
              >
                Trade History
              </h2>
              <div className="relative">
                <Search
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
                  size={18}
                />
                <input
                  type="text"
                  placeholder="Search by stock or action..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="bg-zinc-900 border border-zinc-700 rounded-md pl-10 pr-4 py-1.5 text-sm focus:outline-none focus:border-[#87efff]"
                  aria-label="Search trade history by stock or action"
                />
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-zinc-700">
                    <th className="p-2 text-zinc-400">Coin</th>
                    <th className="p-2 text-zinc-400">Action</th>
                    <th className="p-2 text-zinc-400">Amount</th>
                    <th className="p-2 text-zinc-400">Price</th>
                    <th className="p-2 text-zinc-400">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.map((trade, i) => (
                    <tr key={i} className="border-b border-zinc-800">
                      <td className="p-2">{trade.symbol}</td>
                      <td
                        className={`p-2 ${
                          trade.action === "BUY"
                            ? "text-green-400"
                            : "text-red-400"
                        }`}
                      >
                        {trade.action}
                      </td>
                      <td className="p-2">{trade.amount}</td>
                      <td className="p-2">${trade.price}</td>
                      <td className="p-2">{trade.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}