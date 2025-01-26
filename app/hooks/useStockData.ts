"use client";

import { useState, useEffect } from "react";
import { StockData } from "../types";

async function getStockData(ticker: string) {
  try {
    const res = await fetch(
      `http://127.0.0.1:8000/api/prices?ticker=${ticker}`
    );
    if (!res.ok) throw new Error("Failed to fetch data");

    const data = await res.json();
    if (data.error) throw new Error(data.error);

    return {
      seriesData: data.prices.map((d: any) => ({
        time: d.date,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      })),
      rsiData: data.rsi.map((value: number, index: number) => ({
        time: data.prices[index].date,
        value: value,
      })),
      splits: data.splits?.map((s: any) => ({
        date: s.date,
        split_ratio: s.split_ratio,
      })),
    };
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

export default function useStockData(initialTicker = "AAPL") {
  const [ticker, setTicker] = useState(initialTicker);
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [fetchTrigger, setFetchTrigger] = useState(0); // Add fetch trigger state

  // Add refresh function
  const refreshData = () => {
    setFetchTrigger((prev) => prev + 1);
  };

  useEffect(() => {
    const fetchTickers = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/tickers");
        const data = await res.json();
        setSuggestions(data.tickers);
      } catch (error) {
        console.error("Error fetching tickers:", error);
      }
    };
    fetchTickers();
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await getStockData(ticker);
        setStockData(data);
      } catch (error) {
        console.error("Error loading stock data:", error);
      }
    };
    loadData();
  }, [ticker, fetchTrigger]); // Add fetchTrigger to dependencies

  return { ticker, setTicker, stockData, suggestions, refreshData }; // Add refreshData to return
}
