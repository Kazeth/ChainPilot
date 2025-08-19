"use client"

import { useEffect, useState } from "react"
import { BrainCircuit, TrendingUp, Shield, Zap } from "lucide-react"

export default function LoadingPage() {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)

  const loadingSteps = [
    "Initializing AI Engine...",
    "Connecting to Blockchain...",
    "Analyzing Market Data...",
    "Securing Your Assets...",
    "Ready to Launch!",
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 2
      })
    }, 100)

    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= loadingSteps.length - 1) {
          clearInterval(stepInterval)
          return prev
        }
        return prev + 1
      })
    }, 2000)

    return () => {
      clearInterval(interval)
      clearInterval(stepInterval)
    }
  }, [loadingSteps.length])

  return (
    <div className="h-screen w-screen bg-zinc-900 flex items-center justify-center overflow-hidden relative">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-gradient-to-br from-[#87efff]/20 via-transparent to-[#87efff]/10"></div>
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `
              linear-gradient(rgba(135, 239, 255, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(135, 239, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: "50px 50px",
            animation: "grid-move 20s linear infinite",
          }}
        ></div>
      </div>

      {/* Main loading content */}
      <div className="relative z-10 text-center max-w-md mx-auto px-6">
        {/* Logo/Brand area */}
        <div className="mb-12">
          <div className="relative inline-block">
            <div className="w-20 h-20 mx-auto mb-6 relative">
              <div className="absolute inset-0 bg-[#87efff]/20 rounded-full animate-pulse"></div>
              <div className="absolute inset-2 bg-[#87efff]/40 rounded-full animate-ping"></div>
              <div className="absolute inset-4 bg-[#87efff] rounded-full flex items-center justify-center">
                <BrainCircuit className="w-8 h-8 text-zinc-900" />
              </div>
            </div>

            <div className="relative">
              {/* Moving scan lines */}
              <div className="absolute inset-0 overflow-hidden">
                <div className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-[#87efff] to-transparent animate-scan-line"></div>
                <div className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-[#87efff]/60 to-transparent animate-scan-line-2"></div>
              </div>

              {/* Glitch overlay */}
              <div className="absolute inset-0 animate-glitch-1">
                <h1 className="text-4xl font-bold text-[#87efff]/30" style={{ fontFamily: "'Sprintura', serif" }}>
                  ChainPilot
                </h1>
              </div>
              <div className="absolute inset-0 animate-glitch-2">
                <h1 className="text-4xl font-bold text-[#ff87ef]/20" style={{ fontFamily: "'Sprintura', serif" }}>
                  ChainPilot
                </h1>
              </div>

              {/* Main text with typing effect */}
              <h1
                className="text-4xl font-bold text-white mb-2 relative z-10 animate-text-glow"
                style={{ fontFamily: "'Sprintura', serif" }}
              >
                <span className="inline-block animate-letter-float" style={{ animationDelay: "0s" }}>
                  C
                </span>
                <span className="inline-block animate-letter-float" style={{ animationDelay: "0.1s" }}>
                  h
                </span>
                <span className="inline-block animate-letter-float" style={{ animationDelay: "0.2s" }}>
                  a
                </span>
                <span className="inline-block animate-letter-float" style={{ animationDelay: "0.3s" }}>
                  i
                </span>
                <span className="inline-block animate-letter-float" style={{ animationDelay: "0.4s" }}>
                  n
                </span>
                <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "0.5s" }}>
                  P
                </span>
                <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "0.8s" }}>
                  i
                </span>
                <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "0.9s" }}>
                  l
                </span>
                <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "1s" }}>
                  o
                </span>
                <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "1.1s" }}>
                  t
                </span>
              </h1>

              {/* High-speed particles around text */}
              <div className="absolute inset-0 pointer-events-none">
                {[...Array(8)].map((_, i) => (
                  <div
                    key={i}
                    className="absolute w-1 h-1 bg-[#87efff] rounded-full animate-orbit"
                    style={{
                      left: "50%",
                      top: "50%",
                      animationDelay: `${i * 0.2}s`,
                      animationDuration: "2s",
                      transform: `rotate(${i * 45}deg) translateX(60px)`,
                    }}
                  ></div>
                ))}
              </div>
            </div>

            <p className="text-zinc-400 animate-pulse" style={{ fontFamily: "'Creati Display', sans-serif" }}>
              AI-Powered Trading Platform
            </p>
          </div>
        </div>

        {/* Progress section */}
        <div className="mb-8">
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-zinc-400">Loading Progress</span>
              <span className="text-sm text-[#87efff] font-mono">{progress}%</span>
            </div>
            <div className="w-full bg-zinc-700 rounded-full h-2 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#87efff] to-[#6fe2f6] rounded-full transition-all duration-300 ease-out relative"
                style={{ width: `${progress}%` }}
              >
                <div className="absolute inset-0 bg-white/30 animate-pulse rounded-full"></div>
              </div>
            </div>
          </div>

          {/* Current step */}
          <div className="text-center">
            <p className="text-white font-medium mb-4">{loadingSteps[currentStep]}</p>

            {/* Loading dots animation */}
            <div className="flex justify-center space-x-1">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-2 h-2 bg-[#87efff] rounded-full animate-bounce"
                  style={{ animationDelay: `${i * 0.2}s` }}
                ></div>
              ))}
            </div>
          </div>
        </div>

        {/* Feature icons */}
        <div className="flex justify-center space-x-8">
          {[
            { icon: TrendingUp, label: "AI Signals", delay: "0s" },
            { icon: Shield, label: "Security", delay: "0.5s" },
            { icon: Zap, label: "Speed", delay: "1s" },
          ].map(({ icon: Icon, label, delay }) => (
            <div
              key={label}
              className="text-center opacity-0 animate-fade-in"
              style={{ animationDelay: delay, animationFillMode: "forwards" }}
            >
              <Icon className="w-6 h-6 text-[#87efff] mx-auto mb-2" />
              <p className="text-xs text-zinc-400">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Floating particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-[#87efff]/60 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${3 + Math.random() * 4}s`,
            }}
          ></div>
        ))}
      </div>

      <style>{`
        @keyframes grid-move {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        /* Added high-speed futuristic animations */
        @keyframes scan-line {
          0% { transform: translateY(-20px); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(80px); opacity: 0; }
        }
        
        @keyframes scan-line-2 {
          0% { transform: translateY(80px); opacity: 0; }
          50% { opacity: 0.6; }
          100% { transform: translateY(-20px); opacity: 0; }
        }
        
        @keyframes glitch-1 {
          0%, 100% { transform: translateX(0); }
          20% { transform: translateX(-2px); }
          40% { transform: translateX(2px); }
          60% { transform: translateX(-1px); }
          80% { transform: translateX(1px); }
        }
        
        @keyframes glitch-2 {
          0%, 100% { transform: translateX(0); }
          10% { transform: translateX(2px); }
          30% { transform: translateX(-2px); }
          50% { transform: translateX(1px); }
          70% { transform: translateX(-1px); }
          90% { transform: translateX(2px); }
        }
        
        @keyframes text-glow {
          0%, 100% { text-shadow: 0 0 5px rgba(135, 239, 255, 0.5); }
          50% { text-shadow: 0 0 20px rgba(135, 239, 255, 0.8), 0 0 30px rgba(135, 239, 255, 0.6); }
        }
        
        @keyframes letter-float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-3px); }
        }
        
        @keyframes orbit {
          0% { transform: rotate(0deg) translateX(60px) rotate(0deg); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: rotate(360deg) translateX(60px) rotate(-360deg); opacity: 0; }
        }
        
        .animate-fade-in {
          animation: fade-in 0.8s ease-out;
        }
        
        .animate-float {
          animation: float linear infinite;
        }
        
        .animate-scan-line {
          animation: scan-line 1.5s ease-in-out infinite;
        }
        
        .animate-scan-line-2 {
          animation: scan-line-2 2s ease-in-out infinite;
        }
        
        .animate-glitch-1 {
          animation: glitch-1 0.3s ease-in-out infinite alternate;
        }
        
        .animate-glitch-2 {
          animation: glitch-2 0.4s ease-in-out infinite alternate-reverse;
        }
        
        .animate-text-glow {
          animation: text-glow 2s ease-in-out infinite;
        }
        
        .animate-letter-float {
          animation: letter-float 1s ease-in-out infinite;
        }
        
        .animate-orbit {
          animation: orbit linear infinite;
        }
      `}</style>
    </div>
  )
}
