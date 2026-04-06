// 股票状态管理
import { create } from 'zustand';
import type { Stock, StockPriceHistory } from '@/types/stock';

interface StockState {
  // 当前选中的股票
  selectedStock: string | null;
  // 股票详情
  stockDetail: Stock | null;
  // 股票历史价格
  stockHistory: StockPriceHistory[];
  // 搜索历史
  searchHistory: string[];

  // Actions
  setSelectedStock: (code: string) => void;
  setStockDetail: (stock: Stock | null) => void;
  setStockHistory: (history: StockPriceHistory[]) => void;
  addSearchHistory: (code: string) => void;
  clearSearchHistory: () => void;
  clearStock: () => void;
}

export const useStockStore = create<StockState>((set, get) => ({
  selectedStock: null,
  stockDetail: null,
  stockHistory: [],
  searchHistory: (() => {
    try {
      const saved = localStorage.getItem('search_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  })(),

  setSelectedStock: (code) => set({ selectedStock: code }),

  setStockDetail: (stock) => set({ stockDetail: stock }),

  setStockHistory: (history) => set({ stockHistory: history }),

  addSearchHistory: (code) => {
    const { searchHistory } = get();
    const newHistory = [code, ...searchHistory.filter((c) => c !== code)].slice(
      0,
      10
    );
    set({ searchHistory: newHistory });
    localStorage.setItem('search_history', JSON.stringify(newHistory));
  },

  clearSearchHistory: () => {
    set({ searchHistory: [] });
    localStorage.removeItem('search_history');
  },

  clearStock: () =>
    set({
      selectedStock: null,
      stockDetail: null,
      stockHistory: [],
    }),
}));
