import React, { useState } from "react";
import {
  ArrowDownLeft,
  ArrowUpRight,
  ShieldCheck,
  PlusCircle,
  Settings,
} from "lucide-react";
import Button from "../components/ui/button";
import Card from "../components/ui/card";
import Input from "../components/ui/input";
import Modal from "../components/ui/modal";

// --- Mock Data ---
const userAssets = [
  {
    name: "Bitcoin",
    symbol: "BTC",
    balance: "0.501",
    value: "30,060.00",
    iconUrl: "https://placehold.co/40x40/F7931A/FFFFFF?text=B",
  },
  {
    name: "Ethereum",
    symbol: "ETH",
    balance: "3.120",
    value: "5,928.00",
    iconUrl: "https://placehold.co/40x40/627EEA/FFFFFF?text=E",
  },
  {
    name: "Solana",
    symbol: "SOL",
    balance: "15.80",
    value: "632.00",
    iconUrl: "https://placehold.co/40x40/9945FF/FFFFFF?text=S",
  },
];

// --- Main Wallet Page Component ---
export default function WalletPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProtocolSetup, setIsProtocolSetup] = useState(false);

  const handleSaveSettings = () => {
    setIsProtocolSetup(true);
    setIsModalOpen(false);
  };

  return (
    <>
      <div
        className="container mx-auto py-8 px-4"
        style={{ fontFamily: "'Creati Display', sans-serif" }}
      >
        <h1
          className="text-4xl font-bold text-white mb-8"
          style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
        >
          My Wallet
        </h1>

        {/* Total Balance Card */}
        <Card className="!p-6 mb-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
            <div>
              <p className="text-zinc-400 text-sm">Total Balance</p>
              <p className="text-4xl font-bold text-white mt-1">$36,620.00</p>
              <p className="text-green-400 text-sm mt-1">+2.5% vs last 24h</p>
            </div>
            <div className="flex space-x-3 mt-4 md:mt-0">
              <Button
                className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff]"
                aria-label="Deposit funds"
              >
                <ArrowDownLeft size={16} className="mr-2" /> Deposit
              </Button>
              <Button
                className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff]"
                aria-label="Withdraw funds"
              >
                <ArrowUpRight size={16} className="mr-2" /> Withdraw
              </Button>
            </div>
          </div>
        </Card>

        {/* Assets List */}
        <div className="space-y-4 mb-12">
          <h2
            className="text-2xl font-semibold text-white"
            style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
          >
            Your Assets
          </h2>
          {userAssets.map((asset) => (
            <Card
              key={asset.symbol}
              className="flex items-center justify-between !p-4 hover:border-zinc-600 transition-colors"
            >
              <div className="flex items-center gap-4">
                <img
                  src={asset.iconUrl}
                  alt={asset.name}
                  className="w-10 h-10 rounded-full"
                />
                <div>
                  <p className="font-semibold text-white text-lg">
                    {asset.name}
                  </p>
                  <p className="text-zinc-400 text-sm">{asset.symbol}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-white text-lg">
                  {asset.balance} {asset.symbol}
                </p>
                <p className="text-zinc-400 text-sm">${asset.value}</p>
              </div>
            </Card>
          ))}
        </div>

        {/* Secure Inheritance Section */}
        <Card className="bg-zinc-800 border-2 border-dashed border-zinc-700 !p-6">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="text-[#87efff]">
              <ShieldCheck size={40} />
            </div>
            <div className="flex-grow">
              <h3
                className="text-xl font-bold text-white"
                style={{ fontFamily: "'Creati Display Bold', sans-serif" }}
              >
                Secure Inheritance Protocol
              </h3>
              <p className="text-zinc-400 mt-1">
                {isProtocolSetup
                  ? "Your protocol is active. You can manage your settings at any time."
                  : "Protect your digital legacy. Designate a beneficiary to receive your assets in case of unforeseen circumstances."}
              </p>
            </div>
            <Button
              onClick={() => setIsModalOpen(true)}
              className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff] w-full md:w-auto"
              aria-label={
                isProtocolSetup
                  ? "Manage inheritance settings"
                  : "Set up inheritance protocol"
              }
            >
              {isProtocolSetup ? (
                <>
                  <Settings size={16} className="mr-2" /> Manage Settings
                </>
              ) : (
                <>
                  <PlusCircle size={16} className="mr-2" /> Set Up Protocol
                </>
              )}
            </Button>
          </div>
        </Card>
      </div>

      {/* Inheritance Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Inheritance Protocol Settings"
      >
        <div className="space-y-4">
          <div>
            <label
              htmlFor="walletAddress"
              className="block text-sm font-medium text-zinc-400 mb-1"
            >
              Beneficiary Wallet Address
            </label>
            <Input
              id="walletAddress"
              type="text"
              placeholder="0x..."
              aria-label="Enter beneficiary wallet address"
            />
          </div>
          <div>
            <label
              htmlFor="inactivityPeriod"
              className="block text-sm font-medium text-zinc-400 mb-1"
            >
              Inactivity Period
            </label>
            <select
              id="inactivityPeriod"
              className="w-full bg-zinc-800 border-2 border-zinc-700 text-white rounded-lg py-3 px-4 focus:outline-none focus:border-[#87efff]"
              aria-label="Select inactivity period"
            >
              <option>6 Months</option>
              <option>1 Year</option>
              <option>2 Years</option>
              <option>5 Years</option>
            </select>
          </div>
        </div>
        <div className="mt-6 flex justify-end gap-2">
          <Button
            onClick={() => setIsModalOpen(false)}
            className="border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white hover:border-zinc-500"
            aria-label="Cancel and close modal"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSaveSettings}
            className="bg-[#87efff] border-[#87efff] text-white hover:bg-[#6fe2f6] hover:border-[#6fe2f6]"
            aria-label="Save inheritance settings"
          >
            Save Settings
          </Button>
        </div>
      </Modal>
    </>
  );
}
