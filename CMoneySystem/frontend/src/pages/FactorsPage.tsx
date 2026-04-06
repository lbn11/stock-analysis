import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Save,
  RotateCcw,
  Settings,
  Info,
  Check,
  AlertTriangle,
  TrendingUp,
  Shield,
  Zap,
} from 'lucide-react';
import { getFactorWeights, updateFactorWeights } from '@/services/analysisService';
import { cn } from '@/utils/helpers';

type FactorWeight = {
  fundamental: number;
  macro_economic: number;
  industry: number;
  policy: number;
  international: number;
  funding: number;
  market_structure: number;
};

const FACTOR_CONFIG = {
  fundamental: {
    name: '基本面因素',
    description: '公司业绩、盈利能力、竞争优势',
    icon: '🏢',
    color: 'bg-blue-500',
  },
  macro_economic: {
    name: '宏观环境',
    description: '经济政策、利率变化、通胀水平',
    icon: '🌍',
    color: 'bg-purple-500',
  },
  industry: {
    name: '行业状况',
    description: '行业周期、政策支持、竞争格局',
    icon: '🏭',
    color: 'bg-green-500',
  },
  policy: {
    name: '政策因素',
    description: '产业政策、区域规划、监管政策',
    icon: '📋',
    color: 'bg-orange-500',
  },
  international: {
    name: '国际关系',
    description: '地缘政治、贸易关系、大宗商品',
    icon: '🌐',
    color: 'bg-red-500',
  },
  funding: {
    name: '资金面',
    description: '长期资金、外资流动、市场情绪',
    icon: '💰',
    color: 'bg-yellow-500',
  },
  market_structure: {
    name: '市场结构',
    description: '机构化程度、投资风格变化',
    icon: '📊',
    color: 'bg-pink-500',
  },
};

const PRESET_TEMPLATES = {
  conservative: {
    name: '保守型',
    description: '侧重基本面和行业分析，忽略短期波动',
    icon: <Shield className="w-5 h-5" />,
    weights: {
      fundamental: 40,
      macro_economic: 20,
      industry: 20,
      policy: 10,
      international: 5,
      funding: 3,
      market_structure: 2,
    },
  },
  balanced: {
    name: '平衡型',
    description: '综合考虑各类因素，适合大多数投资者',
    icon: <Settings className="w-5 h-5" />,
    weights: {
      fundamental: 30,
      macro_economic: 20,
      industry: 15,
      policy: 15,
      international: 10,
      funding: 5,
      market_structure: 5,
    },
  },
  aggressive: {
    name: '激进型',
    description: '重视资金面和市场情绪，捕捉短期机会',
    icon: <Zap className="w-5 h-5" />,
    weights: {
      fundamental: 20,
      macro_economic: 15,
      industry: 10,
      policy: 10,
      international: 10,
      funding: 20,
      market_structure: 15,
    },
  },
};

export default function FactorsPage() {
  const queryClient = useQueryClient();
  const [localWeights, setLocalWeights] = useState<FactorWeight>({
    fundamental: 30,
    macro_economic: 20,
    industry: 15,
    policy: 15,
    international: 10,
    funding: 5,
    market_structure: 5,
  });
  const [hasChanges, setHasChanges] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // 获取当前因子权重
  const { data: currentWeights, isLoading } = useQuery({
    queryKey: ['factorWeights'],
    queryFn: getFactorWeights,
    onSuccess: (data) => {
      setLocalWeights(data);
      setHasChanges(false);
    },
  });

  // 更新因子权重
  const updateMutation = useMutation({
    mutationFn: updateFactorWeights,
    onSuccess: () => {
      queryClient.invalidateQueries(['factorWeights']);
      setHasChanges(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    },
  });

  const handleWeightChange = (factor: keyof FactorWeight, value: number) => {
    setLocalWeights((prev) => ({
      ...prev,
      [factor]: value,
    }));
    setHasChanges(true);
    setSaveSuccess(false);
  };

  const handleApplyTemplate = (template: keyof typeof PRESET_TEMPLATES) => {
    setLocalWeights(PRESET_TEMPLATES[template].weights);
    setHasChanges(true);
    setSaveSuccess(false);
  };

  const handleReset = () => {
    if (currentWeights) {
      setLocalWeights(currentWeights);
      setHasChanges(false);
      setSaveSuccess(false);
    }
  };

  const handleSave = () => {
    updateMutation.mutate(localWeights);
  };

  const totalWeight = Object.values(localWeights).reduce((sum, val) => sum + val, 0);
  const isValid = Math.abs(totalWeight - 100) < 0.1;

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold mb-2">因子权重配置</h1>
            <p className="text-gray-600">
              自定义7大分析因子的权重，创建适合您的投资策略
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={cn(
                'px-4 py-2 rounded-lg font-medium',
                isValid ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              )}
            >
              总权重: {totalWeight.toFixed(0)}%
            </div>
          </div>
        </div>

        {/* 预设模板 */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">快速应用预设模板</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(Object.keys(PRESET_TEMPLATES) as Array<keyof typeof PRESET_TEMPLATES>).map(
              (templateKey) => {
                const template = PRESET_TEMPLATES[templateKey];
                return (
                  <button
                    key={templateKey}
                    onClick={() => handleApplyTemplate(templateKey)}
                    className="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-primary hover:bg-blue-50 transition-colors text-left"
                  >
                    <div className="text-primary mt-0.5">{template.icon}</div>
                    <div>
                      <div className="font-semibold">{template.name}</div>
                      <div className="text-sm text-gray-600">{template.description}</div>
                    </div>
                  </button>
                );
              }
            )}
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            disabled={!isValid || !hasChanges || updateMutation.isLoading}
            className={cn(
              'flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors',
              isValid && hasChanges
                ? 'bg-primary text-white hover:bg-primary/90'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            )}
          >
            <Save className="w-4 h-4" />
            {updateMutation.isLoading ? '保存中...' : '保存配置'}
          </button>

          <button
            onClick={handleReset}
            disabled={!hasChanges}
            className={cn(
              'flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors',
              hasChanges
                ? 'border border-gray-300 hover:bg-gray-50'
                : 'border border-gray-200 text-gray-400 cursor-not-allowed'
            )}
          >
            <RotateCcw className="w-4 h-4" />
            重置更改
          </button>

          {saveSuccess && (
            <div className="flex items-center gap-2 text-green-600">
              <Check className="w-5 h-5" />
              <span className="font-medium">保存成功！</span>
            </div>
          )}
        </div>

        {!isValid && (
          <div className="mt-4 flex items-center gap-2 text-red-600 text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>
              权重总和必须为 100%，当前为 {totalWeight.toFixed(0)}%
            </span>
          </div>
        )}
      </div>

      {/* 因子权重调节 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-6">权重分配</h2>

        <div className="space-y-6">
          {(Object.keys(FACTOR_CONFIG) as Array<keyof typeof FACTOR_CONFIG>).map(
            (factorKey) => {
              const config = FACTOR_CONFIG[factorKey];
              const weight = localWeights[factorKey];

              return (
                <div key={factorKey} className="border-b border-gray-200 pb-6 last:border-0">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          'w-10 h-10 rounded-lg flex items-center justify-center text-lg',
                          config.color
                        )}
                      >
                        {config.icon}
                      </div>
                      <div>
                        <div className="font-semibold text-lg">{config.name}</div>
                        <div className="text-sm text-gray-600">{config.description}</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="1"
                        value={weight}
                        onChange={(e) => {
                          const value = Math.max(0, Math.min(100, Number(e.target.value)));
                          handleWeightChange(factorKey, value);
                        }}
                        className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center font-bold numeric"
                      />
                      <span className="text-gray-600">%</span>
                    </div>
                  </div>

                  {/* 滑块 */}
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        step="1"
                        value={weight}
                        onChange={(e) =>
                          handleWeightChange(factorKey, Number(e.target.value))
                        }
                        className={cn(
                          'w-full h-2 rounded-lg appearance-none cursor-pointer',
                          config.color.replace('bg-', 'accent-')
                        )}
                        style={{
                          accentColor: weight > 0 ? undefined : '#d1d5db',
                        }}
                      />
                    </div>

                    {/* 权重指示器 */}
                    <div className="flex gap-1">
                      {Array.from({ length: 10 }).map((_, i) => (
                        <div
                          key={i}
                          className={cn(
                            'w-2 h-6 rounded',
                            i < weight / 10 ? config.color : 'bg-gray-200'
                          )}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              );
            }
          )}
        </div>
      </div>

      {/* 权重对比图表 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-6">权重分布可视化</h2>

        <div className="flex items-end gap-2 h-64">
          {(Object.keys(FACTOR_CONFIG) as Array<keyof typeof FACTOR_CONFIG>).map(
            (factorKey) => {
              const config = FACTOR_CONFIG[factorKey];
              const weight = localWeights[factorKey];

              return (
                <div key={factorKey} className="flex-1 flex flex-col items-center gap-2">
                  <div className="text-sm font-bold numeric">{weight}%</div>
                  <div
                    className={cn(
                      'w-full rounded-t-lg transition-all duration-300',
                      config.color
                    )}
                    style={{ height: `${weight * 2.5}px` }}
                  />
                  <div className="text-xs text-gray-600 text-center leading-tight">
                    {config.icon}
                    <br />
                    {config.name.slice(0, 4)}
                  </div>
                </div>
              );
            }
          )}
        </div>
      </div>

      {/* 因子详细说明 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-6">因子详细说明</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(Object.keys(FACTOR_CONFIG) as Array<keyof typeof FACTOR_CONFIG>).map(
            (factorKey) => {
              const config = FACTOR_CONFIG[factorKey];
              const weight = localWeights[factorKey];

              return (
                <div
                  key={factorKey}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div
                      className={cn(
                        'w-12 h-12 rounded-lg flex items-center justify-center text-2xl',
                        config.color
                      )}
                    >
                      {config.icon}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div className="font-semibold">{config.name}</div>
                        <div className="text-sm font-bold text-primary numeric">
                          {weight}%
                        </div>
                      </div>
                      <div className="text-sm text-gray-600">{config.description}</div>
                    </div>
                  </div>

                  <div className="text-xs text-gray-500">
                    <div className="flex items-center gap-1 mb-1">
                      <Info className="w-3 h-3" />
                      <span className="font-medium">适用场景：</span>
                    </div>
                    <div>
                      {factorKey === 'fundamental' &&
                        '长期价值投资，关注公司内在价值'}
                      {factorKey === 'macro_economic' &&
                        '宏观经济环境分析，把握大趋势'}
                      {factorKey === 'industry' && '行业投资，寻找优质赛道'}
                      {factorKey === 'policy' && '政策导向投资，紧跟国家战略'}
                      {factorKey === 'international' &&
                        '全球化配置，关注国际市场'}
                      {factorKey === 'funding' && '短期交易，跟随资金流向'}
                      {factorKey === 'market_structure' &&
                        '市场风格切换，机构动向跟踪'}
                    </div>
                  </div>
                </div>
              );
            }
          )}
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
        <div className="h-4 bg-gray-200 rounded w-96 mb-6"></div>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-32 mb-6"></div>
        <div className="space-y-6">
          {[1, 2, 3, 4, 5, 6, 7].map((i) => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    </div>
  );
}
