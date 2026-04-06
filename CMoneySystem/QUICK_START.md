# 🚀 CMoney 股价预测系统 - 完整启动指南

## 项目状态

✅ **前端**: 100% 完成（5个页面，2104行代码）
✅ **后端**: 90% 完成（核心功能完整）
⚠️ **数据源**: 框架完成，需要安装依赖
⚠️ **ML模型**: 框架完成，需要训练

---

## 一键启动（推荐）

### 1. 安装后端依赖

```bash
cd /storage/emulated/0/Download/CMoney/CMoneySystem

# 安装 Python 包
pip install flask akshare requests pandas numpy

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
# 在项目根目录
python main.py

# 服务将在 http://localhost:5000 启动
```

### 3. 安装前端依赖

```bash
# 新开一个终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 如果遇到 peer dependency 警告
npm install --legacy-peer-deps
```

### 4. 启动前端服务

```bash
# 在 frontend 目录
npm run dev

# 服务将在 http://localhost:5173 启动
```

### 5. 访问系统

打开浏览器访问：**http://localhost:5173**

---

## 功能测试

### 测试 1: 搜索股票

1. 在首页搜索框输入：`000001` 或 `平安银行`
2. 点击搜索或按回车
3. 应该显示热门股票列表

### 测试 2: 查看分析

访问：**http://localhost:5173/analysis/000001**

应该看到：
- 综合评分：78分
- 投资建议：推荐买入
- 7大因子评分
- 分析依据说明

### 测试 3: 查看预测

访问：**http://localhost:5173/prediction?horizon=medium**

应该看到：
- 趋势预测：上涨
- 置信度：75%
- 目标价位
- 风险评估

### 测试 4: 配置因子

访问：**http://localhost:5173/factors**

应该看到：
- 7大因子权重滑块
- 预设模板（保守/平衡/激进）
- 权重分布图表

### 测试 5: 查看历史

访问：**http://localhost:5173/history**

应该看到：
- 分析/预测记录列表
- 搜索和排序功能
- 分页导航

---

## 测试真实数据源

### 安装 AkShare

```bash
pip install akshare
```

### 运行测试脚本

```bash
python test_data_sources.py
```

预期输出：
```
✓ AkShare 已安装
✓ requests 已安装
✓ AkShareDataSource 导入成功
✓ SinaFinanceDataSource 导入成功

获取 000001 实时行情...
  ✓ 成功!
  名称: 平安银行
  最新价: 12.34
  涨跌幅: +2.3%
```

---

## 页面路由

| 页面 | 路由 | 说明 |
|------|------|------|
| 首页 | `/` | 搜索和快速分析 |
| 综合分析 | `/analysis/:stockCode` | 7大因子分析 |
| 股价预测 | `/prediction?horizon=medium` | 趋势预测 |
| 因子配置 | `/factors` | 权重调整 |
| 历史记录 | `/history` | 历史查询 |

---

## API 接口

### 1. 健康检查
```bash
curl http://localhost:5000/api/health
```

### 2. 股票分析
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000001",
    "analysis_type": "comprehensive",
    "time_horizon": "medium"
  }'
```

### 3. 股价预测
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000001",
    "time_horizon": "short"
  }'
```

### 4. 因子权重
```bash
curl http://localhost:5000/api/factors
```

---

## 常见问题

### Q1: 前端无法连接后端？

**A**: 检查：
1. 后端是否启动（访问 http://localhost:5000/api/health）
2. 前端 `.env.development` 配置
3. 浏览器控制台错误信息

### Q2: npm install 失败？

**A**: 尝试：
```bash
# 清理缓存
npm cache clean --force

# 使用 legacy peer deps
npm install --legacy-peer-deps

# 或使用 cnpm
npm install -g cnpm
cnpm install
```

### Q3: 页面显示空白？

**A**: 检查：
1. 浏览器控制台（F12 → Console）错误
2. 网络请求（F12 → Network）是否失败
3. 后端是否正常响应

### Q4: AkShare 数据获取失败？

**A**: 可能原因：
- 网络连接问题
- API 限流（等待几秒后重试）
- 股票代码格式错误

解决方法：
```bash
# 测试网络
ping akshare.akfamily.xyz

# 使用备用数据源（新浪财经）
# 自动切换，无需修改代码
```

### Q5: 如何查看日志？

**A**: 后端日志会直接输出到终端

---

## 开发模式 vs 生产模式

### 开发模式（当前）

```bash
# 后端
python main.py

# 前端
npm run dev
```

特点：
- 热重载
- 详细日志
- 调试信息

### 生产模式

```bash
# 1. 构建前端
cd frontend
npm run build

# 2. 使用生产配置
# 后端会自动读取 .env.production

# 3. 使用 Gunicorn 启动
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

---

## 目录结构

```
CMoneySystem/
├── api/                    # 后端API
│   └── routes.py          # 路由定义
├── data/                   # 数据层
│   ├── collector.py       # 数据收集
│   ├── processor.py       # 数据处理
│   └── storage.py         # 数据存储
├── data_sources/           # 数据源
│   ├── akshare_source.py  # AkShare
│   └── sina_finance.py    # 新浪财经
├── frontend/              # 前端
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   ├── stores/        # 状态管理
│   │   └── types/         # 类型定义
│   ├── package.json
│   └── vite.config.ts
├── models/                 # 数据模型
├── services/               # 业务逻辑
│   ├── analysis_engine.py
│   ├── factor_analyzer.py
│   └── prediction_service.py
├── utils/                  # 工具函数
├── main.py                # 后端入口
├── config.py              # 配置文件
├── test_system.py         # 系统测试
└── test_data_sources.py   # 数据源测试
```

---

## 技术栈

### 后端
- **Flask** - Web框架
- **Pandas** - 数据处理
- **NumPy** - 数值计算
- **AkShare** - 数据源
- **Requests** - HTTP请求

### 前端
- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式
- **React Query** - 数据获取
- **Zustand** - 状态管理

---

## 文档清单

- ✅ `README.md` - 项目说明
- ✅ `QUICK_START.md` - 快速启动指南（本文档）
- ✅ `DATA_SOURCE_GUIDE.md` - 数据源集成指南
- ✅ `frontend/FINAL_SUMMARY.md` - 前端实现总结
- ✅ `frontend/IMPLEMENTATION_SUMMARY.md` - 实现细节
- ✅ `frontend/RUN_GUIDE.md` - 运行指南

---

## 性能指标

### 预期性能

- **首页加载**: < 2秒
- **分析请求**: < 5秒
- **预测请求**: < 5秒
- **数据查询**: < 1秒

### 优化建议

1. **使用 Redis 缓存**
2. **数据库持久化**
3. **CDN 加速前端**
4. **Gzip 压缩**

---

## 安全建议

⚠️ **生产环境注意事项**：

1. **API 认证**
   - 添加用户登录
   - JWT Token 验证
   - 请求频率限制

2. **数据加密**
   - HTTPS 加密传输
   - 敏感数据加密存储
   - SQL 注入防护

3. **访问控制**
   - CORS 配置
   - IP 白名单
   - 权限管理

---

## 下一步计划

### 短期（1-2周）
- [ ] 集成真实数据源
- [ ] 添加数据库持久化
- [ ] 实现用户认证
- [ ] 部署到生产环境

### 中期（1个月）
- [ ] 训练 ML 预测模型
- [ ] 添加更多图表
- [ ] 实现导出功能
- [ ] 性能优化

### 长期（2-3个月）
- [ ] 移动端 APP
- [ ] 实时推送
- [ ] 机器学习模型优化
- [ ] 多语言支持

---

## 支持

如有问题：
1. 查看文档目录
2. 检查浏览器控制台
3. 查看后端日志
4. 运行测试脚本

---

**🎉 祝你使用愉快！**
