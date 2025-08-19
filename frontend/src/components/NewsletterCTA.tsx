// src/components/NewsletterCTA.tsx

import React from 'react';
import CTA1 from '@/assets/cta1.jpg'; // Assuming these images exist in the assets folder
import CTA2 from '@/assets/cta2.jpg';
import CTA3 from '@/assets/cta3.jpg';

export default function NewsletterCTA() {
  return (
    // Main container with gradient background and rounded corners
    <div className="relative bg-gradient-to-br from-[#87efff] to-[#55c8e2] rounded-2xl overflow-hidden p-8 md:p-12 shadow-2xl">
      <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
        
        {/* Left Side: Text and Form */}
        <div className="text-zinc-900" style={{ fontFamily: "'Creati Display', sans-serif" }}>
          <h2 className="text-3xl md:text-4xl font-bold mb-3">
            Stay Ahead of the Market
          </h2>
          <p className="text-zinc-800 mb-6 max-w-md">
            Subscribe to our newsletter for exclusive AI-driven insights, market analysis, and feature updates delivered directly to your inbox.
          </p>
          
          {/* Email Input Form */}
          <form className="flex flex-col sm:flex-row gap-3">
            <input 
              type="email" 
              placeholder="Enter your email address"
              className="w-full px-4 py-3 rounded-lg bg-white/80 text-zinc-900 placeholder-zinc-600 border-2 border-transparent focus:outline-none focus:border-[#87efff] focus:bg-white transition-all duration-300"
              aria-label="Email Address"
            />
            <button 
              type="submit"
              className="bg-zinc-900 text-white px-6 py-3 rounded-lg font-semibold hover:bg-zinc-800 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#87efff] focus:ring-white"
            >
              Subscribe
            </button>
          </form>
        </div>

        {/* Right Side: Image Carousel */}
        <div className="relative h-64 md:h-80 flex items-center justify-center">
          {/* Image 3 (Back) */}
          <img 
            src={CTA3}
            alt="CTA visual 3"
            className="absolute w-4/5 max-w-xs h-auto object-cover rounded-xl shadow-lg transform rotate-6 transition-transform duration-300 ease-in-out hover:scale-110 hover:-translate-y-3 hover:rotate-3"
            onError={(e) => { e.currentTarget.src = 'https://placehold.co/400x250/3f3f46/FFFFFF?text=CTA+3'; e.currentTarget.onerror = null; }}
          />
          {/* Image 2 (Middle) */}
          <img 
            src={CTA2}
            alt="CTA visual 2"
            className="absolute w-4/5 max-w-xs h-auto object-cover rounded-xl shadow-lg transform -rotate-4 transition-transform duration-300 ease-in-out hover:scale-110 hover:-translate-y-3 hover:rotate-0"
            onError={(e) => { e.currentTarget.src = 'https://placehold.co/400x250/52525b/FFFFFF?text=CTA+2'; e.currentTarget.onerror = null; }}
          />
          {/* Image 1 (Front) */}
          <img 
            src={CTA1}
            alt="CTA visual 1"
            className="absolute w-4/5 max-w-xs h-auto object-cover rounded-xl shadow-lg transform rotate-2 transition-transform duration-300 ease-in-out hover:scale-110 hover:-translate-y-3 hover:-rotate-2"
            onError={(e) => { e.currentTarget.src = 'https://placehold.co/400x250/71717a/FFFFFF?text=CTA+1'; e.currentTarget.onerror = null; }}
          />
        </div>

      </div>
    </div>
  );
}
