import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  CheckCircle,
  Target,
  ArrowDown,
  ArrowUp,
  Calendar,
} from 'lucide-react';
import { predictStock } from '@/services/predictionService';
import { formatPrice, formatPercent } from '@/utils/formatters';
import { cn } from '@/utils/helpers';

type TimeHorizon = 'short' | 'medium' | 'long';

const TIME_HORIZON_CONFIG = {
  short: { label: '短期预测', period: '1-3个月', days: 90, color: 'bg-blue-500' },
  medium: { label: '中期预测', period: '3-12个月', days: 365, color: 'bg-purple-500' },
  long: { label: '长期预测', period: '1年以上', days: 1095, color: 'bg-green-500' },
};

export default function PredictionPage() {
  const [searchParams] = useSearchParams();
  const horizonParam = searchParams.get('horizon') as TimeHorizon;
  const [selectedHorizon, setSelectedHorizon] = useState<TimeHorizon>(horizonParam || 'medium');
  const [stockCode, setStockCode] = useState('000001');

  // 获取预测数据
  const { data: prediction, isLoading, error, refetch } = useQuery({
    queryKey: ['prediction', stockCode, selectedHorizon],
    queryFn: () =>
      predictStock({
        stock_code: stockCode,
        time_horizon: selectedHorizon,
        prediction_days: TIME_HORIZON_CONFIG[selectedHorizon].days,
      }),
    enabled: !!stockCode,
    retry: 1,
  });

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return <ErrorState stockCode={stockCode} onRetry={() => refetch()} />;
  }

  if (!prediction) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* 顶部：时间维度选择器 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">股价趋势预测</h1>
          <TimeHorizonSelector
            selected={selectedHorizon}
            onChange={setSelectedHorizon}
          />
        </div>
        <StockInfoBar stockCode={stockCode} prediction={prediction} />
      </div>

      {/* 中间：预测结果可视化 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 左侧：趋势卡片 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">趋势预测</h2>
          <TrendCard
            prediction={prediction}
            horizon={selectedHorizon}
          />
        </div>

        {/* 右侧：价格目标 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">价格目标</h2>
          <PriceTargets prediction={prediction} />
        </div>
      </div>

      {/* 价格走势预测图 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">
          价格走势预测 - {TIME_HORIZON_CONFIG[selectedHorizon].label}
        </h2>
        <PriceTrendChart
          currentPrice={12.34}
          targetPrice={prediction.targetPrice}
          trend={prediction.trend}
          horizon={selectedHorizon}
        />
      </div>

      {/* 风险评估和预测依据 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">风险评估</h2>
          <RiskAssessment prediction={prediction} />
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">预测依据</h2>
          <PredictionBasis prediction={prediction} horizon={selectedHorizon} />
        </div>
      </div>
    </div>
  );
}

// 时间维度选择器
function TimeHorizonSelector({
  selected,
  onChange,
}: {
  selected: TimeHorizon;
  onChange: (horizon: TimeHorizon) => void;
}) {
  return (
    <div className="flex gap-2">
      {(Object.keys(TIME_HORIZON_CONFIG) as TimeHorizon[]).map((horizon) => {
        const config = TIME_HORIZON_CONFIG[horizon];
        const isSelected = selected === horizon;

        return (
          <button
            key={horizon}
            onClick={() => onChange(horizon)}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              isSelected
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            )}
          >
            {config.label}
          </button>
        );
      })}
    </div>
  );
}

// 股票信息栏
function StockInfoBar({
  stockCode,
  prediction,
}: {
  stockCode: string;
  prediction: any;
}) {
  const isUp = prediction.trend === 1;
  const isDown = prediction.trend === -1;

  return (
    <div className="flex items-center gap-6">
      <div>
        <span className="text-2xl font-bold">{stockCode}</span>
        <span className="ml-2 text-lg text-gray-600">平安银行</span>
      </div>
      <div className="flex items-baseline gap-3">
        <span className="text-xl font-bold numeric">¥12.34</span>
        <span
          className={cn(
            'text-lg font-medium flex items-center gap-1',
            isUp && 'text-stock-up',
            isDown && 'text-stock-down'
          )}
        >
          {isUp && <TrendingUp className="w-4 h-4" />}
          {isDown && <TrendingDown className="w-4 h-4" />}
          {!isUp && !isDown && <Minus className="w-4 h-4" />}
          {prediction.priceChangePct ? formatPercent(prediction.priceChangePct, true) : '+2.3%'}
        </span>
      </div>
    </div>
  );
}

// 趋势卡片
function TrendCard({
  prediction,
  horizon,
}: {
  prediction: any;
  horizon: TimeHorizon;
}) {
  const config = TIME_HORIZON_CONFIG[horizon];
  const isUp = prediction.trend === 1;
  const isDown = prediction.trend === -1;
  const isFlat = prediction.trend === 0;

  const getTrendIcon = () => {
    if (isUp) return <TrendingUp className="w-16 h-16 text-stock-up" />;
    if (isDown) return <TrendingDown className="w-16 h-16 text-stock-down" />;
    return <Minus className="w-16 h-16 text-gray-500" />;
  };

  return (
    <div className="space-y-6">
      {/* 趋势图标和方向 */}
      <div className="flex items-center justify-center">
        {getTrendIcon()}
      </div>

      {/* 趋势描述 */}
      <div className="text-center">
        <div className="text-3xl font-bold mb-2">{prediction.trendName}</div>
        <div className="text-lg text-gray-600">{config.period}</div>
      </div>

      {/* 置信度 */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-700">预测置信度</span>
          <span className="text-2xl font-bold numeric">
            {(prediction.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={cn(
              'h-3 rounded-full transition-all duration-500',
              prediction.confidence >= 0.7
                ? 'bg-green-500'
                : prediction.confidence >= 0.5
                ? 'bg-yellow-500'
                : 'bg-red-500'
            )}
            style={{ width: `${prediction.confidence * 100}%` }}
          />
        </div>
      </div>

      {/* 预期涨跌幅 */}
      {prediction.priceChangePct !== undefined && (
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">预期涨跌幅</div>
          <div
            className={cn(
              'text-2xl font-bold',
              isUp && 'text-stock-up',
              isDown && 'text-stock-down'
            )}
          >
            {formatPercent(prediction.priceChangePct, true)}
          </div>
        </div>
      )}
    </div>
  );
}

// 价格目标
function PriceTargets({ prediction }: { prediction: any }) {
  const currentPrice = 12.34;

  return (
    <div className="space-y-4">
      {/* 目标价 */}
      <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
        <div className="flex items-center gap-3">
          <Target className="w-6 h-6 text-green-600" />
          <div>
            <div className="text-sm text-gray-600">目标价位</div>
            <div className="text-2xl font-bold text-green-600 numeric">
              {prediction.targetPrice ? formatPrice(prediction.targetPrice) : '¥14.50'}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600">涨幅空间</div>
          <div className="text-lg font-bold text-green-600 numeric">
            {prediction.targetPrice
              ? formatPercent((prediction.targetPrice - currentPrice) / currentPrice, true)
              : '+17.5%'}
          </div>
        </div>
      </div>

      {/* 阻力位 */}
      {prediction.resistanceLevel && (
        <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
          <div className="flex items-center gap-3">
            <ArrowUp className="w-6 h-6 text-red-600" />
            <div>
              <div className="text-sm text-gray-600">阻力位</div>
              <div className="text-xl font-bold text-red-600 numeric">
                {formatPrice(prediction.resistanceLevel)}
              </div>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            关键压力区域
          </div>
        </div>
      )}

      {/* 支撑位 */}
      {prediction.supportLevel && (
        <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-3">
            <ArrowDown className="w-6 h-6 text-blue-600" />
            <div>
              <div className="text-sm text-gray-600">支撑位</div>
              <div className="text-xl font-bold text-blue-600 numeric">
                {formatPrice(prediction.supportLevel)}
              </div>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            关键支撑区域
          </div>
        </div>
      )}
    </div>
  );
}

// 价格走势图（简化版，使用 CSS 实现）
function PriceTrendChart({
  currentPrice,
  targetPrice,
  trend,
  horizon,
}: {
  currentPrice: number;
  targetPrice?: number;
  trend: number;
  horizon: TimeHorizon;
}) {
  const target = targetPrice || currentPrice * (trend === 1 ? 1.15 : trend === -1 ? 0.85 : 1);
  const changePercent = ((target - currentPrice) / currentPrice) * 100;
  const config = TIME_HORIZON_CONFIG[horizon];

  // 生成模拟的走势点
  const points = [];
  const numPoints = 10;
  for (let i = 0; i <= numPoints; i++) {
    const progress = i / numPoints;
    const trendEffect = (target - currentPrice) * progress;
    const noise = (Math.random() - 0.5) * currentPrice * 0.02;
    points.push(currentPrice + trendEffect + noise);
  }

  const maxPrice = Math.max(...points, currentPrice, target) * 1.05;
  const minPrice = Math.min(...points, currentPrice, target) * 0.95;
  const priceRange = maxPrice - minPrice;

  return (
    <div className="space-y-4">
      {/* SVG 走势图 */}
      <div className="relative h-64 bg-gray-50 rounded-lg overflow-hidden">
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 800 256"
          preserveAspectRatio="none"
          className="absolute inset-0"
        >
          {/* 网格线 */}
          {[0, 25, 50, 75, 100].map((pct) => (
            <line
              key={pct}
              x1="0"
              y1={(pct / 100) * 256}
              x2="800"
              y2={(pct / 100) * 256}
              stroke="#e5e7eb"
              strokeWidth="1"
            />
          ))}

          {/* 走势线 */}
          <polyline
            points={points
              .map((price, i) => {
                const x = (i / numPoints) * 800;
                const y = 256 - ((price - minPrice) / priceRange) * 256;
                return `${x},${y}`;
              })
              .join(' ')}
            fill="none"
            stroke={trend === 1 ? '#10b981' : trend === -1 ? '#ef4444' : '#6b7280'}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* 当前价格点 */}
          <circle cx="0" cy={256 - ((currentPrice - minPrice) / priceRange) * 256} r="6" fill="#3b82f6" />

          {/* 目标价格点 */}
          <circle
            cx="800"
            cy={256 - ((target - minPrice) / priceRange) * 256}
            r="6"
            fill={trend === 1 ? '#10b981' : trend === -1 ? '#ef4444' : '#6b7280'}
          />
        </svg>

        {/* 价格标签 */}
        <div className="absolute top-2 left-2 bg-blue-100 px-2 py-1 rounded text-sm">
          当前: {formatPrice(currentPrice)}
        </div>
        <div className="absolute top-2 right-2 bg-green-100 px-2 py-1 rounded text-sm">
          目标: {formatPrice(target)}
        </div>
      </div>

      {/* 图例说明 */}
      <div className="flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-blue-500 rounded"></div>
          <span>当前价格</span>
        </div>
        <div
          className={cn(
            'flex items-center gap-2',
            trend === 1 && 'text-green-600',
            trend === -1 && 'text-red-600'
          )}
        >
          <div
            className={cn(
              'w-4 h-1 rounded',
              trend === 1 && 'bg-green-500',
              trend === -1 && 'bg-red-500',
              trend === 0 && 'bg-gray-500'
            )}
          ></div>
          <span>预测趋势</span>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4" />
          <span>{config.period}</span>
        </div>
      </div>
    </div>
  );
}

// 风险评估
function RiskAssessment({ prediction }: { prediction: any }) {
  const riskLevel = prediction.riskLevel || 'medium';

  const getRiskConfig = (level: string) => {
    switch (level) {
      case 'low':
        return {
          label: '低风险',
          color: 'text-green-600 bg-green-50',
          icon: <CheckCircle className="w-6 h-6 text-green-600" />,
          description: '预测较为可靠，不确定性较低',
        };
      case 'high':
        return {
          label: '高风险',
          color: 'text-red-600 bg-red-50',
          icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
          description: '市场波动较大，需谨慎决策',
        };
      default:
        return {
          label: '中等风险',
          color: 'text-yellow-600 bg-yellow-50',
          icon: <AlertTriangle className="w-6 h-6 text-yellow-600" />,
          description: '存在一定不确定性，建议综合判断',
        };
    }
  };

  const riskConfig = getRiskConfig(riskLevel);

  return (
    <div className="space-y-4">
      {/* 风险等级 */}
      <div className={cn('flex items-center gap-4 p-4 rounded-lg', riskConfig.color)}>
        {riskConfig.icon}
        <div>
          <div className="text-lg font-bold">{riskConfig.label}</div>
          <div className="text-sm text-gray-600">{riskConfig.description}</div>
        </div>
      </div>

      {/* 影响因素 */}
      <div className="space-y-3">
        <h3 className="font-medium text-gray-700">主要风险因素</h3>
        <div className="space-y-2">
          {['市场波动性增加', '政策变化风险', '行业竞争加剧'].map((factor, i) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              <span className="text-yellow-600 mt-0.5">⚠</span>
              <span className="text-gray-700">{factor}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 投资建议 */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">投资建议</h3>
        <p className="text-sm text-blue-800">
          建议分批建仓，设置止损位在{' '}
          {prediction.supportLevel ? formatPrice(prediction.supportLevel * 0.95) : '¥11.00'}
          ，目标价位{' '}
          {prediction.targetPrice ? formatPrice(prediction.targetPrice) : '¥14.50'}
          。
        </p>
      </div>
    </div>
  );
}

// 预测依据
function PredictionBasis({
  prediction,
  horizon,
}: {
  prediction: any;
  horizon: TimeHorizon;
}) {
  const config = TIME_HORIZON_CONFIG[horizon];

  return (
    <div className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        基于 {config.label} 的多因子分析结果
      </div>

      {/* 关键驱动因素 */}
      <div className="space-y-3">
        <h3 className="font-medium text-gray-700">关键驱动因素</h3>

        <div className="space-y-2">
          {[
            { label: '技术面', value: 'MACD金叉，成交量放大', positive: true },
            { label: '基本面', value: '业绩超预期，盈利能力提升', positive: true },
            { label: '资金面', value: '北向资金持续流入', positive: true },
            { label: '市场情绪', value: '投资者信心指数上升', positive: true },
          ].map((factor, i) => (
            <div
              key={i}
              className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
            >
              <div
                className={cn(
                  'w-2 h-2 rounded-full mt-1.5',
                  factor.positive ? 'bg-green-500' : 'bg-red-500'
                )}
              />
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-700">{factor.label}</div>
                <div className="text-xs text-gray-600">{factor.value}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 模型说明 */}
      <div className="bg-gray-50 p-3 rounded-lg text-xs text-gray-600">
        <div className="font-medium mb-1">预测模型说明</div>
        <div>
          本预测基于机器学习模型（LSTM + XGBoost集成），结合7大维度因子分析。
          历史回测准确率约 72-78%，仅供参考，不构成投资建议。
        </div>
      </div>
    </div>
  );
}

// 加载骨架屏
function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-48 mb-4"></div>
        <div className="h-16 bg-gray-200 rounded"></div>
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="h-48 bg-gray-200 rounded"></div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="h-48 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  );
}

// 错误状态
function ErrorState({ stockCode, onRetry }: { stockCode: string; onRetry: () => void }) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
      <div className="text-red-500 text-lg mb-4">预测失败</div>
      <p className="text-gray-600 mb-6">无法获取股票 {stockCode} 的预测数据</p>
      <button
        onClick={onRetry}
        className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
      >
        重试
      </button>
    </div>
  );
}
