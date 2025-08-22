"use client"

import { useState, useEffect } from "react"
import CTA1 from "../assets/cta1.jpg" // Assuming these images exist in the assets folder
import CTA2 from "../assets/cta2.jpg"
import CTA3 from "../assets/cta3.jpg"

export default function NewsletterCTA() {
  // State for carousel
  const [activeIndex, setActiveIndex] = useState(0)
  const images = [
    {
      src: CTA1,
      alt: "CTA visual 1",
      placeholder: "https://placehold.co/400x250/71717a/FFFFFF?text=CTA+1",
      transform: "rotate-2",
    },
    {
      src: CTA2,
      alt: "CTA visual 2",
      placeholder: "https://placehold.co/400x250/52525b/FFFFFF?text=CTA+2",
      transform: "-rotate-4",
    },
    {
      src: CTA3,
      alt: "CTA visual 3",
      placeholder: "https://placehold.co/400x250/3f3f46/FFFFFF?text=CTA+3",
      transform: "rotate-6",
    },
  ]

  // Effect for automatic carousel cycling
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prevIndex) => (prevIndex + 1) % images.length)
    }, 3000) // Cycle every 3 seconds
    return () => clearInterval(interval)
  }, [images.length])

  // Determine image order: active, next, last
  const getImageStyles = (index: number) => {
    const relativeIndex = (index - activeIndex + images.length) % images.length
    if (relativeIndex === 0) {
      // Active image: foreground
      return {
        opacity: "opacity-100",
        zIndex: "z-20",
        transform: images[index].transform,
        hoverTransform: images[index].transform.includes("rotate")
          ? images[index].transform.replace("rotate", "-rotate")
          : images[index].transform,
      }
    } else if (relativeIndex === 1) {
      // Next image: middle
      return {
        opacity: "opacity-70",
        zIndex: "z-10",
        transform: images[index].transform,
        hoverTransform: images[index].transform,
      }
    } else {
      // Last image: back
      return {
        opacity: "opacity-40",
        zIndex: "z-0",
        transform: images[index].transform,
        hoverTransform: images[index].transform,
      }
    }
  }

  return (
    // Main container with gradient background and rounded corners
    <div className="relative bg-gradient-to-br from-[#87efff] to-[#55c8e2] rounded-2xl overflow-hidden p-8 md:p-12 shadow-2xl container mx-auto sm:px-6 lg:px-8">
      <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
        {/* Left Side: Text and Form */}
        <div className="text-zinc-900" style={{ fontFamily: "'Creati Display', sans-serif" }}>
          <h2
            className="text-3xl md:text-4xl font-bold mb-3"
            style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
          >
            Stay Ahead of the Market
          </h2>
          <p className="text-zinc-800 mb-6 max-w-md">
            Subscribe to our newsletter for exclusive AI-driven insights, market analysis, and feature updates delivered
            directly to your inbox.
          </p>

          {/* Email Input (No form due to sandbox restrictions) */}
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="email"
              placeholder="Enter your email address"
              className="w-full px-4 py-3 rounded-lg bg-white/80 text-zinc-900 placeholder-zinc-600 border-2 border-transparent focus:outline-none focus:border-[#87efff] focus:bg-white transition-all duration-300"
              aria-label="Email Address"
            />
            <button
              type="button"
              onClick={() => console.log("Subscribe clicked")} // Replace with actual subscription logic
              className="bg-gradient-to-r from-zinc-900 via-zinc-800 to-zinc-900 text-white px-6 py-3 rounded-lg font-semibold hover:from-zinc-800 hover:via-zinc-700 hover:to-zinc-800 hover:shadow-[0_0_20px_rgba(135,239,255,0.6)] transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#87efff] focus:ring-white"
            >
              Subscribe
            </button>
          </div>
        </div>

        {/* Right Side: Image Carousel */}
        <div className="relative h-80 md:h-96 flex items-center justify-center">
          {images.map((image, index) => {
            const styles = getImageStyles(index)
            return (
              <img
                key={index}
                src={image.src || "/placeholder.svg"}
                alt={image.alt}
                className={`absolute w-4/5 max-w-sm h-auto object-cover rounded-xl shadow-lg transition-all duration-500 ease-in-out ${styles.opacity} ${styles.zIndex} ${styles.transform} hover:scale-110 hover:-translate-y-3 hover:${styles.hoverTransform}`}
                onError={(e) => {
                  e.currentTarget.src = image.placeholder
                  e.currentTarget.onerror = null
                }}
              />
            )
          })}
        </div>
      </div>
    </div>
  )
}
