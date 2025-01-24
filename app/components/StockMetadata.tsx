import { SplitData } from "../types";

interface StockMetadataProps {
  splits: SplitData[];
}

export default function StockMetadata({ splits }: StockMetadataProps) {
  return (
    <div className="mt-6 text-gray-400 text-sm">
      <p>Data loaded from yFinance</p>
      <p>RSI calculated server-side</p>
      <p>
        Split ratios:{" "}
        {splits.map((s) => `${s.split_ratio}:1 on ${s.date}`).join(", ")}
      </p>
    </div>
  );
}
