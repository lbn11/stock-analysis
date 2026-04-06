// 分析状态管理
import { create } from 'zustand';
import type { AnalysisResult, FactorWeight } from '@/types/analysis';
import { DEFAULT_FACTOR_WEIGHTS } from '@/utils/constants';

interface AnalysisState {
  // 当前分析结果
  currentAnalysis: AnalysisResult | null;
  // 分析历史
  analysisHistory: AnalysisResult[];
  // 因子权重配置
  factorWeights: FactorWeight;
  // 加载状态
  isAnalyzing: boolean;

  // Actions
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void;
  addAnalysisHistory: (analysis: AnalysisResult) => void;
  setFactorWeights: (weights: FactorWeight) => void;
  setIsAnalyzing: (loading: boolean) => void;
  resetFactorWeights: () => void;
  clearAnalysis: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  currentAnalysis: null,
  analysisHistory: [],
  factorWeights: (() => {
    try {
      const saved = localStorage.getItem('factor_weights');
      return saved ? JSON.parse(saved) : DEFAULT_FACTOR_WEIGHTS;
    } catch {
      return DEFAULT_FACTOR_WEIGHTS;
    }
  })(),
  isAnalyzing: false,

  setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),

  addAnalysisHistory: (analysis) =>
    set((state) => ({
      analysisHistory: [analysis, ...state.analysisHistory].slice(0, 20),
    })),

  setFactorWeights: (weights) => {
    set({ factorWeights: weights });
    localStorage.setItem('factor_weights', JSON.stringify(weights));
  },

  setIsAnalyzing: (loading) => set({ isAnalyzing: loading }),

  resetFactorWeights: () => {
    set({ factorWeights: DEFAULT_FACTOR_WEIGHTS });
    localStorage.removeItem('factor_weights');
  },

  clearAnalysis: () =>
    set({
      currentAnalysis: null,
      isAnalyzing: false,
    }),
}));
