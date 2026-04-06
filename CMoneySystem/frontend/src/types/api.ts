// API 响应类型

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// 请求参数类型

export interface AnalyzeRequest {
  stock_code: string;
  analysis_type?: 'comprehensive' | 'fundamental' | 'technical';
  time_horizon?: 'short' | 'medium' | 'long';
  custom_weights?: Partial<Record<string, number>>;
}

export interface PredictRequest {
  stock_code: string;
  time_horizon?: 'short' | 'medium' | 'long';
  prediction_days?: number;
}

export interface HistoryQueryParams {
  page?: number;
  page_size?: number;
  stock_code?: string;
  start_date?: string;
  end_date?: string;
  trend?: -1 | 0 | 1;
}
