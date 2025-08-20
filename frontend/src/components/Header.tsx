import React, { useState, useEffect } from "react";
import Logo from "@/assets/ChainPilot_logo.png";
import Button from "./ui/button"; // Assuming src/components/ui/Button.tsx exists
import { useAuthContext } from "@/context/AuthContext";
import { Link } from "react-router";

export default function Header() {
  // --- State for UI behavior ---
  const [isVisible, setIsVisible] = useState(true);
  const [isScrolled, setIsScrolled] = useState(false);
  const [lastScrollY, setLastScrollY] = useState(0);

  const auth = useAuthContext();

  // Effect to handle scroll events
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      setIsScrolled(currentScrollY > 10);
      if (currentScrollY > lastScrollY && currentScrollY > 80) {
        setIsVisible(false);
      } else {
        setIsVisible(true);
      }
      setLastScrollY(currentScrollY);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [lastScrollY]);

  // Dynamic CSS classes for the header
  const headerClasses = `
    w-full fixed top-0 z-50 transition-all duration-300 ease-in-out
    ${isVisible ? "translate-y-0" : "-translate-y-full"}
    ${isScrolled ? "bg-zinc-900/80 shadow-lg backdrop-blur-sm" : "bg-transparent"}
  `;

  async function handleLogin() {
    await auth.login();
  }

  async function handleLogout() {
    await auth.logout();
  }

  return (
    <header className={headerClasses}>
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <Link
            to="/"
            className="flex-shrink-0 flex items-center cursor-pointer"
            aria-label="ChainPilot Home"
          >
            <img
              src={Logo}
              alt="ChainPilot Logo"
              className="h-20 w-auto"
              onError={(e) => {
                e.currentTarget.src =
                  "https://placehold.co/100x36/18181b/FFFFFF?text=Logo";
                e.currentTarget.onerror = null;
              }}
            />
            <span
              className="ml-3 text-2xl font-bold text-white"
              style={{ fontFamily: "'Sprintura', serif" }}
            >
              ChainPilot
            </span>
          </Link>
          <div style={{ fontFamily: "'Creati Display', sans-serif" }}>
            {/* Navigation for authenticated and unauthenticated users */}
            {auth.isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <div className="hidden md:flex items-baseline space-x-1">
                  <Link
                    to="/dashboard"
                    className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                    aria-label="Go to Dashboard"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/analytics"
                    className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                    aria-label="Go to Analytics"
                  >
                    Analytics
                  </Link>
                  <Link
                    to="/portfolio"
                    className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                    aria-label="Go to Portfolio"
                  >
                    Portfolio
                  </Link>
                  <Link
                    to="/wallet"
                    className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                    aria-label="Go to Wallet"
                  >
                    Wallet
                  </Link>
                </div>
                <Button
                  onClick={handleLogout}
                  className="bg-zinc-700 border-zinc-700 hover:bg-zinc-600 hover:border-zinc-600"
                  aria-label="Log out from ChainPilot"
                >
                  Log Out
                </Button>
              </div>
            ) : (
              <Button
                onClick={handleLogin}
                className="bg-[#87efff] border-[#87efff] text-white-900 hover:bg-[#6fe2f6] hover:border-[#6fe2f6]"
                aria-label="Log in to ChainPilot"
              >
                Log In
              </Button>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
