import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, TrendingUp, Clock } from 'lucide-react';
import { useStockStore } from '@/stores/useStockStore';
import { useQuery } from '@tanstack/react-query';
import { getPopularStocks } from '@/services/stockService';
import { formatPrice, formatPercent } from '@/utils/formatters';
import { cn } from '@/utils/helpers';

export default function HomePage() {
  const navigate = useNavigate();
  const [searchValue, setSearchValue] = useState('');
  const { addSearchHistory, searchHistory } = useStockStore();

  // 获取热门股票
  const { data: popularStocks, isLoading } = useQuery({
    queryKey: ['popularStocks'],
    queryFn: () => getPopularStocks(8),
    staleTime: 10 * 60 * 1000, // 10分钟
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchValue.trim()) {
      addSearchHistory(searchValue.trim());
      navigate(`/analysis/${searchValue.trim()}`);
    }
  };

  return (
    <div className="space-y-8">
      {/* 搜索区域 */}
      <div className="bg-white rounded-lg shadow-sm p-8">
        <h2 className="text-2xl font-bold text-center mb-6">
          智能股价预测分析
        </h2>
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder="输入股票代码或名称，如：000001 或 平安银行"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              搜索
            </button>
          </div>
        </form>

        {/* 搜索历史 */}
        {searchHistory.length > 0 && (
          <div className="max-w-2xl mx-auto mt-4">
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
              <Clock className="w-4 h-4" />
              <span>最近搜索:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((code) => (
                <button
                  key={code}
                  onClick={() => navigate(`/analysis/${code}`)}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                >
                  {code}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 快速分析卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickAnalysisCard
          title="短期预测"
          description="1-3个月趋势"
          timeHorizon="short"
        />
        <QuickAnalysisCard
          title="中期预测"
          description="3-12个月趋势"
          timeHorizon="medium"
        />
        <QuickAnalysisCard
          title="长期预测"
          description="1年以上趋势"
          timeHorizon="long"
        />
      </div>

      {/* 热门股票 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            热门股票
          </h3>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-24 bg-gray-200 rounded-lg"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {popularStocks?.map((stock) => (
              <StockCard key={stock.code} stock={stock} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// 快速分析卡片组件
function QuickAnalysisCard({
  title,
  description,
  timeHorizon,
}: {
  title: string;
  description: string;
  timeHorizon: string;
}) {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate(`/prediction?horizon=${timeHorizon}`)}
      className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow text-left"
    >
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
      <div className="mt-4 text-primary font-medium">立即分析 →</div>
    </button>
  );
}

// 股票卡片组件
function StockCard({ stock }: { stock: any }) {
  const navigate = useNavigate();
  const isUp = stock.changePercent > 0;
  const isDown = stock.changePercent < 0;

  return (
    <button
      onClick={() => navigate(`/analysis/${stock.code}`)}
      className="bg-gray-50 p-4 rounded-lg hover:bg-gray-100 transition-colors text-left"
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <div className="font-semibold">{stock.code}</div>
          <div className="text-sm text-gray-600">{stock.name}</div>
        </div>
      </div>
      <div className="flex justify-between items-end">
        <div className="text-lg font-bold numeric">
          {formatPrice(stock.currentPrice)}
        </div>
        <div
          className={cn(
            'text-sm font-medium numeric',
            isUp && 'text-stock-up',
            isDown && 'text-stock-down',
            !isUp && !isDown && 'text-stock-flat'
          )}
        >
          {formatPercent(stock.changePercent, true)}
        </div>
      </div>
    </button>
  );
}
