"""数据处理器"""
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
import numpy as np


class DataProcessor:
    """数据处理类"""

    def __init__(self):
        pass

    def clean_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """清理原始数据"""
        # 去除重复项
        # 处理缺失值
        # 标准化数据格式
        cleaned_data = raw_data.copy()

        # 如果有历史数据，清理异常值
        if 'historical' in cleaned_data and cleaned_data['historical']:
            df = pd.DataFrame(cleaned_data['historical'])
            # 移除价格为0或负数的异常值
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df = df[df[col] > 0]

            cleaned_data['historical'] = df.to_dict('records')

        return cleaned_data

    def normalize_data(self, data: Dict[str, Any], method: str = 'min_max') -> Dict[str, Any]:
        """标准化数据"""
        normalized_data = data.copy()

        # 实现最小-最大标准化或z-score标准化
        if method == 'min_max':
            # 最小-最大标准化
            pass
        elif method == 'z_score':
            # z-score标准化
            pass

        return normalized_data

    def aggregate_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合多个数据源的数据"""
        if not data_list:
            return {}

        # 合并多个数据源
        aggregated = {}
        for data in data_list:
            aggregated.update(data)

        return aggregated

    def extract_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """从原始数据中提取特征"""
        features = {}

        # 从价格数据中提取技术指标
        if 'historical' in data and data['historical']:
            df = pd.DataFrame(data['historical'])
            if len(df) >= 2:
                # 计算简单移动平均
                if 'close' in df.columns:
                    df['sma_5'] = df['close'].rolling(window=5).mean()
                    df['sma_20'] = df['close'].rolling(window=20).mean()

                    # 计算价格变化率
                    df['change_pct'] = df['close'].pct_change()

                    # 添加到特征中
                    features['sma_5_latest'] = df['sma_5'].iloc[-1] if not pd.isna(df['sma_5'].iloc[-1]) else 0
                    features['sma_20_latest'] = df['sma_20'].iloc[-1] if not pd.isna(df['sma_20'].iloc[-1]) else 0
                    features['change_pct_latest'] = df['change_pct'].iloc[-1] if not pd.isna(df['change_pct'].iloc[-1]) else 0

        return features