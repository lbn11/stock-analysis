/**股价图表组件
 *
 * 使用 Recharts 实现股价数据可视化
 * 支持 K线图、移动平均线、成交量等多种图表类型
 */
import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  CandlestickChart,
  Candlestick,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma5?: number;
  ma10?: number;
  ma20?: number;
}

interface PriceChartProps {
  data: PriceData[];
  height?: number;
  showMA?: boolean;
  showVolume?: boolean;
  chartType?: 'line' | 'area' | 'candlestick';
}

export const PriceChart: React.FC<PriceChartProps> = ({
  data,
  height = 400,
  showMA = true,
  showVolume = true,
  chartType = 'area'
}) => {
  const [chartData, setChartData] = useState<PriceData[]>([]);

  useEffect(() => {
    setChartData(data);
  }, [data]);

  const formatTooltip = (value: any, name: any, props: any) => {
    if (name === 'volume') {
      return [`${(value / 10000).toFixed(2)} 万`, '成交量'];
    }
    return [value.toFixed(2), name];
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border">
          <p className="text-sm font-semibold">{label}</p>
          <p className="text-sm">开盘: {data.open.toFixed(2)}</p>
          <p className="text-sm">最高: {data.high.toFixed(2)}</p>
          <p className="text-sm">最低: {data.low.toFixed(2)}</p>
          <p className="text-sm">收盘: {data.close.toFixed(2)}</p>
          <p className="text-sm text-gray-500">
            成交量: {(data.volume / 10000).toFixed(2)} 万
          </p>
        </div>
      );
    }
    return null;
  };

  const renderChart = () => {
    if (chartData.length === 0) {
      return (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">暂无数据</p>
        </div>
      );
    }

    if (chartType === 'line') {
      return (
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(value) => format(new Date(value), 'MM/dd', { locale: zhCN })}
            />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="close"
              stroke="#3b82f6"
              strokeWidth={2}
              name="收盘价"
              dot={false}
            />
            {showMA && data[0]?.ma5 && (
              <Line type="monotone" dataKey="ma5" stroke="#f59e0b" strokeWidth={1} name="MA5" dot={false} />
            )}
            {showMA && data[0]?.ma10 && (
              <Line type="monotone" dataKey="ma10" stroke="#10b981" strokeWidth={1} name="MA10" dot={false} />
            )}
            {showMA && data[0]?.ma20 && (
              <Line type="monotone" dataKey="ma20" stroke="#ef4444" strokeWidth={1} name="MA20" dot={false} />
            )}
          </LineChart>
        </ResponsiveContainer>
      );
    }

    if (chartType === 'candlestick') {
      return (
        <ResponsiveContainer width="100%" height={height}>
          <CandlestickChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(value) => format(new Date(value), 'MM/dd', { locale: zhCN })}
            />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Candlestick dataKey="close" fill="#3b82f6" />
          </CandlestickChart>
        </ResponsiveContainer>
      );
    }

    // Default: area chart
    return (
      <>
        <ResponsiveContainer width="100%" height={height - 100}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(value) => format(new Date(value), 'MM/dd', { locale: zhCN })}
            />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="close"
              stroke="#3b82f6"
              fillOpacity={1}
              fill="url(#colorClose)"
              name="收盘价"
            />
            {showMA && data[0]?.ma5 && (
              <Line type="monotone" dataKey="ma5" stroke="#f59e0b" strokeWidth={1} name="MA5" dot={false} />
            )}
            {showMA && data[0]?.ma10 && (
              <Line type="monotone" dataKey="ma10" stroke="#10b981" strokeWidth={1} name="MA10" dot={false} />
            )}
            {showMA && data[0]?.ma20 && (
              <Line type="monotone" dataKey="ma20" stroke="#ef4444" strokeWidth={1} name="MA20" dot={false} />
            )}
          </AreaChart>
        </ResponsiveContainer>

        {showVolume && (
          <ResponsiveContainer width="100%" height={100}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => format(new Date(value), 'MM/dd', { locale: zhCN })}
              />
              <YAxis />
              <Tooltip formatter={formatTooltip} />
              <Bar dataKey="volume" fill="#8b5cf6" name="成交量" opacity={0.5} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </>
    );
  };

  return (
    <div className="w-full">
      {renderChart()}
    </div>
  );
};

export default PriceChart;
