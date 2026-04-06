"""AkShare数据源

AkShare是一个免费开源的金融数据接口库
提供股票、期货、基金、宏观经济等多种数据
GitHub: https://github.com/akfamily/akshare
文档: https://akshare.akfamily.xyz/

安装: pip install akshare
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from data_sources import BaseDataSource

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    logging.warning("AkShare not installed. Install with: pip install akshare")


class AkShareDataSource(BaseDataSource):
    """AkShare数据源"""

    def __init__(self):
        super().__init__("AkShare")

        if not AKSHARE_AVAILABLE:
            self.logger.error("AkShare is not available. Please install: pip install akshare")

    def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票实时行情

        Args:
            stock_code: 股票代码

        Returns:
            行情数据字典
        """
        if not AKSHARE_AVAILABLE:
            return {}

        self._rate_limit()

        try:
            # 使用AkShare获取实时行情
            df = ak.stock_zh_a_spot_em()

            # 查找对应股票
            stock_data = df[df['代码'] == stock_code]

            if stock_data.empty:
                self.logger.warning(f"Stock {stock_code} not found")
                return {}

            row = stock_data.iloc[0]

            quote_data = {
                'stock_code': stock_code,
                'name': row['名称'],
                'current': float(row['最新价']),
                'open': float(row['今开']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'pre_close': float(row['昨收']),
                'volume': int(row['成交量']),
                'turnover': float(row['成交额']),
                'change_pct': float(row['涨跌幅']) / 100,  # 转换为小数
                'change_amount': float(row['涨跌额']),
                'amplitude': float(row['振幅']) / 100 if '振幅' in row else 0,
                'turnover_rate': float(row['换手率']) / 100 if '换手率' in row else 0,
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
        if not AKSHARE_AVAILABLE:
            return []

        self._rate_limit()

        try:
            # 设置默认日期
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            else:
                end_date = end_date.replace('-', '')

            if not start_date:
                # 默认获取最近1年的数据
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            else:
                start_date = start_date.replace('-', '')

            # 根据周期选择接口
            if period == 'daily':
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                       start_date=start_date, end_date=end_date,
                                       adjust="qfq")  # 前复权
            elif period == 'weekly':
                df = ak.stock_zh_a_hist(symbol=stock_code, period="weekly",
                                       start_date=start_date, end_date=end_date,
                                       adjust="qfq")
            elif period == 'monthly':
                df = ak.stock_zh_a_hist(symbol=stock_code, period="monthly",
                                       start_date=start_date, end_date=end_date,
                                       adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                       start_date=start_date, end_date=end_date,
                                       adjust="qfq")

            if df.empty:
                self.logger.warning(f"No history data for {stock_code}")
                return []

            # 转换为字典列表
            history_data = []
            for _, row in df.iterrows():
                data_point = {
                    'date': row['日期'].strftime('%Y-%m-%d') if hasattr(row['日期'], 'strftime') else str(row['日期']),
                    'open': float(row['开盘']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'close': float(row['收盘']),
                    'volume': int(row['成交量']),
                    'turnover': float(row['成交额']),
                    'amplitude': float(row['振幅']) / 100 if '振幅' in row else 0,
                    'change_pct': float(row['涨跌幅']) / 100 if '涨跌幅' in row else 0,
                    'change_amount': float(row['涨跌额']) if '涨跌额' in row else 0,
                    'turnover_rate': float(row['换手率']) / 100 if '换手率' in row else 0
                }
                history_data.append(data_point)

            self.logger.info(f"Fetched {len(history_data)} history records for {stock_code}")
            return history_data

        except Exception as e:
            self.logger.error(f"Error fetching history for {stock_code}: {e}")
            return []

    def get_financial_report(self, stock_code: str, report_type: str = 'annual') -> Dict[str, Any]:
        """
        获取财务报告

        Args:
            stock_code: 股票代码
            report_type: 报告类型 (annual/quarterly)

        Returns:
            财报数据
        """
        if not AKSHARE_AVAILABLE:
            return {}

        self._rate_limit()

        try:
            # 获取最新财报数据
            # 利润表
            df_profit = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")

            if df_profit.empty:
                self.logger.warning(f"No financial report for {stock_code}")
                return {}

            # 获取最新一期数据
            latest = df_profit.iloc[:, 0:2]  # 获取第一列（指标名）和第二列（最新数据）

            financial_data = {
                'stock_code': stock_code,
                'report_type': report_type,
                'report_period': df_profit.columns[1] if len(df_profit.columns) > 1 else 'Unknown',
                'timestamp': datetime.now().isoformat(),
                'source': self.name
            }

            # 提取关键指标
            try:
                for _, row in latest.iterrows():
                    indicator = row.iloc[0]
                    value_str = str(row.iloc[1])

                    # 清理数值（去除逗号等）
                    value_str = value_str.replace(',', '')

                    try:
                        value = float(value_str)
                    except ValueError:
                        continue

                    # 映射关键指标
                    if '营业总收入' in indicator or '营业收入' in indicator:
                        financial_data['revenue'] = value
                    elif '净利润' in indicator and '归属' in indicator:
                        financial_data['net_profit'] = value
                    elif '毛利润' in indicator or '毛利' in indicator:
                        financial_data['gross_profit'] = value
                    elif '经营活动产生的现金流量净额' in indicator:
                        financial_data['operating_cash_flow'] = value

            except Exception as e:
                self.logger.warning(f"Error parsing financial indicators: {e}")

            self.logger.info(f"Fetched financial report for {stock_code}")
            return financial_data

        except Exception as e:
            self.logger.error(f"Error fetching financial report for {stock_code}: {e}")
            return {}

    def get_macro_data(self) -> Dict[str, Any]:
        """
        获取宏观经济数据

        Returns:
            宏观数据字典
        """
        if not AKSHARE_AVAILABLE:
            return {}

        self._rate_limit()

        try:
            macro_data = {
                'timestamp': datetime.now().isoformat(),
                'source': self.name
            }

            # 获取GDP数据
            try:
                df_gdp = ak.macro_china_gdp()
                if not df_gdp.empty:
                    latest_gdp = df_gdp.iloc[-1]
                    macro_data['gdp'] = {
                        'period': latest_gdp['季度'],
                        'value': float(latest_gdp['国内生产总值-绝对值']),
                        'growth_rate': float(latest_gdp['国内生产总值-同比增长'])
                    }
            except Exception as e:
                self.logger.warning(f"Error fetching GDP: {e}")

            # 获取CPI数据
            try:
                df_cpi = ak.macro_china_cpi_yearly()
                if not df_cpi.empty:
                    latest_cpi = df_cpi.iloc[-1]
                    macro_data['cpi'] = {
                        'period': latest_cpi['月份'],
                        'value': float(latest_cpi['全国-同比']),
                    }
            except Exception as e:
                self.logger.warning(f"Error fetching CPI: {e}")

            # 获取PMI数据
            try:
                df_pmi = ak.macro_china_pmi_yearly()
                if not df_pmi.empty:
                    latest_pmi = df_pmi.iloc[-1]
                    macro_data['pmi'] = {
                        'period': latest_pmi['月份'],
                        'manufacturing': float(latest_pmi['制造业-指数']),
                        'non_manufacturing': float(latest_pmi['非制造业-指数'])
                    }
            except Exception as e:
                self.logger.warning(f"Error fetching PMI: {e}")

            # 获取M2数据
            try:
                df_m2 = ak.macro_china_m2_yearly()
                if not df_m2.empty:
                    latest_m2 = df_m2.iloc[-1]
                    macro_data['m2'] = {
                        'period': latest_m2['月份'],
                        'growth_rate': float(latest_m2['货币和准货币(M2)-同比增长'])
                    }
            except Exception as e:
                self.logger.warning(f"Error fetching M2: {e}")

            self.logger.info("Fetched macro economic data")
            return macro_data

        except Exception as e:
            self.logger.error(f"Error fetching macro data: {e}")
            return {}

    def get_index_data(self, index_code: str = '000001') -> Dict[str, Any]:
        """
        获取指数数据

        Args:
            index_code: 指数代码 (000001=上证指数, 399001=深证成指, 399006=创业板指)

        Returns:
            指数数据
        """
        if not AKSHARE_AVAILABLE:
            return {}

        self._rate_limit()

        try:
            # 获取实时指数数据
            df = ak.stock_zh_index_spot_em()

            # 查找对应指数
            index_data = df[df['代码'] == index_code]

            if index_data.empty:
                self.logger.warning(f"Index {index_code} not found")
                return {}

            row = index_data.iloc[0]

            result = {
                'index_code': index_code,
                'name': row['名称'],
                'current': float(row['最新价']),
                'open': float(row['今开']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'pre_close': float(row['昨收']),
                'volume': int(row['成交量']),
                'turnover': float(row['成交额']),
                'change_pct': float(row['涨跌幅']) / 100,
                'change_amount': float(row['涨跌额']),
                'timestamp': datetime.now().isoformat(),
                'source': self.name
            }

            self.logger.info(f"Fetched index data for {index_code}: {result['name']}")
            return result

        except Exception as e:
            self.logger.error(f"Error fetching index data for {index_code}: {e}")
            return {}
