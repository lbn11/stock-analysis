"""因子分析器服务"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from utils.constants import POSITIVE_WORDS, NEGATIVE_WORDS


class FactorAnalyzer:
    """多因子分析器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_fundamental_factors(self, stock_data: Dict, weight: float) -> Dict[str, Any]:
        """
        基本面分析

        分析维度：
        1. 公司业绩：营收增长、净利润、毛利率、现金流
        2. 盈利能力：ROE、ROA、EBITDA利润率
        3. 竞争优势：品牌价值、技术壁垒、网络效应、成本优势

        Args:
            stock_data: 股票数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行基本面分析")

        fundamental_data = stock_data.get('fundamental_data', {})

        # 1. 业绩指标评分
        revenue_growth = fundamental_data.get('revenue_growth', 0)
        net_profit_margin = fundamental_data.get('net_profit_margin', 0)
        cash_flow_ratio = fundamental_data.get('cash_flow_ratio', 0)

        performance_score = self._calculate_performance_score(
            revenue_growth, net_profit_margin, cash_flow_ratio
        )

        # 2. 盈利能力评分
        roe = fundamental_data.get('roe', 0)
        roa = fundamental_data.get('roa', 0)
        ebitda_margin = fundamental_data.get('ebitda_margin', 0)

        profitability_score = self._calculate_profitability_score(
            roe, roa, ebitda_margin
        )

        # 3. 竞争优势评分
        brand_value = fundamental_data.get('brand_value', 0)
        tech_barrier = fundamental_data.get('tech_barrier', 0)
        network_effect = fundamental_data.get('network_effect', 0)

        competitive_score = self._calculate_competitive_score(
            brand_value, tech_barrier, network_effect
        )

        # 综合得分
        total_score = (performance_score * 0.4 +
                      profitability_score * 0.35 +
                      competitive_score * 0.25)

        return {
            'score': total_score,
            'weight': weight,
            'weighted_score': total_score * weight,
            'details': {
                'performance_score': performance_score,
                'profitability_score': profitability_score,
                'competitive_score': competitive_score,
                'metrics': {
                    'revenue_growth': revenue_growth,
                    'net_profit_margin': net_profit_margin,
                    'roe': roe,
                    'roa': roa
                }
            },
            'summary': self._generate_fundamental_summary(total_score)
        }

    def analyze_macro_economic_factors(self, macro_data: Dict, weight: float) -> Dict[str, Any]:
        """
        宏观环境分析

        分析维度：
        1. 经济政策：财政政策、货币政策、结构性政策
        2. 利率变化：基准利率、银行间拆借利率、企业融资成本
        3. 通胀水平：温和通胀、高通胀、通缩风险

        Args:
            macro_data: 宏观经济数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行宏观环境分析")

        # 1. 政策环境评分
        fiscal_policy = macro_data.get('fiscal_policy_score', 0)
        monetary_policy = macro_data.get('monetary_policy_score', 0)

        policy_score = (fiscal_policy + monetary_policy) / 2

        # 2. 利率环境评分
        interest_rate_trend = macro_data.get('interest_rate_trend', 0)
        financing_cost = macro_data.get('financing_cost', 0)

        rate_score = self._calculate_rate_score(interest_rate_trend, financing_cost)

        # 3. 通胀环境评分
        inflation_rate = macro_data.get('inflation_rate', 0)
        inflation_score = self._calculate_inflation_score(inflation_rate)

        # 综合得分
        total_score = (policy_score * 0.4 +
                      rate_score * 0.35 +
                      inflation_score * 0.25)

        return {
            'score': total_score,
            'weight': weight,
            'weighted_score': total_score * weight,
            'details': {
                'policy_score': policy_score,
                'rate_score': rate_score,
                'inflation_score': inflation_score
            },
            'summary': self._generate_macro_summary(total_score)
        }

    def analyze_industry_factors(self, industry_data: Dict, weight: float) -> Dict[str, Any]:
        """
        行业状况分析

        分析维度：
        1. 行业发展周期：导入期、成长期、成熟期、衰退期
        2. 政策支持力度：产业规划、财税支持、准入门槛
        3. 竞争格局：市场集中度、进入壁垒、替代品威胁

        Args:
            industry_data: 行业数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行行业状况分析")

        # 1. 行业生命周期评分
        lifecycle_stage = industry_data.get('lifecycle_stage', 'mature')
        lifecycle_score = self._calculate_lifecycle_score(lifecycle_stage)

        # 2. 政策支持评分
        policy_support = industry_data.get('policy_support_level', 0)

        # 3. 竞争格局评分
        market_concentration = industry_data.get('market_concentration', 0)
        entry_barrier = industry_data.get('entry_barrier', 0)

        competition_score = self._calculate_competition_score(
            market_concentration, entry_barrier
        )

        # 综合得分
        total_score = (lifecycle_score * 0.35 +
                      policy_support * 0.35 +
                      competition_score * 0.30)

        return {
            'score': total_score,
            'weight': weight,
            'weighted_score': total_score * weight,
            'details': {
                'lifecycle_stage': lifecycle_stage,
                'lifecycle_score': lifecycle_score,
                'policy_support': policy_support,
                'competition_score': competition_score
            },
            'summary': self._generate_industry_summary(total_score, lifecycle_stage)
        }

    def analyze_policy_factors(self, policy_data: Dict, weight: float) -> Dict[str, Any]:
        """
        政策因素分析

        分析维度：
        1. 国家产业政策：新兴产业支持、传统产业改造
        2. 区域发展规划：自贸区建设、城市群战略、一带一路
        3. 监管政策：金融监管、反垄断、环保督查

        Args:
            policy_data: 政策数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行政策因素分析")

        # 1. 产业政策评分
        industrial_policy_score = policy_data.get('industrial_policy_score', 0)

        # 2. 区域政策评分
        regional_policy_score = policy_data.get('regional_policy_score', 0)

        # 3. 监管政策评分
        regulation_score = policy_data.get('regulation_score', 0)

        # 综合得分
        total_score = (industrial_policy_score * 0.4 +
                      regional_policy_score * 0.3 +
                      regulation_score * 0.3)

        return {
            'score': total_score,
            'weight': weight,
            'weighted_score': total_score * weight,
            'details': {
                'industrial_policy_score': industrial_policy_score,
                'regional_policy_score': regional_policy_score,
                'regulation_score': regulation_score
            },
            'summary': self._generate_policy_summary(total_score)
        }

    def analyze_international_factors(self, intl_data: Dict, weight: float) -> Dict[str, Any]:
        """
        国际关系分析

        分析维度：
        1. 地缘政治：军事冲突、政治博弈、恐怖主义
        2. 贸易关系：关税政策、贸易协定、制裁措施
        3. 大宗商品价格：原油、有色金属、农产品

        Args:
            intl_data: 国际关系数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行国际关系分析")

        # 1. 地缘政治评分
        geopolitical_risk = intl_data.get('geopolitical_risk', 0)
        geopolitical_score = -geopolitical_risk  # 风险越高，得分越低

        # 2. 贸易关系评分
        trade_relation_score = intl_data.get('trade_relation_score', 0)

        # 3. 大宗商品影响评分
        commodity_impact = intl_data.get('commodity_impact', 0)

        # 综合得分
        total_score = (geopolitical_score * 0.3 +
                      trade_relation_score * 0.4 +
                      commodity_impact * 0.3)

        return {
            'score': total_score,
            'weight': weight,
            'weighted_score': total_score * weight,
            'details': {
                'geopolitical_score': geopolitical_score,
                'trade_relation_score': trade_relation_score,
                'commodity_impact': commodity_impact
            },
            'summary': self._generate_international_summary(total_score)
        }

    def analyze_funding_factors(self, funding_data: Dict, weight: float) -> Dict[str, Any]:
        """
        资金面分析

        分析维度：
        1. 长期资金入市：养老金、保险资金、主权财富基金
        2. 外资流动：北向资金、QFII/RQFII、ETF跨境套利
        3. 市场情绪：恐慌贪婪指数、融资融券余额、成交量变化

        Args:
            funding_data: 资金面数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行资金面分析")

        # 1. 长期资金评分
        long_term_fund_flow = funding_data.get('long_term_fund_flow', 0)

        # 2. 外资流动评分
        foreign_fund_flow = funding_data.get('foreign_fund_flow', 0)

        # 3. 市场情绪评分
        market_sentiment = funding_data.get('market_sentiment', 0)
        volume_change = funding_data.get('volume_change', 0)

        sentiment_score = (market_sentiment + volume_change) / 2

        # 综合得分
        total_score = (long_term_fund_flow * 0.35 +
                      foreign_fund_flow * 0.35 +
                      sentiment_score * 0.30)

        return {
            'score': total_score,
            'weight': weight,
            'weighted_score': total_score * weight,
            'details': {
                'long_term_fund_flow': long_term_fund_flow,
                'foreign_fund_flow': foreign_fund_flow,
                'sentiment_score': sentiment_score
            },
            'summary': self._generate_funding_summary(total_score)
        }

    def analyze_market_structure_factors(self, market_data: Dict, weight: float) -> Dict[str, Any]:
        """
        市场结构分析

        分析维度：
        1. 机构化程度：公募基金占比、私募基金影响、券商自营
        2. 投资风格变化：价值投资、成长股投资、主题投资

        Args:
            market_data: 市场结构数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行市场结构分析")

        # 1. 机构化程度评分
        institutional_ratio = market_data.get('institutional_ratio', 0)

        # 2. 投资风格评分
        investment_style = market_data.get('investment_style', {})
        value_ratio = investment_style.get('value', 0)
        growth_ratio = investment_style.get('growth', 0)

        style_score = self._calculate_style_score(value_ratio, growth_ratio)

        # 综合得分
        total_score = (institutional_ratio * 0.5 + style_score * 0.5)

        return {
            'score': total_score,
            'weight': weight,
            'weighted_score': total_score * weight,
            'details': {
                'institutional_ratio': institutional_ratio,
                'style_score': style_score
            },
            'summary': self._generate_market_structure_summary(total_score)
        }

    def analyze_technical_factors(self, stock_data: Dict, weight: float) -> Dict[str, Any]:
        """
        技术面分析

        Args:
            stock_data: 股票数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行技术面分析")

        technical_data = stock_data.get('technical_data', {})

        # 简化的技术指标评分
        ma_trend = technical_data.get('ma_trend', 0)  # 均线趋势
        macd_signal = technical_data.get('macd_signal', 0)  # MACD信号
        rsi = technical_data.get('rsi', 50)  # RSI指标

        # RSI评分 (30-70为正常区间)
        if rsi < 30:
            rsi_score = -0.5  # 超卖
        elif rsi > 70:
            rsi_score = 0.5  # 超买
        else:
            rsi_score = 0

        total_score = (ma_trend * 0.4 + macd_signal * 0.4 + rsi_score * 0.2)

        return {
            'score': total_score,
            'weight': weight,
            'weighted_score': total_score * weight,
            'details': {
                'ma_trend': ma_trend,
                'macd_signal': macd_signal,
                'rsi': rsi
            },
            'summary': self._generate_technical_summary(total_score)
        }

    def analyze_sentiment_factors(self, news_data: Dict, weight: float) -> Dict[str, Any]:
        """
        情绪面分析（新闻情感分析）

        Args:
            news_data: 新闻数据
            weight: 权重

        Returns:
            分析结果
        """
        self.logger.info("执行情绪面分析")

        news_items = news_data.get('news_items', [])

        if not news_items:
            return {
                'score': 0,
                'weight': weight,
                'weighted_score': 0,
                'details': {
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0
                },
                'summary': '暂无新闻数据'
            }

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for item in news_items:
            content = item.get('content', '') + item.get('title', '')
            sentiment = self._analyze_text_sentiment(content)

            if sentiment > 0:
                positive_count += 1
            elif sentiment < 0:
                negative_count += 1
            else:
                neutral_count += 1

        total_count = len(news_items)
        sentiment_score = (positive_count - negative_count) / total_count if total_count > 0 else 0

        return {
            'score': sentiment_score,
            'weight': weight,
            'weighted_score': sentiment_score * weight,
            'details': {
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_count': total_count
            },
            'summary': self._generate_sentiment_summary(sentiment_score, positive_count, negative_count)
        }

    # 辅助计算方法

    def _calculate_performance_score(self, revenue_growth: float,
                                     net_profit_margin: float,
                                     cash_flow_ratio: float) -> float:
        """计算业绩得分"""
        score = 0

        # 营收增长评分
        if revenue_growth > 0.2:
            score += 0.4
        elif revenue_growth > 0.1:
            score += 0.2
        elif revenue_growth < 0:
            score -= 0.2

        # 净利润率评分
        if net_profit_margin > 0.15:
            score += 0.3
        elif net_profit_margin > 0.05:
            score += 0.15

        # 现金流评分
        if cash_flow_ratio > 0.8:
            score += 0.3
        elif cash_flow_ratio > 0.5:
            score += 0.15

        return max(-1, min(1, score))

    def _calculate_profitability_score(self, roe: float, roa: float, ebitda_margin: float) -> float:
        """计算盈利能力得分"""
        score = 0

        if roe > 0.15:
            score += 0.35
        elif roe > 0.10:
            score += 0.20

        if roa > 0.10:
            score += 0.35
        elif roa > 0.05:
            score += 0.20

        if ebitda_margin > 0.20:
            score += 0.30
        elif ebitda_margin > 0.10:
            score += 0.15

        return max(-1, min(1, score))

    def _calculate_competitive_score(self, brand_value: float,
                                     tech_barrier: float,
                                     network_effect: float) -> float:
        """计算竞争优势得分"""
        return max(-1, min(1, (brand_value + tech_barrier + network_effect) / 3))

    def _calculate_rate_score(self, interest_rate_trend: float, financing_cost: float) -> float:
        """计算利率环境得分"""
        # 利率下降对股市利好
        score = -interest_rate_trend * 0.6 - financing_cost * 0.4
        return max(-1, min(1, score))

    def _calculate_inflation_score(self, inflation_rate: float) -> float:
        """计算通胀环境得分"""
        # 温和通胀(2-3%)最优
        if 0.02 <= inflation_rate <= 0.03:
            return 0.5
        elif inflation_rate > 0.05:  # 高通胀
            return -0.5
        elif inflation_rate < 0:  # 通缩
            return -0.3
        else:
            return 0

    def _calculate_lifecycle_score(self, lifecycle_stage: str) -> float:
        """计算行业生命周期得分"""
        lifecycle_scores = {
            'introduction': 0.3,
            'growth': 0.7,
            'mature': 0.2,
            'decline': -0.5
        }
        return lifecycle_scores.get(lifecycle_stage, 0)

    def _calculate_competition_score(self, market_concentration: float, entry_barrier: float) -> float:
        """计算竞争格局得分"""
        # 市场集中度适中、进入壁垒高较好
        score = (market_concentration * 0.5 + entry_barrier * 0.5)
        return max(-1, min(1, score))

    def _calculate_style_score(self, value_ratio: float, growth_ratio: float) -> float:
        """计算投资风格得分"""
        # 价值和成长均衡最佳
        balance = 1 - abs(value_ratio - growth_ratio)
        return max(-1, min(1, balance))

    def _analyze_text_sentiment(self, text: str) -> float:
        """分析文本情感倾向"""
        if not text:
            return 0

        positive_score = sum(1 for word in POSITIVE_WORDS if word in text)
        negative_score = sum(1 for word in NEGATIVE_WORDS if word in text)

        total = positive_score + negative_score
        if total == 0:
            return 0

        return (positive_score - negative_score) / total

    # 摘要生成方法

    def _generate_fundamental_summary(self, score: float) -> str:
        """生成基本面分析摘要"""
        if score > 0.5:
            return "基本面表现优异，公司业绩强劲，盈利能力突出"
        elif score > 0.2:
            return "基本面表现良好，公司发展稳健"
        elif score > -0.2:
            return "基本面表现平稳，需持续关注"
        else:
            return "基本面表现欠佳，存在经营风险"

    def _generate_macro_summary(self, score: float) -> str:
        """生成宏观环境分析摘要"""
        if score > 0.3:
            return "宏观环境利好，政策支持明显"
        elif score > 0:
            return "宏观环境稳定，总体向好"
        else:
            return "宏观环境存在压力，需谨慎应对"

    def _generate_industry_summary(self, score: float, lifecycle_stage: str) -> str:
        """生成行业状况分析摘要"""
        stage_desc = {
            'introduction': '处于导入期',
            'growth': '处于高速成长期',
            'mature': '处于成熟期',
            'decline': '处于衰退期'
        }
        stage_text = stage_desc.get(lifecycle_stage, '')

        if score > 0.4:
            return f"行业{stage_text}，发展前景良好"
        elif score > 0:
            return f"行业{stage_text}，表现平稳"
        else:
            return f"行业{stage_text}，面临挑战"

    def _generate_policy_summary(self, score: float) -> str:
        """生成政策因素分析摘要"""
        if score > 0.4:
            return "政策环境极为有利，获得强力支持"
        elif score > 0:
            return "政策环境总体有利"
        else:
            return "政策环境存在不确定性"

    def _generate_international_summary(self, score: float) -> str:
        """生成国际关系分析摘要"""
        if score > 0.3:
            return "国际环境稳定，贸易关系良好"
        elif score > -0.3:
            return "国际环境基本稳定"
        else:
            return "国际环境存在较大不确定性"

    def _generate_funding_summary(self, score: float) -> str:
        """生成资金面分析摘要"""
        if score > 0.4:
            return "资金面充裕，市场情绪乐观"
        elif score > 0:
            return "资金面平稳，市场情绪中性"
        else:
            return "资金面偏紧，市场情绪谨慎"

    def _generate_market_structure_summary(self, score: float) -> str:
        """生成市场结构分析摘要"""
        if score > 0.5:
            return "市场结构健康，机构投资者主导"
        elif score > 0:
            return "市场结构稳定"
        else:
            return "市场结构有待优化"

    def _generate_technical_summary(self, score: float) -> str:
        """生成技术面分析摘要"""
        if score > 0.3:
            return "技术面向好，趋势向上"
        elif score > -0.3:
            return "技术面中性，震荡整理"
        else:
            return "技术面偏弱，趋势向下"

    def _generate_sentiment_summary(self, score: float, positive: int, negative: int) -> str:
        """生成情绪面分析摘要"""
        if score > 0.3:
            return f"市场情绪积极，正面新闻({positive})多于负面新闻({negative})"
        elif score > -0.3:
            return f"市场情绪中性，正负新闻基本均衡"
        else:
            return f"市场情绪消极，负面新闻({negative})多于正面新闻({positive})"
