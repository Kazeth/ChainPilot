"use client"

import type React from "react"

import { useState, useEffect, useCallback } from "react"
import { ArrowDownLeft, ArrowUpRight, ShieldCheck, PlusCircle, Settings } from "lucide-react"
import Button from "../components/ui/button"
import Card from "../components/ui/card"
import Input from "../components/ui/input"
import InsuranceModal from "../components/ui/insuranceModal"
import type { Principal } from "@dfinity/principal"
import { HttpAgent } from "@dfinity/agent"
import LegacyButton from "@/components/LegacyButton"
import { useAuthContext } from "@/context/AuthContext"
import { canisterId as walletCanisterId, createActor as createWalletActor } from "@/declarations/wallet_backend"
import {
  canisterId as marketDataCanisterId,
  createActor as createMarketDataActor,
} from "@/declarations/marketData_backend"
import { canisterId as userCanisterId, createActor as createUserActor } from "@/declarations/user_backend"
import {
  canisterId as insuranceCanisterId,
  createActor as createInsuranceActor,
} from "@/declarations/insurance_backend"
import { motion } from "framer-motion"

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

interface Wallet {
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
  iconUrl: string
}

// --- MAIN COMPONENT ---
export default function WalletPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isProtocolSetup, setIsProtocolSetup] = useState(false)
  const [totalBalance, setTotalBalance] = useState(0)
  const [assets, setAssets] = useState<ProcessedAsset[]>([])
  const [status, setStatus] = useState("")
  const [beneficiary, setBeneficiary] = useState("")
  const [inactivityPeriod, setInactivityPeriod] = useState("6 Months")
  const [initialDataLoaded, setInitialDataLoaded] = useState(false)

  const { isAuthenticated, principal, authChecked, actor } = useAuthContext()

  const handleBeneficiaryChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setBeneficiary(e.target.value)
  }, [])

  useEffect(() => {
    if (initialDataLoaded) return

    async function initialize() {
      if (!isAuthenticated || !authChecked || !principal || principal.isAnonymous()) {
        console.log("User not authenticated or principal is anonymous")
        setStatus("Please log in to view your wallet.")
        return
      }

      const agent = new HttpAgent()
      if (process.env.DFX_NETWORK !== "ic") {
        await agent.fetchRootKey().catch(console.error)
      }

      const user_backend = createUserActor(userCanisterId, { agent })
      const wallet_backend = createWalletActor(walletCanisterId, { agent })
      const marketData_backend = createMarketDataActor(marketDataCanisterId, { agent })
      const insurance_backend = createInsuranceActor(insuranceCanisterId, { agent })

      try {
        console.log("[v0] Fetching user data for principal:", principal.toText())
        const userDataRaw = await user_backend.getUserData(principal)
        console.log("[v0] User data raw:", userDataRaw)
        const userData = userDataRaw ? userDataRaw : null
        console.log("[v0] User data retrieved:", userData)

        const insurances = await insurance_backend.getInsurancesByPrincipal(principal)
        console.log("[v0] Insurances retrieved:", insurances)
        if (insurances.length > 0) {
          setBeneficiary(insurances[0].backUpWalletAddress)
          const interval = Number(insurances[0].interval) / (1000 * 60 * 60 * 24 * 30) // Convert nanoseconds to months
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

            return {
              name: asset.name,
              symbol: asset.symbol,
              balance: holding.amount.toString(),
              value: value.toLocaleString("en-US", {
                style: "currency",
                currency: "USD",
              }),
              iconUrl: `https://placehold.co/40x40/${
                asset.symbol === "BTC" ? "F7931A" : asset.symbol === "ETH" ? "627EEA" : "9945FF"
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

    const agent = new HttpAgent()
    if (process.env.DFX_NETWORK !== "ic") {
      await agent.fetchRootKey().catch(console.error)
    }

    const insurance_backend = createInsuranceActor(insuranceCanisterId, { agent })
    const wallet_backend = createWalletActor(walletCanisterId, { agent })

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
              : BigInt(6 * 30 * 24 * 60 * 60 * 1000 * 1000 * 1000) // Convert to nanoseconds

      const newInsurance = await insurance_backend.createInsurance(
        principal,
        walletData.walletId,
        beneficiary,
        "user@example.com", // Placeholder; update with actual user email
        BigInt(Date.now() * 1000 * 1000), // Current time in nanoseconds
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
      <div className="container px-4 py-8 mx-auto" style={{ fontFamily: "'Creati Display', sans-serif" }}>
        <div>
          <h1
            className="mb-8 text-4xl font-bold text-white"
            style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
          >
            My Wallet
          </h1>
          <div className="flex mt-4 space-x-3 md:mt-0">
            <motion.button
              className="border-white text-white bg-transparent border-[#87efff]"
              aria-label="Demo Wallet"
              onClick={() => setStatus("Deposit functionality coming soon")}
              whileTap={{ scale: 0.95 }}
            >
              Create Demo Wallet
            </motion.button>
          </div>
        </div>

        {/* Total Balance Card */}
        <Card className="!p-6 mb-8">
          <div className="flex flex-col items-start justify-between md:flex-row md:items-center">
            <div>
              <p className="text-sm text-zinc-400">Total Balance</p>
              <p className="mt-1 text-4xl font-bold text-white">
                $
                {totalBalance.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </p>
              <p className="mt-1 text-sm text-green-400">+2.5% vs last 24h</p>
            </div>
            <div className="flex mt-4 space-x-3 md:mt-0">
              <Button
                className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff]"
                aria-label="Deposit funds"
                onClick={() => setStatus("Deposit functionality coming soon")}
              >
                <ArrowDownLeft size={16} className="mr-2" /> Deposit
              </Button>
              <Button
                className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff]"
                aria-label="Withdraw funds"
                onClick={() => setStatus("Withdraw functionality coming soon")}
              >
                <ArrowUpRight size={16} className="mr-2" /> Withdraw
              </Button>
            </div>
          </div>
        </Card>

        {/* Assets List */}
        <div className="mb-12 space-y-4">
          <h2 className="text-2xl font-semibold text-white" style={{ fontFamily: "'Creati Display Bold', sans-serif" }}>
            Your Assets
          </h2>
          {assets.length > 0 ? (
            assets.map((asset) => (
              <Card
                key={asset.symbol}
                className="flex items-center justify-between !p-4 hover:border-zinc-600 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <img src={asset.iconUrl || "/placeholder.svg"} alt={asset.name} className="w-10 h-10 rounded-full" />
                  <div>
                    <p className="text-lg font-semibold text-white">{asset.name}</p>
                    <p className="text-sm text-zinc-400">{asset.symbol}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-white">
                    {asset.balance} {asset.symbol}
                  </p>
                  <p className="text-sm text-zinc-400">{asset.value}</p>
                </div>
              </Card>
            ))
          ) : (
            <div className="py-8 text-center">
              <p className="mb-4 text-zinc-400">No assets found. Please connect your wallet or add holdings.</p>
            </div>
          )}
        </div>

        {/* Secure Inheritance Section */}
        <Card className="bg-zinc-800 border-2 border-dashed border-zinc-700 !p-6">
          <div className="flex flex-col items-start gap-6 md:flex-row md:items-center">
            <div className="text-[#87efff]">
              <ShieldCheck size={40} />
            </div>
            <div className="flex-grow">
              <h3 className="text-xl font-bold text-white" style={{ fontFamily: "'Creati Display Bold', sans-serif" }}>
                Secure Inheritance Protocol
              </h3>
              <p className="mt-1 text-zinc-400">
                {isProtocolSetup
                  ? "Your protocol is active. You can manage your settings at any time."
                  : "Protect your digital legacy. Designate a beneficiary to receive your assets in case of unforeseen circumstances."}
              </p>
            </div>
            <Button
              onClick={() => setIsModalOpen(true)}
              className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff] w-full md:w-auto"
              aria-label={isProtocolSetup ? "Manage inheritance settings" : "Set up inheritance protocol"}
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
          </div>
        </Card>
      </div>

      {/* Inheritance Modal */}
      <InsuranceModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Inheritance Protocol Settings">
        <div className="space-y-4">
          <div>
            <label htmlFor="walletAddress" className="block mb-1 text-sm font-medium text-zinc-400">
              Beneficiary Wallet Address
            </label>
            <Input
              id="walletAddress"
              type="text"
              placeholder="0x..."
              value={beneficiary}
              onChange={handleBeneficiaryChange}
              aria-label="Enter beneficiary wallet address"
            />
          </div>
          <div>
            <label htmlFor="inactivityPeriod" className="block mb-1 text-sm font-medium text-zinc-400">
              Inactivity Period
            </label>
            <select
              id="inactivityPeriod"
              value={inactivityPeriod}
              onChange={(e) => setInactivityPeriod(e.target.value)}
              className="w-full bg-zinc-800 border-2 border-zinc-700 text-white rounded-lg py-3 px-4 focus:outline-none focus:border-[#87efff]"
              aria-label="Select inactivity period"
            >
              <option>6 Months</option>
              <option>1 Year</option>
              <option>2 Years</option>
              <option>5 Years</option>
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-6">
          <Button
            onClick={() => setIsModalOpen(false)}
            className="border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white hover:border-zinc-500"
            aria-label="Cancel and close modal"
          >
            Cancel
          </Button>
          <Button
            onClick={() => handleSaveSettings()}
            className="bg-[#87efff] border-[#87efff] text-white hover:bg-[#6fe2f6] hover:border-[#6fe2f6]"
            aria-label="Save inheritance settings"
          >
            Save Settings
          </Button>
        </div>
      </InsuranceModal>

      {status && <div className="fixed p-2 text-purple-200 rounded bottom-4 right-4 bg-purple-900/30">{status}</div>}
      <LegacyButton />
    </>
  )
}
