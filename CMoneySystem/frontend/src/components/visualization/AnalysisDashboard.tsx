/**综合分析仪表板组件
 *
 * 整合所有可视化组件，提供完整的分析结果展示
 */
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import PriceChart from './PriceChart';
import ChipDistributionChart from './ChipDistributionChart';
import FactorRadarChart from './FactorRadarChart';
import SentimentDashboard from './SentimentDashboard';

interface AnalysisResult {
  stock_code: string;
  stock_name?: string;
  current_price: number;
  prediction: {
    trend: number;
    trend_name: string;
    confidence: number;
  };
  comprehensive_score: number;
  recommendation: string;
  factors: Array<{
    factor: string;
    score: number;
    weight: number;
  }>;
  chip_distribution?: any;
  sentiment?: any;
  price_history?: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
}

interface AnalysisDashboardProps {
  data: AnalysisResult;
}

export const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const getTrendColor = (trend: number): string => {
    if (trend > 0) return 'text-red-600'; // 上涨用红色（中国习惯）
    if (trend < 0) return 'text-green-600'; // 下跌用绿色
    return 'text-gray-600';
  };

  const getTrendIcon = (trend: number): string => {
    if (trend > 0) return '📈';
    if (trend < 0) return '📉';
    return '➡️';
  };

  return (
    <div className="w-full space-y-6">
      {/* 标题栏 */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold">{data.stock_name || data.stock_code}</h2>
            <p className="text-sm text-gray-500">{data.stock_code}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">当前价格</p>
            <p className="text-3xl font-bold">¥{data.current_price.toFixed(2)}</p>
          </div>
        </div>

        {/* 预测结果 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">预测趋势</p>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-2xl">{getTrendIcon(data.prediction.trend)}</span>
              <p className={`text-xl font-bold ${getTrendColor(data.prediction.trend)}`}>
                {data.prediction.trend_name}
              </p>
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">置信度</p>
            <p className="text-xl font-bold mt-1">
              {(data.prediction.confidence * 100).toFixed(1)}%
            </p>
          </div>

          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">综合评分</p>
            <p className="text-xl font-bold mt-1">
              {data.comprehensive_score.toFixed(2)}
            </p>
          </div>
        </div>

        {/* 投资建议 */}
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">投资建议</p>
          <p className="text-lg font-semibold">{data.recommendation}</p>
        </div>
      </div>

      {/* 标签页 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">综合概览</TabsTrigger>
          <TabsTrigger value="factors">因子分析</TabsTrigger>
          <TabsTrigger value="chip">筹码分布</TabsTrigger>
          <TabsTrigger value="sentiment">情绪分析</TabsTrigger>
        </TabsList>

        {/* 综合概览 */}
        <TabsContent value="overview" className="space-y-6">
          {/* 价格图表 */}
          {data.price_history && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">价格走势</h3>
              <PriceChart data={data.price_history} height={300} />
            </div>
          )}

          {/* 因子雷达图 */}
          {data.factors && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">因子分析</h3>
              <FactorRadarChart
                data={data.factors.map(f => ({ ...f, fullMark: 100 }))}
                height={400}
              />
            </div>
          )}
        </TabsContent>

        {/* 因子分析 */}
        <TabsContent value="factors" className="space-y-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">详细因子分析</h3>
            <FactorRadarChart
              data={data.factors.map(f => ({ ...f, fullMark: 100 }))}
              height={500}
            />
          </div>

          {/* 因子得分详细列表 */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">因子得分详情</h3>
            <div className="space-y-3">
              {data.factors.map((factor, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <div>
                    <p className="font-semibold">{factor.factor}</p>
                    <p className="text-sm text-gray-500">权重: {(factor.weight * 100).toFixed(1)}%</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold">{factor.score.toFixed(1)}</p>
                    <p className="text-xs text-gray-500">/ 100</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>

        {/* 筹码分布 */}
        <TabsContent value="chip">
          {data.chip_distribution ? (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <ChipDistributionChart data={data.chip_distribution} />
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow text-center py-12">
              <p className="text-gray-500">筹码分布数据暂不可用</p>
            </div>
          )}
        </TabsContent>

        {/* 情绪分析 */}
        <TabsContent value="sentiment">
          {data.sentiment ? (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <SentimentDashboard data={data.sentiment.overall} />
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow text-center py-12">
              <p className="text-gray-500">情绪分析数据暂不可用</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalysisDashboard;
