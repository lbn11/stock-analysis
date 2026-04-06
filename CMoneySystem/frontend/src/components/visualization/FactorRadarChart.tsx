/**因子分析雷达图组件
 *
 * 使用雷达图展示7大因子的分析得分
 */
import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface FactorData {
  factor: string;
  score: number;
  weight: number;
  fullMark: number;
}

interface FactorRadarChartProps {
  data: FactorData[];
  height?: number;
}

export const FactorRadarChart: React.FC<FactorRadarChartProps> = ({
  data,
  height = 400
}) => {
  // 格式化因子名称
  const formatFactorName = (name: string): string => {
    const nameMap: { [key: string]: string } = {
      'fundamental': '基本面',
      'macro_economic': '宏观环境',
      'industry': '行业状况',
      'policy': '政策因素',
      'international': '国际关系',
      'funding': '资金面',
      'market_structure': '市场结构',
      'sentiment': '市场情绪',
      'technical': '技术面'
    };
    return nameMap[name] || name;
  };

  // 格式化数据用于显示
  const chartData = data.map((item) => ({
    factor: formatFactorName(item.factor),
    score: item.score,
    fullMark: item.fullMark || 100
  }));

  // 判断整体趋势
  const avgScore = data.reduce((sum, item) => sum + item.score, 0) / data.length;

  const getTrendColor = (score: number): string => {
    if (score >= 70) return '#10b981'; // green
    if (score >= 50) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const overallTrend = avgScore >= 60 ? 'positive' : avgScore >= 40 ? 'neutral' : 'negative';

  return (
    <div className="w-full space-y-4">
      {/* 雷达图 */}
      <ResponsiveContainer width="100%" height={height}>
        <RadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="factor" tick={{ fontSize: 12 }} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} />
          <Radar
            name="因子得分"
            dataKey="score"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.6}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>

      {/* 整体评价 */}
      <div className={`p-4 rounded-lg ${
        overallTrend === 'positive' ? 'bg-green-50 dark:bg-green-900' :
        overallTrend === 'neutral' ? 'bg-yellow-50 dark:bg-yellow-900' :
        'bg-red-50 dark:bg-red-900'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-300">综合得分</p>
            <p className={`text-2xl font-bold`} style={{ color: getTrendColor(avgScore) }}>
              {avgScore.toFixed(1)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-300">整体趋势</p>
            <p className={`text-lg font-semibold`}>
              {overallTrend === 'positive' && '📈 看涨'}
              {overallTrend === 'neutral' && '➡️ 中性'}
              {overallTrend === 'negative' && '📉 看跌'}
            </p>
          </div>
        </div>
      </div>

      {/* 详细得分列表 */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {data.map((item, index) => {
          const score = item.score;
          const factorName = formatFactorName(item.factor);

          return (
            <div
              key={index}
              className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg"
              style={{ borderLeft: `4px solid ${getTrendColor(score)}` }}
            >
              <p className="text-xs text-gray-600 dark:text-gray-400">{factorName}</p>
              <p className="text-lg font-bold" style={{ color: getTrendColor(score) }}>
                {score.toFixed(1)}
              </p>
            </div>
          );
        })}
      </div>

      {/* 权重说明 */}
      <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
        <h4 className="font-semibold mb-2 text-sm">因子权重配置</h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {data.map((item, index) => (
            <div key={index} className="flex justify-between">
              <span>{formatFactorName(item.factor)}</span>
              <span className="font-semibold">{(item.weight * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FactorRadarChart;
