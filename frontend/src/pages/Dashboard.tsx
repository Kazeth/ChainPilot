"use client"

import { useEffect, useState } from "react"
import { TrendingUp, Wallet, Activity, Shield, RefreshCw } from "lucide-react"

export default function DashboardPage() {
  const [data, setData] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchBalance = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch("http://localhost:8001/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: "get balance bitcoin address bc1q8sxznvhualuyyes0ded7kgt33876phpjhp29rs?",
        }),
      })
      const result = await response.json()
      setData(result.answer)
    } catch (err) {
      setError("Failed to fetch balance data")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchBalance()
  }, [])

  return (
    <div className="h-screen w-screen bg-zinc-900 p-4 md:p-6 overflow-hidden">
      <div className="max-w-7xl mx-auto h-full flex flex-col">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-zinc-400">Welcome to your AI Crypto Agent dashboard</p>
        </div>

        {/* Change 3: Create a new wrapper for the main content that will grow and handle its own scrolling */}
        <div className="flex-1 min-h-0 overflow-y-auto pr-2">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-zinc-800/50 backdrop-blur-sm border border-zinc-700 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-zinc-400 text-sm">Portfolio Value</p>
                  <p className="text-2xl font-bold text-white">$24,580.32</p>
                  <p className="text-[#87efff] text-sm">+12.5% today</p>
                </div>
                <TrendingUp className="h-8 w-8 text-[#87efff]" />
              </div>
            </div>

            <div className="bg-zinc-800/50 backdrop-blur-sm border border-zinc-700 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-zinc-400 text-sm">Active Trades</p>
                  <p className="text-2xl font-bold text-white">7</p>
                  <p className="text-green-400 text-sm">3 profitable</p>
                </div>
                <Activity className="h-8 w-8 text-[#87efff]" />
              </div>
            </div>

            <div className="bg-zinc-800/50 backdrop-blur-sm border border-zinc-700 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-zinc-400 text-sm">AI Signals</p>
                  <p className="text-2xl font-bold text-white">23</p>
                  <p className="text-[#87efff] text-sm">5 new today</p>
                </div>
                <Shield className="h-8 w-8 text-[#87efff]" />
              </div>
            </div>

            <div className="bg-zinc-800/50 backdrop-blur-sm border border-zinc-700 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-zinc-400 text-sm">Success Rate</p>
                  <p className="text-2xl font-bold text-white">87.3%</p>
                  <p className="text-green-400 text-sm">Above average</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-400" />
              </div>
            </div>
          </div>

          {/* Balance Section */}
          <div className="bg-zinc-800/50 backdrop-blur-sm border border-zinc-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Wallet className="h-6 w-6 text-[#87efff]" />
                <h2 className="text-xl font-semibold text-white">Wallet Balance</h2>
              </div>
              <button
                onClick={fetchBalance}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-[#87efff] hover:bg-[#6fe2f6] text-zinc-900 font-medium rounded-lg transition-all duration-200 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
                Refresh
              </button>
            </div>

            {/* Balance Content */}
            <div className="bg-zinc-700/30 rounded-lg p-4">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-8 h-8 border-2 border-[#87efff]/20 border-t-[#87efff] rounded-full animate-spin" />
                </div>
              ) : error ? (
                <div className="text-center py-8">
                  <p className="text-red-400 mb-2">⚠️ {error}</p>
                  <button
                    onClick={fetchBalance}
                    className="text-[#87efff] hover:text-[#6fe2f6] transition-colors duration-200"
                  >
                    Try again
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-400">Address:</span>
                    <span className="text-white font-mono text-sm">bc1q8sx...hp29rs</span>
                  </div>
                  <div className="border-t border-zinc-600 pt-4">
                    <h3 className="text-white font-medium mb-2">Balance Details:</h3>
                    <pre className="text-sm text-zinc-300 bg-zinc-800/50 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}