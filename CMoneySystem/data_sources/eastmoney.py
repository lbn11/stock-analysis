"""东方财富数据源

东方财富网提供丰富的股票、基金、期货等金融数据
官网: http://www.eastmoney.com/
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


class EastMoneyDataSource:
    """东方财富数据源"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.name = "EastMoney"
        self.base_url = "http://push2.eastmoney.com/api"
        self.web_url = "http://data.eastmoney.com"

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://www.eastmoney.com/'
        }

    def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票实时行情

        Args:
            stock_code: 股票代码

        Returns:
            行情数据字典
        """
        if not REQUESTS_AVAILABLE:
            return {}

        try:
            # 转换为东方财富的格式
            secid = self._convert_stock_code(stock_code)

            # 实时行情接口
            url = f"{self.base_url}/qt/stock/get"
            params = {
                'secid': secid,
                'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f107,f116,f117,f127,f152,f161,f162,f167,f168,f169,f170,f171,f84,f85,f115'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('rc') != 0 or not data.get('data'):
                self.logger.warning(f"No data for {stock_code}")
                return {}

            item = data['data']

            # 解析字段（东方财富的字段编码）
            quote_data = {
                'stock_code': stock_code,
                'name': item.get('f58', ''),
                'current': item.get('f43', 0) / 100 if item.get('f43') else 0,  # 最新价
                'open': item.get('f46', 0) / 100 if item.get('f46') else 0,  # 今开
                'pre_close': item.get('f60', 0) / 100 if item.get('f60') else 0,  # 昨收
                'high': item.get('f44', 0) / 100 if item.get('f44') else 0,  # 最高
                'low': item.get('f45', 0) / 100 if item.get('f45') else 0,  # 最低
                'volume': item.get('f47', 0),  # 成交量（手）
                'turnover': item.get('f48', 0) / 10000 if item.get('f48') else 0,  # 成交额（元）
                'amplitude': item.get('f49', 0) / 100 if item.get('f49') else 0,  # 振幅
                'change_pct': item.get('f170', 0) / 100 if item.get('f170') else 0,  # 涨跌幅
                'change_amount': item.get('f169', 0) / 100 if item.get('f169') else 0,  # 涨跌额
                'turnover_rate': item.get('f168', 0) / 100 if item.get('f168') else 0,  # 换手率
                'pe_ratio': item.get('f162', 0) / 100 if item.get('f162') else 0,  # 市盈率
                'pb_ratio': item.get('f167', 0) / 100 if item.get('f167') else 0,  # 市净率
                'total_market_cap': item.get('f116', 0) / 100000000 if item.get('f116') else 0,  # 总市值（亿）
                'circulating_market_cap': item.get('f117', 0) / 100000000 if item.get('f117') else 0,  # 流通市值（亿）
                'timestamp': datetime.now().isoformat(),
                'source': self.name
            }

            self.logger.info(f"Fetched quote for {stock_code}: {quote_data['name']}, price={quote_data['current']}")
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
        if not REQUESTS_AVAILABLE or not PANDAS_AVAILABLE:
            return []

        try:
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

            # 历史K线接口
            url = f"{self.base_url}/qt/stock/kline"
            params = {
                'secid': secid,
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': klt,
                'fqt': '1',  # 1=前复权
                'beg': start_date,
                'end': end_date,
                'lmt': '1000'  # 最多1000条
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

    def get_financial_report(self, stock_code: str, report_type: str = 'profit') -> Dict[str, Any]:
        """
        获取财务报告

        Args:
            stock_code: 股票代码
            report_type: 报告类型 (profit=利润表, balance=资产负债表, cash=现金流量表)

        Returns:
            财报数据
        """
        if not REQUESTS_AVAILABLE:
            return {}

        try:
            secid = self._convert_stock_code(stock_code)

            # 财报接口
            url = f"{self.web_url}/DataCenter_V3/jgdy/lsjz.ashx"

            # 报告类型映射
            report_type_map = {
                'profit': 'RPT_LICO_FN_CPD',
                'balance': 'RPTA_FN_BALASSETS',
                'cash': 'RPTA_FN_CASHFLOW'
            }

            report_tab = report_type_map.get(report_type, 'RPT_LICO_FN_CPD')

            params = {
                'pagesize': '50',
                'page': '1',
                'sortField': 'REPORT_DATE',
                'sortType': '-1',
                'filter': f'(SECURITY_CODE="{stock_code}")',
                'reportTab': report_tab
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data.get('data') or not data['data'].get('diff'):
                self.logger.warning(f"No financial report for {stock_code}")
                return {}

            # 获取最新一期数据
            latest = data['data']['diff'][0]

            financial_data = {
                'stock_code': stock_code,
                'report_type': report_type,
                'report_date': latest.get('REPORT_DATE', ''),
                'timestamp': datetime.now().isoformat(),
                'source': self.name
            }

            # 提取关键指标（根据报告类型）
            if report_type == 'profit':
                financial_data['revenue'] = self._safe_float(latest.get('TOTAL_OPERATE_INCOME'))  # 营业总收入
                financial_data['net_profit'] = self._safe_float(latest.get('PARENT_NETPROFIT'))  # 归属净利润
                financial_data['operating_profit'] = self._safe_float(latest.get('OPERATE_PROFIT'))  # 营业利润

            elif report_type == 'balance':
                financial_data['total_assets'] = self._safe_float(latest.get('TOTAL_ASSETS'))  # 总资产
                financial_data['total_liabilities'] = self._safe_float(latest.get('TOTAL_LIABILITIES'))  # 总负债
                financial_data['equity'] = self._safe_float(latest.get('TOTAL_EQUITY'))  # 股东权益

            elif report_type == 'cash':
                financial_data['operating_cash_flow'] = self._safe_float(latest.get(' OperateCashFlow'))  # 经营现金流

            self.logger.info(f"Fetched financial report for {stock_code}")
            return financial_data

        except Exception as e:
            self.logger.error(f"Error fetching financial report for {stock_code}: {e}")
            return {}

    def get_real_time_quotes_batch(self, stock_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        批量获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            股票代码到行情数据的映射
        """
        if not REQUESTS_AVAILABLE:
            return {}

        try:
            # 批量行情接口
            secids = [self._convert_stock_code(code) for code in stock_codes]
            secid_str = ','.join(secids)

            url = f"{self.base_url}/qt/ulist.np/get"
            params = {
                'fltt': 2,
                'invt': 2,
                'secids': secid_str,
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f31,f32,f28,f29,f30,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f84,f85,f115,f116,f117,f127,f152,f161,f162,f167,f168,f169,f170,f171,f84,f85,f115'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()

            data = response.json()

            if data.get('rc') != 0 or not data.get('data'):
                self.logger.warning("No batch data returned")
                return {}

            result = {}
            for item in data['data']['diff']:
                stock_code = item.get('f12', '')
                quote_data = {
                    'stock_code': stock_code,
                    'name': item.get('f14', ''),
                    'current': item.get('f2', 0),  # 最新价
                    'pre_close': item.get('f18', 0),  # 昨收
                    'open': item.get('f17', 0),  # 今开
                    'high': item.get('f15', 0),  # 最高
                    'low': item.get('f16', 0),  # 最低
                    'volume': item.get('f5', 0),  # 成交量
                    'turnover': item.get('f6', 0),  # 成交额
                    'change_pct': item.get('f170', 0),  # 涨跌幅
                    'change_amount': item.get('f169', 0),  # 涨跌额
                    'timestamp': datetime.now().isoformat(),
                    'source': self.name
                }
                result[stock_code] = quote_data

            self.logger.info(f"Fetched batch quotes for {len(result)} stocks")
            return result

        except Exception as e:
            self.logger.error(f"Error in batch quotes: {e}")
            return {}

    def get_stock_list(self, market: str = 'all') -> List[Dict[str, Any]]:
        """
        获取股票列表

        Args:
            market: 市场类型 (sh=上交所, sz=深交所, all=全部)

        Returns:
            股票列表
        """
        if not REQUESTS_AVAILABLE:
            return []

        try:
            # A股列表接口
            url = f"{self.base_url}/qt/clist/get"
            params = {
                'pn': '1',
                'pz': '5000',
                'po': '1',
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'fid': 'f62',
                'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23' if market == 'all' else f'm:0+t:{market}',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('rc') != 0 or not data.get('data'):
                return []

            result = []
            for item in data['data']['diff']:
                result.append({
                    'stock_code': item.get('f12', ''),
                    'name': item.get('f14', ''),
                    'market': item.get('f13', ''),
                    'industry': item.get('f62', ''),
                    'timestamp': datetime.now().isoformat()
                })

            self.logger.info(f"Fetched {len(result)} stocks")
            return result

        except Exception as e:
            self.logger.error(f"Error fetching stock list: {e}")
            return []

    def _convert_stock_code(self, stock_code: str) -> str:
        """
        转换股票代码为东方财富格式

        Args:
            stock_code: 6位股票代码

        Returns:
            东方财富格式代码 (如 0.000001, 1.600000)
        """
        if stock_code.startswith('6'):
            return f'1.{stock_code}'  # 上交所
        elif stock_code.startswith(('0', '3')):
            return f'0.{stock_code}'  # 深交所
        else:
            return f'1.{stock_code}'

    def _safe_float(self, value: Any) -> float:
        """安全转换为浮点数"""
        if value is None or value == '-':
            return 0.0
        try:
            return float(str(value).replace(',', ''))
        except (ValueError, AttributeError):
            return 0.0
