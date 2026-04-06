import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, TrendingDown, Minus, RefreshCw, Star, Download } from 'lucide-react';
import { analyzeStock } from '@/services/analysisService';
import { formatPrice, formatPercent } from '@/utils/formatters';
import { cn } from '@/utils/helpers';

export default function AnalysisPage() {
  const { stockCode } = useParams<{ stockCode: string }>();

  // 获取分析数据
  const { data: analysis, isLoading, error, refetch } = useQuery({
    queryKey: ['analysis', stockCode],
    queryFn: () => analyzeStock({
      stock_code: stockCode || '000001',
      analysis_type: 'comprehensive',
      time_horizon: 'medium',
    }),
    enabled: !!stockCode,
    retry: 1,
  });

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return <ErrorState stockCode={stockCode || ''} onRetry={() => refetch()} />;
  }

  if (!analysis) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* 顶部：股票信息 + 综合结果 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：股票信息 */}
          <StockInfoHeader
            stockCode={analysis.stockCode}
            currentPrice={12.34}
            changePercent={2.3}
          />

          {/* 中央：综合评分 */}
          <ComprehensiveScore score={analysis.comprehensiveScore} />

          {/* 右侧：投资建议 */}
          <InvestmentRecommendation
            prediction={analysis.prediction}
            recommendation={analysis.recommendation}
            onRetry={() => refetch()}
          />
        </div>
      </div>

      {/* 中间：7大因子雷达图 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">7大因子分析</h2>
        <FactorRadarChart factors={analysis.factors} />
      </div>

      {/* 底部：判断依据 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">分析依据</h2>
        <AnalysisSummary summary={analysis.summary} factors={analysis.factors} />
      </div>
    </div>
  );
}

// 股票信息头部
function StockInfoHeader({
  stockCode,
  currentPrice,
  changePercent,
}: {
  stockCode: string;
  currentPrice: number;
  changePercent: number;
}) {
  const isUp = changePercent > 0;
  const isDown = changePercent < 0;

  return (
    <div className="flex flex-col justify-center">
      <div className="flex items-baseline gap-3 mb-2">
        <h1 className="text-3xl font-bold">{stockCode}</h1>
        <span className="text-lg text-gray-600">平安银行</span>
      </div>
      <div className="flex items-baseline gap-3">
        <span className="text-2xl font-bold numeric">{formatPrice(currentPrice)}</span>
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
          {formatPercent(changePercent, true)}
        </span>
      </div>
    </div>
  );
}

// 综合评分组件
function ComprehensiveScore({ score }: { score: number }) {
  const getGrade = (score: number) => {
    if (score >= 80) return { text: '优秀', color: 'text-green-600' };
    if (score >= 60) return { text: '良好', color: 'text-blue-600' };
    if (score >= 40) return { text: '一般', color: 'text-yellow-600' };
    return { text: '较差', color: 'text-red-600' };
  };

  const grade = getGrade(score);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative">
        <svg width="200" height="200" className="transform -rotate-90">
          {/* 背景圆 */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke="#e5e7eb"
            strokeWidth="12"
            fill="none"
          />
          {/* 进度圆 */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke={score >= 80 ? '#10b981' : score >= 60 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#ef4444'}
            strokeWidth="12"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center transform rotate-90">
          <span className="text-4xl font-bold">{score}</span>
          <span className="text-sm text-gray-500 mt-1">综合评分</span>
        </div>
      </div>
      <div className={cn('text-lg font-semibold mt-3', grade.color)}>{grade.text}</div>
    </div>
  );
}

// 投资建议组件
function InvestmentRecommendation({
  prediction,
  recommendation,
  onRetry,
}: {
  prediction: any;
  recommendation: string;
  onRetry: () => void;
}) {
  const getRecommendationColor = (rec: string) => {
    if (rec.includes('买入')) return 'text-stock-up bg-green-50';
    if (rec.includes('卖出')) return 'text-stock-down bg-red-50';
    return 'text-gray-700 bg-gray-50';
  };

  return (
    <div className="flex flex-col justify-center items-center text-center">
      <div className="mb-4">
        <div className={cn('text-2xl font-bold px-6 py-3 rounded-lg', getRecommendationColor(recommendation))}>
          {recommendation}
        </div>
      </div>

      <div className="text-lg mb-4">
        <span className="text-gray-600">置信度：</span>
        <span className="font-bold numeric">{(prediction.confidence * 100).toFixed(0)}%</span>
      </div>

      <div className="flex gap-2">
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          重新分析
        </button>
        <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
          <Star className="w-4 h-4" />
          加入自选
        </button>
        <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
          <Download className="w-4 h-4" />
          导出
        </button>
      </div>
    </div>
  );
}

// 因子雷达图组件（简化版，使用 CSS 实现）
function FactorRadarChart({ factors }: { factors: any[] }) {
  const factorNames = {
    fundamental: '基本面',
    macro_economic: '宏观',
    industry: '行业',
    policy: '政策',
    international: '国际',
    funding: '资金',
    market_structure: '市场',
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
      {factors.map((factor) => {
        const score = factor.score || 0;
        const getColor = (s: number) => {
          if (s >= 80) return 'bg-green-500';
          if (s >= 60) return 'bg-blue-500';
          if (s >= 40) return 'bg-yellow-500';
          return 'bg-red-500';
        };

        return (
          <div key={factor.name} className="flex flex-col items-center">
            <div className="w-full bg-gray-100 rounded-lg p-4">
              <div className="text-sm text-gray-600 mb-2 text-center">
                {factorNames[factor.name as keyof typeof factorNames] || factor.name}
              </div>
              <div className="text-3xl font-bold text-center mb-2 numeric">{score}</div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={cn('h-2 rounded-full transition-all duration-500', getColor(score))}
                  style={{ width: `${score}%` }}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// 分析依据组件
function AnalysisSummary({ summary, factors }: { summary: string; factors: any[] }) {
  return (
    <div className="space-y-3">
      <p className="text-gray-700 leading-relaxed">{summary}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        {factors.slice(0, 6).map((factor) => (
          <div key={factor.name} className="border-l-4 border-primary pl-4 py-2">
            <div className="font-medium text-sm mb-1">{factor.name}</div>
            <div className="text-sm text-gray-600">
              评分: <span className="font-bold numeric">{factor.score}</span>
              <span className="mx-2">•</span>
              权重: <span className="numeric">{(factor.weight * 100).toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// 加载骨架屏
function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
        <div className="grid grid-cols-3 gap-6">
          <div className="h-24 bg-gray-200 rounded"></div>
          <div className="h-24 bg-gray-200 rounded"></div>
          <div className="h-24 bg-gray-200 rounded"></div>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
        <div className="h-96 bg-gray-200 rounded"></div>
      </div>
    </div>
  );
}

// 错误状态
function ErrorState({ stockCode, onRetry }: { stockCode: string; onRetry: () => void }) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
      <div className="text-red-500 text-lg mb-4">分析失败</div>
      <p className="text-gray-600 mb-6">无法获取股票 {stockCode} 的分析数据</p>
      <button
        onClick={onRetry}
        className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
      >
        重试
      </button>
    </div>
  );
}
