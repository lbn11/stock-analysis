// 常量定义

// 时间维度配置
export const TIME_HORIZONS = {
  short: {
    value: 'short' as const,
    label: '短期',
    description: '1-3个月',
    days: 90,
  },
  medium: {
    value: 'medium' as const,
    label: '中期',
    description: '3-12个月',
    days: 365,
  },
  long: {
    value: 'long' as const,
    label: '长期',
    description: '1年以上',
    days: 1095,
  },
} as const;

// 趋势类型
export const TREND_TYPES = {
  UP: {
    value: 1,
    label: '上涨',
    icon: '↑',
    color: 'text-stock-up',
    bgColor: 'bg-green-50',
  },
  DOWN: {
    value: -1,
    label: '下跌',
    icon: '↓',
    color: 'text-stock-down',
    bgColor: 'bg-red-50',
  },
  FLAT: {
    value: 0,
    label: '横盘',
    icon: '→',
    color: 'text-stock-flat',
    bgColor: 'bg-gray-50',
  },
} as const;

// 风险等级
export const RISK_LEVELS = {
  low: {
    label: '低',
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    description: '风险较小，适合稳健投资',
  },
  medium: {
    label: '中',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    description: '风险适中，需要关注市场变化',
  },
  high: {
    label: '高',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    description: '风险较大，需谨慎投资',
  },
} as const;

// 投资建议
export const RECOMMENDATIONS = {
  STRONG_BUY: {
    value: 'strong_buy',
    label: '强烈买入',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
  },
  BUY: {
    value: 'buy',
    label: '买入',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
  },
  HOLD: {
    value: 'hold',
    label: '持有',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
  },
  SELL: {
    value: 'sell',
    label: '卖出',
    color: 'text-red-600',
    bgColor: 'bg-red-50',
  },
  STRONG_SELL: {
    value: 'strong_sell',
    label: '强烈卖出',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
  },
} as const;

// 因子名称映射
export const FACTOR_NAMES = {
  fundamental: '基本面因素',
  macro_economic: '宏观环境因素',
  industry: '行业状况因素',
  policy: '政策因素',
  international: '国际关系因素',
  funding: '资金面因素',
  market_structure: '市场结构因素',
} as const;

// 默认因子权重
export const DEFAULT_FACTOR_WEIGHTS = {
  fundamental: 0.30,
  macro_economic: 0.20,
  industry: 0.15,
  policy: 0.15,
  international: 0.10,
  funding: 0.05,
  market_structure: 0.05,
} as const;

// 预设因子权重模板
export const FACTOR_WEIGHT_PRESETS = {
  conservative: {
    name: '保守型',
    description: '侧重基本面和宏观环境',
    weights: {
      fundamental: 0.40,
      macro_economic: 0.25,
      industry: 0.15,
      policy: 0.10,
      international: 0.05,
      funding: 0.03,
      market_structure: 0.02,
    },
  },
  balanced: {
    name: '平衡型',
    description: '均衡考虑各项因素',
    weights: DEFAULT_FACTOR_WEIGHTS,
  },
  aggressive: {
    name: '激进型',
    description: '侧重市场情绪和资金面',
    weights: {
      fundamental: 0.20,
      macro_economic: 0.15,
      industry: 0.15,
      policy: 0.10,
      international: 0.15,
      funding: 0.15,
      market_structure: 0.10,
    },
  },
} as const;

// API 端点
export const API_ENDPOINTS = {
  HEALTH: '/health',
  ANALYZE: '/analyze',
  PREDICT: '/predict',
  FACTORS: '/factors',
  STOCKS_SEARCH: '/stocks/search',
  STOCKS_DETAIL: '/stocks/:code',
  STOCKS_HISTORY: '/stocks/:code/history',
  ANALYSIS_HISTORY: '/analysis/history',
  PREDICTION_HISTORY: '/prediction/history',
} as const;

// 本地存储键名
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_INFO: 'user_info',
  FACTOR_WEIGHTS: 'factor_weights',
  SEARCH_HISTORY: 'search_history',
  THEME: 'theme',
} as const;

// 图表颜色配置
export const CHART_COLORS = {
  primary: '#2563eb',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  neutral: '#6b7280',
  grid: '#e5e7eb',
  tooltip: {
    bg: 'rgba(255, 255, 255, 0.95)',
    border: '#d1d5db',
  },
} as const;
