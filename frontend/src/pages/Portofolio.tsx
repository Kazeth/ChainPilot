import React, { useState, useEffect } from "react";
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
import { wallet_backend } from "@/declarations/wallet_backend";
import { marketData_backend } from "@/declarations/marketData_backend";
import { transaction_backend } from "@/declarations/transaction_backend";
import { user_backend } from "@/declarations/user_backend";
import { Principal } from "@dfinity/principal";
import { useAuthContext } from "@/context/AuthContext";

// --- Type Definitions ---
interface Asset {
  assetId: string;
  name: string;
  symbol: string;
  currentPrice: number;
}

interface Holding {
  asset: Asset;
  amount: number;
  valueUSD?: number;
}

interface Wallet {
  walletId: string;
  principal: Principal;
}

interface Transaction {
  txType: string;
  amount: number;
  timestamp: bigint;
}

interface PortfolioAsset {
  name: string;
  symbol: string;
  balance: string;
  avgBuyPrice: string;
  currentValue: string;
  pnl: string;
  pnlPercent: string;
  "24hChange": string;
  iconUrl: string;
  takeProfit: string | null;
  stopLoss: string | null;
}

interface TradeHistoryItem {
  symbol: string;
  action: string;
  amount: string;
  price: string;
  date: string;
}

// --- Main Portfolio Page Component ---
export default function PortfolioPage() {
  const [activeTab, setActiveTab] = useState("coins");
  const [searchTerm, setSearchTerm] = useState("");
  const [isBalanceVisible, setIsBalanceVisible] = useState(true);
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [portfolioData, setPortfolioData] = useState<PortfolioAsset[]>([]);
  const [history, setHistory] = useState<TradeHistoryItem[]>([]);

  const auth = useAuthContext();

  // Reset selected asset when switching tabs to prevent state issues
  const handleTabChange = (tabName: string) => {
    setActiveTab(tabName);
    if (tabName !== "coins") {
      setSelectedAsset(null);
    }
  };

  const filteredHistory = history.filter(
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
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 },
  };

  const TabButton = ({
    tabName,
    label,
    icon: Icon,
  }: {
    tabName: string;
    label: string;
    icon: React.ComponentType<{ size?: number }>;
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

  // Fetch data from backend (unchanged)
  useEffect(() => {
    async function initialize() {
      try {
        try {
          const userDataResponse = await user_backend.getUserData(auth.principal);
          const userData = Array.isArray(userDataResponse) && userDataResponse.length > 0
            ? userDataResponse[0]
            : null;
          console.log("[v0] User data retrieved:", userData);
        } catch (error) {
          console.log("[v0] User data not found, continuing without username", error);
        }

        const walletsResponse = await wallet_backend.getWalletsByPrincipal(auth.principal);
        const wallets = walletsResponse as unknown as Array<[Principal, Wallet[]]>;
        const walletData = wallets.length > 0 ? wallets[0][1][0] : null;

        if (walletData) {
          const holdingsResponse = await wallet_backend.getHoldingsByWalletId(walletData.walletId);
          const holdings = holdingsResponse as unknown as Array<[string, Holding[]]>;
          const holdingsData = holdings.length > 0 ? holdings[0][1] : [];

          const assetPromises = holdingsData.map(
            async (holding: Holding): Promise<PortfolioAsset> => {
              const asset = holding.asset;
              let assetData: Asset | null = null;

              try {
                const assetDataResponse = await marketData_backend.getAssetByAssetId(asset.assetId);
                assetData = Array.isArray(assetDataResponse) && assetDataResponse.length > 0
                  ? assetDataResponse[0] as Asset
                  : null;
              } catch (error) {
                console.log("[v0] Asset data not found for:", asset.assetId, error);
                assetData = null;
              }

              const currentPrice = assetData?.currentPrice ?? 16.0;
              const value = holding.valueUSD ?? holding.amount * currentPrice;
              const avgBuyPrice = "0.00";
              const avgBuyPriceNum = parseFloat(avgBuyPrice);
              const pnl = avgBuyPriceNum > 0 ? value - holding.amount * avgBuyPriceNum : 0;
              const pnlPercent = avgBuyPriceNum > 0
                ? (pnl / (holding.amount * avgBuyPriceNum)) * 100
                : 0;

              const change24h = assetData
                ? (
                    ((assetData.currentPrice - assetData.currentPrice / 1.025) /
                      assetData.currentPrice) *
                    100
                  ).toFixed(1)
                : "0.0";

              return {
                name: asset.name,
                symbol: asset.symbol,
                balance: holding.amount.toString(),
                avgBuyPrice,
                currentValue: value.toFixed(2),
                pnl: pnl.toFixed(2),
                pnlPercent: pnlPercent.toFixed(2) + "%",
                "24hChange": change24h + "%",
                iconUrl: `https://placehold.co/40x40/${
                  asset.symbol === "BTC"
                    ? "F7931A"
                    : asset.symbol === "ETH"
                      ? "627EEA"
                      : "9945FF"
                }/FFFFFF?text=${asset.symbol[0]}`,
                takeProfit: null,
                stopLoss: null,
              };
            }
          );

          const assetList = await Promise.all(assetPromises);
          setPortfolioData(assetList);

          try {
            const txsResponse = await transaction_backend.getAllUserTransactions(auth.principal);
            const txs = txsResponse as unknown as Array<[string, Transaction]>;
            
            const historyData = txs.map(([, tx]) => ({
              symbol: "Unknown",
              action: tx.txType,
              amount: tx.amount.toString(),
              price: "0.00",
              date: new Date(Number(tx.timestamp) / 1000000).toLocaleDateString(),
            }));
            
            setHistory(historyData);
          } catch (error) {
            console.error("Failed to fetch transactions:", error);
          }
        }
      } catch (error) {
        console.error("Initialization failed:", error);
      }
    }
    initialize();
  }, [auth.principal]);

  // Calculate total profit/loss and identify best/worst performers
  const totalPnL = portfolioData.reduce((sum, asset) => sum + parseFloat(asset.pnl), 0).toFixed(2);
  const totalPnLPercent = portfolioData.length > 0
    ? portfolioData.reduce((sum, asset) => {
        const value = parseFloat(asset.currentValue);
        const buyValue = parseFloat(asset.avgBuyPrice) * parseFloat(asset.balance);
        return buyValue > 0 ? sum + (value - buyValue) / buyValue * 100 : sum;
      }, 0).toFixed(2) + "%"
    : "0.00%";

  const sortedBy24hChange = [...portfolioData].sort((a, b) => 
    parseFloat(b["24hChange"]) - parseFloat(a["24hChange"])
  );
  const bestPerformer = sortedBy24hChange[0];
  const worstPerformer = sortedBy24hChange[sortedBy24hChange.length - 1];

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
              <p className="text-zinc-400 mt-1">
                Track your crypto investments
              </p>
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

            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
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
                          <p className="text-zinc-400 text-sm mb-1">
                            Total Profit / Loss
                          </p>
                          <p
                            className={`text-3xl font-bold ${isBalanceVisible ? "text-green-400" : "text-zinc-500"}`}
                          >
                            {isBalanceVisible ? `$${totalPnL}` : "••••••"}
                          </p>
                          <p className="text-zinc-400 text-sm mt-1">
                            {totalPnLPercent}
                          </p>
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
                          <p className="text-zinc-400 text-sm mb-1">
                            Best Performer (24h)
                          </p>
                          <p className="text-3xl font-bold text-white">
                            {bestPerformer ? bestPerformer.name : "N/A"}
                          </p>
                          <p className="text-green-400 text-sm mt-1 flex items-center gap-1">
                            <ArrowUpRight size={16} />
                            {bestPerformer ? bestPerformer["24hChange"] : "0.0%"}
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
                          <p className="text-zinc-400 text-sm mb-1">
                            Worst Performer (24h)
                          </p>
                          <p className="text-3xl font-bold text-white">
                            {worstPerformer ? worstPerformer.name : "N/A"}
                          </p>
                          <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                            <ArrowDownRight size={16} />
                            {worstPerformer ? worstPerformer["24hChange"] : "0.0%"}
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
                <motion.div className="space-y-6" variants={containerVariants}>
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
                    {portfolioData.length > 0 ? (
                      portfolioData.map((asset) => (
                        <motion.div
                          key={`asset-${asset.symbol}`}
                          variants={itemVariants}
                          whileHover={{ scale: 1.02, y: -5 }}
                          transition={{ duration: 0.2 }}
                        >
                          <Card
                            className={`!p-0 overflow-hidden cursor-pointer transition-all duration-300 ${
                              selectedAsset === asset.symbol
                                ? "ring-2 ring-blue-500/50 bg-blue-500/5"
                                : "hover:bg-zinc-800/50"
                            }`}
                            onClick={() =>
                              setSelectedAsset(
                                selectedAsset === asset.symbol
                                  ? null
                                  : asset.symbol
                              )
                            }
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
                                  <p className="font-semibold text-white text-lg">
                                    {asset.name}
                                  </p>
                                  <p className="text-zinc-400 text-sm">
                                    {isBalanceVisible
                                      ? `${asset.balance} ${asset.symbol}`
                                      : "••••••"}
                                  </p>
                                </div>
                              </div>

                              <div className="hidden md:block text-right">
                                <p className="font-semibold text-white text-lg">
                                  {isBalanceVisible
                                    ? `$${asset.currentValue}`
                                    : "••••••"}
                                </p>
                                <p
                                  className={`text-sm flex items-center gap-1 justify-end ${
                                    asset["24hChange"].startsWith("+")
                                      ? "text-green-400"
                                      : "text-red-400"
                                  }`}
                                >
                                  {asset["24hChange"].startsWith("+") ? (
                                    <ArrowUpRight size={14} />
                                  ) : (
                                    <ArrowDownRight size={14} />
                                  )}
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
                                  {isBalanceVisible ? asset.pnl : "••••••"}
                                </p>
                                <p className="text-zinc-400 text-sm">
                                  {asset.pnlPercent}
                                </p>
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
                                      <TrendingUp
                                        size={16}
                                        className="text-green-400"
                                      />
                                      <span className="text-zinc-400">
                                        Take Profit:
                                      </span>
                                      <span className="font-mono text-green-400 font-medium">
                                        ${asset.takeProfit}
                                      </span>
                                    </div>
                                  )}
                                  {asset.stopLoss && (
                                    <div className="flex items-center gap-2 text-sm">
                                      <TrendingDown
                                        size={16}
                                        className="text-red-400"
                                      />
                                      <span className="text-zinc-400">
                                        Stop Loss:
                                      </span>
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
                      ))
                    ) : (
                      <motion.div
                        className="text-center text-zinc-400 py-8"
                        variants={itemVariants}
                      >
                        No assets found in your portfolio.
                      </motion.div>
                    )}
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
                      style={{
                        fontFamily: "'Creati Display Bold', sans-serif",
                      }}
                    >
                      Open Orders
                    </h2>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-zinc-700">
                          <th className="p-3 text-zinc-400 font-medium">
                            Coin
                          </th>
                          <th className="p-3 text-zinc-400 font-medium">
                            Action
                          </th>
                          <th className="p-3 text-zinc-400 font-medium">
                            Amount
                          </th>
                          <th className="p-3 text-zinc-400 font-medium">
                            Price
                          </th>
                          <th className="p-3 text-zinc-400 font-medium">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <motion.tr
                          className="border-b border-zinc-800 hover:bg-zinc-800/30 transition-colors"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.1 }}
                        >
                          <td className="p-3 font-medium">N/A</td>
                          <td className="p-3 font-medium text-zinc-400">N/A</td>
                          <td className="p-3">N/A</td>
                          <td className="p-3 font-mono">N/A</td>
                          <td className="p-3">
                            <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">
                              N/A
                            </span>
                          </td>
                        </motion.tr>
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
                        style={{
                          fontFamily: "'Creati Display Bold', sans-serif",
                        }}
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
                          <th className="p-3 text-zinc-400 font-medium">
                            Coin
                          </th>
                          <th className="p-3 text-zinc-400 font-medium">
                            Action
                          </th>
                          <th className="p-3 text-zinc-400 font-medium">
                            Amount
                          </th>
                          <th className="p-3 text-zinc-400 font-medium">
                            Price
                          </th>
                          <th className="p-3 text-zinc-400 font-medium">
                            Date
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <AnimatePresence>
                          {filteredHistory.length > 0 ? (
                            filteredHistory.map((trade, index) => (
                              <motion.tr
                                key={`${trade.symbol}-${index}`}
                                className="border-b border-zinc-800 hover:bg-zinc-800/30 transition-colors"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                transition={{ delay: index * 0.05 }}
                              >
                                <td className="p-3 font-medium">
                                  {trade.symbol}
                                </td>
                                <td
                                  className={`p-3 font-medium ${
                                    trade.action === "BUY"
                                      ? "text-green-400"
                                      : "text-red-400"
                                  }`}
                                >
                                  {trade.action}
                                </td>
                                <td className="p-3">{trade.amount}</td>
                                <td className="p-3 font-mono">${trade.price}</td>
                                <td className="p-3 text-zinc-400">
                                  {trade.date}
                                </td>
                              </motion.tr>
                            ))
                          ) : (
                            <motion.tr
                              className="border-b border-zinc-800"
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                            >
                              <td colSpan={5} className="p-3 text-center text-zinc-400">
                                No trade history found.
                              </td>
                            </motion.tr>
                          )}
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