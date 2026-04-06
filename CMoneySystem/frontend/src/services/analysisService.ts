// 分析相关 API 服务
import api from './api';
import type { ApiResponse, AnalyzeRequest } from '@/types/api';
import type { AnalysisResult, FactorWeight } from '@/types/analysis';

/**
 * 执行股票分析
 */
export const analyzeStock = async (
  request: AnalyzeRequest
): Promise<AnalysisResult> => {
  const response = await api.post<ApiResponse<AnalysisResult>>(
    '/analyze',
    request
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '分析失败');
  }

  return response.data;
};

/**
 * 获取因子权重配置
 */
export const getFactorWeights = async (): Promise<FactorWeight> => {
  const response = await api.get<ApiResponse<{ weights: FactorWeight }>>(
    '/factors'
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '获取因子配置失败');
  }

  return response.data.weights;
};

/**
 * 更新因子权重配置
 */
export const updateFactorWeights = async (
  weights: FactorWeight
): Promise<void> => {
  const response = await api.post<ApiResponse>('/factors/update', { weights });

  if (!response.success) {
    throw new Error(response.message || '更新因子配置失败');
  }
};

/**
 * 获取分析历史记录
 */
export const getAnalysisHistory = async (params?: {
  page?: number;
  page_size?: number;
  stock_code?: string;
}): Promise<{
  items: AnalysisResult[];
  total: number;
  page: number;
  pageSize: number;
}> => {
  const response = await api.get<ApiResponse>('/analysis/history', { params });

  if (!response.success || !response.data) {
    throw new Error(response.message || '获取历史记录失败');
  }

  return response.data;
};
