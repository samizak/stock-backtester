// app/page.tsx
"use client";

import StockChart from "./components/StockChart";
import SearchBar from "./components/SearchBar";
import StockMetadata from "./components/StockMetadata";
import useStockData from "./hooks/useStockData";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const { ticker, setTicker, stockData, suggestions } = useStockData();

  const handleSearch = (selectedTicker: string) => {
    setTicker(selectedTicker);
    router.push(`?ticker=${selectedTicker}`);
  };

  if (!stockData) return <div className="text-white">Loading...</div>;

  return (
    <main className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <SearchBar suggestions={suggestions} onSearch={handleSearch} />

        <h1 className="text-3xl font-bold text-white mb-8">
          {ticker} Stock Analysis
        </h1>

        <StockChart
          data={stockData.seriesData}
          rsiData={stockData.rsiData}
          splits={stockData.splits}
        />

        <StockMetadata splits={stockData.splits} />
      </div>
    </main>
  );
}
