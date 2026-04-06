"""股票分析数据模型"""
from datetime import datetime
from main import db


class StockAnalysis(db.Model):
    """股票分析记录表"""
    __tablename__ = 'stock_analysis'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_code = db.Column(db.String(20), nullable=False, index=True)
    analysis_type = db.Column(db.String(50), nullable=False)
    time_horizon = db.Column(db.String(20), nullable=False)

    # 分析结果
    comprehensive_score = db.Column(db.Float)

    # 各因子得分
    fundamental_score = db.Column(db.Float)
    macro_economic_score = db.Column(db.Float)
    industry_score = db.Column(db.Float)
    policy_score = db.Column(db.Float)
    international_score = db.Column(db.Float)
    funding_score = db.Column(db.Float)
    market_structure_score = db.Column(db.Float)
    technical_score = db.Column(db.Float)
    sentiment_score = db.Column(db.Float)

    # 详细结果 (JSON格式)
    analysis_details = db.Column(db.JSON)

    # 投资建议
    recommendation = db.Column(db.String(100))

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StockAnalysis {self.stock_code} - {self.analysis_type}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'analysis_type': self.analysis_type,
            'time_horizon': self.time_horizon,
            'comprehensive_score': self.comprehensive_score,
            'scores': {
                'fundamental': self.fundamental_score,
                'macro_economic': self.macro_economic_score,
                'industry': self.industry_score,
                'policy': self.policy_score,
                'international': self.international_score,
                'funding': self.funding_score,
                'market_structure': self.market_structure_score,
                'technical': self.technical_score,
                'sentiment': self.sentiment_score
            },
            'analysis_details': self.analysis_details,
            'recommendation': self.recommendation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class NewsData(db.Model):
    """新闻资讯表"""
    __tablename__ = 'news_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_code = db.Column(db.String(20), nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    source = db.Column(db.String(100))
    url = db.Column(db.String(500))

    # 情感分析结果
    sentiment_score = db.Column(db.Float)  # -1 到 1
    sentiment_label = db.Column(db.String(20))  # positive/negative/neutral

    # 关键词
    keywords = db.Column(db.JSON)

    # 时间戳
    publish_time = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NewsData {self.stock_code} - {self.title[:30]}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'url': self.url,
            'sentiment_score': self.sentiment_score,
            'sentiment_label': self.sentiment_label,
            'keywords': self.keywords,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FinancialReport(db.Model):
    """财报数据表"""
    __tablename__ = 'financial_report'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_code = db.Column(db.String(20), nullable=False, index=True)
    report_period = db.Column(db.String(20), nullable=False)  # 2023Q3, 2023
    report_type = db.Column(db.String(20), nullable=False)  # quarterly, annual

    # 业绩指标
    revenue = db.Column(db.Float)  # 营收
    net_profit = db.Column(db.Float)  # 净利润
    gross_profit_margin = db.Column(db.Float)  # 毛利率
    net_profit_margin = db.Column(db.Float)  # 净利率
    revenue_growth = db.Column(db.Float)  # 营收增长率
    net_profit_growth = db.Column(db.Float)  # 净利润增长率

    # 盈利能力指标
    roe = db.Column(db.Float)  # 净资产收益率
    roa = db.Column(db.Float)  # 资产收益率
    roic = db.Column(db.Float)  # 投入资本回报率

    # 现金流指标
    operating_cash_flow = db.Column(db.Float)  # 经营现金流
    free_cash_flow = db.Column(db.Float)  # 自由现金流
    cash_flow_ratio = db.Column(db.Float)  # 现金流比率

    # 资产负债指标
    total_assets = db.Column(db.Float)  # 总资产
    total_liabilities = db.Column(db.Float)  # 总负债
    debt_to_asset_ratio = db.Column(db.Float)  # 资产负债率

    # 完整财报数据 (JSON格式)
    full_data = db.Column(db.JSON)

    # 时间戳
    report_date = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FinancialReport {self.stock_code} - {self.report_period}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'report_period': self.report_period,
            'report_type': self.report_type,
            'revenue': self.revenue,
            'net_profit': self.net_profit,
            'gross_profit_margin': self.gross_profit_margin,
            'net_profit_margin': self.net_profit_margin,
            'revenue_growth': self.revenue_growth,
            'net_profit_growth': self.net_profit_growth,
            'roe': self.roe,
            'roa': self.roa,
            'roic': self.roic,
            'operating_cash_flow': self.operating_cash_flow,
            'free_cash_flow': self.free_cash_flow,
            'cash_flow_ratio': self.cash_flow_ratio,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'debt_to_asset_ratio': self.debt_to_asset_ratio,
            'full_data': self.full_data,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MacroEconomicData(db.Model):
    """宏观经济数据表"""
    __tablename__ = 'macro_economic_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_period = db.Column(db.String(20), nullable=False, index=True)  # 2023-10
    data_type = db.Column(db.String(50), nullable=False)  # gdp, cpi, ppi, interest_rate

    # 经济指标
    gdp_growth = db.Column(db.Float)  # GDP增长率
    cpi = db.Column(db.Float)  # 消费者物价指数
    ppi = db.Column(db.Float)  # 生产者物价指数
    inflation_rate = db.Column(db.Float)  # 通胀率
    benchmark_interest_rate = db.Column(db.Float)  # 基准利率
    m2_growth = db.Column(db.Float)  # M2增长率

    # 政策相关
    fiscal_policy_score = db.Column(db.Float)  # 财政政策评分
    monetary_policy_score = db.Column(db.Float)  # 货币政策评分

    # 完整数据 (JSON格式)
    full_data = db.Column(db.JSON)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MacroEconomicData {self.data_period} - {self.data_type}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'data_period': self.data_period,
            'data_type': self.data_type,
            'gdp_growth': self.gdp_growth,
            'cpi': self.cpi,
            'ppi': self.ppi,
            'inflation_rate': self.inflation_rate,
            'benchmark_interest_rate': self.benchmark_interest_rate,
            'm2_growth': self.m2_growth,
            'fiscal_policy_score': self.fiscal_policy_score,
            'monetary_policy_score': self.monetary_policy_score,
            'full_data': self.full_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
