// 股票相关类型定义

export interface Stock {
  code: string;
  name: string;
  currentPrice: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  industry: string;
}

export interface StockPriceHistory {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface FundamentalData {
  revenue: number;
  netProfit: number;
  grossMargin: number;
  roe: number;
  roa: number;
  eps: number;
  pe: number;
  pb: number;
  debtRatio: number;
}
