"""LSTM时间序列预测模型

Long Short-Term Memory (LSTM) 是一种特殊的循环神经网络（RNN），
非常适合处理时间序列数据和序列预测任务。

依赖: pip install tensorflow keras
"""
from typing import Dict, List, Any, Tuple
import numpy as np
import logging
from ml_models import BaseMLModel, FeatureEngineering

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not installed. Install with: pip install tensorflow")


class LSTMPredictor(BaseMLModel):
    """LSTM股价预测模型"""

    def __init__(self, lookback: int = 20, forecast_horizon: int = 1):
        """
        初始化LSTM预测器

        Args:
            lookback: 回看窗口大小（使用多少天的数据）
            forecast_horizon: 预测未来多少天
        """
        super().__init__("LSTM_Predictor")
        self.lookback = lookback
        self.forecast_horizon = forecast_horizon
        self.scaler_params = None

        if not TENSORFLOW_AVAILABLE:
            self.logger.error("TensorFlow is not available")

    def _build_model(self, input_shape: Tuple) -> Sequential:
        """
        构建LSTM模型

        Args:
            input_shape: 输入形状

        Returns:
            Keras模型
        """
        model = Sequential([
            # 第一层LSTM
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),

            # 第二层LSTM
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),

            # 第三层LSTM
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),

            # 全连接层
            Dense(units=25, activation='relu'),
            Dense(units=self.forecast_horizon)
        ])

        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )

        return model

    def _prepare_data(self, X: np.ndarray, y: np.ndarray = None
                     ) -> Tuple[np.ndarray, np.ndarray]:
        """
        准备数据（归一化和reshape）

        Args:
            X: 特征数据
            y: 标签数据

        Returns:
            处理后的(X, y)
        """
        # 归一化
        if self.scaler_params is None:
            self.scaler_params = {
                'X_min': X.min(),
                'X_max': X.max()
            }

        X_scaled = (X - self.scaler_params['X_min']) / \
                   (self.scaler_params['X_max'] - self.scaler_params['X_min'] + 1e-8)

        # Reshape for LSTM: (samples, timesteps, features)
        if len(X_scaled.shape) == 2:
            X_scaled = X_scaled.reshape(X_scaled.shape[0], X_scaled.shape[1], 1)

        if y is not None:
            y_scaled = (y - self.scaler_params['X_min']) / \
                       (self.scaler_params['X_max'] - self.scaler_params['X_min'] + 1e-8)
            return X_scaled, y_scaled

        return X_scaled, None

    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2,
              epochs: int = 50, batch_size: int = 32) -> Dict[str, Any]:
        """
        训练LSTM模型

        Args:
            X: 特征数据 (samples, timesteps) 或 (samples, timesteps, features)
            y: 标签数据
            validation_split: 验证集比例
            epochs: 训练轮数
            batch_size: 批次大小

        Returns:
            训练历史
        """
        if not TENSORFLOW_AVAILABLE:
            self.logger.error("Cannot train: TensorFlow not available")
            return {}

        try:
            self.logger.info(f"Training LSTM model with {len(X)} samples")

            # 准备数据
            X_scaled, y_scaled = self._prepare_data(X, y)

            # 构建模型
            input_shape = (X_scaled.shape[1], X_scaled.shape[2])
            self.model = self._build_model(input_shape)

            self.logger.info(f"Model architecture:")
            self.model.summary(print_fn=self.logger.info)

            # 回调函数
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True,
                    verbose=1
                )
            ]

            # 训练
            history = self.model.fit(
                X_scaled, y_scaled,
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )

            self.is_trained = True

            # 记录训练结果
            train_result = {
                'final_loss': float(history.history['loss'][-1]),
                'final_val_loss': float(history.history['val_loss'][-1]),
                'final_mae': float(history.history['mae'][-1]),
                'final_val_mae': float(history.history['val_mae'][-1]),
                'epochs_trained': len(history.history['loss']),
                'history': history.history
            }

            self.logger.info(f"Training completed. Final val_loss: {train_result['final_val_loss']:.4f}")
            return train_result

        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测

        Args:
            X: 特征数据

        Returns:
            预测结果（反归一化后）
        """
        if not self.is_trained:
            self.logger.warning("Model not trained yet")
            return np.array([])

        try:
            # 准备数据
            X_scaled, _ = self._prepare_data(X)

            # 预测
            predictions_scaled = self.model.predict(X_scaled, verbose=0)

            # 反归一化
            predictions = predictions_scaled * \
                         (self.scaler_params['X_max'] - self.scaler_params['X_min']) + \
                         self.scaler_params['X_min']

            return predictions.flatten()

        except Exception as e:
            self.logger.error(f"Error predicting: {e}")
            return np.array([])

    def predict_future(self, initial_sequence: np.ndarray, steps: int = 5) -> np.ndarray:
        """
        递归预测未来多步

        Args:
            initial_sequence: 初始序列数据
            steps: 预测步数

        Returns:
            未来预测值数组
        """
        if not self.is_trained:
            self.logger.warning("Model not trained yet")
            return np.array([])

        try:
            predictions = []
            current_sequence = initial_sequence.copy()

            for _ in range(steps):
                # 预测下一步
                next_pred = self.predict(current_sequence.reshape(1, -1))

                predictions.append(next_pred[0])

                # 更新序列（移除最旧的，添加新预测）
                current_sequence = np.append(current_sequence[1:], next_pred[0])

            return np.array(predictions)

        except Exception as e:
            self.logger.error(f"Error in future prediction: {e}")
            return np.array([])


class SimpleLSTMPredictor:
    """
    简化的LSTM预测器（不依赖TensorFlow，使用简单RNN逻辑）

    当TensorFlow不可用时的备选方案
    """

    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        self.logger = logging.getLogger("SimpleLSTM")
        self.weights = None
        self.is_trained = False

    def train(self, prices: np.ndarray) -> Dict:
        """使用简单的时间序列分析进行"训练" """
        try:
            # 计算移动平均权重
            self.weights = np.arange(1, self.lookback + 1)
            self.weights = self.weights / self.weights.sum()
            self.is_trained = True

            self.logger.info("Simple LSTM trained")
            return {'success': True}

        except Exception as e:
            self.logger.error(f"Error training: {e}")
            return {'success': False}

    def predict(self, sequence: np.ndarray) -> float:
        """简单的加权移动平均预测"""
        if not self.is_trained:
            return sequence[-1]

        if len(sequence) < self.lookback:
            return sequence[-1]

        # 使用加权移动平均
        recent = sequence[-self.lookback:]
        prediction = np.dot(recent, self.weights)

        # 添加趋势分量
        if len(sequence) >= 3:
            trend = (sequence[-1] - sequence[-3]) / 2
            prediction += trend

        return prediction

    def predict_future(self, initial_sequence: np.ndarray, steps: int = 5) -> np.ndarray:
        """预测未来多步"""
        predictions = []
        current_sequence = initial_sequence.copy()

        for _ in range(steps):
            next_pred = self.predict(current_sequence)
            predictions.append(next_pred)
            current_sequence = np.append(current_sequence[1:], next_pred)

        return np.array(predictions)


class LSTMPredictorAdvanced:
    """
    高级LSTM股价预测器

    包含完整的数据预处理、特征工程、模型训练、预测和评估功能
    """

    def __init__(self, lookback: int = 60, forecast_horizon: int = 5):
        """
        初始化高级LSTM预测器

        Args:
            lookback: 回看窗口（默认60天）
            forecast_horizon: 预测未来天数（默认5天）
        """
        self.lookback = lookback
        self.forecast_horizon = forecast_horizon
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.is_trained = False

        # 检查依赖
        self._check_dependencies()

    def _check_dependencies(self):
        """检查必要的依赖库"""
        self.tensorflow_available = TENSORFLOW_AVAILABLE
        self.pandas_available = True

        try:
            import pandas as pd
            self.pd = pd
        except ImportError:
            self.pandas_available = False
            self.logger.warning("pandas not installed")

        try:
            from sklearn.preprocessing import MinMaxScaler
            self.MinMaxScaler = MinMaxScaler
        except ImportError:
            self.MinMaxScaler = None
            self.logger.warning("sklearn not installed")

    def prepare_features(self, historical_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """
        准备训练特征

        Args:
            historical_data: 历史数据列表

        Returns:
            (X, y) 特征和标签
        """
        if not self.pandas_available or not historical_data:
            return np.array([]), np.array([])

        try:
            # 转换为DataFrame
            df = self.pd.DataFrame(historical_data)

            # 确保必要的列存在
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    self.logger.error(f"Missing column: {col}")
                    return np.array([]), np.array([])

            # 创建技术指标特征
            df['returns'] = df['close'].pct_change()
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['rsi'] = self._calculate_rsi(df['close'])
            df['volume_ma5'] = df['volume'].rolling(window=5).mean()

            # 删除NaN值
            df = df.dropna()

            # 选择特征列
            self.feature_columns = ['close', 'returns', 'ma5', 'ma10', 'ma20', 'rsi', 'volume']

            # 准备数据
            feature_data = df[self.feature_columns].values

            # 创建时间序列样本
            X, y = [], []
            for i in range(self.lookback, len(feature_data) - self.forecast_horizon):
                X.append(feature_data[i - self.lookback:i])
                y.append(feature_data[i:i + self.forecast_horizon, 0])  # 预测收盘价

            X = np.array(X)
            y = np.array(y)

            self.logger.info(f"Prepared features: X shape={X.shape}, y shape={y.shape}")
            return X, y

        except Exception as e:
            self.logger.error(f"Error preparing features: {e}")
            return np.array([]), np.array([])

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """
        计算RSI指标

        Args:
            prices: 价格序列
            period: RSI周期

        Returns:
            RSI值序列
        """
        rsi = np.zeros_like(prices)

        for i in range(period, len(prices)):
            price_slice = prices[i - period:i + 1]
            deltas = np.diff(price_slice)

            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)

            if avg_loss == 0:
                rsi[i] = 100
            else:
                rs = avg_gain / avg_loss
                rsi[i] = 100 - (100 / (1 + rs))

        return rsi

    def train(self, historical_data: List[Dict[str, Any]],
              validation_split: float = 0.2,
              epochs: int = 100,
              batch_size: int = 32) -> Dict[str, Any]:
        """
        训练LSTM模型

        Args:
            historical_data: 历史数据
            validation_split: 验证集比例
            epochs: 训练轮数
            batch_size: 批次大小

        Returns:
            训练结果
        """
        if not self.tensorflow_available:
            self.logger.error("TensorFlow not available, cannot train LSTM model")
            return {}

        try:
            # 准备特征
            X, y = self.prepare_features(historical_data)

            if len(X) == 0:
                self.logger.error("No training data prepared")
                return {}

            # 数据归一化
            if self.MinMaxScaler:
                self.scaler = self.MinMaxScaler()
                X_reshaped = X.reshape(-1, X.shape[-1])
                X_scaled = self.scaler.fit_transform(X_reshaped)
                X_scaled = X_scaled.reshape(X.shape)
            else:
                # 简单归一化
                X_scaled = X / np.max(np.abs(X))

            # 标签归一化
            y_scaler = self.MinMaxScaler() if self.MinMaxScaler else None
            if y_scaler:
                y_scaled = y_scaler.fit_transform(y)
            else:
                y_scaled = y / np.max(np.abs(y))

            # 构建模型
            self.model = Sequential([
                LSTM(128, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
                Dropout(0.2),
                LSTM(64, return_sequences=True),
                Dropout(0.2),
                LSTM(32, return_sequences=False),
                Dropout(0.2),
                Dense(16, activation='relu'),
                Dense(self.forecast_horizon)
            ])

            self.model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )

            self.logger.info("Model architecture:")
            self.model.summary(print_fn=self.logger.info)

            # 训练
            early_stop = EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            )

            history = self.model.fit(
                X_scaled, y_scaled,
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=[early_stop],
                verbose=0
            )

            self.is_trained = True

            # 保存scaler
            self.y_scaler = y_scaler

            # 返回训练结果
            result = {
                'success': True,
                'epochs_trained': len(history.history['loss']),
                'final_loss': float(history.history['loss'][-1]),
                'final_val_loss': float(history.history['val_loss'][-1]),
                'final_mae': float(history.history['mae'][-1]),
                'final_val_mae': float(history.history['val_mae'][-1])
            }

            self.logger.info(f"Training completed: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def predict(self, recent_data: List[Dict[str, Any]]) -> np.ndarray:
        """
        预测未来价格

        Args:
            recent_data: 最近的数据（至少lookback条）

        Returns:
            预测的价格序列
        """
        if not self.is_trained:
            self.logger.warning("Model not trained yet")
            return np.array([])

        try:
            # 准备特征
            X, _ = self.prepare_features(recent_data)

            if len(X) == 0:
                self.logger.error("Failed to prepare prediction features")
                return np.array([])

            # 取最后一个样本
            X_last = X[-1:].copy()

            # 归一化
            if self.scaler:
                X_reshaped = X_last.reshape(-1, X_last.shape[-1])
                X_scaled = self.scaler.transform(X_reshaped)
                X_scaled = X_scaled.reshape(X_last.shape)
            else:
                X_scaled = X_last / np.max(np.abs(X_last))

            # 预测
            predictions_scaled = self.model.predict(X_scaled, verbose=0)

            # 反归一化
            if self.y_scaler:
                predictions = self.y_scaler.inverse_transform(predictions_scaled)
            else:
                predictions = predictions_scaled * np.max(np.abs(recent_data[-1]['close']))

            return predictions.flatten()

        except Exception as e:
            self.logger.error(f"Error predicting: {e}")
            return np.array([])

    def evaluate(self, test_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        评估模型性能

        Args:
            test_data: 测试数据

        Returns:
            评估指标
        """
        if not self.is_trained:
            return {}

        try:
            X, y_true = self.prepare_features(test_data)

            if len(X) == 0:
                return {}

            predictions = []
            for i in range(len(X)):
                pred = self.model.predict(X[i:i+1], verbose=0)
                predictions.append(pred[0])

            y_pred = np.array(predictions)

            # 计算评估指标
            mse = np.mean((y_true - y_pred) ** 2)
            mae = np.mean(np.abs(y_true - y_pred))
            mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100

            return {
                'mse': float(mse),
                'mae': float(mae),
                'mape': float(mape),
                'samples': len(X)
            }

        except Exception as e:
            self.logger.error(f"Error evaluating: {e}")
            return {}

    def save_model(self, filepath: str):
        """保存模型"""
        if not self.is_trained:
            self.logger.warning("No model to save")
            return

        try:
            import pickle

            model_data = {
                'model_config': self.model.get_config() if self.model else None,
                'scaler': self.scaler,
                'y_scaler': self.y_scaler,
                'feature_columns': self.feature_columns,
                'lookback': self.lookback,
                'forecast_horizon': self.forecast_horizon
            }

            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)

            # 保存Keras模型
            if self.model:
                self.model.save(filepath.replace('.pkl', '_keras.h5'))

            self.logger.info(f"Model saved to {filepath}")

        except Exception as e:
            self.logger.error(f"Error saving model: {e}")

    def load_model(self, filepath: str):
        """加载模型"""
        try:
            import pickle

            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)

            self.scaler = model_data.get('scaler')
            self.y_scaler = model_data.get('y_scaler')
            self.feature_columns = model_data.get('feature_columns')
            self.lookback = model_data.get('lookback')
            self.forecast_horizon = model_data.get('forecast_horizon')

            # 加载Keras模型
            keras_path = filepath.replace('.pkl', '_keras.h5')
            if self.tensorflow_available:
                self.model = keras.models.load_model(keras_path)
                self.is_trained = True

            self.logger.info(f"Model loaded from {filepath}")

        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
