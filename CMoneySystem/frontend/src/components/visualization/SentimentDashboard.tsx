/**情感分析仪表板组件
 *
 * 展示新闻情感分析结果和市场情绪指标
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface SentimentData {
  overall_sentiment: 'positive' | 'negative' | 'neutral';
  average_score: number;
  news_count: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  positive_ratio: number;
  negative_ratio: number;
}

interface SentimentDashboardProps {
  data: SentimentData;
}

export const SentimentDashboard: React.FC<SentimentDashboardProps> = ({ data }) => {
  const getSentimentIcon = (sentiment: string): string => {
    switch (sentiment) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😟';
      default:
        return '😐';
    }
  };

  const getSentimentColor = (sentiment: string): string => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600 bg-green-50 dark:bg-green-900';
      case 'negative':
        return 'text-red-600 bg-red-50 dark:bg-red-900';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-800';
    }
  };

  const getSentimentLabel = (sentiment: string): string => {
    switch (sentiment) {
      case 'positive':
        return '积极';
      case 'negative':
        return '消极';
      default:
        return '中性';
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* 整体情绪概览 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-6 rounded-lg ${getSentimentColor(data.overall_sentiment)}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-5xl">{getSentimentIcon(data.overall_sentiment)}</span>
            <div>
              <p className="text-sm opacity-75">市场整体情绪</p>
              <p className="text-2xl font-bold">{getSentimentLabel(data.overall_sentiment)}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm opacity-75">情绪得分</p>
            <p className="text-3xl font-bold">
              {(data.average_score * 100).toFixed(1)}
            </p>
            <p className="text-xs opacity-75">
              {data.average_score >= 0.1 ? '(偏多头)' : data.average_score <= -0.1 ? '(偏空头)' : '(中性)'}
            </p>
          </div>
        </div>
      </motion.div>

      {/* 情绪分布 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 积极新闻 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-green-50 dark:bg-green-900 p-4 rounded-lg"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-2xl">😊</span>
            <span className="text-sm text-green-600 dark:text-green-400 font-semibold">
              积极
            </span>
          </div>
          <p className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">
            {data.positive_count}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            占比 {(data.positive_ratio * 100).toFixed(1)}%
          </p>
          <div className="mt-3 bg-green-200 dark:bg-green-800 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${data.positive_ratio * 100}%` }}
            />
          </div>
        </motion.div>

        {/* 中性新闻 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-2xl">😐</span>
            <span className="text-sm text-gray-600 dark:text-gray-400 font-semibold">
              中性
            </span>
          </div>
          <p className="text-3xl font-bold text-gray-600 dark:text-gray-400 mb-1">
            {data.neutral_count}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            占比 {((data.neutral_count / data.news_count) * 100).toFixed(1)}%
          </p>
          <div className="mt-3 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-gray-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(data.neutral_count / data.news_count) * 100}%` }}
            />
          </div>
        </motion.div>

        {/* 消极新闻 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-red-50 dark:bg-red-900 p-4 rounded-lg"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-2xl">😟</span>
            <span className="text-sm text-red-600 dark:text-red-400 font-semibold">
              消极
            </span>
          </div>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">
            {data.negative_count}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            占比 {(data.negative_ratio * 100).toFixed(1)}%
          </p>
          <div className="mt-3 bg-red-200 dark:bg-red-800 rounded-full h-2">
            <div
              className="bg-red-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${data.negative_ratio * 100}%` }}
            />
          </div>
        </motion.div>
      </div>

      {/* 统计摘要 */}
      <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
        <h4 className="font-semibold mb-3">情绪分析摘要</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600 dark:text-gray-300">分析新闻总数</p>
            <p className="text-xl font-bold">{data.news_count}</p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-300">情绪强度</p>
            <p className="text-xl font-bold">
              {Math.abs(data.average_score) >= 0.3 ? '强' :
               Math.abs(data.average_score) >= 0.1 ? '中' : '弱'}
            </p>
          </div>
        </div>

        {/* 投资建议 */}
        {data.overall_sentiment === 'positive' && data.positive_ratio > 0.6 && (
          <div className="mt-4 p-3 bg-green-100 dark:bg-green-800 rounded-lg">
            <p className="text-sm font-semibold text-green-800 dark:text-green-200">
              💡 市场情绪积极，利好消息占主导，可考虑适度参与
            </p>
          </div>
        )}

        {data.overall_sentiment === 'negative' && data.negative_ratio > 0.6 && (
          <div className="mt-4 p-3 bg-red-100 dark:bg-red-800 rounded-lg">
            <p className="text-sm font-semibold text-red-800 dark:text-red-200">
              ⚠️ 市场情绪消极，利空消息较多，建议谨慎操作
            </p>
          </div>
        )}

        {data.overall_sentiment === 'neutral' && (
          <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              ℹ️ 市场情绪中性，多空消息相对平衡，建议观望
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SentimentDashboard;
