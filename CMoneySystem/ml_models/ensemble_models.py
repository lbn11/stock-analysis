"""XGBoost和随机森林集成模型

集成学习方法结合多个弱学习器来提高预测性能

依赖:
- pip install xgboost
- pip install scikit-learn
"""
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
import logging
from ml_models import BaseMLModel, FeatureEngineering

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not installed. Install with: pip install xgboost")

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not installed. Install with: pip install scikit-learn")


class XGBoostPredictor(BaseMLModel):
    """XGBoost股价预测模型"""

    def __init__(self, n_estimators: int = 100, max_depth: int = 5):
        """
        初始化XGBoost预测器

        Args:
            n_estimators: 树的数量
            max_depth: 树的最大深度
        """
        super().__init__("XGBoost_Predictor")
        self.n_estimators = n_estimators
        self.max_depth = max_depth

        if not XGBOOST_AVAILABLE:
            self.logger.error("XGBoost is not available")

    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        训练XGBoost模型

        Args:
            X: 特征数据
            y: 标签数据
            validation_split: 验证集比例

        Returns:
            训练结果
        """
        if not XGBOOST_AVAILABLE:
            self.logger.error("Cannot train: XGBoost not available")
            return {}

        try:
            self.logger.info(f"Training XGBoost model with {len(X)} samples")

            # 分割训练集和验证集
            if validation_split > 0:
                split_idx = int(len(X) * (1 - validation_split))
                X_train, X_val = X[:split_idx], X[split_idx:]
                y_train, y_val = y[:split_idx], y[split_idx:]
            else:
                X_train, X_val = X, None
                y_train, y_val = y, None

            # 创建DMatrix（XGBoost的优化数据结构）
            dtrain = xgb.DMatrix(X_train, label=y_train)

            # 设置参数
            params = {
                'objective': 'reg:squarederror',
                'max_depth': self.max_depth,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'min_child_weight': 1,
                'gamma': 0,
                'reg_alpha': 0,
                'reg_lambda': 1,
                'seed': 42
            }

            # 设置验证集（如果有）
            evals = [(dtrain, 'train')]
            if X_val is not None:
                dval = xgb.DMatrix(X_val, label=y_val)
                evals.append((dval, 'val'))

            # 训练
            self.model = xgb.train(
                params,
                dtrain,
                num_boost_round=self.n_estimators,
                evals=evals,
                early_stopping_rounds=10,
                verbose_eval=10
            )

            self.is_trained = True

            # 评估
            train_pred = self.model.predict(dtrain)
            train_rmse = np.sqrt(np.mean((train_pred - y_train) ** 2))

            result = {
                'train_rmse': float(train_rmse),
                'best_iteration': self.model.best_iteration,
                'num_trees': self.model.num_boosted_rounds()
            }

            if X_val is not None:
                val_pred = self.model.predict(dval)
                val_rmse = np.sqrt(np.mean((val_pred - y_val) ** 2))
                result['val_rmse'] = float(val_rmse)

            self.logger.info(f"Training completed. Train RMSE: {train_rmse:.4f}")
            return result

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
            预测结果
        """
        if not self.is_trained:
            self.logger.warning("Model not trained yet")
            return np.array([])

        try:
            dtest = xgb.DMatrix(X)
            predictions = self.model.predict(dtest)
            return predictions

        except Exception as e:
            self.logger.error(f"Error predicting: {e}")
            return np.array([])

    def get_feature_importance(self) -> Dict[str, float]:
        """
        获取特征重要性

        Returns:
            特征重要性字典
        """
        if not self.is_trained:
            return {}

        try:
            importance = self.model.get_score(importance_type='weight')
            return importance

        except Exception as e:
            self.logger.error(f"Error getting feature importance: {e}")
            return {}


class RandomForestPredictor(BaseMLModel):
    """随机森林股价预测模型"""

    def __init__(self, n_estimators: int = 100, max_depth: int = 10):
        """
        初始化随机森林预测器

        Args:
            n_estimators: 树的数量
            max_depth: 树的最大深度
        """
        super().__init__("RandomForest_Predictor")
        self.n_estimators = n_estimators
        self.max_depth = max_depth

        if not SKLEARN_AVAILABLE:
            self.logger.error("Scikit-learn is not available")

    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        训练随机森林模型

        Args:
            X: 特征数据
            y: 标签数据
            validation_split: 验证集比例

        Returns:
            训练结果
        """
        if not SKLEARN_AVAILABLE:
            self.logger.error("Cannot train: Scikit-learn not available")
            return {}

        try:
            self.logger.info(f"Training Random Forest model with {len(X)} samples")

            # 创建模型
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                verbose=1
            )

            # 分割数据
            if validation_split > 0:
                X_train, X_val, y_train, y_val = train_test_split(
                    X, y, test_size=validation_split, random_state=42
                )
            else:
                X_train, X_val = X, None
                y_train, y_val = y, None

            # 训练
            self.model.fit(X_train, y_train)
            self.is_trained = True

            # 评估
            train_pred = self.model.predict(X_train)
            train_rmse = np.sqrt(np.mean((train_pred - y_train) ** 2))
            train_score = self.model.score(X_train, y_train)

            result = {
                'train_rmse': float(train_rmse),
                'train_r2': float(train_score),
                'n_estimators': self.n_estimators
            }

            if X_val is not None:
                val_pred = self.model.predict(X_val)
                val_rmse = np.sqrt(np.mean((val_pred - y_val) ** 2))
                val_score = self.model.score(X_val, y_val)
                result['val_rmse'] = float(val_rmse)
                result['val_r2'] = float(val_score)

            self.logger.info(f"Training completed. Train RMSE: {train_rmse:.4f}, R²: {train_score:.4f}")
            return result

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
            预测结果
        """
        if not self.is_trained:
            self.logger.warning("Model not trained yet")
            return np.array([])

        try:
            predictions = self.model.predict(X)
            return predictions

        except Exception as e:
            self.logger.error(f"Error predicting: {e}")
            return np.array([])

    def get_feature_importance(self, feature_names: List[str] = None) -> Dict[str, float]:
        """
        获取特征重要性

        Args:
            feature_names: 特征名称列表

        Returns:
            特征重要性字典
        """
        if not self.is_trained:
            return {}

        try:
            importances = self.model.feature_importances_

            if feature_names is None:
                feature_names = [f'feature_{i}' for i in range(len(importances))]

            importance_dict = {name: float(imp) for name, imp in zip(feature_names, importances)}

            # 按重要性排序
            importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))

            return importance_dict

        except Exception as e:
            self.logger.error(f"Error getting feature importance: {e}")
            return {}


class EnsemblePredictor:
    """集成多个模型的预测器"""

    def __init__(self, models: List[BaseMLModel], weights: List[float] = None, method: str = 'weighted'):
        """
        初始化集成预测器

        Args:
            models: 模型列表
            weights: 各模型权重（None表示等权重）
            method: 集成方法 ('weighted'=加权平均, 'voting'=投票, 'stacking'=堆叠)
        """
        self.logger = logging.getLogger("EnsemblePredictor")
        self.models = models
        self.weights = weights if weights else [1.0 / len(models)] * len(models)
        self.method = method

        if len(self.weights) != len(self.models):
            raise ValueError("Number of weights must match number of models")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        集成预测

        Args:
            X: 特征数据

        Returns:
            加权平均预测结果
        """
        try:
            predictions = []

            for model in self.models:
                if model.is_trained:
                    pred = model.predict(X)
                    predictions.append(pred)

            if not predictions:
                self.logger.warning("No trained models available")
                return np.array([])

            # 根据方法选择集成策略
            if self.method == 'weighted':
                return self._weighted_average(predictions)
            elif self.method == 'voting':
                return self._voting(predictions)
            elif self.method == 'median':
                return np.median(predictions, axis=0)
            else:
                return self._weighted_average(predictions)

        except Exception as e:
            self.logger.error(f"Error in ensemble prediction: {e}")
            return np.array([])

    def _weighted_average(self, predictions: List[np.ndarray]) -> np.ndarray:
        """加权平均"""
        weighted_pred = np.average(predictions, axis=0, weights=self.weights[:len(predictions)])
        return weighted_pred

    def _voting(self, predictions: List[np.ndarray]) -> np.ndarray:
        """投票法（取中位数）"""
        return np.median(predictions, axis=0)

    def get_model_stats(self) -> Dict[str, Any]:
        """获取各模型统计信息"""
        stats = {}
        for i, model in enumerate(self.models):
            stats[model.model_name] = {
                'is_trained': model.is_trained,
                'weight': self.weights[i],
                'metrics': model.metrics
            }
        return stats


class StackingEnsemble:
    """堆叠集成模型

    使用第一层模型的预测结果作为第二层模型的特征
    """

    def __init__(self, base_models: List[Any], meta_model: Any = None):
        """
        初始化堆叠集成模型

        Args:
            base_models: 第一层基础模型列表
            meta_model: 第二层元模型（默认使用线性回归）
        """
        self.logger = logging.getLogger("StackingEnsemble")
        self.base_models = base_models
        self.meta_model = meta_model
        self.is_trained = False

        # 如果没有指定元模型，使用简单的线性回归
        if self.meta_model is None:
            if SKLEARN_AVAILABLE:
                from sklearn.linear_model import LinearRegression
                self.meta_model = LinearRegression()
            else:
                self.logger.warning("Scikit-learn not available, using simple averaging")
                self.meta_model = None

    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2):
        """
        训练堆叠模型

        Args:
            X: 特征数据
            y: 标签数据
            validation_split: 验证集比例

        Returns:
            训练结果
        """
        try:
            # 分割数据
            split_idx = int(len(X) * (1 - validation_split))
            X_train_base, X_meta = X[:split_idx], X[split_idx:]
            y_train_base, y_meta = y[:split_idx], y[split_idx:]

            # 训练基础模型
            self.logger.info(f"Training {len(self.base_models)} base models")
            meta_features = []

            for model in self.base_models:
                if hasattr(model, 'train'):
                    model.train(X_train_base, y_train_base)
                    pred = model.predict(X_meta)
                    meta_features.append(pred)

            # 准备元特征
            meta_features = np.column_stack(meta_features)

            # 训练元模型
            if self.meta_model is not None:
                self.logger.info("Training meta model")
                self.meta_model.fit(meta_features, y_meta)

            self.is_trained = True

            # 评估
            final_pred = self.predict(X_meta)
            mse = np.mean((final_pred - y_meta) ** 2)

            return {
                'success': True,
                'meta_mse': float(mse),
                'n_base_models': len(self.base_models)
            }

        except Exception as e:
            self.logger.error(f"Error training stacking ensemble: {e}")
            return {'success': False, 'error': str(e)}

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测

        Args:
            X: 特征数据

        Returns:
            预测结果
        """
        if not self.is_trained:
            self.logger.warning("Stacking ensemble not trained yet")
            return np.array([])

        try:
            # 获取基础模型预测
            meta_features = []
            for model in self.base_models:
                pred = model.predict(X)
                meta_features.append(pred)

            meta_features = np.column_stack(meta_features)

            # 元模型预测
            if self.meta_model is not None:
                return self.meta_model.predict(meta_features)
            else:
                # 简单平均
                return np.mean(meta_features, axis=1)

        except Exception as e:
            self.logger.error(f"Error in stacking prediction: {e}")
            return np.array([])


class VotingEnsemble:
    """投票集成模型

    支持硬投票（少数服从多数）和软投票（加权平均概率）
    """

    def __init__(self, models: List[Any], voting: str = 'soft', weights: List[float] = None):
        """
        初始化投票集成模型

        Args:
            models: 模型列表
            voting: 'soft'=软投票（加权平均）, 'hard'=硬投票（多数决）
            weights: 模型权重
        """
        self.logger = logging.getLogger("VotingEnsemble")
        self.models = models
        self.voting = voting
        self.weights = weights
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray):
        """训练所有基础模型"""
        try:
            for model in self.models:
                if hasattr(model, 'train'):
                    model.train(X, y)

            self.is_trained = True
            return {'success': True}

        except Exception as e:
            self.logger.error(f"Error training voting ensemble: {e}")
            return {'success': False, 'error': str(e)}

    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        if not self.is_trained:
            return np.array([])

        try:
            predictions = []
            for model in self.models:
                pred = model.predict(X)
                predictions.append(pred)

            predictions = np.array(predictions)

            if self.voting == 'soft':
                # 软投票：加权平均
                if self.weights:
                    return np.average(predictions, axis=0, weights=self.weights)
                else:
                    return np.mean(predictions, axis=0)
            else:
                # 硬投票：中位数
                return np.median(predictions, axis=0)

        except Exception as e:
            self.logger.error(f"Error in voting prediction: {e}")
            return np.array([])


class AdvancedEnsembleSystem:
    """高级集成系统

    结合多种集成策略，提供更强大的预测能力
    """

    def __init__(self):
        self.logger = logging.getLogger("AdvancedEnsembleSystem")
        self.models = {}
        self.ensemble = None
        self.is_trained = False

    def add_model(self, name: str, model: Any):
        """添加模型到系统"""
        self.models[name] = model
        self.logger.info(f"Added model: {name}")

    def create_ensemble(self, method: str = 'weighted', weights: Dict[str, float] = None):
        """
        创建集成模型

        Args:
            method: 集成方法
            weights: 模型权重字典
        """
        model_list = list(self.models.values())

        if weights:
            weight_list = [weights.get(name, 1.0) for name in self.models.keys()]
            # 归一化权重
            total = sum(weight_list)
            weight_list = [w / total for w in weight_list]
        else:
            weight_list = None

        if method == 'stacking':
            self.ensemble = StackingEnsemble(model_list)
        elif method == 'voting':
            self.ensemble = VotingEnsemble(model_list, weights=weight_list)
        else:
            self.ensemble = EnsemblePredictor(model_list, weights=weight_list, method=method)

        self.logger.info(f"Created {method} ensemble with {len(model_list)} models")

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """训练集成系统"""
        if self.ensemble is None:
            self.logger.warning("No ensemble created, using weighted ensemble")
            self.create_ensemble('weighted')

        result = self.ensemble.train(X, y, **kwargs)
        self.is_trained = True
        return result

    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        if not self.is_trained:
            self.logger.warning("Ensemble not trained yet")
            return np.array([])

        return self.ensemble.predict(X)

    def compare_models(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Dict]:
        """
        比较各个模型的性能

        Args:
            X_test: 测试特征
            y_test: 测试标签

        Returns:
            各模型性能指标
        """
        results = {}

        for name, model in self.models.items():
            try:
                if hasattr(model, 'predict'):
                    pred = model.predict(X_test)
                    mse = np.mean((pred - y_test) ** 2)
                    mae = np.mean(np.abs(pred - y_test))

                    results[name] = {
                        'mse': float(mse),
                        'mae': float(mae),
                        'rmse': float(np.sqrt(mse))
                    }
            except Exception as e:
                self.logger.error(f"Error evaluating {name}: {e}")
                results[name] = {'error': str(e)}

        return results

    def get_best_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Tuple[str, Dict]:
        """
        获取最佳模型

        Returns:
            (模型名称, 性能指标)
        """
        comparison = self.compare_models(X_test, y_test)

        # 按MSE排序
        sorted_models = sorted(comparison.items(), key=lambda x: x[1].get('mse', float('inf')))

        if sorted_models:
            return sorted_models[0]
        else:
            return None, {}
