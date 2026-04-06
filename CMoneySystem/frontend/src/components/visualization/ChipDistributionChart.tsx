/**筹码分布图表组件
 *
 * 可视化筹码分布情况，显示支撑位、压力位等关键信息
 */
import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Label
} from 'recharts';

interface ChipDistributionData {
  price_bins: number[];
  bin_centers: number[];
  chip_distribution: number[];
  total_chips: number;
  peak_price: number;
  peak_chips: number;
  concentration_ratio: number;
  weighted_avg_price: number;
  support_level: number;
  pressure_level: number;
  current_price?: number;
}

interface ChipDistributionChartProps {
  data: ChipDistributionData;
  height?: number;
}

export const ChipDistributionChart: React.FC<ChipDistributionChartProps> = ({
  data,
  height = 400
}) => {
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    // 转换数据格式用于图表显示
    const formatted = data.bin_centers.map((price, index) => ({
      price: price.toFixed(2),
      chips: data.chip_distribution[index],
      price_num: price
    }));

    setChartData(formatted);
  }, [data]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const price = payload[0].payload.price_num;
      const chips = payload[0].value;
      const ratio = (chips / data.total_chips * 100).toFixed(2);

      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border">
          <p className="text-sm font-semibold">价格: {price.toFixed(2)} 元</p>
          <p className="text-sm">筹码量: {chips.toFixed(0)}</p>
          <p className="text-sm">占比: {ratio}%</p>
        </div>
      );
    }
    return null;
  };

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">暂无筹码分布数据</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* 筹码分布柱状图 */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">筹码分布图</h3>
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={chartData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis
              type="category"
              dataKey="price"
              interval={0}
              tick={{ fontSize: 10 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="chips" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 关键指标信息 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300">筹码重心</p>
          <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
            {data.weighted_avg_price.toFixed(2)} 元
          </p>
        </div>

        <div className="bg-green-50 dark:bg-green-900 p-4 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300">支撑位</p>
          <p className="text-xl font-bold text-green-600 dark:text-green-400">
            {data.support_level.toFixed(2)} 元
          </p>
        </div>

        <div className="bg-red-50 dark:bg-red-900 p-4 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300">压力位</p>
          <p className="text-xl font-bold text-red-600 dark:text-red-400">
            {data.pressure_level.toFixed(2)} 元
          </p>
        </div>

        <div className="bg-purple-50 dark:bg-purple-900 p-4 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300">集中度</p>
          <p className="text-xl font-bold text-purple-600 dark:text-purple-400">
            {(data.concentration_ratio * 100).toFixed(2)}%
          </p>
        </div>
      </div>

      {/* 信号说明 */}
      {data.current_price && (
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
          <h4 className="font-semibold mb-2">当前价格位置分析</h4>
          <div className="space-y-2 text-sm">
            {data.current_price > data.weighted_avg_price && (
              <p className="text-green-600">
                ✓ 当前价格在筹码重心上方，筹码分布偏多头
              </p>
            )}
            {data.current_price < data.weighted_avg_price && (
              <p className="text-red-600">
                ⚠ 当前价格在筹码重心下方，筹码分布偏空头
              </p>
            )}
            {data.current_price <= data.support_level * 1.02 && (
              <p className="text-blue-600">
                ✓ 价格接近支撑位 {data.support_level.toFixed(2)} 元，可能获得支撑
              </p>
            )}
            {data.current_price >= data.pressure_level * 0.98 && (
              <p className="text-orange-600">
                ⚠ 价格接近压力位 {data.pressure_level.toFixed(2)} 元，可能遇到阻力
              </p>
            )}
            {data.concentration_ratio > 0.3 && (
              <p className="text-purple-600">
                ℹ 筹码集中度较高（{(data.concentration_ratio * 100).toFixed(1)}%），价格波动可能加剧
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChipDistributionChart;
