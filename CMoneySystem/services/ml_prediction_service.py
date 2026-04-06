"""ML增强的预测服务

集成机器学习模型到预测服务中
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import numpy as np
import pandas as pd
import os

from services.prediction_service import PredictionService
from utils.constants import TIME_HORIZONS, PREDICTION_MAP

# 导入ML模型
try:
    from ml_models.lstm_model import LSTMPredictor, SimpleLSTMPredictor
    from ml_models.ensemble_models import XGBoostPredictor, RandomForestPredictor, EnsemblePredictor
    from ml_models import FeatureEngineering
    ML_MODELS_AVAILABLE = True
except ImportError:
    ML_MODELS_AVAILABLE = False
    logging.warning("ML models not available")


class MLEnhancedPredictionService(PredictionService):
    """集成机器学习的增强预测服务"""

    def __init__(self, use_ml: bool = True, model_path: str = './saved_models'):
        """
        初始化ML增强预测服务

        Args:
            use_ml: 是否使用ML模型
            model_path: 模型保存路径
        """
        super().__init__()
        self.use_ml = use_ml and ML_MODELS_AVAILABLE
        self.model_path = model_path
        self.ml_models = {}

        if self.use_ml:
            self._init_ml_models()
        else:
            self.logger.info("ML models disabled or not available, using traditional methods")

    def _init_ml_models(self):
        """初始化ML模型"""
        try:
            # 尝试加载已训练的模型
            if os.path.exists(self.model_path):
                self._load_trained_models()
            else:
                self.logger.info("No trained models found, will use traditional methods")

        except Exception as e:
            self.logger.warning(f"Error initializing ML models: {e}")
            self.use_ml = False

    def _load_trained_models(self):
        """加载已训练的模型"""
        try:
            # LSTM模型
            lstm_path = os.path.join(self.model_path, 'lstm_model.pkl')
            if os.path.exists(lstm_path):
                lstm_model = LSTMPredictor()
                lstm_model.load(lstm_path)
                self.ml_models['lstm'] = lstm_model
                self.logger.info("Loaded LSTM model")

            # XGBoost模型
            xgb_path = os.path.join(self.model_path, 'xgboost_model.pkl')
            if os.path.exists(xgb_path):
                xgb_model = XGBoostPredictor()
                xgb_model.load(xgb_path)
                self.ml_models['xgboost'] = xgb_model
                self.logger.info("Loaded XGBoost model")

            # 随机森林模型
            rf_path = os.path.join(self.model_path, 'rf_model.pkl')
            if os.path.exists(rf_path):
                rf_model = RandomForestPredictor()
                rf_model.load(rf_path)
                self.ml_models['random_forest'] = rf_model
                self.logger.info("Loaded Random Forest model")

        except Exception as e:
            self.logger.error(f"Error loading models: {e}")

    def predict(self, stock_code: str, historical_data: List[Dict] = None,
                prediction_days: int = 30, time_horizon: str = 'short',
                use_ml: bool = None) -> Dict[str, Any]:
        """
        增强的预测方法

        Args:
            stock_code: 股票代码
            historical_data: 历史数据
            prediction_days: 预测天数
            time_horizon: 时间范围
            use_ml: 是否使用ML（覆盖默认设置）

        Returns:
            预测结果
        """
        # 确定是否使用ML
        should_use_ml = use_ml if use_ml is not None else self.use_ml

        # 如果使用ML且有可用模型和足够的历史数据
        if should_use_ml and self.ml_models and historical_data and len(historical_data) >= 30:
            try:
                ml_prediction = self._ml_predict(historical_data, time_horizon)

                if ml_prediction:
                    self.logger.info(f"Using ML prediction for {stock_code}")
                    ml_prediction.update({
                        'stock_code': stock_code,
                        'time_horizon': time_horizon,
                        'prediction_method': 'machine_learning',
                        'timestamp': datetime.now().isoformat()
                    })
                    return ml_prediction

            except Exception as e:
                self.logger.warning(f"ML prediction failed, falling back to traditional: {e}")

        # 回退到传统方法
        self.logger.info(f"Using traditional prediction for {stock_code}")
        traditional_prediction = super().predict(stock_code, historical_data, prediction_days, time_horizon)
        traditional_prediction['prediction_method'] = 'traditional'
        return traditional_prediction

    def _ml_predict(self, historical_data: List[Dict], time_horizon: str) -> Optional[Dict[str, Any]]:
        """
        使用ML模型进行预测

        Args:
            historical_data: 历史数据
            time_horizon: 时间范围

        Returns:
            预测结果
        """
        try:
            # 转换为DataFrame
            df = pd.DataFrame(historical_data)

            if 'close' not in df.columns:
                self.logger.warning("No 'close' price in historical data")
                return None

            # 提取收盘价
            prices = df['close'].values

            if len(prices) < 30:
                self.logger.warning("Insufficient historical data for ML prediction")
                return None

            # 使用不同模型进行预测
            predictions = {}

            # LSTM预测
            if 'lstm' in self.ml_models:
                lstm_pred = self._lstm_predict(prices)
                if lstm_pred is not None:
                    predictions['lstm'] = lstm_pred

            # XGBoost预测
            if 'xgboost' in self.ml_models:
                xgb_pred = self._xgboost_predict(df)
                if xgb_pred is not None:
                    predictions['xgboost'] = xgb_pred

            # 随机森林预测
            if 'random_forest' in self.ml_models:
                rf_pred = self._rf_predict(df)
                if rf_pred is not None:
                    predictions['random_forest'] = rf_pred

            if not predictions:
                return None

            # 集成预测结果（加权平均）
            weights = {
                'lstm': 0.4,
                'xgboost': 0.35,
                'random_forest': 0.25
            }

            final_prediction = 0
            total_weight = 0

            for model_name, pred_value in predictions.items():
                weight = weights.get(model_name, 0.33)
                final_prediction += pred_value * weight
                total_weight += weight

            if total_weight > 0:
                final_prediction /= total_weight

            # 计算预测变化
            current_price = prices[-1]
            predicted_change = (final_prediction - current_price) / current_price

            # 确定趋势
            if predicted_change > 0.02:
                trend = 1
            elif predicted_change < -0.02:
                trend = -1
            else:
                trend = 0

            # 计算置信度（基于模型一致性）
            if len(predictions) > 1:
                pred_values = list(predictions.values())
                pred_std = np.std(pred_values)
                # 标准差越小，置信度越高
                confidence = max(0.5, min(0.95, 1.0 - pred_std / current_price))
            else:
                confidence = 0.7

            # 获取horizon配置
            horizon_config = TIME_HORIZONS.get(time_horizon, TIME_HORIZONS['short'])

            return {
                'horizon_name': horizon_config['name'],
                'horizon_days': horizon_config['days'],
                'trend': trend,
                'trend_name': PREDICTION_MAP.get(trend, '未知'),
                'confidence': confidence,
                'price_change_pct': predicted_change,
                'predicted_price': final_prediction,
                'current_price': current_price,
                'risk_level': self._assess_risk(0.02, confidence),  # 简化波动率
                'key_factors': [
                    f"ML模型集成预测（使用{len(predictions)}个模型）",
                    f"预测价格: {final_prediction:.2f}",
                    f"当前价格: {current_price:.2f}"
                ],
                'model_predictions': predictions,
                'summary': self._generate_ml_summary(trend, confidence, predicted_change)
            }

        except Exception as e:
            self.logger.error(f"Error in ML prediction: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _lstm_predict(self, prices: np.ndarray) -> Optional[float]:
        """使用LSTM预测"""
        try:
            model = self.ml_models['lstm']

            # 使用最近20天的数据预测下一天
            lookback = 20
            if len(prices) >= lookback:
                recent_prices = prices[-lookback:]
                prediction = model.predict(recent_prices.reshape(1, -1))

                if len(prediction) > 0:
                    return float(prediction[0])

            return None

        except Exception as e:
            self.logger.warning(f"LSTM prediction error: {e}")
            return None

    def _xgboost_predict(self, df: pd.DataFrame) -> Optional[float]:
        """使用XGBoost预测"""
        try:
            model = self.ml_models['xgboost']

            # 创建特征
            df_features = FeatureEngineering.create_technical_features(df)

            # 选择最新的特征
            feature_cols = ['ma_5', 'ma_10', 'ma_20', 'rsi', 'macd', 'volatility_20']
            latest_features = []

            for col in feature_cols:
                if col in df_features.columns:
                    value = df_features[col].iloc[-1]
                    latest_features.append(value if not pd.isna(value) else 0)
                else:
                    latest_features.append(0)

            if len(latest_features) > 0:
                X = np.array(latest_features).reshape(1, -1)
                prediction = model.predict(X)

                if len(prediction) > 0:
                    return float(prediction[0])

            return None

        except Exception as e:
            self.logger.warning(f"XGBoost prediction error: {e}")
            return None

    def _rf_predict(self, df: pd.DataFrame) -> Optional[float]:
        """使用随机森林预测"""
        try:
            model = self.ml_models['random_forest']

            # 使用与XGBoost相同的特征
            df_features = FeatureEngineering.create_technical_features(df)

            feature_cols = ['ma_5', 'ma_10', 'ma_20', 'rsi', 'macd', 'volatility_20']
            latest_features = []

            for col in feature_cols:
                if col in df_features.columns:
                    value = df_features[col].iloc[-1]
                    latest_features.append(value if not pd.isna(value) else 0)
                else:
                    latest_features.append(0)

            if len(latest_features) > 0:
                X = np.array(latest_features).reshape(1, -1)
                prediction = model.predict(X)

                if len(prediction) > 0:
                    return float(prediction[0])

            return None

        except Exception as e:
            self.logger.warning(f"Random Forest prediction error: {e}")
            return None

    def _generate_ml_summary(self, trend: int, confidence: float, change_pct: float) -> str:
        """生成ML预测摘要"""
        trend_name = PREDICTION_MAP.get(trend, '未知')
        confidence_pct = confidence * 100
        change_pct_display = abs(change_pct) * 100

        if trend == 1:
            return f"机器学习模型预测：{trend_name}，预期涨幅{change_pct_display:.2f}%，置信度{confidence_pct:.1f}%"
        elif trend == -1:
            return f"机器学习模型预测：{trend_name}，预期跌幅{change_pct_display:.2f}%，置信度{confidence_pct:.1f}%"
        else:
            return f"机器学习模型预测：{trend_name}，置信度{confidence_pct:.1f}%，建议观望"

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        info = {
            'ml_enabled': self.use_ml,
            'loaded_models': list(self.ml_models.keys()),
            'model_path': self.model_path
        }

        if self.ml_models:
            model_stats = {}
            for name, model in self.ml_models.items():
                model_stats[name] = {
                    'is_trained': model.is_trained,
                    'metrics': model.metrics
                }
            info['model_stats'] = model_stats

        return info
