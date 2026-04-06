"""数据源基类和管理器"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import time


class BaseDataSource(ABC):
    """数据源抽象基类"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"DataSource.{name}")
        self._request_count = 0
        self._last_request_time = None
        self.rate_limit_delay = 0.5  # 请求间隔（秒）

    def _rate_limit(self):
        """速率限制"""
        if self._last_request_time:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)

        self._last_request_time = time.time()
        self._request_count += 1

    @abstractmethod
    def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """获取股票实时行情"""
        pass

    @abstractmethod
    def get_stock_history(self, stock_code: str, start_date: str = None,
                          end_date: str = None, period: str = 'daily') -> List[Dict[str, Any]]:
        """获取股票历史数据"""
        pass

    @abstractmethod
    def get_financial_report(self, stock_code: str, report_type: str = 'annual') -> Dict[str, Any]:
        """获取财务报告"""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """获取数据源统计信息"""
        return {
            'name': self.name,
            'request_count': self._request_count,
            'last_request_time': self._last_request_time
        }


class DataSourceManager:
    """数据源管理器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._sources: Dict[str, BaseDataSource] = {}
        self._priority_order: List[str] = []

    def register_source(self, source: BaseDataSource, priority: int = 0):
        """
        注册数据源

        Args:
            source: 数据源实例
            priority: 优先级（数字越小优先级越高）
        """
        self._sources[source.name] = source

        # 按优先级排序
        self._priority_order.append((priority, source.name))
        self._priority_order.sort()

        self.logger.info(f"Registered data source: {source.name} (priority: {priority})")

    def get_source(self, name: str) -> Optional[BaseDataSource]:
        """获取指定数据源"""
        return self._sources.get(name)

    def get_stock_quote(self, stock_code: str, preferred_source: str = None) -> Optional[Dict[str, Any]]:
        """
        获取股票行情（支持多数据源fallback）

        Args:
            stock_code: 股票代码
            preferred_source: 首选数据源名称

        Returns:
            行情数据
        """
        sources_to_try = []

        # 如果指定了首选数据源，先尝试
        if preferred_source and preferred_source in self._sources:
            sources_to_try.append(preferred_source)

        # 按优先级添加其他数据源
        for _, source_name in self._priority_order:
            if source_name not in sources_to_try:
                sources_to_try.append(source_name)

        # 依次尝试各数据源
        for source_name in sources_to_try:
            try:
                source = self._sources[source_name]
                data = source.get_stock_quote(stock_code)
                if data:
                    self.logger.info(f"Successfully fetched quote from {source_name}")
                    return data
            except Exception as e:
                self.logger.warning(f"Failed to fetch from {source_name}: {e}")
                continue

        self.logger.error(f"Failed to fetch quote for {stock_code} from all sources")
        return None

    def get_stock_history(self, stock_code: str, start_date: str = None,
                         end_date: str = None, period: str = 'daily',
                         preferred_source: str = None) -> List[Dict[str, Any]]:
        """
        获取股票历史数据（支持多数据源fallback）

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期 (daily/weekly/monthly)
            preferred_source: 首选数据源

        Returns:
            历史数据列表
        """
        sources_to_try = []

        if preferred_source and preferred_source in self._sources:
            sources_to_try.append(preferred_source)

        for _, source_name in self._priority_order:
            if source_name not in sources_to_try:
                sources_to_try.append(source_name)

        for source_name in sources_to_try:
            try:
                source = self._sources[source_name]
                data = source.get_stock_history(stock_code, start_date, end_date, period)
                if data and len(data) > 0:
                    self.logger.info(f"Successfully fetched history from {source_name}, {len(data)} records")
                    return data
            except Exception as e:
                self.logger.warning(f"Failed to fetch history from {source_name}: {e}")
                continue

        self.logger.error(f"Failed to fetch history for {stock_code} from all sources")
        return []

    def get_financial_report(self, stock_code: str, report_type: str = 'annual',
                            preferred_source: str = None) -> Optional[Dict[str, Any]]:
        """
        获取财务报告

        Args:
            stock_code: 股票代码
            report_type: 报告类型 (annual/quarterly)
            preferred_source: 首选数据源

        Returns:
            财报数据
        """
        sources_to_try = []

        if preferred_source and preferred_source in self._sources:
            sources_to_try.append(preferred_source)

        for _, source_name in self._priority_order:
            if source_name not in sources_to_try:
                sources_to_try.append(source_name)

        for source_name in sources_to_try:
            try:
                source = self._sources[source_name]
                data = source.get_financial_report(stock_code, report_type)
                if data:
                    self.logger.info(f"Successfully fetched financial report from {source_name}")
                    return data
            except Exception as e:
                self.logger.warning(f"Failed to fetch financial report from {source_name}: {e}")
                continue

        self.logger.error(f"Failed to fetch financial report for {stock_code} from all sources")
        return None

    def get_all_stats(self) -> Dict[str, Dict]:
        """获取所有数据源的统计信息"""
        return {name: source.get_stats() for name, source in self._sources.items()}


# 全局数据源管理器实例
data_source_manager = DataSourceManager()


# 自动注册所有数据源
def register_all_sources():
    """注册所有可用的数据源"""
    try:
        from data_sources.akshare_source import AkShareDataSource
        data_source_manager.register_source(AkShareDataSource(), priority=1)
    except ImportError:
        pass

    try:
        from data_sources.sina_finance import SinaFinanceDataSource
        data_source_manager.register_source(SinaFinanceDataSource(), priority=2)
    except ImportError:
        pass

    try:
        from data_sources.eastmoney import EastMoneyDataSource
        data_source_manager.register_source(EastMoneyDataSource(), priority=3)
    except ImportError:
        pass

    try:
        from data_sources.ths import TonghuashunDataSource
        data_source_manager.register_source(TonghuashunDataSource(), priority=4)
    except ImportError:
        pass


# 自动注册
register_all_sources()
