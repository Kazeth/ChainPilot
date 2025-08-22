"use client";

import { useState, useEffect } from "react";
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
import { wallet_backend } from "@/declarations/wallet_backend";
import { marketData_backend } from "@/declarations/marketdata_backend";
import { user_backend } from "@/declarations/user_backend";
import { Principal } from "@dfinity/principal";

interface Asset {
  assetId: string;
  symbol: string;
  name: string;
  currentPrice?: number;
  marketCap?: number;
  volume24h?: number;
  network?: string;
}

interface Holding {
  asset: Asset;
  amount: number; // Matches canister's number type based on error
  valueUSD?: number;
}

interface Wallet {
  walletId: string;
  owner: Principal;
  blockchainNetwork: string;
  balance: number;
  connectedExchange: string;
}

interface ProcessedAsset {
  name: string;
  symbol: string;
  balance: string;
  value: string;
  iconUrl: string;
}

// --- MAIN COMPONENT ---
export default function WalletPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProtocolSetup, setIsProtocolSetup] = useState(false);
  const [totalBalance, setTotalBalance] = useState(0);
  const [assets, setAssets] = useState<ProcessedAsset[]>([]);
  const [status, setStatus] = useState("");

  useEffect(() => {
    async function initialize() {
      try {
        // Mock Principal for testing (replace with real authentication)
        const mockPrincipalStr =
          "b77a5-d2g6j-l4g7b-a5b7g-6g6a5-d2g6j-l4g7b-a5b7g-cai";
        const mockPrincipal = Principal.fromText(mockPrincipalStr);

        try {
          const userDataRaw = await user_backend.getUserData(mockPrincipal);
          const userData =
            Array.isArray(userDataRaw) && userDataRaw.length > 0
              ? userDataRaw[0]
              : null;
          console.log("[v0] User data retrieved:", userData);
        } catch {
          console.log("[v0] User data not found, continuing without username");
        }

        const wallets = (await wallet_backend.getWalletsByPrincipal(
          mockPrincipal
        )) as Array<[Principal, Wallet[]]>;
        const walletData = wallets.length > 0 ? wallets[0][1][0] : null;
        if (walletData) {
          const holdings = (await wallet_backend.getHoldingsByWalletId(
            walletData.walletId
          )) as Array<[string, Holding[]]>;
          const holdingsData = holdings.length > 0 ? holdings[0][1] : [];

          const assetPromises = holdingsData.map(
            async (holding: Holding): Promise<ProcessedAsset> => {
              const asset = holding.asset;
              let assetData: Asset | null | undefined = null;
              try {
                const assetDataRaw = await marketData_backend.getAssetByAssetId(
                  asset.assetId
                );
                assetData =
                  Array.isArray(assetDataRaw) && assetDataRaw.length > 0
                    ? assetDataRaw[0]
                    : null;
              } catch {
                console.log("[v0] Asset data not found for:", asset.assetId);
                assetData = null; // Explicitly set to null on failure
              }

              const currentPrice = assetData?.currentPrice ?? 16.0;
              const value = holding.valueUSD ?? holding.amount * currentPrice;

              return {
                name: asset.name,
                symbol: asset.symbol,
                balance: holding.amount.toString(),
                value: value.toLocaleString("en-US", {
                  style: "currency",
                  currency: "USD",
                }),
                iconUrl: `https://placehold.co/40x40/${
                  asset.symbol === "BTC"
                    ? "F7931A"
                    : asset.symbol === "ETH"
                      ? "627EEA"
                      : "9945FF"
                }/FFFFFF?text=${asset.symbol[0]}`,
              };
            }
          );

          const assetList = await Promise.all(assetPromises);
          setAssets(assetList);

          const total = assetList.reduce(
            (sum: number, asset: ProcessedAsset) => {
              const numericValue = Number.parseFloat(
                asset.value.replace(/[$,]/g, "")
              );
              return sum + numericValue;
            },
            0
          );
          setTotalBalance(total);
        }
      } catch (error) {
        console.error("Initialization failed:", error);
        setStatus("Failed to initialize: " + (error as Error).message);
      }
    }
    initialize();
  }, []);

  const handleSaveSettings = () => {
    setIsProtocolSetup(true);
    setIsModalOpen(false);
    // TODO: Extend User.mo to save beneficiary and inactivity period
    // Example: await user_backend.setInheritance(mockPrincipal, beneficiary, inactivity);
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
              <p className="text-4xl font-bold text-white mt-1">
                $
                {totalBalance.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </p>
              <p className="text-green-400 text-sm mt-1">+2.5% vs last 24h</p>
            </div>
            <div className="flex space-x-3 mt-4 md:mt-0">
              <Button
                className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff]"
                aria-label="Deposit funds"
                onClick={() => setStatus("Deposit functionality coming soon")}
              >
                <ArrowDownLeft size={16} className="mr-2" /> Deposit
              </Button>
              <Button
                className="border-white text-white bg-transparent hover:bg-[#87efff] hover:text-zinc-900 hover:border-[#87efff]"
                aria-label="Withdraw funds"
                onClick={() => setStatus("Withdraw functionality coming soon")}
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
          {assets.length > 0 ? (
            assets.map((asset) => (
              <Card
                key={asset.symbol}
                className="flex items-center justify-between !p-4 hover:border-zinc-600 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <img
                    src={asset.iconUrl || "/placeholder.svg"}
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
                  <p className="text-zinc-400 text-sm">{asset.value}</p>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8">
              <p className="text-zinc-400 mb-4">
                No assets found. Please connect your wallet or add holdings.
              </p>
            </div>
          )}
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

      {status && (
        <div className="fixed bottom-4 right-4 bg-purple-900/30 text-purple-200 p-2 rounded">
          {status}
        </div>
      )}
    <LegacyBuztton />
    </>
  );
}