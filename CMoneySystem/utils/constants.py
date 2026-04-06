"""常量定义"""

# 分析因子权重
FACTOR_WEIGHTS = {
    'fundamental': 0.30,      # 基本面因素
    'macro_economic': 0.20,   # 宏观环境因素
    'industry': 0.15,         # 行业状况因素
    'policy': 0.15,           # 政策因素
    'international': 0.10,    # 国际关系因素
    'funding': 0.05,          # 资金面因素
    'market_structure': 0.05  # 市场结构因素
}

# 时间维度定义
TIME_HORIZONS = {
    'short': {'days': 90, 'name': '短期'},    # 短期预测(3个月)
    'medium': {'days': 365, 'name': '中期'},  # 中期预测(1年)
    'long': {'days': 1095, 'name': '长期'}    # 长期预测(3年)
}

# 股票代码正则表达式
STOCK_CODE_PATTERN = r'^[0-9]{6}$'

# 预测结果映射
PREDICTION_MAP = {
    1: '上涨',
    0: '横盘',
    -1: '下跌'
}

# 情感分析词汇
POSITIVE_WORDS = [
    '增长', '上涨', '利好', '买入', '推荐', '盈利', '增长',
    '强势', '突破', '创新高', '复苏', '向好', '改善', '提升'
]

NEGATIVE_WORDS = [
    '下跌', '亏损', '利空', '卖出', '减持', '危机', '下跌',
    '弱势', '破位', '创新低', '衰退', '恶化', '下降', '风险'
]

# 数据源配置
DATA_SOURCES = {
    'financial_news': ['sina', 'eastmoney', 'hexun'],
    'stock_data': ['tencent', 'sina', '163'],
    'policy_news': ['gov', 'csrc', 'pbc']
}