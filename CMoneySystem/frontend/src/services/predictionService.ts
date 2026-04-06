// 预测相关 API 服务
import api from './api';
import type { ApiResponse, PredictRequest } from '@/types/api';
import type { PredictionResult } from '@/types/analysis';

/**
 * 执行股价预测
 */
export const predictStock = async (
  request: PredictRequest
): Promise<PredictionResult & { summary: string }> => {
  const response = await api.post<ApiResponse>('/predict', request);

  if (!response.success || !response.data) {
    throw new Error(response.message || '预测失败');
  }

  return response.data;
};

/**
 * 获取预测历史记录
 */
export const getPredictionHistory = async (params?: {
  stock_code?: string;
  time_horizon?: string;
  page?: number;
  page_size?: number;
}): Promise<{
  items: Array<PredictionResult & { timestamp: string; stockCode: string }>;
  total: number;
}> => {
  const response = await api.get<ApiResponse>('/prediction/history', { params });

  if (!response.success || !response.data) {
    throw new Error(response.message || '获取预测历史失败');
  }

  return response.data;
};

/**
 * 比较预测准确率
 */
export const getPredictionAccuracy = async (params?: {
  stock_code?: string;
  start_date?: string;
  end_date?: string;
}): Promise<{
  totalPredictions: number;
  correctPredictions: number;
  accuracy: number;
  byTimeHorizon: Record<string, { accuracy: number; count: number }>;
}> => {
  const response = await api.get<ApiResponse>('/prediction/accuracy', { params });

  if (!response.success || !response.data) {
    throw new Error(response.message || '获取准确率统计失败');
  }

  return response.data;
};
