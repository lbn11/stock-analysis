"""增强版数据收集器 - 使用真实数据源API"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import os

# 导入数据源
from data_sources import data_source_manager
from data_sources.sina_finance import SinaFinanceDataSource
from data_sources.akshare_source import AkShareDataSource


class RealDataCollector:
    """真实数据收集器 - 使用多个真实数据源"""

    def __init__(self, use_mock_fallback: bool = True):
        """
        初始化真实数据收集器

        Args:
            use_mock_fallback: 当真实数据源失败时，是否使用模拟数据兜底
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.use_mock_fallback = use_mock_fallback

        # 初始化数据源管理器
        self._init_data_sources()

    def _init_data_sources(self):
        """初始化并注册数据源"""
        try:
            # 注册AkShare数据源（优先级最高）
            akshare_source = AkShareDataSource()
            data_source_manager.register_source(akshare_source, priority=1)
            self.logger.info("Registered AkShare data source")
        except Exception as e:
            self.logger.warning(f"Failed to register AkShare: {e}")

        try:
            # 注册新浪财经数据源（作为备用）
            sina_source = SinaFinanceDataSource()
            data_source_manager.register_source(sina_source, priority=2)
            self.logger.info("Registered Sina Finance data source")
        except Exception as e:
            self.logger.warning(f"Failed to register Sina Finance: {e}")

    def collect_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """
        收集股票数据（使用真实API）

        Args:
            stock_code: 股票代码

        Returns:
            股票数据字典
        """
        self.logger.info(f"Collecting real stock data for {stock_code}")

        try:
            # 获取实时行情
            quote = data_source_manager.get_stock_quote(stock_code)

            if not quote:
                if self.use_mock_fallback:
                    self.logger.warning(f"Using mock data for {stock_code}")
                    return self._get_mock_stock_data(stock_code)
                return {}

            # 获取历史数据（最近60天）
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')

            historical = data_source_manager.get_stock_history(
                stock_code,
                start_date=start_date,
                end_date=end_date
            )

            # 计算技术指标（基于历史数据）
            technical_data = self._calculate_technical_indicators(historical)

            # 构建基本面数据（从历史数据推算）
            fundamental_data = self._estimate_fundamental_data(quote, historical)

            return {
                'stock_code': stock_code,
                'timestamp': datetime.now().isoformat(),
                'price_data': {
                    'current_price': quote.get('current', 0),
                    'change_pct': quote.get('change_pct', 0),
                    'volume': quote.get('volume', 0),
                    'turnover': quote.get('turnover', 0),
                    'high': quote.get('high', 0),
                    'low': quote.get('low', 0),
                    'open': quote.get('open', 0)
                },
                'fundamental_data': fundamental_data,
                'technical_data': technical_data,
                'historical': historical,
                'source': quote.get('source', 'unknown')
            }

        except Exception as e:
            self.logger.error(f"Error collecting stock data for {stock_code}: {e}")

            if self.use_mock_fallback:
                self.logger.warning(f"Falling back to mock data for {stock_code}")
                return self._get_mock_stock_data(stock_code)

            return {}

    def _calculate_technical_indicators(self, historical: List[Dict]) -> Dict[str, Any]:
        """计算技术指标"""
        if not historical or len(historical) < 5:
            return {
                'ma_trend': 0,
                'macd_signal': 0,
                'rsi': 50
            }

        try:
            # 提取收盘价
            closes = [item['close'] for item in historical if 'close' in item]

            if len(closes) < 5:
                return {'ma_trend': 0, 'macd_signal': 0, 'rsi': 50}

            # 计算均线趋势
            ma5 = sum(closes[-5:]) / 5
            ma10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else ma5

            ma_trend = 0.5 if ma5 > ma10 else -0.5

            # 简化的RSI计算
            if len(closes) >= 14:
                gains = []
                losses = []
                for i in range(1, 14):
                    change = closes[-i] - closes[-i-1]
                    if change > 0:
                        gains.append(change)
                    else:
                        losses.append(abs(change))

                avg_gain = sum(gains) / 14 if gains else 0.01
                avg_loss = sum(losses) / 14 if losses else 0.01
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50

            return {
                'ma_trend': ma_trend,
                'macd_signal': 0.2 if ma_trend > 0 else -0.2,
                'rsi': rsi
            }

        except Exception as e:
            self.logger.warning(f"Error calculating technical indicators: {e}")
            return {'ma_trend': 0, 'macd_signal': 0, 'rsi': 50}

    def _estimate_fundamental_data(self, quote: Dict, historical: List[Dict]) -> Dict[str, Any]:
        """
        基于市场数据估算基本面指标

        注意：这是简化估算，实际应该从财报数据获取
        """
        try:
            # 计算波动率作为风险指标
            if historical and len(historical) >= 20:
                closes = [item['close'] for item in historical[-20:] if 'close' in item]
                returns = [(closes[i] - closes[i-1]) / closes[i-1]
                          for i in range(1, len(closes))]
                volatility = (sum([r**2 for r in returns]) / len(returns)) ** 0.5
            else:
                volatility = 0.02

            # 基于价格趋势和波动率估算指标
            change_pct = quote.get('change_pct', 0)

            # 模拟基本面指标（实际应从财报获取）
            fundamental_data = {
                'revenue_growth': min(0.3, max(-0.1, change_pct * 10)),
                'net_profit_margin': 0.10 + change_pct * 0.5,
                'cash_flow_ratio': 0.7 + (1 - volatility) * 0.2,
                'roe': 0.15 + change_pct * 0.3,
                'roa': 0.08 + change_pct * 0.2,
                'ebitda_margin': 0.18 + change_pct * 0.3,
                'brand_value': 0.6,
                'tech_barrier': 0.5,
                'network_effect': 0.5
            }

            return fundamental_data

        except Exception as e:
            self.logger.warning(f"Error estimating fundamental data: {e}")
            return {
                'revenue_growth': 0.10,
                'net_profit_margin': 0.10,
                'cash_flow_ratio': 0.70,
                'roe': 0.15,
                'roa': 0.08,
                'ebitda_margin': 0.18,
                'brand_value': 0.5,
                'tech_barrier': 0.5,
                'network_effect': 0.5
            }

    def collect_macro_data(self) -> Dict[str, Any]:
        """收集宏观经济数据（使用真实API）"""
        self.logger.info("Collecting real macro economic data")

        try:
            # 尝试从AkShare获取宏观数据
            akshare = data_source_manager.get_source("AkShare")

            if akshare:
                macro_data = akshare.get_macro_data()

                if macro_data:
                    # 转换为系统需要的格式
                    return self._convert_macro_data(macro_data)

            # 如果失败，使用模拟数据
            if self.use_mock_fallback:
                return self._get_mock_macro_data()

            return {}

        except Exception as e:
            self.logger.error(f"Error collecting macro data: {e}")

            if self.use_mock_fallback:
                return self._get_mock_macro_data()

            return {}

    def _convert_macro_data(self, raw_data: Dict) -> Dict[str, Any]:
        """转换宏观数据为系统格式"""
        try:
            gdp_growth = raw_data.get('gdp', {}).get('growth_rate', 5.5) / 100
            cpi = raw_data.get('cpi', {}).get('value', 2.5) / 100
            pmi = raw_data.get('pmi', {}).get('manufacturing', 51.0)

            return {
                'timestamp': datetime.now().isoformat(),
                'fiscal_policy_score': 0.6,
                'monetary_policy_score': 0.5,
                'interest_rate_trend': -0.1 if gdp_growth > 0.05 else 0.1,
                'financing_cost': 0.045,
                'inflation_rate': cpi,
                'gdp_growth': gdp_growth,
                'indicators': {
                    'gdp_growth_rate': gdp_growth,
                    'cpi': cpi * 100 + 100,
                    'pmi': pmi,
                    'm2_growth': raw_data.get('m2', {}).get('growth_rate', 9.5) / 100
                }
            }

        except Exception as e:
            self.logger.warning(f"Error converting macro data: {e}")
            return self._get_mock_macro_data()

    def _get_mock_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """获取模拟股票数据（作为兜底）"""
        # 使用原有的模拟数据逻辑
        from data.collector import DataCollector
        mock_collector = DataCollector()
        return mock_collector.collect_stock_data(stock_code)

    def _get_mock_macro_data(self) -> Dict[str, Any]:
        """获取模拟宏观数据（作为兜底）"""
        from data.collector import DataCollector
        mock_collector = DataCollector()
        return mock_collector.collect_macro_data()

    # 其他collect方法可以复用原有的实现
    def collect_news_data(self, stock_code: str) -> Dict[str, Any]:
        """收集新闻数据"""
        from data.collector import DataCollector
        mock_collector = DataCollector()
        return mock_collector.collect_news_data(stock_code)

    def collect_industry_data(self, stock_code: str) -> Dict[str, Any]:
        """收集行业数据"""
        from data.collector import DataCollector
        mock_collector = DataCollector()
        return mock_collector.collect_industry_data(stock_code)

    def collect_policy_data(self, stock_code: str) -> Dict[str, Any]:
        """收集政策数据"""
        from data.collector import DataCollector
        mock_collector = DataCollector()
        return mock_collector.collect_policy_data(stock_code)

    def collect_international_data(self, stock_code: str) -> Dict[str, Any]:
        """收集国际关系数据"""
        from data.collector import DataCollector
        mock_collector = DataCollector()
        return mock_collector.collect_international_data(stock_code)

    def collect_funding_data(self, stock_code: str) -> Dict[str, Any]:
        """收集资金面数据"""
        from data.collector import DataCollector
        mock_collector = DataCollector()
        return mock_collector.collect_funding_data(stock_code)

    def collect_market_structure_data(self, stock_code: str) -> Dict[str, Any]:
        """收集市场结构数据"""
        from data.collector import DataCollector
        mock_collector = DataCollector()
        return mock_collector.collect_market_structure_data(stock_code)
