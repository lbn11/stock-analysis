# CMoney 股价预测系统

基于多因子分析的智能股价预测系统，支持短期、中期、长期趋势预测。

## 项目概述

本系统通过分析7大类影响因素，为股票提供全面的分析和预测：

1. **基本面分析** - 公司业绩、盈利能力、竞争优势
2. **宏观环境分析** - 经济政策、利率变化、通胀水平
3. **行业状况分析** - 行业周期、政策支持、竞争格局
4. **政策因素分析** - 产业政策、区域规划、监管政策
5. **国际关系分析** - 地缘政治、贸易关系、大宗商品
6. **资金面分析** - 长期资金、外资流动、市场情绪
7. **市场结构分析** - 机构化程度、投资风格变化

## 技术架构

- **后端**: Python Flask + SQLAlchemy
- **数据处理**: Pandas + NumPy
- **机器学习**: Scikit-learn (预留接口)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **缓存**: Redis

## 项目结构

```
CMoneySystem/
├── api/                    # API接口层
│   ├── routes.py          # 路由定义
│   └── controllers.py     # 控制器逻辑
├── data/                   # 数据处理层
│   ├── collector.py       # 数据收集模块 ✓
│   ├── processor.py       # 数据处理器 ✓
│   └── storage.py         # 数据存储 ✓
├── models/                 # 数据模型 ✓
│   ├── stock_analysis.py  # 股票分析模型
│   └── prediction.py      # 预测模型
├── services/               # 业务逻辑层
│   ├── analysis_engine.py # 分析引擎 ✓
│   ├── factor_analyzer.py # 因子分析器 ✓
│   └── prediction_service.py # 预测服务 ✓
├── utils/                  # 工具函数
│   ├── constants.py       # 常量定义
│   ├── helpers.py         # 辅助函数
│   └── validators.py      # 数据验证
├── tests/                  # 测试文件
├── requirements.txt        # 依赖包列表
├── config.py              # 配置文件
├── main.py                # 主程序入口
└── test_system.py         # 系统测试脚本 ✓
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行系统测试

```bash
python test_system.py
```

这将测试所有核心功能模块，包括：
- 模块导入测试
- 数据收集功能
- 因子分析功能
- 预测服务功能
- 完整分析流程

### 3. 启动API服务

```bash
python main.py
```

服务将在 `http://localhost:5000` 启动

### 4. 测试API接口

#### 健康检查
```bash
curl http://localhost:5000/api/health
```

#### 股票分析
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000001",
    "analysis_type": "comprehensive",
    "time_horizon": "medium"
  }'
```

#### 股价预测
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000001",
    "time_horizon": "short"
  }'
```

#### 获取因子权重配置
```bash
curl http://localhost:5000/api/factors
```

## API接口说明

### 1. POST /api/analyze - 股票综合分析

**请求参数:**
```json
{
  "stock_code": "000001",           // 必填：股票代码
  "analysis_type": "comprehensive", // 可选：分析类型 (comprehensive/fundamental/technical)
  "time_horizon": "medium",         // 可选：时间范围 (short/medium/long)
  "custom_weights": {               // 可选：自定义因子权重
    "fundamental": 0.35,
    "macro_economic": 0.20
  }
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "stock_code": "000001",
    "analysis_type": "comprehensive",
    "comprehensive_score": 0.456,
    "prediction": {
      "trend": 1,
      "trend_name": "上涨",
      "confidence": 0.75
    },
    "recommendation": "推荐买入",
    "factors_considered": ["fundamental", "macro_economic", "industry", ...]
  }
}
```

### 2. POST /api/predict - 股价预测

**请求参数:**
```json
{
  "stock_code": "000001",      // 必填：股票代码
  "time_horizon": "short",     // 可选：short/medium/long
  "prediction_days": 30        // 可选：预测天数
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "stock_code": "000001",
    "trend_name": "上涨",
    "confidence": 0.75,
    "price_change_pct": 0.12,
    "risk_level": "中",
    "summary": "短期趋势预测：上涨，置信度75.0%..."
  }
}
```

### 3. GET /api/factors - 获取因子配置

返回系统中配置的所有分析因子权重和时间维度设置。

## 核心功能模块

### 1. 因子分析器 (FactorAnalyzer)

提供7大类因子的专业分析：

```python
from services.factor_analyzer import FactorAnalyzer

analyzer = FactorAnalyzer()

# 基本面分析
result = analyzer.analyze_fundamental_factors(stock_data, weight=0.30)

# 宏观环境分析
result = analyzer.analyze_macro_economic_factors(macro_data, weight=0.20)

# 情绪分析
result = analyzer.analyze_sentiment_factors(news_data, weight=0.10)
```

### 2. 预测服务 (PredictionService)

支持多时间维度的股价预测：

```python
from services.prediction_service import PredictionService

predictor = PredictionService()

# 短期预测 (1-3个月)
short_pred = predictor.predict(stock_code, historical_data, time_horizon='short')

# 中期预测 (3-12个月)
medium_pred = predictor.predict(stock_code, historical_data, time_horizon='medium')

# 长期预测 (1年以上)
long_pred = predictor.predict(stock_code, historical_data, time_horizon='long')
```

### 3. 分析引擎 (AnalysisEngine)

整合所有分析模块，提供一站式分析服务：

```python
from services.analysis_engine import AnalysisEngine

engine = AnalysisEngine()
result = engine.analyze(
    stock_code="000001",
    analysis_type="comprehensive",
    time_horizon="medium"
)
```

## 数据模型

系统包含以下主要数据模型：

- `StockAnalysis` - 股票分析记录
- `PredictionResult` - 预测结果
- `StockPriceHistory` - 股价历史数据
- `NewsData` - 新闻资讯
- `FinancialReport` - 财报数据
- `MacroEconomicData` - 宏观经济数据
- `AnalysisTask` - 分析任务
- `User` - 用户信息

## 配置说明

### 因子权重配置 (utils/constants.py)

```python
FACTOR_WEIGHTS = {
    'fundamental': 0.30,      # 基本面因素 30%
    'macro_economic': 0.20,   # 宏观环境因素 20%
    'industry': 0.15,         # 行业状况因素 15%
    'policy': 0.15,           # 政策因素 15%
    'international': 0.10,    # 国际关系因素 10%
    'funding': 0.05,          # 资金面因素 5%
    'market_structure': 0.05  # 市场结构因素 5%
}
```

### 时间维度配置

```python
TIME_HORIZONS = {
    'short': {'days': 90, 'name': '短期'},    # 1-3个月
    'medium': {'days': 365, 'name': '中期'},  # 3-12个月
    'long': {'days': 1095, 'name': '长期'}    # 1年以上
}
```

## 开发状态

✓ **已完成的功能：**
- 核心分析引擎
- 7大因子分析器
- 多时间维度预测服务
- 数据收集模块（模拟数据）
- 数据存储模块
- RESTful API接口
- 数据模型定义

🔄 **待实现功能：**
- 真实数据源集成（新闻API、财报API等）
- 机器学习模型训练
- 前端界面
- 异步任务队列
- 完整的单元测试
- 性能优化

## 注意事项

⚠️ **当前版本说明：**
1. 数据收集器目前返回**模拟数据**，用于系统测试
2. 需要安装numpy才能运行预测服务
3. 生产环境需要配置真实的数据源API
4. 建议使用Python 3.8+

## 下一步计划

根据项目计划文档 (`股价预测系统项目计划.md`)，建议按以下顺序继续开发：

1. ✅ 完成核心分析引擎（已完成）
2. 🔲 集成真实数据源API
3. 🔲 实现机器学习预测模型
4. 🔲 开发前端界面
5. 🔲 添加异步任务处理
6. 🔲 编写完整的测试用例
7. 🔲 性能优化和部署准备

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过issue反馈。
