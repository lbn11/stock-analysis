# CMoney 股价预测系统 - 前端架构设计

## 技术栈选择

### 核心技术
- **React 18.2+** - UI 框架
- **TypeScript 5.0+** - 类型安全
- **Vite 4.0+** - 构建工具（更快的开发体验）
- **Tailwind CSS 3.0+** - 样式框架
- **React Router 6** - 路由管理

### 状态管理
- **Zustand** - 轻量级状态管理（比 Redux 更简单）
- **React Query (TanStack Query)** - 服务端状态管理和数据获取

### 数据可视化
- **Recharts** - React 图表库
- **Apache ECharts** - 专业金融图表
- **D3.js** - 自定义可视化（按需）

### UI 组件库
- **shadcn/ui** - 高质量 React 组件（基于 Radix UI + Tailwind）
- **Lucide React** - 图标库
- **Framer Motion** - 动画库

### 工具库
- **Axios** - HTTP 请求
- **date-fns** - 日期处理
- **Zod** - 数据验证
- **React Hook Form** - 表单管理

## 项目结构

```
frontend/
├── public/                    # 静态资源
│   ├── favicon.ico
│   └── logo.png
├── src/
│   ├── assets/               # 资源文件
│   │   ├── images/
│   │   └── styles/
│   ├── components/           # 可复用组件
│   │   ├── ui/              # 基础 UI 组件（shadcn/ui）
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   └── ...
│   │   ├── charts/          # 图表组件
│   │   │   ├── StockLineChart.tsx
│   │   │   ├── FactorRadarChart.tsx
│   │   │   ├── TrendGaugeChart.tsx
│   │   │   └── PredictionChart.tsx
│   │   ├── stock/           # 股票相关组件
│   │   │   ├── StockSearchBar.tsx
│   │   │   ├── StockCard.tsx
│   │   │   └── StockList.tsx
│   │   ├── analysis/        # 分析相关组件
│   │   │   ├── FactorAnalysisPanel.tsx
│   │   │   ├── PredictionPanel.tsx
│   │   │   └── RecommendationCard.tsx
│   │   └── layout/          # 布局组件
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       ├── Footer.tsx
│   │       └── MainLayout.tsx
│   ├── pages/               # 页面组件
│   │   ├── HomePage.tsx            # 首页
│   │   ├── AnalysisPage.tsx        # 综合分析页
│   │   ├── PredictionPage.tsx      # 预测页面
│   │   ├── FactorsPage.tsx         # 因子配置页
│   │   ├── HistoryPage.tsx         # 历史记录
│   │   └── SettingsPage.tsx        # 设置页面
│   ├── services/            # API 服务
│   │   ├── api.ts                  # API 基础配置
│   │   ├── stockService.ts         # 股票相关 API
│   │   ├── analysisService.ts      # 分析相关 API
│   │   └── predictionService.ts    # 预测相关 API
│   ├── stores/              # 状态管理
│   │   ├── useStockStore.ts        # 股票状态
│   │   ├── useAnalysisStore.ts     # 分析状态
│   │   └── useUserStore.ts         # 用户状态
│   ├── hooks/               # 自定义 Hooks
│   │   ├── useStockData.ts
│   │   ├── useAnalysis.ts
│   │   └── usePrediction.ts
│   ├── types/               # TypeScript 类型定义
│   │   ├── stock.ts
│   │   ├── analysis.ts
│   │   └── prediction.ts
│   ├── utils/               # 工具函数
│   │   ├── formatters.ts           # 格式化函数
│   │   ├── validators.ts           # 验证函数
│   │   └── constants.ts            # 常量定义
│   ├── App.tsx              # 根组件
│   ├── main.tsx             # 入口文件
│   └── index.css            # 全局样式
├── .env.development         # 开发环境变量
├── .env.production          # 生产环境变量
├── index.html               # HTML 模板
├── package.json             # 依赖配置
├── tsconfig.json            # TypeScript 配置
├── tailwind.config.js       # Tailwind 配置
├── vite.config.ts           # Vite 配置
└── README.md                # 前端说明文档
```

## 核心功能模块

### 1. 首页 (HomePage)
- 股票搜索功能
- 热门股票推荐
- 最近分析记录
- 快速分析入口

### 2. 综合分析页 (AnalysisPage)
- 股票基本信息展示
- 7大因子分析结果
  - 基本面分析
  - 宏观环境分析
  - 行业状况分析
  - 政策因素分析
  - 国际关系分析
  - 资金面分析
  - 市场结构分析
- 综合得分显示
- 投资建议展示

### 3. 预测页面 (PredictionPage)
- 时间维度选择（短期/中期/长期）
- 趋势预测结果
- 置信度展示
- 价格走势图
- 风险等级评估

### 4. 因子配置页 (FactorsPage)
- 因子权重调整
- 自定义分析参数
- 预设配置模板

### 5. 历史记录页 (HistoryPage)
- 分析历史列表
- 预测历史对比
- 准确率统计

## 设计原则

### 1. 响应式设计
- 桌面端优先（主要使用场景）
- 适配平板和移动端
- 断点设置：
  - Mobile: < 640px
  - Tablet: 640px - 1024px
  - Desktop: > 1024px

### 2. 用户体验
- 快速加载（首屏 < 2秒）
- 流畅交互（动画 60fps）
- 清晰的视觉层次
- 直观的操作流程

### 3. 可访问性
- 语义化 HTML
- 键盘导航支持
- ARIA 标签
- 高对比度模式

### 4. 性能优化
- 代码分割（React.lazy）
- 图片懒加载
- 虚拟滚动（长列表）
- 缓存策略（React Query）

## 色彩系统

### 主题色
- **主色调（Primary）**: 蓝色系 - 代表专业、信任
  - `#2563eb` (blue-600)
  - `#1d4ed8` (blue-700)

- **成功色（Success）**: 绿色系 - 股价上涨
  - `#10b981` (green-500)
  - `#059669` (green-600)

- **警告色（Warning）**: 黄色系 - 风险提示
  - `#f59e0b` (amber-500)
  - `#d97706` (amber-600)

- **危险色（Danger）**: 红色系 - 股价下跌
  - `#ef4444` (red-500)
  - `#dc2626` (red-600)

- **中性色（Neutral）**: 灰色系 - 横盘
  - `#6b7280` (gray-500)
  - `#4b5563` (gray-600)

### 背景色
- 浅色主题（默认）
  - 背景: `#f9fafb` (gray-50)
  - 卡片: `#ffffff` (white)
  - 边框: `#e5e7eb` (gray-200)

- 深色主题（可选）
  - 背景: `#111827` (gray-900)
  - 卡片: `#1f2937` (gray-800)
  - 边框: `#374151` (gray-700)

## 组件设计规范

### 按钮（Button）
- 尺寸：small, medium, large
- 变体：primary, secondary, outline, ghost
- 状态：default, hover, active, disabled, loading

### 卡片（Card）
- 统一圆角：8px
- 阴影：subtle（默认）, medium（hover）
- 内边距：16px（mobile）, 24px（desktop）

### 表单（Form）
- 输入框高度：40px（medium）, 48px（large）
- 标签位置：top（默认）, left
- 验证提示：inline（实时）, submit（提交时）

### 图表（Chart）
- 统一配色方案
- 响应式尺寸
- 交互式 tooltip
- 数据标注清晰

## API 集成

### 请求封装
```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    const message = error.response?.data?.message || '请求失败';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

export default api;
```

### 数据获取策略
- 使用 React Query 管理服务端状态
- 自动缓存和重新验证
- 乐观更新
- 错误重试机制

## 状态管理

### Zustand Store 示例
```typescript
// stores/useStockStore.ts
import { create } from 'zustand';

interface StockState {
  selectedStock: string | null;
  stockData: any | null;
  setSelectedStock: (code: string) => void;
  clearStock: () => void;
}

export const useStockStore = create<StockState>((set) => ({
  selectedStock: null,
  stockData: null,
  setSelectedStock: (code) => set({ selectedStock: code }),
  clearStock: () => set({ selectedStock: null, stockData: null }),
}));
```

## 路由设计

```typescript
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="analysis/:stockCode" element={<AnalysisPage />} />
          <Route path="prediction/:stockCode" element={<PredictionPage />} />
          <Route path="factors" element={<FactorsPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

## 开发工作流

### 1. 开发阶段
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码检查
npm run lint

# 格式化代码
npm run format
```

### 2. 构建阶段
```bash
# 生产构建
npm run build

# 预览构建结果
npm run preview
```

### 3. 测试阶段
```bash
# 运行单元测试
npm run test

# 运行 E2E 测试
npm run test:e2e
```

## 性能目标

- **首屏加载时间**: < 2秒
- **交互响应时间**: < 100ms
- **FPS**: 保持 60fps
- **包体积**: 主包 < 200KB（gzip）
- **Lighthouse 分数**: > 90

## 浏览器支持

- Chrome/Edge: 最新版及前两个主要版本
- Firefox: 最新版及前两个主要版本
- Safari: 最新版及前两个主要版本
- 移动端: iOS Safari 14+, Chrome Android 最新版

## 下一步计划

1. ✅ 完成架构设计文档
2. 🔄 创建 UI/UX 设计原型
3. ⏳ 搭建项目脚手架
4. ⏳ 实现基础组件库
5. ⏳ 开发核心页面
6. ⏳ 集成后端 API
7. ⏳ 性能优化
8. ⏳ 测试和部署
