"""辅助函数"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging
from utils.constants import STOCK_CODE_PATTERN


def validate_stock_code(stock_code: str) -> bool:
    """
    验证股票代码格式

    Args:
        stock_code: 股票代码

    Returns:
        bool: 验证结果
    """
    return bool(re.match(STOCK_CODE_PATTERN, stock_code))


def normalize_text(text: str) -> str:
    """
    标准化文本

    Args:
        text: 原始文本

    Returns:
        str: 标准化后的文本
    """
    if not text:
        return ""

    # 去除多余空白字符
    text = re.sub(r'\s+', ' ', text.strip())

    return text


def calculate_time_weight(base_date: datetime, current_date: datetime, decay_rate: float = 0.1) -> float:
    """
    计算时间权重（越近的信息权重越高）

    Args:
        base_date: 基准日期
        current_date: 当前日期
        decay_rate: 衰减率

    Returns:
        float: 时间权重
    """
    days_diff = abs((current_date - base_date).days)
    weight = max(0.1, 1.0 - decay_rate * days_diff / 30)  # 每30天衰减一次
    return weight


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    格式化百分比

    Args:
        value: 数值
        decimal_places: 小数位数

    Returns:
        str: 格式化后的百分比字符串
    """
    return f"{round(value * 100, decimal_places)}%"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    安全的JSON解析

    Args:
        json_str: JSON字符串
        default: 默认值

    Returns:
        Any: 解析后的对象
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 记录器名称
        log_file: 日志文件路径
        level: 日志级别

    Returns:
        logging.Logger: 配置好的记录器
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def merge_dicts(dict1: Dict, dict2: Dict, priority: str = 'dict2') -> Dict:
    """
    合并字典

    Args:
        dict1: 第一个字典
        dict2: 第二个字典
        priority: 冲突时优先级 ('dict1' 或 'dict2')

    Returns:
        Dict: 合并后的字典
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result:
            if priority == 'dict2':
                result[key] = value
        else:
            result[key] = value

    return result