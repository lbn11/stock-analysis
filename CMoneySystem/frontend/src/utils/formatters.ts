// 格式化工具函数
import { format, parseISO } from 'date-fns';
import { zhCN } from 'date-fns/locale';

/**
 * 格式化价格
 * @param price 价格
 * @param decimals 小数位数，默认2位
 */
export const formatPrice = (price: number, decimals: number = 2): string => {
  return `¥${price.toFixed(decimals)}`;
};

/**
 * 格式化百分比
 * @param value 数值（0-1之间或0-100之间）
 * @param includeSign 是否包含正负号
 */
export const formatPercent = (
  value: number,
  includeSign: boolean = false
): string => {
  const percent = value > 1 ? value : value * 100;
  const formatted = percent.toFixed(2);
  if (includeSign && percent > 0) {
    return `+${formatted}%`;
  }
  return `${formatted}%`;
};

/**
 * 格式化大数字（如市值）
 * @param value 数值
 */
export const formatLargeNumber = (value: number): string => {
  if (value >= 1e12) {
    return `${(value / 1e12).toFixed(2)}万亿`;
  }
  if (value >= 1e8) {
    return `${(value / 1e8).toFixed(2)}亿`;
  }
  if (value >= 1e4) {
    return `${(value / 1e4).toFixed(2)}万`;
  }
  return value.toString();
};

/**
 * 格式化日期
 * @param date 日期字符串或Date对象
 * @param formatStr 格式字符串
 */
export const formatDate = (
  date: string | Date,
  formatStr: string = 'yyyy-MM-dd'
): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatStr, { locale: zhCN });
};

/**
 * 格式化日期时间
 * @param date 日期字符串或Date对象
 */
export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, 'yyyy-MM-dd HH:mm:ss');
};

/**
 * 格式化相对时间
 * @param date 日期字符串或Date对象
 */
export const formatRelativeTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const now = new Date();
  const diff = now.getTime() - dateObj.getTime();

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 7) {
    return formatDate(dateObj);
  }
  if (days > 0) {
    return `${days}天前`;
  }
  if (hours > 0) {
    return `${hours}小时前`;
  }
  if (minutes > 0) {
    return `${minutes}分钟前`;
  }
  return '刚刚';
};

/**
 * 格式化股票代码
 * @param code 股票代码
 */
export const formatStockCode = (code: string): string => {
  return code.toUpperCase().padStart(6, '0');
};

/**
 * 格式化置信度
 * @param confidence 置信度（0-1之间）
 */
export const formatConfidence = (confidence: number): string => {
  return `${(confidence * 100).toFixed(1)}%`;
};

/**
 * 获取趋势文本
 * @param trend 趋势值（-1, 0, 1）
 */
export const getTrendText = (trend: -1 | 0 | 1): string => {
  const trendMap = {
    '1': '上涨',
    '0': '横盘',
    '-1': '下跌',
  };
  return trendMap[trend.toString() as '1' | '0' | '-1'];
};

/**
 * 获取趋势颜色类名
 * @param trend 趋势值（-1, 0, 1）
 */
export const getTrendColorClass = (trend: -1 | 0 | 1): string => {
  const colorMap = {
    '1': 'text-stock-up',
    '0': 'text-stock-flat',
    '-1': 'text-stock-down',
  };
  return colorMap[trend.toString() as '1' | '0' | '-1'];
};

/**
 * 获取趋势图标
 * @param trend 趋势值（-1, 0, 1）
 */
export const getTrendIcon = (trend: -1 | 0 | 1): string => {
  const iconMap = {
    '1': '↑',
    '0': '→',
    '-1': '↓',
  };
  return iconMap[trend.toString() as '1' | '0' | '-1'];
};
