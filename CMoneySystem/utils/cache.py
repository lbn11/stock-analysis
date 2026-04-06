"""缓存和性能优化模块

提供内存缓存、Redis缓存等功能，提升系统性能
"""
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import logging
import hashlib
import json
import threading
import time


class CacheEntry:
    """缓存条目"""

    def __init__(self, key: str, value: Any, ttl: int = 3600):
        """
        初始化缓存条目

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.hits = 0
        self.last_access = self.created_at

    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.created_at > self.ttl

    def touch(self):
        """更新访问时间"""
        self.last_access = time.time()
        self.hits += 1


class MemoryCache:
    """内存缓存"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化内存缓存

        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认生存时间（秒）
        """
        self.logger = logging.getLogger("MemoryCache")
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在或已过期返回None
        """
        with self.lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]

            # 检查是否过期
            if entry.is_expired():
                del self.cache[key]
                self.logger.debug(f"Cache entry expired: {key}")
                return None

            # 更新访问信息
            entry.touch()

            return entry.value

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），None表示使用默认值

        Returns:
            是否成功
        """
        with self.lock:
            # 如果缓存已满，删除最旧的条目
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_oldest()

            ttl = ttl or self.default_ttl
            self.cache[key] = CacheEntry(key, value, ttl)

            return True

    def delete(self, key: str) -> bool:
        """
        删除缓存值

        Args:
            key: 缓存键

        Returns:
            是否成功
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        清理过期缓存

        Returns:
            清理的条目数
        """
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self.cache[key]

            if expired_keys:
                self.logger.info(f"Cleaned up {len(expired_keys)} expired entries")

            return len(expired_keys)

    def _evict_oldest(self):
        """淘汰最旧的缓存条目"""
        if not self.cache:
            return

        # 找到最旧的条目
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_access
        )

        del self.cache[oldest_key]
        self.logger.debug(f"Evicted oldest cache entry: {oldest_key}")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            total_hits = sum(entry.hits for entry in self.cache.values())

            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'total_hits': total_hits,
                'default_ttl': self.default_ttl
            }


class CacheDecorator:
    """缓存装饰器

    用于装饰函数，自动缓存函数结果
    """

    def __init__(self, cache: MemoryCache, ttl: int = 3600,
                 key_prefix: str = None):
        """
        初始化缓存装饰器

        Args:
            cache: 缓存实例
            ttl: 生存时间
            key_prefix: 键前缀
        """
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix or 'func'

    def __call__(self, func: Callable) -> Callable:
        """装饰器"""

        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = self._generate_cache_key(func, args, kwargs)

            # 尝试从缓存获取
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            self.cache.set(cache_key, result, self.ttl)

            return result

        return wrapper

    def _generate_cache_key(self, func: Callable, args: tuple,
                           kwargs: dict) -> str:
        """生成缓存键"""
        # 组合函数名和参数
        key_parts = [
            self.key_prefix,
            func.__name__,
            str(args),
            str(sorted(kwargs.items()))
        ]

        key_string = ':'.join(key_parts)

        # 使用哈希避免键过长
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"{self.key_prefix}:{func.__name__}:{key_hash}"


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.logger = logging.getLogger("PerformanceMonitor")
        self.metrics: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def record_execution(self, func_name: str, execution_time: float,
                       success: bool = True):
        """
        记录函数执行情况

        Args:
            func_name: 函数名
            execution_time: 执行时间（秒）
            success: 是否成功
        """
        with self.lock:
            if func_name not in self.metrics:
                self.metrics[func_name] = {
                    'count': 0,
                    'total_time': 0.0,
                    'success_count': 0,
                    'failure_count': 0,
                    'min_time': float('inf'),
                    'max_time': 0.0
                }

            metrics = self.metrics[func_name]
            metrics['count'] += 1
            metrics['total_time'] += execution_time

            if success:
                metrics['success_count'] += 1
            else:
                metrics['failure_count'] += 1

            metrics['min_time'] = min(metrics['min_time'], execution_time)
            metrics['max_time'] = max(metrics['max_time'], execution_time)

    def get_metrics(self, func_name: str = None) -> Dict[str, Dict]:
        """
        获取性能指标

        Args:
            func_name: 函数名，None表示获取所有

        Returns:
            性能指标字典
        """
        with self.lock:
            if func_name:
                return {func_name: self.metrics.get(func_name, {})}

            # 计算平均时间
            result = {}
            for name, metrics in self.metrics.items():
                if metrics['count'] > 0:
                    result[name] = {
                        **metrics,
                        'avg_time': metrics['total_time'] / metrics['count']
                    }

            return result

    def reset_metrics(self, func_name: str = None):
        """重置性能指标"""
        with self.lock:
            if func_name:
                if func_name in self.metrics:
                    del self.metrics[func_name]
            else:
                self.metrics.clear()

            self.logger.info(f"Performance metrics reset: {func_name or 'all'}")


def performance_monitor(monitor: PerformanceMonitor = None):
    """
    装饰器：监控函数性能

    Args:
        monitor: 性能监控器实例
    """
    if monitor is None:
        monitor = PerformanceMonitor()

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False

            try:
                result = func(*args, **kwargs)
                success = True
                return result

            except Exception as e:
                monitor.logger.error(f"Error in {func.__name__}: {e}")
                raise

            finally:
                execution_time = time.time() - start_time
                monitor.record_execution(func.__name__, execution_time, success)

        return wrapper

    return decorator


# 全局缓存实例
global_cache = MemoryCache(max_size=1000, default_ttl=3600)

# 全局性能监控器
global_monitor = PerformanceMonitor()


def cached(ttl: int = 3600, key_prefix: str = None):
    """
    缓存装饰器（便捷函数）

    Args:
        ttl: 生存时间
        key_prefix: 键前缀
    """
    return CacheDecorator(global_cache, ttl, key_prefix)


def monitor_performance(func: Callable = None):
    """
    性能监控装饰器（便捷函数）
    """
    def decorator(f: Callable) -> Callable:
        return performance_monitor(global_monitor)(f)

    if func is None:
        return decorator
    else:
        return decorator(func)
