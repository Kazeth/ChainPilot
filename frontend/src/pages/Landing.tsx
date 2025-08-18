// src/pages/LandingPage.tsx
// This is the main landing page for ChainPilot.

import React from 'react';
import { BrainCircuit, ShieldCheck, TrendingUp } from 'lucide-react'; // Example icons
import Button from '../components/ui/button';
import Card from '../components/ui/card';

// Data for team members - in a real app, this might come from an API
const teamMembers = [
  { name: 'Alex Johnson', role: 'Lead Architect', imageUrl: 'https://placehold.co/400x400/18181b/FFFFFF?text=Alex' },
  { name: 'Maria Garcia', role: 'AI Specialist', imageUrl: 'https://placehold.co/400x400/18181b/FFFFFF?text=Maria' },
  { name: 'James Smith', role: 'Frontend Developer', imageUrl: 'https://placehold.co/400x400/18181b/FFFFFF?text=James' },
  { name: 'Priya Patel', role: 'Security Expert', imageUrl: 'https://placehold.co/400x400/18181b/FFFFFF?text=Priya' },
  { name: 'Chen Wei', role: 'UI/UX Designer', imageUrl: 'https://placehold.co/400x400/18181b/FFFFFF?text=Chen' },
];

export default function LandingPage() {
  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8">
      
      {/* 1. Hero Section */}
      <section className="relative text-center py-20 md:py-32 overflow-hidden">
        <div className="relative z-10">
          <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight" style={{ fontFamily: "'Sprintura', serif" }}>
            AI-Powered Trading
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-lg text-zinc-400" style={{ fontFamily: "'Creati Display', sans-serif" }}>
            Unleash the power of artificial intelligence to navigate the crypto markets with precision and confidence.
          </p>
          <div className="mt-8">
            <Button className="bg-[#87efff] border-[#87efff] text-zinc-900 hover:bg-[#6fe2f6] hover:border-[#6fe2f6] px-8 py-3 text-base">
              Start Now
            </Button>
          </div>
        </div>
        
        {/* Video Widget */}
        <div className="absolute inset-0 -top-20 z-0">
          <div className="relative w-full h-full max-w-4xl mx-auto">
            <video
              className="absolute top-0 left-0 w-full h-full object-cover rounded-b-full opacity-20"
              src="https://cdn.pixabay.com/video/2022/05/23/116121-711985399_large.mp4" // Placeholder video
              autoPlay
              loop
              muted
              playsInline
            />
            {/* Seamless blur effect */}
            <div className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-zinc-900 to-transparent"></div>
          </div>
        </div>
      </section>

      {/* 2. About Section */}
      <section className="py-16 md:py-24 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">What is ChainPilot?</h2>
        <p className="max-w-3xl mx-auto text-zinc-400">
          ChainPilot is a next-generation crypto application that empowers you to navigate the digital asset market with unparalleled intelligence and security. We provide a seamless platform that integrates AI-driven trade signals, disciplined risk management, and a pioneering feature to secure your assets for the future.
        </p>
      </section>

      {/* 3. Features Section */}
      <section className="py-16 md:py-24">
        <h2 className="text-3xl font-bold text-white text-center mb-12">Core Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card className="text-center">
            <TrendingUp className="h-10 w-10 mx-auto text-[#87efff]" />
            <h3 className="mt-4 text-xl font-semibold text-white">AI Trade Signals</h3>
            <p className="mt-2 text-zinc-400">Our advanced AI analyzes thousands of data points to provide clear, actionable intelligence on what to buy and when to trade.</p>
          </Card>
          <Card className="text-center">
            <BrainCircuit className="h-10 w-10 mx-auto text-[#87efff]" />
            <h3 className="mt-4 text-xl font-semibold text-white">Automated Execution</h3>
            <p className="mt-2 text-zinc-400">Set your rules once and let ChainPilot manage your positions, protecting your capital and securing profits 24/7.</p>
          </Card>
          <Card className="text-center">
            <ShieldCheck className="h-10 w-10 mx-auto text-[#87efff]" />
            <h3 className="mt-4 text-xl font-semibold text-white">Secure Inheritance</h3>
            <p className="mt-2 text-zinc-400">Our groundbreaking protocol ensures your digital assets can be safely passed on to your chosen beneficiary.</p>
          </Card>
        </div>
      </section>

      {/* 4. Meet Our Team Section */}
      <section className="py-16 md:py-24">
        <h2 className="text-3xl font-bold text-white text-center mb-12">Meet Our Team</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-8">
          {teamMembers.map((member) => (
            <div key={member.name} className="group text-center">
              <div className="relative w-32 h-32 md:w-40 md:h-40 mx-auto rounded-full overflow-hidden border-2 border-zinc-700 group-hover:border-[#87efff] transition-all duration-300">
                <img 
                  src={member.imageUrl} 
                  alt={member.name} 
                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-white">{member.name}</h3>
              <p className="text-sm text-zinc-400">{member.role}</p>
            </div>
          ))}
        </div>
      </section>

    </div>
  );
}
