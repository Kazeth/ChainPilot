import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowDownLeft,
  ArrowUpRight,
  ShieldCheck,
  PlusCircle,
  Settings,
  Wallet,
  Eye,
  EyeOff,
  TrendingUp,
  Copy,
  CheckCircle,
} from "lucide-react";
import Button from "../components/ui/button";
import Card from "../components/ui/card";
import Input from "../components/ui/input";
import Modal from "../components/ui/modal";

// --- Mock Data ---
const userAssets = [
  {
    name: "Bitcoin",
    symbol: "BTC",
    balance: "0.501",
    value: "30,060.00",
    change24h: "+2.45%",
    changeAmount: "+$720.34",
    iconUrl: "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
  },
  {
    name: "Ethereum",
    symbol: "ETH",
    balance: "3.120",
    value: "5,928.00",
    change24h: "+1.87%",
    changeAmount: "+$108.92",
    iconUrl: "https://cryptologos.cc/logos/ethereum-eth-logo.png",
  },
  {
    name: "Solana",
    symbol: "SOL",
    balance: "15.80",
    value: "632.00",
    change24h: "-0.92%",
    changeAmount: "-$5.85",
    iconUrl: "https://cryptologos.cc/logos/solana-sol-logo.png",
  },
  {
    name: "Cardano",
    symbol: "ADA",
    balance: "1,250.00",
    value: "375.00",
    change24h: "+4.12%",
    changeAmount: "+$14.85",
    iconUrl: "https://cryptologos.cc/logos/cardano-ada-logo.png",
  },
];

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.4,
    },
  },
};

// --- Main Wallet Page Component ---
export default function WalletPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProtocolSetup, setIsProtocolSetup] = useState(false);
  const [isBalanceVisible, setIsBalanceVisible] = useState(true);
  const [copiedAddress, setCopiedAddress] = useState(false);

  const totalBalance = userAssets.reduce((sum, asset) => sum + parseFloat(asset.value.replace(',', '')), 0);
  const walletAddress = "0x742d35Cc6632C0532c718bE9c2EA5e6cFb8dd72A";

  const handleSaveSettings = () => {
    setIsProtocolSetup(true);
    setIsModalOpen(false);
  };

  const copyAddress = () => {
    navigator.clipboard.writeText(walletAddress);
    setCopiedAddress(true);
    setTimeout(() => setCopiedAddress(false), 2000);
  };

  return (
    <>
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="container mx-auto py-8 px-4 scrollbar-modern"
        style={{ fontFamily: "'Creati Display', sans-serif" }}
      >
        <motion.div
          className="flex items-center justify-between mb-8"
          variants={itemVariants}
        >
          <motion.h1
            className="text-4xl font-bold text-white flex items-center gap-4"
            style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
            whileHover={{ scale: 1.02 }}
          >
            <motion.div
              className="p-3 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-xl"
              whileHover={{ rotate: 5, scale: 1.1 }}
            >
              <Wallet size={32} className="text-blue-400" />
            </motion.div>
            My Wallet
          </motion.h1>
          
          <motion.div
            className="flex items-center gap-3"
            variants={itemVariants}
          >
            <motion.button
              onClick={() => setIsBalanceVisible(!isBalanceVisible)}
              className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              aria-label={isBalanceVisible ? "Hide balance" : "Show balance"}
            >
              {isBalanceVisible ? (
                <Eye size={20} className="text-zinc-400" />
              ) : (
                <EyeOff size={20} className="text-zinc-400" />
              )}
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Wallet Address Card */}
        <motion.div variants={itemVariants} className="mb-6">
          <Card className="!p-4 bg-gradient-to-r from-zinc-800/50 to-zinc-700/50 border-zinc-600/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Wallet size={20} className="text-blue-400" />
                </div>
                <div>
                  <p className="text-zinc-400 text-sm">Wallet Address</p>
                  <p className="text-white font-mono text-sm">
                    {walletAddress.slice(0, 6)}...{walletAddress.slice(-6)}
                  </p>
                </div>
              </div>
              <motion.button
                onClick={copyAddress}
                className="flex items-center gap-2 px-3 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-lg transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                aria-label="Copy wallet address"
              >
                <AnimatePresence mode="wait">
                  {copiedAddress ? (
                    <motion.div
                      key="check"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="flex items-center gap-2"
                    >
                      <CheckCircle size={16} className="text-green-400" />
                      <span className="text-green-400 text-sm">Copied!</span>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="copy"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="flex items-center gap-2"
                    >
                      <Copy size={16} className="text-zinc-400" />
                      <span className="text-zinc-400 text-sm">Copy</span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.button>
            </div>
          </Card>
        </motion.div>

        {/* Total Balance Card */}
        <motion.div variants={itemVariants} className="mb-8">
          <Card className="!p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20 hover:border-green-500/30 transition-all duration-300">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
              <div className="flex items-center gap-4">
                <motion.div
                  className="p-4 bg-green-500/20 rounded-xl"
                  whileHover={{ scale: 1.1, rotate: 5 }}
                >
                  <TrendingUp size={32} className="text-green-400" />
                </motion.div>
                <div>
                  <p className="text-zinc-400 text-sm mb-1">Total Portfolio Value</p>
                  <motion.p 
                    className={`text-4xl font-bold mt-1 ${isBalanceVisible ? 'text-white' : 'text-zinc-500'}`}
                    key={isBalanceVisible ? 'visible' : 'hidden'}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {isBalanceVisible ? `$${totalBalance.toLocaleString()}` : '••••••••'}
                  </motion.p>
                  <motion.p 
                    className="text-green-400 text-sm mt-2 flex items-center gap-2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <TrendingUp size={16} />
                    +2.5% vs last 24h (+$843.27)
                  </motion.p>
                </div>
              </div>
              <motion.div 
                className="flex space-x-3 mt-6 md:mt-0"
                variants={containerVariants}
              >
                <motion.div variants={itemVariants}>
                  <motion.div
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff] transition-all duration-300"
                      aria-label="Deposit funds"
                    >
                      <ArrowDownLeft size={16} className="mr-2" /> Deposit
                    </Button>
                  </motion.div>
                </motion.div>
                <motion.div variants={itemVariants}>
                  <motion.div
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff] transition-all duration-300"
                      aria-label="Withdraw funds"
                    >
                      <ArrowUpRight size={16} className="mr-2" /> Withdraw
                    </Button>
                  </motion.div>
                </motion.div>
              </motion.div>
            </div>
          </Card>
        </motion.div>

        {/* Assets List */}
        <motion.div 
          className="space-y-6 mb-12"
          variants={containerVariants}
        >
          <motion.h2
            className="text-2xl font-semibold text-white flex items-center gap-3"
            style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
            variants={itemVariants}
          >
            <motion.div
              className="p-2 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg"
              whileHover={{ rotate: 5, scale: 1.1 }}
            >
              <Wallet size={24} className="text-purple-400" />
            </motion.div>
            Your Assets
          </motion.h2>
          
          <motion.div 
            className="grid gap-4"
            variants={containerVariants}
          >
            {userAssets.map((asset, index) => (
              <motion.div
                key={asset.symbol}
                variants={itemVariants}
                whileHover={{ scale: 1.02, y: -5 }}
                transition={{ duration: 0.2 }}
              >
                <Card className="!p-6 hover:border-zinc-600 transition-all duration-300 bg-gradient-to-r from-zinc-800/30 to-zinc-700/30 hover:from-zinc-800/50 hover:to-zinc-700/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <motion.div
                        className="relative"
                        whileHover={{ scale: 1.1 }}
                      >
                        <img
                          src={asset.iconUrl}
                          alt={asset.name}
                          className="w-12 h-12 rounded-full"
                          onError={(e) => {
                            e.currentTarget.src = `https://placehold.co/48x48/6B7280/FFFFFF?text=${asset.symbol[0]}`;
                          }}
                        />
                      </motion.div>
                      <div>
                        <p className="font-semibold text-white text-lg">
                          {asset.name}
                        </p>
                        <p className="text-zinc-400 text-sm">{asset.symbol}</p>
                      </div>
                    </div>
                    
                    <div className="hidden md:block text-center">
                      <p className="text-zinc-400 text-sm mb-1">Balance</p>
                      <p className="font-semibold text-white text-lg">
                        {isBalanceVisible ? `${asset.balance} ${asset.symbol}` : '••••••'}
                      </p>
                    </div>
                    
                    <div className="text-right">
                      <p className="font-semibold text-white text-lg">
                        {isBalanceVisible ? `$${asset.value}` : '••••••'}
                      </p>
                      <div className="flex items-center gap-2 justify-end">
                        <motion.p 
                          className={`text-sm font-medium ${
                            asset.change24h.startsWith("+") ? "text-green-400" : "text-red-400"
                          }`}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: index * 0.1 + 0.3 }}
                        >
                          {asset.change24h}
                        </motion.p>
                        <motion.p 
                          className={`text-xs ${
                            asset.changeAmount.startsWith("+") ? "text-green-400" : "text-red-400"
                          }`}
                          initial={{ opacity: 0, x: 10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 + 0.4 }}
                        >
                          ({asset.changeAmount})
                        </motion.p>
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Secure Inheritance Section */}
        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-br from-zinc-800/50 to-zinc-700/50 border-2 border-dashed border-zinc-600/50 hover:border-zinc-500/50 !p-6 transition-all duration-300">
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
              <motion.div 
                className="text-[#87efff]"
                whileHover={{ scale: 1.1, rotate: 5 }}
              >
                <ShieldCheck size={40} />
              </motion.div>
              <div className="flex-grow">
                <motion.h3
                  className="text-xl font-bold text-white"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                  whileHover={{ scale: 1.02 }}
                >
                  Secure Inheritance Protocol
                </motion.h3>
                <motion.p 
                  className="text-zinc-400 mt-2"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  {isProtocolSetup
                    ? "Your protocol is active. You can manage your settings at any time."
                    : "Protect your digital legacy. Designate a beneficiary to receive your assets in case of unforeseen circumstances."}
                </motion.p>
              </div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  onClick={() => setIsModalOpen(true)}
                  className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff] w-full md:w-auto transition-all duration-300"
                  aria-label={
                    isProtocolSetup
                      ? "Manage inheritance settings"
                      : "Set up inheritance protocol"
                  }
                >
                  {isProtocolSetup ? (
                    <>
                      <Settings size={16} className="mr-2" /> Manage Settings
                    </>
                  ) : (
                    <>
                      <PlusCircle size={16} className="mr-2" /> Set Up Protocol
                    </>
                  )}
                </Button>
              </motion.div>
            </div>
          </Card>
        </motion.div>
      </motion.div>

      {/* Inheritance Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <Modal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            title="Inheritance Protocol Settings"
          >
            <motion.div 
              className="space-y-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <label
                  htmlFor="walletAddress"
                  className="block text-sm font-medium text-zinc-400 mb-2"
                >
                  Beneficiary Wallet Address
                </label>
                <Input
                  id="walletAddress"
                  type="text"
                  placeholder="0x..."
                  aria-label="Enter beneficiary wallet address"
                />
                <p className="text-xs text-zinc-500 mt-1">
                  This address will receive your assets if the protocol is activated
                </p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <label
                  htmlFor="inactivityPeriod"
                  className="block text-sm font-medium text-zinc-400 mb-2"
                >
                  Inactivity Period
                </label>
                <select
                  id="inactivityPeriod"
                  className="w-full bg-zinc-800 border-2 border-zinc-700 text-white rounded-lg py-3 px-4 focus:outline-none focus:border-[#87efff] transition-colors"
                  aria-label="Select inactivity period"
                >
                  <option>6 Months</option>
                  <option>1 Year</option>
                  <option>2 Years</option>
                  <option>5 Years</option>
                </select>
                <p className="text-xs text-zinc-500 mt-1">
                  How long after your last activity should the protocol wait before activation
                </p>
              </motion.div>
              
              <motion.div
                className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
              >
                <div className="flex items-start gap-3">
                  <ShieldCheck size={20} className="text-blue-400 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-medium text-white mb-1">Security Notice</h4>
                    <p className="text-xs text-zinc-400">
                      Your beneficiary will only be able to access your assets after the specified inactivity period. 
                      You can cancel or modify this protocol at any time while you're active.
                    </p>
                  </div>
                </div>
              </motion.div>
            </motion.div>
            
            <motion.div 
              className="mt-8 flex justify-end gap-3"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  onClick={() => setIsModalOpen(false)}
                  className="border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white hover:border-zinc-500"
                  aria-label="Cancel and close modal"
                >
                  Cancel
                </Button>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  onClick={handleSaveSettings}
                  className="bg-[#87efff] border-[#87efff] text-zinc-900 hover:bg-[#6fe2f6] hover:border-[#6fe2f6] font-medium"
                  aria-label="Save inheritance settings"
                >
                  <ShieldCheck size={16} className="mr-2" />
                  Save Settings
                </Button>
              </motion.div>
            </motion.div>
          </Modal>
        )}
      </AnimatePresence>
    </>
  );
}
