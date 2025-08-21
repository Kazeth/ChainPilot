import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  TrendingUp,
  TrendingDown,
  Settings,
  PlusCircle,
  Search,
  Eye,
  EyeOff,
  BarChart3,
  PieChart,
  Activity,
  DollarSign,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
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
  const [isBalanceVisible, setIsBalanceVisible] = useState(true);
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);

  // Reset selected asset when switching tabs to prevent state issues
  const handleTabChange = (tabName: string) => {
    setActiveTab(tabName);
    if (tabName !== "coins") {
      setSelectedAsset(null);
    }
  };

  const filteredHistory = tradeHistory.filter(
    (trade) =>
      trade.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      trade.action.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  const TabButton = ({
    tabName,
    label,
    icon: Icon,
  }: {
    tabName: string;
    label: string;
    icon: React.ComponentType<any>;
  }) => (
    <motion.button
      onClick={() => handleTabChange(tabName)}
      className={`relative px-6 py-3 text-sm font-medium rounded-lg transition-all duration-200 flex items-center gap-2 ${
        activeTab === tabName
          ? "bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg"
          : "text-zinc-400 hover:bg-zinc-800 hover:text-white"
      }`}
      style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
      aria-label={`Switch to ${label} tab`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Icon size={16} />
      {label}
      {activeTab === tabName && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-lg"
          layoutId="activeTab"
          transition={{ duration: 0.3 }}
        />
      )}
    </motion.button>
  );

  return (
    <motion.div
      className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 py-8 px-4"
      style={{ fontFamily: "'Creati Display', sans-serif" }}
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <div className="container mx-auto max-w-7xl">
        {/* Header Section */}
        <motion.div 
          className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-8 gap-6"
          variants={itemVariants}
        >
          <div className="flex items-center gap-4">
            <motion.div
              className="p-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl shadow-lg"
              whileHover={{ scale: 1.05, rotate: 5 }}
              transition={{ duration: 0.2 }}
            >
              <Wallet size={28} className="text-white" />
            </motion.div>
            <div>
              <h1
                className="text-4xl lg:text-5xl font-bold text-white"
                style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
              >
                My Portfolio
              </h1>
              <p className="text-zinc-400 mt-1">Track your crypto investments</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <motion.button
              onClick={() => setIsBalanceVisible(!isBalanceVisible)}
              className="p-3 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isBalanceVisible ? <Eye size={20} /> : <EyeOff size={20} />}
            </motion.button>
            
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Button
                className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2"
                aria-label="Add new transaction"
              >
                <PlusCircle size={18} />
                Add Transaction
              </Button>
            </motion.div>
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div 
          className="flex flex-wrap gap-3 mb-8 p-2 bg-zinc-900/50 backdrop-blur-sm rounded-xl border border-zinc-800/50"
          variants={itemVariants}
        >
          <TabButton tabName="coins" label="Coins" icon={PieChart} />
          <TabButton tabName="orders" label="Orders" icon={Activity} />
          <TabButton tabName="history" label="History" icon={BarChart3} />
        </motion.div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === "coins" && (
              <motion.div 
                key="coins-content"
                className="space-y-8"
                initial="hidden"
                animate="visible"
                variants={containerVariants}
              >
                {/* Portfolio Overview Cards */}
                <motion.div 
                  className="grid grid-cols-1 md:grid-cols-3 gap-6"
                  variants={containerVariants}
                >
                  <motion.div variants={itemVariants}>
                    <Card className="!p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20 hover:border-green-500/30 transition-all duration-300">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-zinc-400 text-sm mb-1">Total Profit / Loss</p>
                          <p className={`text-3xl font-bold ${isBalanceVisible ? 'text-green-400' : 'text-zinc-500'}`}>
                            {isBalanceVisible ? '+$1,637.00' : '••••••'}
                          </p>
                          <p className="text-zinc-400 text-sm mt-1">+4.68% all time</p>
                        </div>
                        <motion.div
                          className="p-3 bg-green-500/20 rounded-lg"
                          whileHover={{ scale: 1.1, rotate: 5 }}
                        >
                          <TrendingUp size={24} className="text-green-400" />
                        </motion.div>
                      </div>
                    </Card>
                  </motion.div>

                  <motion.div variants={itemVariants}>
                    <Card className="!p-6 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/20 hover:border-blue-500/30 transition-all duration-300">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-zinc-400 text-sm mb-1">Best Performer (24h)</p>
                          <p className="text-3xl font-bold text-white">Solana</p>
                          <p className="text-green-400 text-sm mt-1 flex items-center gap-1">
                            <ArrowUpRight size={16} />
                            +7.8%
                          </p>
                        </div>
                        <motion.div
                          className="p-3 bg-blue-500/20 rounded-lg"
                          whileHover={{ scale: 1.1, rotate: -5 }}
                        >
                          <BarChart3 size={24} className="text-blue-400" />
                        </motion.div>
                      </div>
                    </Card>
                  </motion.div>

                  <motion.div variants={itemVariants}>
                    <Card className="!p-6 bg-gradient-to-br from-red-500/10 to-orange-500/10 border-red-500/20 hover:border-red-500/30 transition-all duration-300">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-zinc-400 text-sm mb-1">Worst Performer (24h)</p>
                          <p className="text-3xl font-bold text-white">Ethereum</p>
                          <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                            <ArrowDownRight size={16} />
                            -1.2%
                          </p>
                        </div>
                        <motion.div
                          className="p-3 bg-red-500/20 rounded-lg"
                          whileHover={{ scale: 1.1, rotate: 5 }}
                        >
                          <TrendingDown size={24} className="text-red-400" />
                        </motion.div>
                      </div>
                    </Card>
                  </motion.div>
                </motion.div>

                {/* Assets List */}
                <motion.div 
                  className="space-y-6"
                  variants={containerVariants}
                >
                  <motion.h2
                    className="text-2xl font-semibold text-white flex items-center gap-3"
                    style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                    variants={itemVariants}
                  >
                    <DollarSign size={28} className="text-blue-400" />
                    Asset Details
                  </motion.h2>
                  
                  <motion.div 
                    className="space-y-4"
                    variants={containerVariants}
                  >
                    {portfolioAssets.map((asset, index) => (
                      <motion.div
                        key={`asset-${asset.symbol}`}
                        variants={itemVariants}
                        whileHover={{ scale: 1.02, y: -5 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Card 
                          className={`!p-0 overflow-hidden cursor-pointer transition-all duration-300 ${
                            selectedAsset === asset.symbol 
                              ? 'ring-2 ring-blue-500/50 bg-blue-500/5' 
                              : 'hover:bg-zinc-800/50'
                          }`}
                          onClick={() => setSelectedAsset(selectedAsset === asset.symbol ? null : asset.symbol)}
                        >
                          <div className="flex items-center justify-between p-6">
                            <div className="flex items-center gap-4">
                              <motion.img
                                src={asset.iconUrl}
                                alt={asset.name}
                                className="w-12 h-12 rounded-full"
                                whileHover={{ scale: 1.1 }}
                              />
                              <div>
                                <p className="font-semibold text-white text-lg">{asset.name}</p>
                                <p className="text-zinc-400 text-sm">
                                  {isBalanceVisible ? `${asset.balance} ${asset.symbol}` : '••••••'}
                                </p>
                              </div>
                            </div>
                            
                            <div className="hidden md:block text-right">
                              <p className="font-semibold text-white text-lg">
                                {isBalanceVisible ? `$${asset.currentValue}` : '••••••'}
                              </p>
                              <p className={`text-sm flex items-center gap-1 justify-end ${
                                asset["24hChange"].startsWith("+") ? "text-green-400" : "text-red-400"
                              }`}>
                                {asset["24hChange"].startsWith("+") ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                                {asset["24hChange"]}
                              </p>
                            </div>
                            
                            <div className="hidden lg:block text-right">
                              <p className={`font-semibold text-lg ${
                                asset.pnl.startsWith("+") ? "text-green-400" : "text-red-400"
                              }`}>
                                {isBalanceVisible ? asset.pnl : '••••••'}
                              </p>
                              <p className="text-zinc-400 text-sm">{asset.pnlPercent}</p>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <motion.div
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                              >
                                <Button
                                  className="!px-3 !py-2 border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white hover:border-zinc-500"
                                  aria-label={`Edit settings for ${asset.name}`}
                                >
                                  <Settings size={16} />
                                </Button>
                              </motion.div>
                            </div>
                          </div>
                          
                          {(asset.takeProfit || asset.stopLoss) && (
                            <motion.div 
                              className="bg-zinc-900/50 px-6 py-4 border-t border-zinc-700/50"
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: "auto", opacity: 1 }}
                              transition={{ duration: 0.3 }}
                            >
                              <div className="flex flex-wrap gap-x-8 gap-y-3">
                                {asset.takeProfit && (
                                  <div className="flex items-center gap-2 text-sm">
                                    <TrendingUp size={16} className="text-green-400" />
                                    <span className="text-zinc-400">Take Profit:</span>
                                    <span className="font-mono text-green-400 font-medium">
                                      ${asset.takeProfit}
                                    </span>
                                  </div>
                                )}
                                {asset.stopLoss && (
                                  <div className="flex items-center gap-2 text-sm">
                                    <TrendingDown size={16} className="text-red-400" />
                                    <span className="text-zinc-400">Stop Loss:</span>
                                    <span className="font-mono text-red-400 font-medium">
                                      ${asset.stopLoss}
                                    </span>
                                  </div>
                                )}
                              </div>
                            </motion.div>
                          )}
                        </Card>
                      </motion.div>
                    ))}
                  </motion.div>
                </motion.div>
              </motion.div>
            )}

            {activeTab === "orders" && (
              <motion.div 
                key="orders-content" 
                initial="hidden"
                animate="visible"
                variants={containerVariants}
              >
                <Card className="!p-6">
                  <div className="flex items-center gap-3 mb-6">
                    <Activity size={28} className="text-blue-400" />
                    <h2
                      className="text-2xl font-semibold text-white"
                      style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                    >
                      Open Orders
                    </h2>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-zinc-700">
                          <th className="p-3 text-zinc-400 font-medium">Coin</th>
                          <th className="p-3 text-zinc-400 font-medium">Action</th>
                          <th className="p-3 text-zinc-400 font-medium">Amount</th>
                          <th className="p-3 text-zinc-400 font-medium">Price</th>
                          <th className="p-3 text-zinc-400 font-medium">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {openOrders.map((order, index) => (
                          <motion.tr
                            key={order.symbol}
                            className="border-b border-zinc-800 hover:bg-zinc-800/30 transition-colors"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <td className="p-3 font-medium">{order.symbol}</td>
                            <td className={`p-3 font-medium ${
                              order.action === "BUY" ? "text-green-400" : "text-red-400"
                            }`}>
                              {order.action}
                            </td>
                            <td className="p-3">{order.amount}</td>
                            <td className="p-3 font-mono">${order.price}</td>
                            <td className="p-3">
                              <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">
                                {order.status}
                              </span>
                            </td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </motion.div>
            )}

            {activeTab === "history" && (
              <motion.div 
                key="history-content" 
                initial="hidden"
                animate="visible"
                variants={containerVariants}
              >
                <Card className="!p-6">
                  <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
                    <div className="flex items-center gap-3">
                      <BarChart3 size={28} className="text-blue-400" />
                      <h2
                        className="text-2xl font-semibold text-white"
                        style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                      >
                        Trade History
                      </h2>
                    </div>
                    <div className="relative">
                      <Search
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
                        size={18}
                      />
                      <input
                        type="text"
                        placeholder="Search by coin or action..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="bg-zinc-800 border border-zinc-700 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                        aria-label="Search trade history by coin or action"
                      />
                    </div>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-zinc-700">
                          <th className="p-3 text-zinc-400 font-medium">Coin</th>
                          <th className="p-3 text-zinc-400 font-medium">Action</th>
                          <th className="p-3 text-zinc-400 font-medium">Amount</th>
                          <th className="p-3 text-zinc-400 font-medium">Price</th>
                          <th className="p-3 text-zinc-400 font-medium">Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        <AnimatePresence>
                          {filteredHistory.map((trade, index) => (
                            <motion.tr
                              key={`${trade.symbol}-${index}`}
                              className="border-b border-zinc-800 hover:bg-zinc-800/30 transition-colors"
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              exit={{ opacity: 0, x: 20 }}
                              transition={{ delay: index * 0.05 }}
                            >
                              <td className="p-3 font-medium">{trade.symbol}</td>
                              <td className={`p-3 font-medium ${
                                trade.action === "BUY" ? "text-green-400" : "text-red-400"
                              }`}>
                                {trade.action}
                              </td>
                              <td className="p-3">{trade.amount}</td>
                              <td className="p-3 font-mono">${trade.price}</td>
                              <td className="p-3 text-zinc-400">{trade.date}</td>
                            </motion.tr>
                          ))}
                        </AnimatePresence>
                      </tbody>
                    </table>
                  </div>
                </Card>
              </motion.div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
}