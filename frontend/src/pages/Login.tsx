

import type React from "react"

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Mail, Lock, ArrowRight, Eye, EyeOff } from "lucide-react"

export default function LoginPage() {
  const [email, setEmail] = useState<string>("")
  const [password, setPassword] = useState<string>("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1200))

    // TODO: Implement login logic
    navigate("/dashboard")
    setIsLoading(false)
  }

  return (
    <div className="min-h-screen w-screen bg-zinc-900 flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-zinc-800 to-zinc-900 items-center justify-center p-12">
        <div className="max-w-md text-center">
          <div className="w-20 h-20 bg-[#87efff] rounded-2xl flex items-center justify-center mx-auto mb-8">
            <div className="w-10 h-10 bg-zinc-900 rounded-lg"></div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">ChainPilot</h1>
          <p className="text-zinc-400 text-lg leading-relaxed">
            Navigate the crypto markets with AI-powered precision and confidence. Your intelligent trading companion
            awaits.
          </p>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="w-16 h-16 bg-[#87efff] rounded-xl flex items-center justify-center mx-auto mb-4">
              <div className="w-8 h-8 bg-zinc-900 rounded-md"></div>
            </div>
            <h1 className="text-2xl font-bold text-white">ChainPilot</h1>
          </div>

          {/* Form Header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">Sign In</h2>
            <p className="text-zinc-400">Access your trading dashboard</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-zinc-300">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-zinc-400" />
                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-3 bg-zinc-800/50 border border-zinc-600 rounded-xl text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-[#87efff] focus:border-transparent transition-all duration-200"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium text-zinc-300">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-zinc-400" />
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-10 pr-12 py-3 bg-zinc-800/50 border border-zinc-600 rounded-xl text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-[#87efff] focus:border-transparent transition-all duration-200"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-zinc-400 hover:text-zinc-300 transition-colors duration-200"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="w-4 h-4 text-[#87efff] bg-zinc-800 border-zinc-600 rounded focus:ring-[#87efff] focus:ring-2"
                />
                <span className="ml-2 text-sm text-zinc-400">Remember me</span>
              </label>
              <a href="#" className="text-sm text-[#87efff] hover:text-[#6fe2f6] transition-colors duration-200">
                Forgot password?
              </a>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#87efff] hover:bg-[#6fe2f6] text-zinc-900 font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group shadow-lg shadow-[#87efff]/20"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-zinc-900/20 border-t-zinc-900 rounded-full animate-spin" />
              ) : (
                <>
                  Sign In to Dashboard
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-200" />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-zinc-400 text-sm">
              Don't have an account?{" "}
              <a href="#" className="text-[#87efff] hover:text-[#6fe2f6] font-medium transition-colors duration-200">
                Sign up for free
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
