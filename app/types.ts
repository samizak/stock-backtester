export interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  split_ratio: number;
}

export interface SplitData {
  date: string;
  split_ratio: number;
}

export interface StockData {
  seriesData: any[];
  rsiData: any[];
  splits: SplitData[];
}
