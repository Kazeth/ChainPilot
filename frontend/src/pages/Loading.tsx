"use client"

import { useEffect, useState } from "react"
import { BrainCircuit, TrendingUp, Shield, Network } from "lucide-react"

export default function LoadingPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [scannerPosition, setScannerPosition] = useState(0)

  const loadingSteps = [
    "Initializing AI Engine...",
    "Connecting to Blockchain...",
    "Analyzing Market Data...",
    "Securing Your Assets...",
    "Calibrating Neural Networks...",
    "Establishing Secure Channels...",
    "Loading Trading Algorithms...",
    "Optimizing Performance Matrix...",
  ]

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStep(Math.floor(Math.random() * loadingSteps.length))
    }, 1500)

    const scannerInterval = setInterval(() => {
      setScannerPosition((prev) => (prev + 1) % 100)
    }, 50)

    return () => {
      clearInterval(stepInterval)
      clearInterval(scannerInterval)
    }
  }, [loadingSteps.length])

  return (
    <div className="h-screen w-screen bg-zinc-900 flex items-center justify-center overflow-hidden relative">
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0 bg-gradient-to-br from-[#87efff]/10 via-transparent to-[#87efff]/5"></div>
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(rgba(135, 239, 255, 0.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(135, 239, 255, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: "50px 50px",
            animation: "grid-move 20s linear infinite",
          }}
        ></div>
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(rgba(135, 239, 255, 0.02) 1px, transparent 1px),
              linear-gradient(90deg, rgba(135, 239, 255, 0.02) 1px, transparent 1px)
            `,
            backgroundSize: "25px 25px",
            animation: "grid-move-reverse 15s linear infinite",
          }}
        ></div>
      </div>

      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute w-full h-1 bg-gradient-to-r from-transparent via-[#87efff]/40 to-transparent animate-scanner-sweep"
          style={{
            top: `${scannerPosition}%`,
            filter: "blur(1px)",
          }}
        ></div>
        <div
          className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-[#87efff]/60 to-transparent"
          style={{
            top: `${scannerPosition}%`,
          }}
        ></div>
      </div>

      <div className="absolute inset-0 pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="absolute w-px h-full bg-gradient-to-b from-transparent via-[#87efff]/15 to-transparent animate-data-stream"
            style={{
              left: `${15 + i * 15}%`,
              animationDelay: `${i * 0.8}s`,
              animationDuration: "4s",
            }}
          ></div>
        ))}
      </div>

      {/* Main loading content */}
      <div className="relative z-10 text-center max-w-md mx-auto px-6">
        {/* Logo/Brand area */}
        <div className="mb-12">
          <div className="relative inline-block">
            <div className="w-24 h-24 mx-auto mb-6 relative">
              <div className="absolute inset-0 bg-[#87efff]/5 rounded-full animate-pulse-ring-1"></div>
              <div className="absolute inset-1 bg-[#87efff]/10 rounded-full animate-pulse-ring-2"></div>
              <div className="absolute inset-2 bg-[#87efff]/15 rounded-full animate-pulse-ring-3"></div>
              <div className="absolute inset-4 bg-[#87efff] rounded-full flex items-center justify-center animate-spin-slow">
                <BrainCircuit className="w-10 h-10 text-zinc-900" />
              </div>
              <div className="absolute inset-0 border-2 border-[#87efff]/20 rounded-full animate-spin"></div>
              <div className="absolute inset-2 border border-[#87efff]/30 rounded-full animate-spin-reverse"></div>
            </div>

            <div className="absolute inset-0 animate-glitch-1 -z-10 top-[110px]">
              <h1 className="text-4xl font-bold text-[#87efff]/15" style={{ fontFamily: "'Sprintura', serif" }}>
                ChainPilot
              </h1>
            </div>
            <div className="absolute inset-0 animate-glitch-2 -z-10 top-[130px]">
              <h1 className="text-4xl font-bold text-[#ff87ef]/10" style={{ fontFamily: "'Sprintura', serif" }}>
                ChainPilot
              </h1>
            </div>

            <h1
              className="text-4xl font-bold text-white mb-2 relative animate-text-glow-subtle"
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
              <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "0.6s" }}>
                i
              </span>
              <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "0.7s" }}>
                l
              </span>
              <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "0.8s" }}>
                o
              </span>
              <span className="inline-block animate-letter-float text-[#87efff]" style={{ animationDelay: "0.9s" }}>
                t
              </span>
            </h1>

            <div className="absolute inset-0 pointer-events-none">
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className="absolute w-1 h-1 bg-[#87efff]/40 rounded-full animate-orbit"
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
        </div>

        <div className="mb-8">
          <div className="text-center">
            <div className="mb-4">
              <p className="text-white font-medium text-lg">{loadingSteps[currentStep]}</p>
            </div>

            <div className="flex justify-center space-x-2">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 h-2 bg-[#87efff]/60 rounded-full animate-matrix-rain"
                  style={{
                    animationDelay: `${i * 0.15}s`,
                    animationDuration: "1.5s",
                  }}
                ></div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6 max-w-xs mx-auto">
          {[
            { icon: TrendingUp, label: "AI Signals", delay: "0s" },
            { icon: Shield, label: "Security", delay: "0.2s" },
            { icon: Network, label: "Neural", delay: "0.4s" },
          ].map(({ icon: Icon, label, delay }) => (
            <div
              key={label}
              className="text-center opacity-0 animate-fade-in"
              style={{ animationDelay: delay, animationFillMode: "forwards" }}
            >
              <div className="relative mb-2">
                <Icon className="w-5 h-5 text-[#87efff] mx-auto" />
              </div>
              <p className="text-xs text-zinc-400">{label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="absolute inset-0 pointer-events-none">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className={`absolute bg-[#87efff]/30 rounded-full animate-float ${
              i % 3 === 0 ? "w-1 h-1" : i % 3 === 1 ? "w-0.5 h-0.5" : "w-1.5 h-1.5"
            }`}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${2 + Math.random() * 6}s`,
            }}
          ></div>
        ))}
      </div>

      <style>{`
        @keyframes grid-move {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes grid-move-reverse {
          0% { transform: translate(0, 0); }
          100% { transform: translate(-25px, -25px); }
        }
        
        @keyframes scanner-sweep {
          0% { opacity: 0; transform: translateY(-10px); }
          50% { opacity: 1; }
          100% { opacity: 0; transform: translateY(10px); }
        }
        
        @keyframes data-stream {
          0% { transform: translateY(-100vh); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(100vh); opacity: 0; }
        }
        
        @keyframes pulse-ring-1 {
          0%, 100% { transform: scale(1); opacity: 0.3; }
          50% { transform: scale(1.1); opacity: 0.1; }
        }
        
        @keyframes pulse-ring-2 {
          0%, 100% { transform: scale(1); opacity: 0.4; }
          50% { transform: scale(1.15); opacity: 0.2; }
        }
        
        @keyframes pulse-ring-3 {
          0%, 100% { transform: scale(1); opacity: 0.5; }
          50% { transform: scale(1.2); opacity: 0.3; }
        }
        
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        @keyframes spin-reverse {
          from { transform: rotate(360deg); }
          to { transform: rotate(0deg); }
        }
        
        @keyframes matrix-rain {
          0%, 100% { opacity: 0.3; transform: translateY(0); }
          50% { opacity: 1; transform: translateY(-5px); }
        }
        
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        
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
        
        @keyframes text-glow-subtle {
          0%, 100% { text-shadow: 0 0 3px rgba(135, 239, 255, 0.3); }
          50% { text-shadow: 0 0 8px rgba(135, 239, 255, 0.5), 0 0 12px rgba(135, 239, 255, 0.3); }
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
        
        .animate-scanner-sweep {
          animation: scanner-sweep 3s ease-in-out infinite;
        }
        
        .animate-data-stream {
          animation: data-stream linear infinite;
        }
        
        .animate-pulse-ring-1 {
          animation: pulse-ring-1 2s ease-in-out infinite;
        }
        
        .animate-pulse-ring-2 {
          animation: pulse-ring-2 2.5s ease-in-out infinite;
        }
        
        .animate-pulse-ring-3 {
          animation: pulse-ring-3 3s ease-in-out infinite;
        }
        
        .animate-spin-slow {
          animation: spin-slow 8s linear infinite;
        }
        
        .animate-spin-reverse {
          animation: spin-reverse 6s linear infinite;
        }
        
        .animate-matrix-rain {
          animation: matrix-rain ease-in-out infinite;
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
        
        .animate-text-glow-subtle {
          animation: text-glow-subtle 2s ease-in-out infinite;
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
