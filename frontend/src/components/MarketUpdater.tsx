import { useEffect } from "react";
import { marketData_backend } from "@/declarations/marketData_backend";
import { wallet_backend } from "@/declarations/wallet_backend";
import { user_backend } from "@/declarations/user_backend";
import { insurance_backend } from "@/declarations/insurance_backend";

export default function MarketUpdater() {
    useEffect(() => {
        const fetchAndUpdate = async () => {

            const res = await fetch(
                "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
            );
            const data = await res.json();
            for (const coin of data) {
                console.log("MarketUpdater fetching coins");
                await marketData_backend.fetchAsset(
                    coin.id,
                    coin.symbol,
                    coin.name,
                    Number(coin.current_price),
                    Number(coin.market_cap),
                    Number(coin.total_volume),
                    "CoinGecko"
                );
            }

            console.log("✅ assets berhasil diupdate ke backend");

        };

        fetchAndUpdate();

        const interval = setInterval(fetchAndUpdate, 60_000);

        return () => clearInterval(interval); // cleanup
    }, []);

    return null;
}
