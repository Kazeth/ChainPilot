"use client";

import {
  BrainCircuit,
  Target,
  StopCircle,
  Settings,
  Clock,
  Users,
  Send,
  Shield,
  TrendingUp,
  Bot,
  Lock,
} from "lucide-react";
import Button from "../components/ui/button";
import Card from "../components/ui/card";
import HeroVideo from "../assets/HeroSection_video.mp4"; // Import the video
import AboutImage1 from "../assets/About1.jpg"; // Import carousel images
import AboutImage2 from "../assets/About2.jpg";
import AboutImage3 from "../assets/About3.jpg";
import AboutImage4 from "../assets/About4.jpg";
import { useState, useEffect } from "react";

// Data for team members - in a real app, this might come from an API
const teamMembers = [
  {
    name: "Alex Johnson",
    role: "Lead Architect",
    imageUrl: "https://placehold.co/400x400/18181b/FFFFFF?text=Alex",
  },
  {
    name: "Maria Garcia",
    role: "AI Specialist",
    imageUrl: "https://placehold.co/400x400/18181b/FFFFFF?text=Maria",
  },
  {
    name: "James Smith",
    role: "Frontend Developer",
    imageUrl: "https://placehold.co/400x400/18181b/FFFFFF?text=James",
  },
  {
    name: "Priya Patel",
    role: "Security Expert",
    imageUrl: "https://placehold.co/400x400/18181b/FFFFFF?text=Priya",
  },
  {
    name: "Chen Wei",
    role: "UI/UX Designer",
    imageUrl: "https://placehold.co/400x400/18181b/FFFFFF?text=Chen",
  },
];

// Carousel images from assets
const carouselImages = [
  { src: AboutImage1, alt: "ChainPilot Feature 1" },
  { src: AboutImage2, alt: "ChainPilot Feature 2" },
  { src: AboutImage3, alt: "ChainPilot Feature 3" },
  { src: AboutImage4, alt: "ChainPilot Feature 4" },
];

export default function LandingPage() {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % carouselImages.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="px-4 sm:px-6 lg:px-8 relative">
      {/* Animated background grid (full page) */}
      <div className="absolute inset-0 opacity-10 z-0">
        <div
          className="absolute inset-0 animate-grid-move"
          style={{
            backgroundImage: `
              linear-gradient(rgba(135, 239, 255, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(135, 239, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: "50px 50px",
          }}
        />
      </div>

      {/* Floating particles (full page) */}
      <div className="absolute inset-0 pointer-events-none z-0">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-[#87efff] rounded-full opacity-60 animate-float-particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDuration: `${3 + Math.random() * 4}s`,
              animationDelay: `${Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      {/* 1. Hero Section */}
      <section className="relative text-center py-24 md:py-40 min-h-[80vh] overflow-hidden">
        <div className="relative z-10">
          <h1
            className="text-5xl md:text-7xl font-bold text-white tracking-tight"
            style={{ fontFamily: "'Sprintura', serif" }}
          >
            AI-Powered Trading
          </h1>
          <p
            className="mt-4 max-w-2xl mx-auto text-lg text-zinc-400"
            style={{ fontFamily: "'Creati Display', sans-serif" }}
          >
            Unleash the power of artificial intelligence to navigate the crypto
            markets with precision and confidence.
          </p>
          <div className="mt-8">
            <Button className="bg-[#87efff] border-[#87efff] text-white-900 hover:bg-[#6fe2f6] hover:border-[#6fe2f6] px-8 py-3 text-base">
              Start Now
            </Button>
          </div>
        </div>

        {/* Video Widget */}
        <div className="absolute inset-0 z-1">
          <video
            className="absolute top-0 left-0 w-full h-full object-cover opacity-20"
            src={HeroVideo}
            autoPlay
            loop
            muted
            playsInline
          />
          {/* Enhanced fade effect */}
          <div className="absolute bottom-0 left-0 w-full h-2/3 bg-gradient-to-t from-zinc-900 via-zinc-900/70 to-transparent"></div>
        </div>
      </section>

      {/* 2. About Section */}
      <section className="py-16 md:py-24 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Text Content (Left) */}
            <div className="md:w-1/2 text-left">
              <h2
                className="text-3xl font-bold text-white mb-4"
                style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
              >
                What is ChainPilot?
              </h2>
              <p
                className="text-zinc-400"
                style={{ fontFamily: "'Creati Display', sans-serif" }}
              >
                ChainPilot is a next-generation crypto application that empowers
                you to navigate the digital asset market with unparalleled
                intelligence and security. We provide a seamless platform that
                integrates AI-driven trade signals, disciplined risk management,
                and a pioneering feature to secure your assets for the future.
              </p>
            </div>

            <div className="md:w-1/2">
              <div className="relative">
                {/* Main carousel image */}
                <div className="relative overflow-hidden rounded-lg">
                  <img
                    src={
                      carouselImages[currentImageIndex].src ||
                      "/placeholder.svg"
                    }
                    alt={carouselImages[currentImageIndex].alt}
                    className="w-full h-80 object-cover transition-all duration-1000 hover:scale-105 hover:shadow-2xl hover:shadow-[#87efff]/50"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Core Features Sections - Restructured */}
      <section className="py-8 md:py-12 relative z-10">
        <div className="max-w-7xl mx-auto text-center">
          <h2
            className="text-4xl md:text-5xl font-bold text-white"
            style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
          >
            <span style={{ color: "#87efff" }}>Core</span> Features
          </h2>
        </div>
      </section>

      {/* AI-Powered Analytical Review */}
      <section className="py-16 md:py-24 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-6">
            <div className="flex items-center gap-4">
              <BrainCircuit className="h-10 w-10 text-[#87efff]" />
              <h2 className="text-3xl font-bold text-white" style={{ fontFamily: "'Creati Display Bold', sans-serif" }}>
                AI-Powered Analytical Review
              </h2>
            </div>
            <p className="text-zinc-400 text-lg max-w-md" style={{ fontFamily: "'Creati Display', sans-serif" }}>
              Advanced AI algorithms analyze market data, sentiment, and technical indicators to provide intelligent
              trading recommendations and optimal timing signals.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* What to Buy Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <TrendingUp className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-2xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  "What to Buy" Suggestions
                </h3>
                <p className="text-zinc-400 text-lg" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  AI scans for high-potential opportunities using on-chain fundamentals, market sentiment, and technical
                  analysis. Stop guessing and start making data-driven decisions with our advanced AI that analyzes
                  thousands of data points across the market.
                </p>
              </div>
            </Card>

            {/* When to Buy/Sell Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <Clock className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-2xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  "When to Buy/Sell" Signals
                </h3>
                <p className="text-zinc-400 text-lg" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  Real-time alerts signal opportune moments to enter or exit positions, maximizing gains and minimizing
                  losses. Get precise timing recommendations based on market conditions and technical indicators.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Automated Buy/Sell Execution */}
      <section className="py-16 md:py-24 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-6">
            <div className="flex items-center gap-4">
              <Settings className="h-10 w-10 text-[#87efff]" />
              <h2 className="text-3xl font-bold text-white" style={{ fontFamily: "'Creati Display Bold', sans-serif" }}>
                Automated Buy/Sell Execution
              </h2>
            </div>
            <p className="text-zinc-400 text-lg max-w-md" style={{ fontFamily: "'Creati Display', sans-serif" }}>
              Disciplined automated trading with customizable take profit and stop loss levels. Execute your strategy
              24/7 without emotional interference.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Take Profit Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <Target className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-2xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  Take Profit (TP)
                </h3>
                <p className="text-zinc-400 text-lg" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  Set specific price targets. When reached, ChainPilot automatically sells to lock in your gains.
                  Execute your trading strategy with precision and discipline, 24/7.
                </p>
              </div>
            </Card>

            {/* Stop Loss Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <StopCircle className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-2xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  Stop Loss (SL)
                </h3>
                <p className="text-zinc-400 text-lg" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  Critical risk management tool that automatically exits trades to protect from significant losses. Set
                  your rules once and let ChainPilot manage your positions.
                </p>
              </div>
            </Card>

            {/* Set & Forget Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <Bot className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-2xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  Set & Forget
                </h3>
                <p className="text-zinc-400 text-lg" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  Configure TP/SL levels once and gain peace of mind that your strategy is active even when offline.
                  Automated execution ensures you never miss an opportunity.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Secure Wallet Inheritance Protocol */}
      <section className="py-16 md:py-24 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-6">
            <div className="flex items-center gap-4">
              <Shield className="h-10 w-10 text-[#87efff]" />
              <h2 className="text-3xl font-bold text-white" style={{ fontFamily: "'Creati Display Bold', sans-serif" }}>
                Secure Wallet Inheritance Protocol
              </h2>
            </div>
            <p className="text-zinc-400 text-lg max-w-md" style={{ fontFamily: "'Creati Display', sans-serif" }}>
              Revolutionary inheritance system that securely transfers your crypto assets to designated beneficiaries
              after periods of inactivity, ensuring your legacy is protected.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Inactivity Fallback Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <Clock className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  Inactivity Fallback Safe
                </h3>
                <p className="text-zinc-400" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  Digital "dead man's switch" - define a specific period of inactivity for automatic protocol
                  activation.
                </p>
              </div>
            </Card>

            {/* Beneficiary Designation Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <Users className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  Beneficiary Designation
                </h3>
                <p className="text-zinc-400" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  Securely designate a beneficiary wallet address within the encrypted ChainPilot system.
                </p>
              </div>
            </Card>

            {/* Automated Transfer Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <Send className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  Automated Transfer
                </h3>
                <p className="text-zinc-400" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  After verification process, assets are automatically and safely transferred to designated beneficiary.
                </p>
              </div>
            </Card>

            {/* Full User Control Widget */}
            <Card className="p-8 bg-zinc-900/50 border-2 border-zinc-700/50 rounded-xl hover:border-[#87efff]/50 transition-all duration-300 hover:shadow-2xl hover:shadow-[#87efff]/20 hover:scale-105">
              <div className="text-center">
                <Lock className="h-16 w-16 mx-auto text-[#87efff] mb-6" />
                <h3
                  className="text-xl font-semibold text-white mb-4"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  Full User Control
                </h3>
                <p className="text-zinc-400" style={{ fontFamily: "'Creati Display', sans-serif" }}>
                  Change inactivity period, update beneficiary address, or disable the feature at any time.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* 4. Meet Our Team Section */}
      <section className="py-16 md:py-24 relative z-10">
        <div className="max-w-7xl mx-auto">
          <h2
            className="text-3xl font-bold text-white text-center mb-12"
            style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
          >
            Meet Our Team
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-8">
            {teamMembers.map((member) => (
              <div key={member.name} className="group text-center">
                <div className="relative w-32 h-32 md:w-40 md:h-40 mx-auto rounded-full overflow-hidden border-2 border-zinc-700 group-hover:border-[#87efff] transition-all duration-300">
                  <img
                    src={member.imageUrl || "/placeholder.svg"}
                    alt={member.name}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                  />
                </div>
                <h3
                  className="mt-4 text-lg font-semibold text-white"
                  style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
                >
                  {member.name}
                </h3>
                <p
                  className="text-sm text-zinc-400"
                  style={{ fontFamily: "'Creati Display', sans-serif" }}
                >
                  {member.role}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
