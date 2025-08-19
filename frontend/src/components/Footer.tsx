// Import gambar dari assets folder
import logo from "../assets/ChainPilot_logo.png"

// SVG Icons for social media links.
const InstagramIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="feather feather-instagram"
  >
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
    <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
  </svg>
)

const GithubIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="feather feather-github"
  >
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
  </svg>
)

const LinkedinIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="feather feather-linkedin"
  >
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
    <rect x="2" y="9" width="4" height="12"></rect>
    <circle cx="4" cy="4" r="2"></circle>
  </svg>
)

// A helper component to generate the repeating, colored text
const MarqueeContent = () => (
  <>
    {[...Array(15)].map((_, i) => (
      <span key={i} className={`text-4xl ${i % 2 === 0 ? "text-white" : "text-[#87efff]"}`}>
        ChainPilot
      </span>
    ))}
  </>
)

export default function Footer() {
  return (
    <footer className="bg-zinc-900 border-t border-zinc-800 pt-12 pb-8 overflow-x-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center">
        {/* 1. Logo */}
        {/* Contoh penggunaan gambar yang diimpor */}
        <img
          src={logo || "/placeholder.svg"}
          alt="ChainPilot Logo"
          className="h-10 w-auto mb-6"
          onError={(e) => {
            e.currentTarget.src = "https://placehold.co/120x40/18181b/FFFFFF?text=Logo"
            e.currentTarget.onerror = null
          }}
        />

        {/* 2. Social Media Icons */}
        <div className="flex space-x-6 mb-8">
          <a href="#" className="text-zinc-500 hover:text-[#87efff] transition-colors duration-300">
            <InstagramIcon />
          </a>
          <a href="#" className="text-zinc-500 hover:text-[#87efff] transition-colors duration-300">
            <GithubIcon />
          </a>
          <a href="#" className="text-zinc-500 hover:text-[#87efff] transition-colors duration-300">
            <LinkedinIcon />
          </a>
        </div>
      </div>

      {/* 3. Endless Looping Marquee - Full Width */}
      <div className="relative w-screen h-12 flex items-center justify-center overflow-hidden mb-8 -mx-4 sm:-mx-6 lg:-mx-8">
        <div className="absolute flex animate-marquee whitespace-nowrap" style={{ fontFamily: "'Sprintura', serif" }}>
          {/* The content is duplicated to create a seamless loop */}
          <MarqueeContent />
          <MarqueeContent />
        </div>
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center">
        {/* 4. Separator */}
        <hr className="w-full max-w-lg border-zinc-800 mb-6" />

        {/* 5. Credit Text */}
        <p className="text-zinc-600 text-sm" style={{ fontFamily: "'Creati Display', sans-serif" }}>
          Made by Crazy Killers 😝😝😝
        </p>
      </div>
    </footer>
  )
}
