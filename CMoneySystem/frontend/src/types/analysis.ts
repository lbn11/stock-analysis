// 分析相关类型定义

export interface FactorScore {
  name: string;
  score: number;
  weight: number;
  details: Record<string, any>;
}

export interface AnalysisResult {
  stockCode: string;
  analysisType: 'comprehensive' | 'fundamental' | 'technical';
  comprehensiveScore: number;
  prediction: PredictionResult;
  factors: FactorScore[];
  recommendation: string;
  riskLevel: 'low' | 'medium' | 'high';
  summary: string;
  timestamp: string;
}

export interface PredictionResult {
  trend: -1 | 0 | 1; // -1: 下跌, 0: 横盘, 1: 上涨
  trendName: string;
  confidence: number;
  priceChangePct: number;
  targetPrice?: number;
  supportLevel?: number;
  resistanceLevel?: number;
}

export interface FactorWeight {
  fundamental: number;
  macro_economic: number;
  industry: number;
  policy: number;
  international: number;
  funding: number;
  market_structure: number;
}

export interface TimeHorizon {
  value: 'short' | 'medium' | 'long';
  label: string;
  days: number;
}
