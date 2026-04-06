# 真实数据源集成指南

## 概述

系统已集成了两个免费的数据源：
- **AkShare** - 主要推荐，数据全面
- **新浪财经** - 备用，实时行情快速

---

## 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd /storage/emulated/0/Download/CMoney/CMoneySystem

# 安装 Python 依赖
pip install akshare requests pandas numpy

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 2. 测试数据源

```bash
# 运行测试脚本
python test_data_sources.py
```

测试脚本会自动测试：
- ✓ AkShare 实时行情获取
- ✓ AkShare 历史数据获取
- ✓ AkShare 宏观数据获取
- ✓ 新浪财经实时行情获取

---

## 数据源对比

| 功能 | AkShare | 新浪财经 |
|------|---------|----------|
| 实时行情 | ✅ 推荐 | ✅ 备用 |
| 历史数据 | ✅ 完整 | ❌ 不支持 |
| 财报数据 | ✅ 支持 | ❌ 不支持 |
| 宏观数据 | ✅ 丰富 | ❌ 不支持 |
| 批量查询 | ✅ 支持 | ✅ 支持 |
| 响应速度 | 中等 | 快 |
| 稳定性 | 高 | 中 |
| 免费额度 | 无限制 | 无限制 |

**推荐使用 AkShare 作为主要数据源**

---

## 使用方法

### 方法 1：在代码中直接使用

```python
from data_sources.akshare_source import AkShareDataSource

# 初始化数据源
source = AkShareDataSource()

# 获取实时行情
quote = source.get_stock_quote('000001')
print(f"股票名称: {quote['name']}")
print(f"当前价格: {quote['current']}")
print(f"涨跌幅: {quote['change_pct']*100:.2f}%")

# 获取历史数据
history = source.get_stock_history(
    stock_code='000001',
    start_date='2024-01-01',
    end_date='2024-12-31'
)
print(f"获取 {len(history)} 条历史记录")

# 获取宏观数据
macro = source.get_macro_data()
print(f"GDP增长率: {macro['gdp']['growth_rate']}%")
```

### 方法 2：使用 RealDataCollector

```python
from data.real_collector import RealDataCollector

# 初始化（会自动使用真实数据源）
collector = RealDataCollector(use_mock_fallback=True)

# 收集股票数据（自动获取真实数据）
data = collector.collect_stock_data('000001')

# 数据包含：
# - price_data: 实时行情
# - fundamental_data: 基本面指标
# - technical_data: 技术指标
# - historical: 历史数据
```

---

## 数据源 API 对接

### AkSupport 支持的数据接口

#### 1. 股票实时行情
```python
ak.stock_zh_a_spot_em()  # A股实时行情
```

#### 2. 股票历史数据
```python
ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"  # 前复权
)
```

#### 3. 财务报告
```python
ak.stock_financial_report_sina(stock="000001", symbol="利润表")
```

#### 4. 宏观经济数据
```python
ak.macro_china_gdp()          # GDP数据
ak.macro_china_cpi_yearly()   # CPI数据
ak.macro_china_pmi_yearly()   # PMI数据
ak.macro_china_m2_yearly()    # M2数据
```

#### 5. 指数数据
```python
ak.stock_zh_index_spot_em()  # 实时指数
```

---

## 集成到系统

### 后端 API 使用

```python
from data.real_collector import RealDataCollector
from services.analysis_engine import AnalysisEngine

# 使用真实数据收集器
collector = RealDataCollector(use_mock_fallback=True)

# 收集数据
stock_data = collector.collect_stock_data('000001')
macro_data = collector.collect_macro_data()

# 分析引擎会自动使用真实数据
engine = AnalysisEngine()
result = engine.analyze(
    stock_code='000001',
    analysis_type='comprehensive',
    time_horizon='medium'
)
```

### 前端调用

前端无需修改，会自动使用真实数据：

```typescript
// 分析页面会自动调用后端API
const response = await fetch('/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    stock_code: '000001',
    analysis_type: 'comprehensive',
    time_horizon: 'medium'
  })
});
```

后端会使用 RealDataCollector 获取真实数据。

---

## 配置选项

### 1. 启用真实数据源

编辑 `config.py`:

```python
# 数据源配置
DATA_SOURCE = 'akshare'  # 'akshare' 或 'sina'
USE_MOCK_FALLBACK = True  # 数据源失败时使用模拟数据
```

### 2. 请求频率限制

编辑 `data_sources/__init__.py`:

```python
class BaseDataSource:
    MIN_REQUEST_INTERVAL = 1.0  # 每次请求最少间隔1秒
```

---

## 常见问题

### Q1: AkShare 安装失败？

**A**: 尝试以下方法：
```bash
# 使用国内镜像源
pip install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或升级 pip 后安装
python -m pip install --upgrade pip
pip install akshare
```

### Q2: 数据获取超时？

**A**: 可能是网络问题，尝试：
1. 检查网络连接
2. 增加超时时间
3. 使用多个数据源轮换

### Q3: 股票代码不存在？

**A**: 确保使用正确的股票代码格式：
- 深交所: `000001`, `000002` 等（0开头）
- 上交所: `600000`, `600036` 等（6开头）

### Q4: 如何获取更多数据？

**A**: 查看 AkShare 官方文档：
- 官网: https://akshare.akfamily.xyz/
- GitHub: https://github.com/akfamily/akshare

---

## 数据更新策略

### 实时数据更新频率
- **实时行情**: 每次请求时获取（交易时间内）
- **历史数据**: 缓存24小时
- **宏观数据**: 缓存7天
- **财报数据**: 缓存30天

### 自动更新

可以设置定时任务定期更新数据：

```python
# 在服务器上使用 cron 或 Celery Beat
# 每天收盘后更新数据
```

---

## 性能优化

### 1. 使用缓存

```python
# data/storage.py 中实现缓存
class DataStorage:
    def cache_quote(self, stock_code, data):
        # 缓存5分钟
        pass
```

### 2. 批量获取

```python
# 批量获取多只股票的行情
quotes = sina_source.get_real_time_data_batch([
    '000001', '000002', '600000'
])
```

### 3. 异步请求

```python
# 使用 asyncio + aiohttp 并发请求
import asyncio
import aiohttp

async def fetch_multiple_stocks(stock_codes):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_quote(session, code) for code in stock_codes]
        return await asyncio.gather(*tasks)
```

---

## 下一步

1. ✅ 安装依赖：`pip install akshare requests`
2. ✅ 运行测试：`python test_data_sources.py`
3. ✅ 启动后端：`python main.py`
4. ✅ 测试前端：访问 http://localhost:5173
5. ✅ 查看真实数据：分析任何股票代码

---

## 注意事项

⚠️ **数据使用限制**:
- 遵守数据源的使用条款
- 不要过度频繁请求（建议每秒不超过1次）
- 商业使用需确认授权

⚠️ **数据准确性**:
- 免费数据可能有延迟
- 建议多个数据源交叉验证
- 重要决策建议参考官方数据

⚠️ **免责声明**:
- 系统仅供参考，不构成投资建议
- 投资有风险，决策需谨慎
- 开发者不对投资损失负责

---

**开始使用真实数据，让系统更强大！** 🚀
