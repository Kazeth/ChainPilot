"use client"

import type React from "react"
import crypto from "crypto";
import { useState, useEffect, useCallback } from "react"
import { 
  ArrowDownLeft, 
  ArrowUpRight, 
  ShieldCheck, 
  PlusCircle, 
  Settings, 
  WalletIcon,
  Wallet,
  Eye,
  EyeOff,
  Copy,
  CheckCircle,
  TrendingUp
} from "lucide-react"
import Button from "../components/ui/button"
import Card from "../components/ui/card"
import Input from "../components/ui/input"
import InsuranceModal from "../components/ui/insuranceModal"
import type { Principal } from "@dfinity/principal"
import LegacyButton from "@/components/LegacyButton"
import { useAuthContext } from "@/context/AuthContext"
import { wallet_backend } from "@/declarations/wallet_backend"
import { marketData_backend } from "@/declarations/marketData_backend"
import { user_backend } from "@/declarations/user_backend"
import { insurance_backend } from "@/declarations/insurance_backend"
import { motion, AnimatePresence } from "framer-motion"

interface Asset {
  assetId: string
  symbol: string
  name: string
  currentPrice?: number
  marketCap?: number
  volume24h?: number
  network?: string
}

interface Holding {
  asset: Asset
  amount: number
  valueUSD?: number
}

interface WalletData {
  walletId: string
  owner: Principal
  blockchainNetwork: string
  balance: number
  connectedExchange: string
}

interface Insurance {
  user: Principal
  walletAddress: string
  backUpWalletAddress: string
  email: string
  dateStart: bigint
  interval: bigint
  warnCount: number
}

interface ProcessedAsset {
  name: string
  symbol: string
  balance: string
  value: string
  change24h: string
  changeAmount: string
  iconUrl: string
}

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

// --- MAIN COMPONENT ---
export default function WalletPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isProtocolSetup, setIsProtocolSetup] = useState(false)
  const [isBalanceVisible, setIsBalanceVisible] = useState(true)
  const [copiedAddress, setCopiedAddress] = useState(false)
  const [totalBalance, setTotalBalance] = useState(0)
  const [assets, setAssets] = useState<ProcessedAsset[]>([])
  const [status, setStatus] = useState("")
  const [beneficiary, setBeneficiary] = useState("")
  const [inactivityPeriod, setInactivityPeriod] = useState("6 Months")
  const [initialDataLoaded, setInitialDataLoaded] = useState(false)
  const [hasWallet, setHasWallet] = useState<boolean | null>(null)
  const [walletAddress, setWalletAddress] = useState("")

  const { isAuthenticated, principal, authChecked } = useAuthContext()

  const handleBeneficiaryChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setBeneficiary(e.target.value)
  }, [])

  const copyAddress = useCallback(() => {
    if (walletAddress) {
      navigator.clipboard.writeText(walletAddress)
      setCopiedAddress(true)
      setTimeout(() => setCopiedAddress(false), 2000)
    }
  }, [walletAddress])

  const handleCreateWallet = async () => {
    if (!isAuthenticated || !principal || principal.isAnonymous()) {
      setStatus("Please log in to create a wallet.")
      return
    }

    try {
      setStatus("Creating wallet...");
      const address = generateWalletAddress();

      const newWallet = await wallet_backend.addWallet(address, principal, "network1", 0, "exchange1");

      console.log("[v0] Wallet created:", newWallet)
      setHasWallet(true)
      setWalletAddress(address)
      setStatus("Wallet created successfully! You can now use all features.")

      setInitialDataLoaded(false)
    } catch (error) {
      console.error("Failed to create wallet:", error)
      setStatus("Failed to create wallet: " + (error as Error).message)
    }
  }

  function generateWalletAddress() {
    // 20 byte = 160 bit
    const array = new Uint8Array(20);
    window.crypto.getRandomValues(array); // generate random bytes
    // ubah ke hex string
    const address = "0x" + Array.from(array)
      .map(b => b.toString(16).padStart(2, "0"))
      .join("");
    return address;
  }

  useEffect(() => {
    if (initialDataLoaded) return

    async function initialize() {
      if (!isAuthenticated || !authChecked || !principal || principal.isAnonymous()) {
        console.log("User not authenticated or principal is anonymous")
        setStatus("Please log in to view your wallet.")
        return
      }

      try {
        console.log("[v0] Fetching user data for principal:", principal.toText())
        const userDataRaw = await user_backend.getUserData(principal)
        console.log("[v0] User data raw:", userDataRaw)
        const userData = userDataRaw ? userDataRaw : null
        console.log("[v0] User data retrieved:", userData)

        console.log("[v0] Fetching wallets for principal:", principal.toText())
        const wallets = await wallet_backend.getWalletsByPrincipal(principal)
        console.log("[v0] Wallets retrieved:", wallets)
        const walletData = wallets.length > 0 ? wallets[0] : null

        if (!walletData) {
          setHasWallet(false)
          setInitialDataLoaded(true)
          return
        }

        setHasWallet(true)
        setWalletAddress(walletData.walletId)

        const insurances = await insurance_backend.getInsurancesByPrincipal(principal)
        console.log("[v0] Insurances retrieved:", insurances)
        if (insurances.length > 0) {
          setBeneficiary(insurances[0].backUpWalletAddress)
          const interval = Number(insurances[0].interval) / (1000 * 60 * 60 * 24 * 30)
          setInactivityPeriod(
            interval >= 60 ? "5 Years" : interval >= 24 ? "2 Years" : interval >= 12 ? "1 Year" : "6 Months",
          )
          setIsProtocolSetup(true)
        }
      } catch (error) {
        console.log("[v0] User data or insurance not found:", error)
      }

      try {
        console.log("[v0] Fetching wallets for principal:", principal.toText())
        const wallets = await wallet_backend.getWalletsByPrincipal(principal)
        console.log("[v0] Wallets retrieved:", wallets)
        const walletData = wallets.length > 0 ? wallets[0] : null
        if (walletData) {
          setTotalBalance(walletData.balance);
          const holdings = await wallet_backend.getHoldingsByWalletId(walletData.walletId)
          const holdingsData = holdings.length > 0 ? holdings[0][1] : []

          const assetPromises = holdingsData.map(async (holding: Holding): Promise<ProcessedAsset> => {
            const asset = holding.asset
            let assetData: Asset | null | undefined = null
            try {
              const assetDataRaw = await marketData_backend.getAssetByAssetId(asset.assetId)
              assetData = Array.isArray(assetDataRaw) && assetDataRaw.length > 0 ? assetDataRaw[0] : null
            } catch {
              console.log("[v0] Asset data not found for:", asset.assetId)
              assetData = null
            }

            const currentPrice = assetData?.currentPrice ?? 16.0
            const value = holding.valueUSD ?? holding.amount * currentPrice

            // Generate mock price change data
            const changePercent = (Math.random() - 0.5) * 10 // Random between -5% and +5%
            const changeValue = value * (changePercent / 100)

            return {
              name: asset.name,
              symbol: asset.symbol,
              balance: holding.amount.toString(),
              value: value.toLocaleString("en-US", {
                style: "currency",
                currency: "USD",
              }),
              change24h: `${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`,
              changeAmount: `${changeValue >= 0 ? '+' : ''}$${Math.abs(changeValue).toFixed(2)}`,
              iconUrl: `https://placehold.co/48x48/${asset.symbol === "BTC" ? "F7931A" : asset.symbol === "ETH" ? "627EEA" : "9945FF"
                }/FFFFFF?text=${asset.symbol[0]}`,
            }
          })

          const assetList = await Promise.all(assetPromises)
          setAssets(assetList)

          const total = assetList.reduce((sum: number, asset: ProcessedAsset) => {
            const numericValue = Number.parseFloat(asset.value.replace(/[$,]/g, ""))
            return sum + numericValue
          }, 0)
          setTotalBalance(total)
        }
      } catch (error) {
        console.error("Initialization failed:", error)
        setStatus("Failed to initialize: " + (error as Error).message)
      }

      setInitialDataLoaded(true)
    }
    initialize()
  }, [isAuthenticated, authChecked, principal, initialDataLoaded])

  const handleSaveSettings = async () => {
    if (!isAuthenticated || !principal || principal.isAnonymous()) {
      setStatus("Please log in to save inheritance settings.")
      return
    }

    try {
      const wallets = await wallet_backend.getWalletsByPrincipal(principal)
      const walletData = wallets.length > 0 ? wallets[0] : null
      if (!walletData) {
        setStatus("No wallet found for the user.")
        return
      }

      const interval =
        inactivityPeriod === "5 Years"
          ? BigInt(60 * 30 * 24 * 60 * 60 * 1000 * 1000 * 1000)
          : inactivityPeriod === "2 Years"
            ? BigInt(24 * 30 * 24 * 60 * 60 * 1000 * 1000 * 1000)
            : inactivityPeriod === "1 Year"
              ? BigInt(12 * 30 * 24 * 60 * 60 * 1000 * 1000 * 1000)
              : BigInt(6 * 30 * 24 * 60 * 60 * 1000 * 1000 * 1000)

      const newInsurance = await insurance_backend.createInsurance(
        principal,
        walletData.walletId,
        beneficiary,
        "user@example.com",
        BigInt(Date.now() * 1000 * 1000),
        interval,
      )

      console.log("[v0] Insurance created:", newInsurance)
      setIsProtocolSetup(true)
      setIsModalOpen(false)
      setStatus("Inheritance protocol set up successfully.")
    } catch (error) {
      console.error("Failed to set inheritance protocol:", error)
      setStatus("Failed to save settings: " + (error as Error).message)
    }
  }

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

        {hasWallet === false ? (
          <motion.div variants={itemVariants}>
            <Card className="!p-8 mb-8 text-center bg-gradient-to-br from-zinc-800/50 to-zinc-700/50 border-zinc-600/50">
              <motion.div 
                className="text-[#87efff] mb-4"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", delay: 0.2 }}
              >
                <WalletIcon size={64} className="mx-auto" />
              </motion.div>
              <motion.h2
                className="text-2xl font-bold text-white mb-4"
                style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                No Wallet Found
              </motion.h2>
              <motion.p 
                className="text-zinc-400 mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                You need to create a wallet first to access all features including asset management and inheritance
                protocol.
              </motion.p>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <Button
                  onClick={handleCreateWallet}
                  className="bg-[#87efff] border-[#87efff] text-zinc-900 hover:bg-[#6fe2f6] hover:border-[#6fe2f6] font-medium"
                  aria-label="Create your first wallet"
                >
                  <PlusCircle size={16} className="mr-2" />
                  Create Your First Wallet
                </Button>
              </motion.div>
            </Card>
          </motion.div>
        ) : (
          <>
            {/* Wallet Address Card */}
            {walletAddress && (
              <motion.div variants={itemVariants} className="mb-6">
                <Card className="!p-4 bg-gradient-to-r from-zinc-800/50 to-zinc-700/50 border-zinc-600/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <motion.div 
                        className="p-2 bg-blue-500/20 rounded-lg"
                        whileHover={{ scale: 1.1 }}
                      >
                        <Wallet size={20} className="text-blue-400" />
                      </motion.div>
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
            )}

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
                      <p className="text-zinc-400 text-sm mb-1">Your Balance</p>
                      <motion.p 
                        className={`text-4xl font-bold mt-1 ${isBalanceVisible ? 'text-white' : 'text-zinc-500'}`}
                        key={isBalanceVisible ? 'visible' : 'hidden'}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        {isBalanceVisible ? `$${totalBalance.toLocaleString()}` : '••••••••'}
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
                          onClick={() => setStatus("Deposit functionality coming soon")}
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
                          onClick={() => setStatus("Withdraw functionality coming soon")}
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
                {assets.length > 0 ? (
                  assets.map((asset, index) => (
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
                              {isBalanceVisible ? asset.value : '••••••'}
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
                  ))
                ) : (
                  <motion.div 
                    className="py-8 text-center"
                    variants={itemVariants}
                  >
                    <p className="mb-4 text-zinc-400">No assets found. Please connect your wallet or add holdings.</p>
                  </motion.div>
                )}
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
          </>
        )}
      </motion.div>

      {status && (
        <motion.div 
          className="fixed p-4 text-white rounded-lg bottom-4 right-4 bg-zinc-900/90 border border-zinc-700"
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 100 }}
        >
          {status}
        </motion.div>
      )}
      
      <LegacyButton />
    </>
  )
}