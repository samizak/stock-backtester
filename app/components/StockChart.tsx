// components/StockChart.tsx
"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  CrosshairMode,
  SeriesMarker,
  SeriesMarkerPosition,
  Time,
} from "lightweight-charts";

interface StockChartProps {
  data: Array<{
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
  }>;
  rsiData: Array<{
    time: string;
    value: number;
  }>;
  splits: Array<{
    date: string;
    split_ratio: number;
  }>;
}

export default function StockChart({ data, rsiData, splits }: StockChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const rsiContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !rsiContainerRef.current || !data.length)
      return;

    // Create charts
    const priceChart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      crosshair: { mode: CrosshairMode.Normal },
      layout: {
        background: { color: "#1a1a1a" },
        textColor: "rgba(255, 255, 255, 0.9)",
      },
      grid: {
        vertLines: { color: "#334155" },
        horzLines: { color: "#334155" },
      },
    });

    const candlestickSeries = priceChart.addCandlestickSeries({
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
    });
    candlestickSeries.setData(data);

    // Add split markers
    const splitMarkers: SeriesMarker<Time>[] = splits.map((split) => ({
      time: split.date,
      position: "belowBar",
      color: "#ffff",
      shape: "arrowUp",
      text: `${split.split_ratio}:1 Split`,
      size: 2.5,
    }));

    candlestickSeries.setMarkers(splitMarkers);

    // Create RSI chart
    const rsiChart = createChart(rsiContainerRef.current, {
      width: rsiContainerRef.current.clientWidth,
      height: 200,
      layout: {
        background: { color: "#1a1a1a" },
        textColor: "rgba(255, 255, 255, 0.9)",
      },
      grid: {
        vertLines: { color: "#334155" },
        horzLines: { color: "#334155" },
      },
    });

    const rsiSeries = rsiChart.addLineSeries({
      color: "#BF40BF",
      lineWidth: 2,
      priceLineVisible: false,
    });
    rsiSeries.setData(rsiData);

    // Synchronization
    const syncHandler = (range: any) => {
      if (range) {
        rsiChart.timeScale().setVisibleLogicalRange(range);
      }
    };
    priceChart.timeScale().subscribeVisibleLogicalRangeChange(syncHandler);

    // Resize handler
    const resizeObserver = new ResizeObserver(() => {
      priceChart.resize(chartContainerRef.current?.clientWidth || 0, 400);
      rsiChart.resize(rsiContainerRef.current?.clientWidth || 0, 200);
    });

    resizeObserver.observe(chartContainerRef.current);

    rsiSeries.createPriceLine({
      price: 70.0,
      color: "gray",
      lineWidth: 1,
      lineStyle: 3,
      axisLabelVisible: false,
    });
    rsiSeries.createPriceLine({
      price: 30.0,
      color: "gray",
      lineWidth: 1,
      lineStyle: 3,
      axisLabelVisible: false,
    });

    return () => {
      resizeObserver.disconnect();
      priceChart.remove();
      rsiChart.remove();
    };
  }, [data, rsiData, splits]);

  return (
    <div className="space-y-4">
      <div className="rounded-lg overflow-hidden border border-gray-700">
        <div ref={chartContainerRef} />
      </div>
      <div className="rounded-lg overflow-hidden border border-gray-700">
        <div className="p-4 bg-gray-800 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">RSI (14)</h2>
        </div>
        <div ref={rsiContainerRef} />
      </div>
    </div>
  );
}
