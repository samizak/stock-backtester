// app/page.tsx
"use client";

import StockChart from "./components/StockChart";
import SearchBar from "./components/SearchBar";
import StockMetadata from "./components/StockMetadata";
import useStockData from "./hooks/useStockData";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const { ticker, setTicker, stockData, suggestions, refreshData } =
    useStockData();

  const handleSearch = (selectedTicker: string) => {
    setTicker(selectedTicker);
    router.push(`?ticker=${selectedTicker}`);
  };

  if (!stockData) return <div className="text-white">Loading...</div>;

  const handleRegenerate = () => {
    refreshData();
  };

  return (
    <main className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <SearchBar suggestions={suggestions} onSearch={handleSearch} />

        <h1 className="text-3xl font-bold text-white mb-8">
          {ticker} Stock Analysis
        </h1>

        {ticker == "Synthetic_Prices" && (
          <button
            className="bg-slate-500 p-2 mb-4 rounded-lg font-mono text-lg font-semibold uppercase"
            onClick={handleRegenerate}
          >
            Regenerate
          </button>
        )}

        <StockChart
          data={stockData.seriesData}
          rsiData={stockData.rsiData}
          splits={stockData.splits}
        />

        {ticker != "Synthetic_Prices" && (
          <StockMetadata splits={stockData.splits} />
        )}
      </div>
    </main>
  );
}
