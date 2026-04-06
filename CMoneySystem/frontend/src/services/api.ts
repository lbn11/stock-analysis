// API 基础配置
import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证 token（如果需要）
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 添加请求时间戳
    config.metadata = { startTime: new Date().getTime() };

    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 计算请求耗时
    const endTime = new Date().getTime();
    const startTime = response.config.metadata?.startTime || endTime;
    const duration = endTime - startTime;

    console.log(`API ${response.config.url} took ${duration}ms`);

    return response.data;
  },
  (error: AxiosError) => {
    // 统一错误处理
    let message = '请求失败，请稍后重试';

    if (error.response) {
      // 服务器返回错误
      const status = error.response.status;
      const data = error.response.data as any;

      switch (status) {
        case 400:
          message = data?.message || '请求参数错误';
          break;
        case 401:
          message = '未授权，请先登录';
          // 可以在这里跳转到登录页面
          break;
        case 403:
          message = '没有权限访问';
          break;
        case 404:
          message = '请求的资源不存在';
          break;
        case 500:
          message = '服务器内部错误';
          break;
        default:
          message = data?.message || message;
      }
    } else if (error.request) {
      // 请求发出但没有响应
      message = '网络连接失败，请检查网络';
    }

    console.error('Response error:', message, error);

    return Promise.reject({
      message,
      error,
    });
  }
);

// 类型扩展
declare module 'axios' {
  export interface AxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}

export default api;
