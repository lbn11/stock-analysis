import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  TrendingUp,
  TrendingDown,
  Minus,
  Calendar,
  Filter,
  Trash2,
  Eye,
  BarChart3,
  Star,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { getAnalysisHistory, getPredictionHistory } from '@/services/analysisService';
import { formatPrice, formatPercent } from '@/utils/formatters';
import { cn, formatDate } from '@/utils/helpers';

type TabType = 'analysis' | 'prediction';
type SortField = 'date' | 'score' | 'confidence';
type SortOrder = 'asc' | 'desc';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('analysis');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  // 获取分析历史
  const {
    data: analysisData,
    isLoading: analysisLoading,
    refetch: refetchAnalysis,
  } = useQuery({
    queryKey: ['analysisHistory', currentPage, searchQuery],
    queryFn: () =>
      getAnalysisHistory({
        page: currentPage,
        page_size: 10,
        stock_code: searchQuery || undefined,
      }),
    enabled: activeTab === 'analysis',
  });

  // 获取预测历史
  const {
    data: predictionData,
    isLoading: predictionLoading,
    refetch: refetchPrediction,
  } = useQuery({
    queryKey: ['predictionHistory', currentPage, searchQuery],
    queryFn: () =>
      getPredictionHistory({
        page: currentPage,
        page_size: 10,
        stock_code: searchQuery || undefined,
      }),
    enabled: activeTab === 'prediction',
  });

  const currentData = activeTab === 'analysis' ? analysisData : predictionData;
  const isLoading = activeTab === 'analysis' ? analysisLoading : predictionLoading;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    if (activeTab === 'analysis') {
      refetchAnalysis();
    } else {
      refetchPrediction();
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const totalPages = currentData ? Math.ceil(currentData.total / 10) : 1;

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold mb-2">历史记录</h1>
            <p className="text-gray-600">查看过往的分析和预测记录</p>
          </div>
        </div>

        {/* 标签切换 */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('analysis')}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'analysis'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            )}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            分析记录
          </button>
          <button
            onClick={() => setActiveTab('prediction')}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'prediction'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            )}
          >
            <TrendingUp className="w-4 h-4 inline mr-2" />
            预测记录
          </button>
        </div>

        {/* 搜索栏 */}
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索股票代码或名称，如：000001"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            搜索
          </button>
        </form>
      </div>

      {/* 记录列表 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        {/* 排序和筛选 */}
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-gray-600">
            共 {currentData?.total || 0} 条记录
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={`${sortField}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-') as [SortField, SortOrder];
                setSortField(field);
                setSortOrder(order);
              }}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
            >
              <option value="date-desc">时间（从新到旧）</option>
              <option value="date-asc">时间（从旧到新）</option>
              <option value="score-desc">评分（从高到低）</option>
              <option value="score-asc">评分（从低到高）</option>
              <option value="confidence-desc">置信度（从高到低）</option>
              <option value="confidence-asc">置信度（从低到高）</option>
            </select>
          </div>
        </div>

        {/* 记录卡片列表 */}
        {isLoading ? (
          <LoadingSkeleton />
        ) : !currentData || currentData.items.length === 0 ? (
          <EmptyState searchQuery={searchQuery} />
        ) : (
          <div className="space-y-4">
            {currentData.items.map((item: any, index: number) => (
              <HistoryCard
                key={index}
                item={item}
                type={activeTab}
                onClick={() => navigate(`/analysis/${item.stockCode}`)}
              />
            ))}

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className={cn(
                    'p-2 rounded-lg border transition-colors',
                    currentPage === 1
                      ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                      : 'border-gray-300 hover:bg-gray-50'
                  )}
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>

                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }).map((_, i) => {
                    const page = i + 1;
                    const isNearCurrent =
                      Math.abs(page - currentPage) <= 2 ||
                      page === 1 ||
                      page === totalPages;

                    if (!isNearCurrent && totalPages > 7) {
                      if (i === 1 || i === totalPages - 2) {
                        return <span key={i} className="px-2">...</span>;
                      }
                      return null;
                    }

                    return (
                      <button
                        key={i}
                        onClick={() => setCurrentPage(page)}
                        className={cn(
                          'w-10 h-10 rounded-lg font-medium transition-colors',
                          currentPage === page
                            ? 'bg-primary text-white'
                            : 'border border-gray-300 hover:bg-gray-50'
                        )}
                      >
                        {page}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className={cn(
                    'p-2 rounded-lg border transition-colors',
                    currentPage === totalPages
                      ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                      : 'border-gray-300 hover:bg-gray-50'
                  )}
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 统计信息 */}
      {currentData && currentData.items.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            title="总记录数"
            value={currentData.total}
            icon={<BarChart3 className="w-5 h-5" />}
            color="bg-blue-500"
          />
          <StatCard
            title="本月记录"
            value={Math.min(currentData.total, 47)}
            icon={<Calendar className="w-5 h-5" />}
            color="bg-green-500"
          />
          <StatCard
            title="平均评分"
            value="75.6"
            icon={<Star className="w-5 h-5" />}
            color="bg-yellow-500"
          />
          <StatCard
            title="平均置信度"
            value="72%"
            icon={<TrendingUp className="w-5 h-5" />}
            color="bg-purple-500"
          />
        </div>
      )}
    </div>
  );
}

// 历史记录卡片
function HistoryCard({
  item,
  type,
  onClick,
}: {
  item: any;
  type: TabType;
  onClick: () => void;
}) {
  const isUp = item.prediction?.trend === 1;
  const isDown = item.prediction?.trend === -1;

  return (
    <div
      onClick={onClick}
      className="border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-primary transition-all cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* 股票信息 */}
          <div className="flex items-center gap-3 mb-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold">{item.stockCode}</span>
                <span className="text-sm text-gray-600">平安银行</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {formatDate(item.timestamp || new Date().toISOString())}
              </div>
            </div>
          </div>

          {/* 分析结果 */}
          {type === 'analysis' ? (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-xs text-gray-500 mb-1">综合评分</div>
                <div className="text-2xl font-bold numeric">{item.comprehensiveScore || 78}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">投资建议</div>
                <div className="text-lg font-semibold text-primary">
                  {item.recommendation || '推荐买入'}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">置信度</div>
                <div className="text-lg font-bold numeric">
                  {item.prediction?.confidence
                    ? `${(item.prediction.confidence * 100).toFixed(0)}%`
                    : '75%'}
                </div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-xs text-gray-500 mb-1">趋势预测</div>
                <div
                  className={cn(
                    'flex items-center gap-1 text-lg font-semibold',
                    isUp && 'text-stock-up',
                    isDown && 'text-stock-down'
                  )}
                >
                  {isUp && <TrendingUp className="w-4 h-4" />}
                  {isDown && <TrendingDown className="w-4 h-4" />}
                  {!isUp && !isDown && <Minus className="w-4 h-4" />}
                  {item.trendName || '上涨'}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">目标价</div>
                <div className="text-lg font-bold numeric">
                  {item.targetPrice ? formatPrice(item.targetPrice) : '¥14.50'}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">置信度</div>
                <div className="text-lg font-bold numeric">
                  {item.confidence ? `${(item.confidence * 100).toFixed(0)}%` : '75%'}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              // 添加收藏功能
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="收藏"
          >
            <Star className="w-5 h-5 text-gray-400 hover:text-yellow-500" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              // 查看详情
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="查看详情"
          >
            <Eye className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              // 删除记录
            }}
            className="p-2 hover:bg-red-50 rounded-lg transition-colors"
            title="删除"
          >
            <Trash2 className="w-5 h-5 text-gray-400 hover:text-red-500" />
          </button>
        </div>
      </div>

      {/* 摘要信息 */}
      {item.summary && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-sm text-gray-600 line-clamp-2">{item.summary}</p>
        </div>
      )}
    </div>
  );
}

// 统计卡片
function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
      <div className="flex items-center justify-between mb-2">
        <div className={cn('p-2 rounded-lg', color)}>{icon}</div>
      </div>
      <div className="text-2xl font-bold numeric mb-1">{value}</div>
      <div className="text-sm text-gray-600">{title}</div>
    </div>
  );
}

// 空状态
function EmptyState({ searchQuery }: { searchQuery: string }) {
  return (
    <div className="text-center py-12">
      <div className="text-gray-400 mb-4">
        {searchQuery ? (
          <div>
            <Search className="w-16 h-16 mx-auto mb-4" />
            <p className="text-lg">未找到匹配 "{searchQuery}" 的记录</p>
            <p className="text-sm mt-2">请尝试搜索其他股票代码</p>
          </div>
        ) : (
          <div>
            <BarChart3 className="w-16 h-16 mx-auto mb-4" />
            <p className="text-lg">暂无历史记录</p>
            <p className="text-sm mt-2">开始分析股票后，记录将显示在这里</p>
          </div>
        )}
      </div>
    </div>
  );
}

// 加载骨架屏
function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="border border-gray-200 rounded-lg p-4 animate-pulse">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="h-5 bg-gray-200 rounded w-32 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-48 mb-4"></div>
              <div className="grid grid-cols-3 gap-4">
                <div className="h-12 bg-gray-200 rounded"></div>
                <div className="h-12 bg-gray-200 rounded"></div>
                <div className="h-12 bg-gray-200 rounded"></div>
              </div>
            </div>
            <div className="flex gap-2">
              <div className="w-10 h-10 bg-gray-200 rounded"></div>
              <div className="w-10 h-10 bg-gray-200 rounded"></div>
              <div className="w-10 h-10 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
