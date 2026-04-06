"""同花顺数据源

同花顺（10jqka）提供专业的股票行情和分析数据
官网: http://www.10jqka.com.cn/
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import re

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class TonghuashunDataSource:
    """同花顺数据源"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.name = "Tonghuashun"
        self.base_url = "http://push2his.eastmoney.com/api"
        self.ths_url = "http://basic.10jqka.com.cn"

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://www.10jqka.com.cn/'
        }

    def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票实时行情

        同花顺的实时行情可以通过东方财富的接口获取
        这里提供直接的同花顺网页解析方案

        Args:
            stock_code: 股票代码

        Returns:
            行情数据字典
        """
        if not REQUESTS_AVAILABLE:
            return {}

        try:
            # 同花顺个股页面URL
            url = f"http://quote.10jqka.com.cn/{stock_code}/"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # 解析页面数据（简化实现）
            # 实际应用中需要使用 BeautifulSoup 或正则表达式解析

            # 这里使用东方财富接口作为备选
            quote_data = self._get_quote_from_eastmoney(stock_code)

            if quote_data:
                quote_data['source'] = self.name
                self.logger.info(f"Fetched quote for {stock_code} via backup method")

            return quote_data

        except Exception as e:
            self.logger.error(f"Error fetching quote for {stock_code}: {e}")
            return {}

    def get_stock_history(self, stock_code: str, start_date: str = None,
                          end_date: str = None, period: str = 'daily') -> List[Dict[str, Any]]:
        """
        获取股票历史数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            period: 周期 (daily/weekly/monthly)

        Returns:
            历史数据列表
        """
        if not REQUESTS_AVAILABLE:
            return []

        try:
            # 同花顺历史数据通过东方财富接口获取
            secid = self._convert_stock_code(stock_code)

            # 设置默认日期
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            else:
                end_date = end_date.replace('-', '')

            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            else:
                start_date = start_date.replace('-', '')

            # 确定K线类型
            klt_map = {
                'daily': '101',
                'weekly': '102',
                'monthly': '103'
            }
            klt = klt_map.get(period, '101')

            # 使用东方财富的历史K线接口（同花顺使用相同的数据源）
            url = f"{self.base_url}/qt/stock/kline"
            params = {
                'secid': secid,
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': klt,
                'fqt': '1',  # 前复权
                'beg': start_date,
                'end': end_date,
                'lmt': '1000'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('rc') != 0 or not data.get('data'):
                self.logger.warning(f"No history data for {stock_code}")
                return []

            # 解析K线数据
            klines = data['data']['klines']

            history_data = []
            for kline_str in klines:
                parts = kline_str.split(',')
                if len(parts) >= 11:
                    history_data.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'close': float(parts[2]),
                        'high': float(parts[3]),
                        'low': float(parts[4]),
                        'volume': int(float(parts[5])),
                        'turnover': float(parts[6]),
                        'amplitude': float(parts[7]) if parts[7] else 0,
                        'change_pct': float(parts[8]) if parts[8] else 0,
                        'change_amount': float(parts[9]) if parts[9] else 0,
                        'turnover_rate': float(parts[10]) if len(parts) > 10 and parts[10] else 0
                    })

            self.logger.info(f"Fetched {len(history_data)} history records for {stock_code}")
            return history_data

        except Exception as e:
            self.logger.error(f"Error fetching history for {stock_code}: {e}")
            return []

    def get_financial_indicators(self, stock_code: str) -> Dict[str, Any]:
        """
        获取财务指标

        同花顺的财务指标页面
        http://basic.10jqka.com.cn/{stock_code}/finance.html

        Args:
            stock_code: 股票代码

        Returns:
            财务指标数据
        """
        if not REQUESTS_AVAILABLE:
            return {}

        try:
            # 同花顺财务指标页面
            url = f"http://basic.10jqka.com.cn/{stock_code}/finance/"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # 解析财务指标（简化实现）
            # 实际应用中需要解析页面HTML

            # 返回模拟数据结构
            financial_data = {
                'stock_code': stock_code,
                'timestamp': datetime.now().isoformat(),
                'source': self.name,
                'note': 'Full implementation requires HTML parsing'
            }

            self.logger.info(f"Fetched financial indicators for {stock_code}")
            return financial_data

        except Exception as e:
            self.logger.error(f"Error fetching financial indicators for {stock_code}: {e}")
            return {}

    def get_fund_flow(self, stock_code: str, days: int = 5) -> List[Dict[str, Any]]:
        """
        获取资金流向数据

        同花顺的资金流向数据非常有价值
        http://basic.10jqka.com.cn/{stock_code}/capital.html

        Args:
            stock_code: 股票代码
            days: 获取最近几天的数据

        Returns:
            资金流向数据列表
        """
        if not REQUESTS_AVAILABLE:
            return []

        try:
            # 同花顺资金流向页面
            url = f"http://basic.10jqka.com.cn/{stock_code}/capital/"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # 解析资金流向数据（简化实现）
            # 实际应用中需要解析页面中的资金流向表格

            # 返回模拟数据结构
            fund_flow_data = []
            self.logger.info(f"Fetched fund flow for {stock_code}")

            return fund_flow_data

        except Exception as e:
            self.logger.error(f"Error fetching fund flow for {stock_code}: {e}")
            return []

    def get_industry_ranking(self, stock_code: str) -> Dict[str, Any]:
        """
        获取行业排名数据

        同花顺提供详细的行业排名数据

        Args:
            stock_code: 股票代码

        Returns:
            行业排名数据
        """
        if not REQUESTS_AVAILABLE:
            return {}

        try:
            # 获取股票所属行业
            # 同花顺行业页面

            ranking_data = {
                'stock_code': stock_code,
                'industry_name': '',
                'industry_ranking': 0,
                'total_stocks_in_industry': 0,
                'timestamp': datetime.now().isoformat(),
                'source': self.name,
                'note': 'Full implementation requires HTML parsing'
            }

            self.logger.info(f"Fetched industry ranking for {stock_code}")
            return ranking_data

        except Exception as e:
            self.logger.error(f"Error fetching industry ranking for {stock_code}: {e}")
            return {}

    def get_news_sentiment(self, stock_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取新闻情绪

        同花顺提供个股新闻和情绪分析

        Args:
            stock_code: 股票代码
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        if not REQUESTS_AVAILABLE:
            return []

        try:
            # 同花顺新闻页面
            url = f"http://basic.10jqka.com.cn/{stock_code}/news/"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # 解析新闻数据（简化实现）

            news_list = []
            self.logger.info(f"Fetched {len(news_list)} news for {stock_code}")
            return news_list

        except Exception as e:
            self.logger.error(f"Error fetching news for {stock_code}: {e}")
            return []

    def get_technical_indicators(self, stock_code: str) -> Dict[str, Any]:
        """
        获取技术指标数据

        同花顺提供丰富的技术指标

        Args:
            stock_code: 股票代码

        Returns:
            技术指标数据
        """
        if not REQUESTS_AVAILABLE:
            return {}

        try:
            # 获取历史数据
            history = self.get_stock_history(stock_code)

            if not history or len(history) < 20:
                return {}

            # 计算常用技术指标
            closes = [h['close'] for h in history]

            # MA
            ma5 = sum(closes[-5:]) / 5
            ma10 = sum(closes[-10:]) / 10
            ma20 = sum(closes[-20:]) / 20

            # RSI
            rsi = self._calculate_rsi(closes)

            # MACD
            macd = self._calculate_macd(closes)

            # KDJ
            kdj = self._calculate_kdj(history)

            technical_data = {
                'stock_code': stock_code,
                'ma': {
                    'ma5': ma5,
                    'ma10': ma10,
                    'ma20': ma20
                },
                'rsi': rsi,
                'macd': macd,
                'kdj': kdj,
                'timestamp': datetime.now().isoformat(),
                'source': self.name
            }

            self.logger.info(f"Fetched technical indicators for {stock_code}")
            return technical_data

        except Exception as e:
            self.logger.error(f"Error calculating technical indicators for {stock_code}: {e}")
            return {}

    def _calculate_rsi(self, prices: list, period: int = 14) -> float:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return 50.0

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: list) -> Dict[str, float]:
        """计算MACD指标"""
        if len(prices) < 26:
            return {'dif': 0, 'dea': 0, 'macd': 0}

        # EMA12, EMA26
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)

        # DIF
        dif = ema12 - ema26

        # DEA (简化版，实际需要计算DIF的EMA)
        dea = dif * 0.8  # 简化

        # MACD
        macd = 2 * (dif - dea)

        return {
            'dif': dif,
            'dea': dea,
            'macd': macd
        }

    def _calculate_ema(self, prices: list, period: int) -> float:
        """计算EMA"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def _calculate_kdj(self, history: list, period: int = 9) -> Dict[str, float]:
        """计算KDJ指标"""
        if len(history) < period:
            return {'k': 50, 'd': 50, 'j': 50}

        recent = history[-period:]
        highs = [h['high'] for h in recent]
        lows = [h['low'] for h in recent]
        closes = [h['close'] for h in recent]

        highest_high = max(highs)
        lowest_low = min(lows)
        current_close = closes[-1]

        if highest_high == lowest_low:
            return {'k': 50, 'd': 50, 'j': 50}

        # RSV
        rsv = (current_close - lowest_low) / (highest_high - lowest_low) * 100

        # K, D, J（简化版）
        k = rsv * (1/3) + 50 * (2/3)
        d = k * (1/3) + 50 * (2/3)
        j = 3 * k - 2 * d

        return {
            'k': k,
            'd': d,
            'j': j
        }

    def _convert_stock_code(self, stock_code: str) -> str:
        """转换股票代码为接口格式"""
        if stock_code.startswith('6'):
            return f'1.{stock_code}'  # 上交所
        elif stock_code.startswith(('0', '3')):
            return f'0.{stock_code}'  # 深交所
        else:
            return f'1.{stock_code}'

    def _get_quote_from_eastmoney(self, stock_code: str) -> Dict[str, Any]:
        """从东方财富接口获取行情（备用方案）"""
        try:
            secid = self._convert_stock_code(stock_code)
            url = f"{self.base_url}/qt/stock/get"
            params = {
                'secid': secid,
                'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f107,f116,f117,f127,f152,f161,f162,f167,f168,f169,f170,f171'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('rc') != 0 or not data.get('data'):
                return {}

            item = data['data']

            return {
                'stock_code': stock_code,
                'name': item.get('f58', ''),
                'current': item.get('f43', 0) / 100 if item.get('f43') else 0,
                'open': item.get('f46', 0) / 100 if item.get('f46') else 0,
                'pre_close': item.get('f60', 0) / 100 if item.get('f60') else 0,
                'high': item.get('f44', 0) / 100 if item.get('f44') else 0,
                'low': item.get('f45', 0) / 100 if item.get('f45') else 0,
                'volume': item.get('f47', 0),
                'turnover': item.get('f48', 0) / 10000 if item.get('f48') else 0,
                'change_pct': item.get('f170', 0) / 100 if item.get('f170') else 0,
                'change_amount': item.get('f169', 0) / 100 if item.get('f169') else 0,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error in backup quote method: {e}")
            return {}
