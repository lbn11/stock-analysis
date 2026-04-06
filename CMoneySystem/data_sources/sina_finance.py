"""新浪财经数据源"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
import json
import re
from data_sources import BaseDataSource


class SinaFinanceDataSource(BaseDataSource):
    """新浪财经数据源"""

    def __init__(self):
        super().__init__("SinaFinance")
        self.base_url = "http://hq.sinajs.cn"
        self.history_url = "https://quotes.sina.com.cn/js/jsonp.php"

    def _convert_stock_code(self, stock_code: str) -> str:
        """
        转换股票代码为新浪格式

        Args:
            stock_code: 6位股票代码

        Returns:
            新浪格式代码 (如 sh600000, sz000001)
        """
        if stock_code.startswith('6'):
            return f'sh{stock_code}'
        elif stock_code.startswith(('0', '3')):
            return f'sz{stock_code}'
        else:
            return f'sh{stock_code}'

    def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票实时行情

        Args:
            stock_code: 股票代码

        Returns:
            行情数据字典
        """
        self._rate_limit()

        try:
            sina_code = self._convert_stock_code(stock_code)
            url = f"{self.base_url}/list={sina_code}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 解析返回数据
            content = response.text
            if not content or 'var hq_str_' not in content:
                self.logger.warning(f"No data returned for {stock_code}")
                return {}

            # 提取数据部分
            data_str = content.split('"')[1]
            data_parts = data_str.split(',')

            if len(data_parts) < 32:
                self.logger.warning(f"Invalid data format for {stock_code}")
                return {}

            # 解析字段
            quote_data = {
                'stock_code': stock_code,
                'name': data_parts[0],
                'open': float(data_parts[1]) if data_parts[1] else 0,
                'pre_close': float(data_parts[2]) if data_parts[2] else 0,
                'current': float(data_parts[3]) if data_parts[3] else 0,
                'high': float(data_parts[4]) if data_parts[4] else 0,
                'low': float(data_parts[5]) if data_parts[5] else 0,
                'bid': float(data_parts[6]) if data_parts[6] else 0,
                'ask': float(data_parts[7]) if data_parts[7] else 0,
                'volume': int(float(data_parts[8])) if data_parts[8] else 0,  # 成交量（股）
                'turnover': float(data_parts[9]) if data_parts[9] else 0,  # 成交额（元）
                'date': data_parts[30],
                'time': data_parts[31],
                'timestamp': datetime.now().isoformat(),
                'source': self.name
            }

            # 计算涨跌幅
            if quote_data['pre_close'] > 0:
                quote_data['change_amount'] = quote_data['current'] - quote_data['pre_close']
                quote_data['change_pct'] = quote_data['change_amount'] / quote_data['pre_close']
            else:
                quote_data['change_amount'] = 0
                quote_data['change_pct'] = 0

            self.logger.info(f"Fetched quote for {stock_code}: {quote_data['name']}, price={quote_data['current']}")
            return quote_data

        except requests.RequestException as e:
            self.logger.error(f"Request error for {stock_code}: {e}")
            return {}
        except (ValueError, IndexError) as e:
            self.logger.error(f"Parse error for {stock_code}: {e}")
            return {}

    def get_stock_history(self, stock_code: str, start_date: str = None,
                          end_date: str = None, period: str = 'daily') -> List[Dict[str, Any]]:
        """
        获取股票历史数据

        注意：新浪财经的历史数据接口比较复杂，这里提供简化实现
        建议使用AkShare或Tushare获取历史数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            period: 周期 (daily/weekly/monthly)

        Returns:
            历史数据列表
        """
        self.logger.warning("SinaFinance history data API is limited, recommend using AkShare instead")

        # 新浪历史数据接口较复杂，这里返回空列表
        # 实际应用中建议使用AkShare或其他专业数据源
        return []

    def get_financial_report(self, stock_code: str, report_type: str = 'annual') -> Dict[str, Any]:
        """
        获取财务报告

        新浪财经的财报数据需要复杂的解析，建议使用专业数据源

        Args:
            stock_code: 股票代码
            report_type: 报告类型

        Returns:
            财报数据
        """
        self.logger.warning("SinaFinance financial report API is not implemented, use AkShare instead")
        return {}

    def get_real_time_data_batch(self, stock_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        批量获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            股票代码到行情数据的映射
        """
        self._rate_limit()

        try:
            # 转换所有股票代码
            sina_codes = [self._convert_stock_code(code) for code in stock_codes]
            codes_str = ','.join(sina_codes)

            url = f"{self.base_url}/list={codes_str}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            # 解析批量数据
            result = {}
            lines = response.text.strip().split('\n')

            for i, line in enumerate(lines):
                if i < len(stock_codes):
                    stock_code = stock_codes[i]
                    try:
                        data_str = line.split('"')[1]
                        data_parts = data_str.split(',')

                        if len(data_parts) >= 32:
                            quote_data = {
                                'stock_code': stock_code,
                                'name': data_parts[0],
                                'current': float(data_parts[3]) if data_parts[3] else 0,
                                'high': float(data_parts[4]) if data_parts[4] else 0,
                                'low': float(data_parts[5]) if data_parts[5] else 0,
                                'volume': int(float(data_parts[8])) if data_parts[8] else 0,
                                'source': self.name
                            }
                            result[stock_code] = quote_data
                    except (IndexError, ValueError) as e:
                        self.logger.warning(f"Failed to parse data for {stock_code}: {e}")
                        continue

            self.logger.info(f"Fetched batch quotes for {len(result)} stocks")
            return result

        except Exception as e:
            self.logger.error(f"Batch quote error: {e}")
            return {}
