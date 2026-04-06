"""机器学习模型基类"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import pandas as pd
from datetime import datetime
import logging
import pickle
import os


class BaseMLModel(ABC):
    """机器学习模型抽象基类"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.logger = logging.getLogger(f"MLModel.{model_name}")
        self.model = None
        self.is_trained = False
        self.metrics = {}

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        训练模型

        Args:
            X: 特征数据
            y: 标签数据
            validation_split: 验证集比例

        Returns:
            训练结果字典
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测

        Args:
            X: 特征数据

        Returns:
            预测结果
        """
        pass

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        评估模型

        Args:
            X: 特征数据
            y: 真实标签

        Returns:
            评估指标字典
        """
        if not self.is_trained:
            self.logger.warning("Model not trained yet")
            return {}

        try:
            predictions = self.predict(X)

            # 计算评估指标
            mse = np.mean((predictions - y) ** 2)
            mae = np.mean(np.abs(predictions - y))
            rmse = np.sqrt(mse)

            # 计算方向准确率（预测涨跌方向）
            if len(predictions) > 1:
                pred_direction = np.sign(np.diff(predictions))
                true_direction = np.sign(np.diff(y))
                direction_accuracy = np.mean(pred_direction == true_direction)
            else:
                direction_accuracy = 0

            metrics = {
                'mse': float(mse),
                'mae': float(mae),
                'rmse': float(rmse),
                'direction_accuracy': float(direction_accuracy)
            }

            self.metrics = metrics
            return metrics

        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {}

    def save(self, filepath: str):
        """
        保存模型

        Args:
            filepath: 保存路径
        """
        if not self.is_trained:
            self.logger.warning("Cannot save untrained model")
            return

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # 保存模型和元数据
            save_data = {
                'model': self.model,
                'model_name': self.model_name,
                'is_trained': self.is_trained,
                'metrics': self.metrics,
                'timestamp': datetime.now().isoformat()
            }

            with open(filepath, 'wb') as f:
                pickle.dump(save_data, f)

            self.logger.info(f"Model saved to {filepath}")

        except Exception as e:
            self.logger.error(f"Error saving model: {e}")

    def load(self, filepath: str):
        """
        加载模型

        Args:
            filepath: 模型文件路径
        """
        try:
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)

            self.model = save_data['model']
            self.model_name = save_data.get('model_name', self.model_name)
            self.is_trained = save_data.get('is_trained', False)
            self.metrics = save_data.get('metrics', {})

            self.logger.info(f"Model loaded from {filepath}")

        except Exception as e:
            self.logger.error(f"Error loading model: {e}")


class FeatureEngineering:
    """特征工程工具类"""

    @staticmethod
    def create_time_series_features(data: pd.DataFrame, target_col: str = 'close',
                                   lookback: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """
        创建时间序列特征

        Args:
            data: 原始数据DataFrame
            target_col: 目标列名
            lookback: 回看窗口大小

        Returns:
            (X, y) 特征和标签数组
        """
        if target_col not in data.columns:
            raise ValueError(f"Target column {target_col} not found")

        prices = data[target_col].values

        X, y = [], []
        for i in range(lookback, len(prices)):
            X.append(prices[i-lookback:i])
            y.append(prices[i])

        return np.array(X), np.array(y)

    @staticmethod
    def create_technical_features(data: pd.DataFrame) -> pd.DataFrame:
        """
        创建技术指标特征

        Args:
            data: 包含OHLCV的DataFrame

        Returns:
            添加了技术指标的DataFrame
        """
        df = data.copy()

        # 移动平均
        for window in [5, 10, 20, 60]:
            df[f'ma_{window}'] = df['close'].rolling(window=window).mean()

        # 价格变化率
        df['returns'] = df['close'].pct_change()

        # 波动率
        df['volatility_20'] = df['returns'].rolling(window=20).std()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

        # 布林带
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)

        # 成交量特征
        if 'volume' in df.columns:
            df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma_5']

        return df

    @staticmethod
    def normalize_features(X: np.ndarray, method: str = 'minmax') -> np.ndarray:
        """
        特征归一化

        Args:
            X: 特征数组
            method: 归一化方法 (minmax/zscore)

        Returns:
            归一化后的特征
        """
        if method == 'minmax':
            X_min = X.min(axis=0)
            X_max = X.max(axis=0)
            return (X - X_min) / (X_max - X_min + 1e-8)
        elif method == 'zscore':
            mean = X.mean(axis=0)
            std = X.std(axis=0)
            return (X - mean) / (std + 1e-8)
        else:
            return X

    @staticmethod
    def create_classification_labels(prices: np.ndarray, threshold: float = 0.02) -> np.ndarray:
        """
        创建分类标签（涨/跌/横盘）

        Args:
            prices: 价格序列
            threshold: 涨跌阈值

        Returns:
            标签数组 (1: 上涨, 0: 横盘, -1: 下跌)
        """
        returns = np.diff(prices) / prices[:-1]

        labels = np.zeros(len(returns))
        labels[returns > threshold] = 1  # 上涨
        labels[returns < -threshold] = -1  # 下跌

        return labels


class ModelEvaluator:
    """模型评估工具"""

    @staticmethod
    def evaluate_trading_strategy(predictions: np.ndarray, actual_prices: np.ndarray,
                                  initial_capital: float = 100000) -> Dict[str, Any]:
        """
        评估交易策略

        Args:
            predictions: 预测价格序列
            actual_prices: 实际价格序列
            initial_capital: 初始资金

        Returns:
            策略评估结果
        """
        # 简单策略：预测上涨则买入，预测下跌则卖出
        positions = []  # 持仓状态
        cash = initial_capital
        shares = 0
        portfolio_values = []

        for i in range(1, len(predictions)):
            current_price = actual_prices[i]

            # 预测未来涨跌
            if i < len(predictions) - 1:
                predicted_return = (predictions[i+1] - predictions[i]) / predictions[i]

                # 买入信号
                if predicted_return > 0.01 and shares == 0:
                    shares = cash / current_price
                    cash = 0
                    positions.append(('buy', i, current_price))

                # 卖出信号
                elif predicted_return < -0.01 and shares > 0:
                    cash = shares * current_price
                    shares = 0
                    positions.append(('sell', i, current_price))

            # 计算当前组合价值
            portfolio_value = cash + shares * current_price
            portfolio_values.append(portfolio_value)

        # 计算收益指标
        final_value = portfolio_values[-1] if portfolio_values else initial_capital
        total_return = (final_value - initial_capital) / initial_capital

        # 计算最大回撤
        peak = initial_capital
        max_drawdown = 0
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # 计算夏普比率（简化版）
        if len(portfolio_values) > 1:
            returns = [(portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                      for i in range(1, len(portfolio_values))]
            sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(252)
        else:
            sharpe_ratio = 0

        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'num_trades': len(positions),
            'portfolio_values': portfolio_values
        }
