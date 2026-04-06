# CMoney 股价预测系统 - 前端

基于 React + TypeScript + Tailwind CSS 构建的现代化股价预测系统前端应用。

## 技术栈

- **React 18.2** - UI 框架
- **TypeScript 5.2** - 类型安全
- **Vite 5.0** - 构建工具
- **Tailwind CSS 3.3** - 样式框架
- **React Router 6** - 路由管理
- **Zustand** - 状态管理
- **TanStack Query** - 数据获取和缓存
- **Recharts / ECharts** - 数据可视化
- **Axios** - HTTP 客户端

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

如果安装较慢，可以使用国内镜像：

```bash
npm install --registry=https://registry.npmmirror.com
```

### 2. 配置环境变量

复制环境变量文件：

```bash
cp .env.development .env.local
```

编辑 `.env.local` 文件，修改 API 地址（如果需要）：

```
VITE_API_BASE_URL=http://localhost:5000/api
```

### 3. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

### 4. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

### 5. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── assets/              # 静态资源
│   ├── components/          # 组件
│   │   └── layout/          # 布局组件
│   ├── pages/               # 页面组件
│   │   ├── HomePage.tsx     # 首页 ✅
│   │   ├── AnalysisPage.tsx # 分析页（待完善）
│   │   ├── PredictionPage.tsx # 预测页（待完善）
│   │   ├── FactorsPage.tsx  # 因子配置页（待完善）
│   │   └── HistoryPage.tsx  # 历史记录页（待完善）
│   ├── services/            # API 服务 ✅
│   │   ├── api.ts
│   │   ├── stockService.ts
│   │   ├── analysisService.ts
│   │   └── predictionService.ts
│   ├── stores/              # 状态管理 ✅
│   │   ├── useStockStore.ts
│   │   └── useAnalysisStore.ts
│   ├── types/               # 类型定义 ✅
│   │   ├── stock.ts
│   │   ├── analysis.ts
│   │   └── api.ts
│   ├── utils/               # 工具函数 ✅
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   └── helpers.ts
│   ├── App.tsx              # 根组件 ✅
│   ├── main.tsx             # 入口文件 ✅
│   └── index.css            # 全局样式 ✅
├── public/                  # 公共资源
├── index.html               # HTML 模板 ✅
├── package.json             # 依赖配置 ✅
├── tsconfig.json            # TS 配置 ✅
├── vite.config.ts           # Vite 配置 ✅
└── tailwind.config.js       # Tailwind 配置 ✅
```

## 功能模块

### 已实现 ✅

1. **项目基础架构**
   - Vite + React + TypeScript 配置
   - Tailwind CSS 样式系统
   - 路由配置（React Router）
   - 状态管理（Zustand）
   - API 客户端（Axios）

2. **类型定义**
   - 股票相关类型
   - 分析相关类型
   - API 请求/响应类型

3. **工具函数**
   - 价格、百分比、日期格式化
   - 趋势判断和显示
   - 防抖、节流等辅助函数

4. **API 服务封装**
   - 股票服务（搜索、详情、历史数据）
   - 分析服务（执行分析、因子配置）
   - 预测服务（股价预测、准确率统计）

5. **基础页面**
   - 首页（搜索、热门股票）
   - 主布局（导航、页头页脚）

### 待实现 🔄

1. **数据可视化组件**
   - 股价走势图（K线图）
   - 因子雷达图
   - 趋势仪表盘
   - 预测置信度图表

2. **完整页面实现**
   - 综合分析页
   - 股价预测页
   - 因子配置页
   - 历史记录页

3. **UI 组件库**
   - Button, Card, Input 等基础组件
   - Modal, Toast 等交互组件
   - Loading, Empty 等状态组件

4. **功能优化**
   - 实时数据更新（WebSocket）
   - 离线支持（PWA）
   - 深色模式
   - 响应式优化

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `src/App.tsx` 添加路由配置
3. 在 `src/components/layout/MainLayout.tsx` 添加导航链接

### 添加新 API

1. 在 `src/types/` 定义类型
2. 在 `src/services/` 创建服务函数
3. 使用 React Query 的 `useQuery` 或 `useMutation` 调用

### 样式开发

项目使用 Tailwind CSS，推荐：

- 使用 utility classes 快速开发
- 自定义样式放在 `index.css`
- 组件级样式使用 `className`

### 状态管理

使用 Zustand 管理全局状态：

```typescript
import { useStockStore } from '@/stores/useStockStore';

function Component() {
  const { selectedStock, setSelectedStock } = useStockStore();
  // ...
}
```

## 命令说明

```bash
# 开发
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run preview      # 预览生产构建

# 代码质量
npm run lint         # ESLint 检查
npm run format       # Prettier 格式化
npm run type-check   # TypeScript 类型检查
```

## API 集成

前端通过 Axios 与后端 API 通信：

- 开发环境：`http://localhost:5000/api`
- 生产环境：`/api`（通过反向代理）

API 配置在 `src/services/api.ts`，包含：

- 请求/响应拦截器
- 错误处理
- Token 管理
- 请求耗时统计

## 浏览器支持

- Chrome/Edge: 最新版及前两个主要版本
- Firefox: 最新版及前两个主要版本
- Safari: 最新版
- 移动端: iOS Safari 14+, Chrome Android

## 性能优化

- 代码分割（React.lazy）
- 图片懒加载
- React Query 缓存
- 虚拟滚动（长列表）
- 生产构建优化

## 下一步计划

1. ✅ 完成基础架构搭建
2. 🔄 实现数据可视化组件
3. ⏳ 完善所有页面功能
4. ⏳ 集成后端 API
5. ⏳ 性能优化和测试
6. ⏳ 部署和上线

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

## 许可证

仅供学习和研究使用。
