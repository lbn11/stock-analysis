// 股票相关 API 服务
import api from './api';
import type { ApiResponse } from '@/types/api';
import type { Stock, StockPriceHistory, FundamentalData } from '@/types/stock';

/**
 * 搜索股票
 */
export const searchStocks = async (keyword: string): Promise<Stock[]> => {
  const response = await api.get<ApiResponse<Stock[]>>('/stocks/search', {
    params: { q: keyword },
  });
  return response.data || [];
};

/**
 * 获取股票详情
 */
export const getStockDetail = async (stockCode: string): Promise<Stock> => {
  const response = await api.get<ApiResponse<Stock>>(`/stocks/${stockCode}`);
  if (!response.success || !response.data) {
    throw new Error(response.message || '获取股票详情失败');
  }
  return response.data;
};

/**
 * 获取股票历史价格
 */
export const getStockHistory = async (
  stockCode: string,
  days: number = 90
): Promise<StockPriceHistory[]> => {
  const response = await api.get<ApiResponse<StockPriceHistory[]>>(
    `/stocks/${stockCode}/history`,
    { params: { days } }
  );
  return response.data || [];
};

/**
 * 获取股票基本面数据
 */
export const getStockFundamentals = async (
  stockCode: string
): Promise<FundamentalData> => {
  const response = await api.get<ApiResponse<FundamentalData>>(
    `/stocks/${stockCode}/fundamentals`
  );
  if (!response.success || !response.data) {
    throw new Error(response.message || '获取基本面数据失败');
  }
  return response.data;
};

/**
 * 获取热门股票列表
 */
export const getPopularStocks = async (limit: number = 10): Promise<Stock[]> => {
  const response = await api.get<ApiResponse<Stock[]>>('/stocks/popular', {
    params: { limit },
  });
  return response.data || [];
};
