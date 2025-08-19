"use client"

import { useState, useEffect } from "react"
import { Link } from "react-router"

export default function NotFound() {
  const [glitchText, setGlitchText] = useState("404")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const glitchChars = ["4", "0", "4", "█", "▓", "▒", "░", "◆", "◇", "◈"]
    let glitchInterval: NodeJS.Timeout

    const startGlitch = () => {
      glitchInterval = setInterval(() => {
        if (Math.random() > 0.7) {
          const randomText = Array.from(
            { length: 3 },
            () => glitchChars[Math.floor(Math.random() * glitchChars.length)],
          ).join("")
          setGlitchText(randomText)

          setTimeout(() => setGlitchText("404"), 100)
        }
      }, 2000)
    }

    startGlitch()
    return () => clearInterval(glitchInterval)
  }, [])

  if (!mounted) return null

  return (
    <div className="min-h-screen w-screen bg-zinc-900 flex items-center justify-center relative overflow-hidden">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `
            linear-gradient(rgba(135, 239, 255, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(135, 239, 255, 0.1) 1px, transparent 1px)
          `,
            backgroundSize: "50px 50px",
            animation: "grid-move 20s linear infinite",
          }}
        />
      </div>

      {/* Floating particles */}
      <div className="absolute inset-0 pointer-events-none">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-[#87efff] rounded-full opacity-60"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `float-particle ${3 + Math.random() * 4}s ease-in-out infinite`,
              animationDelay: `${Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      <div className="text-center z-10 px-4">
        {/* Glitchy 404 text */}
        <div className="relative mb-8">
          <h1 className="text-8xl md:text-9xl font-bold text-white relative">
            <span className="relative inline-block">
              {glitchText}
              {/* Scanning line effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#87efff] to-transparent opacity-30 w-full h-1 animate-scan" />

              {/* Glitch overlays */}
              <span className="absolute inset-0 text-[#87efff] opacity-70 animate-glitch-1">{glitchText}</span>
              <span className="absolute inset-0 text-red-500 opacity-50 animate-glitch-2">{glitchText}</span>
            </span>
          </h1>

          {/* Glow effect */}
          <div className="absolute inset-0 text-8xl md:text-9xl font-bold text-[#87efff] opacity-20 blur-lg animate-pulse">
            404
          </div>
        </div>

        {/* Error message */}
        <div className="mb-8 space-y-4">
          <h2 className="text-2xl md:text-3xl font-semibold text-white animate-fade-in-up">SYSTEM ERROR</h2>
          <p className="text-zinc-400 text-lg max-w-md mx-auto animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
            The requested neural pathway could not be found in the ChainPilot network.
          </p>
        </div>

        {/* Action buttons */}
        <div
          className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in-up"
          style={{ animationDelay: "0.4s" }}
        >
          <Link
            to="/"
            className="group relative px-8 py-3 bg-[#87efff] text-zinc-900 font-semibold rounded-lg transition-all duration-300 hover:bg-white hover:shadow-lg hover:shadow-[#87efff]/25 overflow-hidden"
          >
            <span className="relative z-10">Return to Base</span>
            <div className="absolute inset-0 bg-gradient-to-r from-[#87efff] to-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </Link>

          <button
            onClick={() => window.history.back()}
            className="px-8 py-3 border border-zinc-700 text-white font-semibold rounded-lg transition-all duration-300 hover:border-[#87efff] hover:text-[#87efff] hover:shadow-lg hover:shadow-[#87efff]/10"
          >
            Go Back
          </button>
        </div>

        {/* Status indicators */}
        <div className="mt-12 flex justify-center space-x-8 animate-fade-in-up" style={{ animationDelay: "0.6s" }}>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-zinc-500 text-sm">CONNECTION LOST</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-[#87efff] rounded-full animate-pulse" />
            <span className="text-zinc-500 text-sm">REROUTING...</span>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes grid-move {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes float-particle {
          0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.6; }
          50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
        }
        
        @keyframes scan {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        @keyframes glitch-1 {
          0%, 100% { transform: translate(0); }
          20% { transform: translate(-2px, 2px); }
          40% { transform: translate(-2px, -2px); }
          60% { transform: translate(2px, 2px); }
          80% { transform: translate(2px, -2px); }
        }
        
        @keyframes glitch-2 {
          0%, 100% { transform: translate(0); }
          20% { transform: translate(2px, -2px); }
          40% { transform: translate(2px, 2px); }
          60% { transform: translate(-2px, -2px); }
          80% { transform: translate(-2px, 2px); }
        }
        
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-scan {
          animation: scan 2s linear infinite;
        }
        
        .animate-glitch-1 {
          animation: glitch-1 0.3s infinite;
        }
        
        .animate-glitch-2 {
          animation: glitch-2 0.3s infinite reverse;
        }
        
        .animate-fade-in-up {
          animation: fade-in-up 0.8s ease-out forwards;
          opacity: 0;
        }
      `}</style>
    </div>
  )
}
