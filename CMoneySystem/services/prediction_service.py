"""预测服务"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import numpy as np
from utils.constants import TIME_HORIZONS, PREDICTION_MAP


class PredictionService:
    """股价预测服务"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def predict(self,
                stock_code: str,
                historical_data: List[Dict] = None,
                prediction_days: int = 30,
                time_horizon: str = 'short') -> Dict[str, Any]:
        """
        执行股价预测

        Args:
            stock_code: 股票代码
            historical_data: 历史数据
            prediction_days: 预测天数
            time_horizon: 时间范围 (short/medium/long)

        Returns:
            预测结果
        """
        self.logger.info(f"执行股价预测: {stock_code}, 时间范围: {time_horizon}")

        if historical_data is None:
            historical_data = []

        # 获取时间范围配置
        horizon_config = TIME_HORIZONS.get(time_horizon, TIME_HORIZONS['short'])
        horizon_days = horizon_config['days']
        horizon_name = horizon_config['name']

        # 执行不同时间维度的预测
        if time_horizon == 'short':
            prediction_result = self._predict_short_term(historical_data, prediction_days)
        elif time_horizon == 'medium':
            prediction_result = self._predict_medium_term(historical_data, prediction_days)
        elif time_horizon == 'long':
            prediction_result = self._predict_long_term(historical_data, prediction_days)
        else:
            prediction_result = self._predict_short_term(historical_data, prediction_days)

        return {
            'stock_code': stock_code,
            'time_horizon': time_horizon,
            'horizon_name': horizon_name,
            'horizon_days': horizon_days,
            'prediction_days': prediction_days,
            'trend': prediction_result['trend'],
            'trend_name': PREDICTION_MAP.get(prediction_result['trend'], '未知'),
            'confidence': prediction_result['confidence'],
            'price_change_pct': prediction_result['price_change_pct'],
            'key_factors': prediction_result['key_factors'],
            'risk_level': prediction_result['risk_level'],
            'summary': prediction_result['summary'],
            'timestamp': datetime.now().isoformat()
        }

    def _predict_short_term(self, historical_data: List[Dict], prediction_days: int) -> Dict[str, Any]:
        """
        短期预测 (1-3个月)

        重点关注：
        - 技术面指标
        - 市场情绪
        - 资金流向
        - 短期新闻事件

        Args:
            historical_data: 历史数据
            prediction_days: 预测天数

        Returns:
            预测结果
        """
        self.logger.info("执行短期预测")

        if not historical_data or len(historical_data) < 5:
            return self._generate_default_prediction("short")

        # 提取价格数据
        prices = [item.get('close', 0) for item in historical_data[-20:]]

        # 计算短期趋势
        short_ma = np.mean(prices[-5:]) if len(prices) >= 5 else 0
        long_ma = np.mean(prices[-10:]) if len(prices) >= 10 else 0

        # 计算动量
        momentum = self._calculate_momentum(prices)

        # 计算波动率
        volatility = self._calculate_volatility(prices)

        # 综合判断趋势
        trend_score = 0

        # 均线判断
        if short_ma > long_ma:
            trend_score += 0.4
        elif short_ma < long_ma:
            trend_score -= 0.4

        # 动量判断
        if momentum > 0.02:
            trend_score += 0.3
        elif momentum < -0.02:
            trend_score -= 0.3

        # 价格位置判断
        current_price = prices[-1] if prices else 0
        price_max = max(prices) if prices else 0
        price_min = min(prices) if prices else 0

        if price_max > price_min:
            price_position = (current_price - price_min) / (price_max - price_min)
            if price_position > 0.7:
                trend_score += 0.2
            elif price_position < 0.3:
                trend_score -= 0.2

        # 确定趋势方向
        if trend_score > 0.3:
            trend = 1  # 上涨
            confidence = min(0.85, 0.6 + abs(trend_score) * 0.3)
            price_change_pct = min(0.15, abs(trend_score) * 0.2)
        elif trend_score < -0.3:
            trend = -1  # 下跌
            confidence = min(0.85, 0.6 + abs(trend_score) * 0.3)
            price_change_pct = -min(0.15, abs(trend_score) * 0.2)
        else:
            trend = 0  # 横盘
            confidence = 0.6
            price_change_pct = 0

        # 风险评估
        risk_level = self._assess_risk(volatility, confidence)

        # 关键因素
        key_factors = [
            "技术指标显示均线" + ("多头" if short_ma > long_ma else "空头") + "排列",
            f"短期动量{'向上' if momentum > 0 else '向下'}",
            f"波动率{'较高' if volatility > 0.02 else '正常'}"
        ]

        return {
            'trend': trend,
            'confidence': confidence,
            'price_change_pct': price_change_pct,
            'key_factors': key_factors,
            'risk_level': risk_level,
            'summary': self._generate_prediction_summary(trend, confidence, 'short')
        }

    def _predict_medium_term(self, historical_data: List[Dict], prediction_days: int) -> Dict[str, Any]:
        """
        中期预测 (3-12个月)

        重点关注：
        - 基本面因素
        - 行业趋势
        - 宏观经济环境
        - 政策因素

        Args:
            historical_data: 历史数据
            prediction_days: 预测天数

        Returns:
            预测结果
        """
        self.logger.info("执行中期预测")

        if not historical_data or len(historical_data) < 10:
            return self._generate_default_prediction("medium")

        # 提取价格数据
        prices = [item.get('close', 0) for item in historical_data[-60:]]

        # 计算中期趋势
        ma_30 = np.mean(prices[-30:]) if len(prices) >= 30 else 0
        ma_60 = np.mean(prices[-60:]) if len(prices) >= 60 else 0

        # 计算趋势强度
        trend_strength = self._calculate_trend_strength(prices)

        # 计算价格变化率
        if len(prices) >= 30:
            price_change = (prices[-1] - prices[-30]) / prices[-30] if prices[-30] != 0 else 0
        else:
            price_change = 0

        # 综合判断
        trend_score = 0

        # 均线趋势
        if ma_30 > ma_60:
            trend_score += 0.35
        elif ma_30 < ma_60:
            trend_score -= 0.35

        # 价格变化趋势
        if price_change > 0.1:
            trend_score += 0.30
        elif price_change < -0.1:
            trend_score -= 0.30

        # 趋势强度
        trend_score += trend_strength * 0.35

        # 确定趋势方向
        if trend_score > 0.25:
            trend = 1  # 上涨
            confidence = min(0.80, 0.55 + abs(trend_score) * 0.3)
            price_change_pct = min(0.30, abs(trend_score) * 0.4)
        elif trend_score < -0.25:
            trend = -1  # 下跌
            confidence = min(0.80, 0.55 + abs(trend_score) * 0.3)
            price_change_pct = -min(0.30, abs(trend_score) * 0.4)
        else:
            trend = 0  # 横盘
            confidence = 0.55
            price_change_pct = 0

        # 波动率
        volatility = self._calculate_volatility(prices)
        risk_level = self._assess_risk(volatility, confidence)

        # 关键因素
        key_factors = [
            f"中期均线趋势{'向上' if ma_30 > ma_60 else '向下'}",
            f"近30日价格变化{price_change*100:.1f}%",
            f"趋势强度{'强' if abs(trend_strength) > 0.5 else '中等'}"
        ]

        return {
            'trend': trend,
            'confidence': confidence,
            'price_change_pct': price_change_pct,
            'key_factors': key_factors,
            'risk_level': risk_level,
            'summary': self._generate_prediction_summary(trend, confidence, 'medium')
        }

    def _predict_long_term(self, historical_data: List[Dict], prediction_days: int) -> Dict[str, Any]:
        """
        长期预测 (1年以上)

        重点关注：
        - 公司战略方向
        - 行业发展周期
        - 长期政策导向
        - 经济周期

        Args:
            historical_data: 历史数据
            prediction_days: 预测天数

        Returns:
            预测结果
        """
        self.logger.info("执行长期预测")

        if not historical_data or len(historical_data) < 20:
            return self._generate_default_prediction("long")

        # 提取价格数据
        prices = [item.get('close', 0) for item in historical_data[-250:]]

        # 计算长期趋势
        ma_120 = np.mean(prices[-120:]) if len(prices) >= 120 else 0
        ma_250 = np.mean(prices[-250:]) if len(prices) >= 250 else 0

        # 计算年化收益率
        if len(prices) >= 250:
            annual_return = (prices[-1] - prices[-250]) / prices[-250] if prices[-250] != 0 else 0
        else:
            annual_return = 0

        # 计算长期趋势强度
        trend_strength = self._calculate_trend_strength(prices[-120:] if len(prices) >= 120 else prices)

        # 综合判断
        trend_score = 0

        # 均线趋势
        if ma_120 > ma_250:
            trend_score += 0.30
        elif ma_120 < ma_250:
            trend_score -= 0.30

        # 年化收益
        if annual_return > 0.15:
            trend_score += 0.35
        elif annual_return < -0.15:
            trend_score -= 0.35

        # 长期趋势强度
        trend_score += trend_strength * 0.35

        # 确定趋势方向
        if trend_score > 0.2:
            trend = 1  # 上涨
            confidence = min(0.75, 0.50 + abs(trend_score) * 0.3)
            price_change_pct = min(0.50, abs(trend_score) * 0.6)
        elif trend_score < -0.2:
            trend = -1  # 下跌
            confidence = min(0.75, 0.50 + abs(trend_score) * 0.3)
            price_change_pct = -min(0.50, abs(trend_score) * 0.6)
        else:
            trend = 0  # 横盘
            confidence = 0.50
            price_change_pct = 0

        # 波动率
        volatility = self._calculate_volatility(prices)
        risk_level = self._assess_risk(volatility, confidence)

        # 关键因素
        key_factors = [
            f"长期均线趋势{'向上' if ma_120 > ma_250 else '向下'}",
            f"年化收益率{annual_return*100:.1f}%",
            "需关注行业发展周期和政策导向"
        ]

        return {
            'trend': trend,
            'confidence': confidence,
            'price_change_pct': price_change_pct,
            'key_factors': key_factors,
            'risk_level': risk_level,
            'summary': self._generate_prediction_summary(trend, confidence, 'long')
        }

    # 辅助计算方法

    def _calculate_momentum(self, prices: List[float]) -> float:
        """计算动量指标"""
        if len(prices) < 2:
            return 0

        recent_change = (prices[-1] - prices[-2]) / prices[-2] if prices[-2] != 0 else 0
        return recent_change

    def _calculate_volatility(self, prices: List[float]) -> float:
        """计算波动率"""
        if len(prices) < 2:
            return 0

        returns = [(prices[i] - prices[i-1]) / prices[i-1]
                  for i in range(1, len(prices)) if prices[i-1] != 0]

        if not returns:
            return 0

        return float(np.std(returns))

    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """计算趋势强度"""
        if len(prices) < 10:
            return 0

        # 使用线性回归斜率表示趋势强度
        x = np.arange(len(prices))
        y = np.array(prices)

        if len(x) == 0 or len(y) == 0:
            return 0

        # 简化的趋势计算
        slope = (y[-1] - y[0]) / len(y) if len(y) > 0 and y[0] != 0 else 0
        normalized_slope = slope / y[0] if y[0] != 0 else 0

        return max(-1, min(1, normalized_slope * 100))

    def _assess_risk(self, volatility: float, confidence: float) -> str:
        """评估风险等级"""
        if volatility > 0.03 or confidence < 0.5:
            return "高"
        elif volatility > 0.02 or confidence < 0.65:
            return "中"
        else:
            return "低"

    def _generate_default_prediction(self, time_horizon: str) -> Dict[str, Any]:
        """生成默认预测结果（数据不足时）"""
        return {
            'trend': 0,
            'confidence': 0.4,
            'price_change_pct': 0,
            'key_factors': ["历史数据不足", "建议补充更多数据"],
            'risk_level': "高",
            'summary': f"由于{TIME_HORIZONS[time_horizon]['name']}历史数据不足，无法给出可靠预测"
        }

    def _generate_prediction_summary(self, trend: int, confidence: float, time_horizon: str) -> str:
        """生成预测摘要"""
        trend_name = PREDICTION_MAP.get(trend, '未知')
        horizon_name = TIME_HORIZONS.get(time_horizon, {}).get('name', '未知')
        confidence_pct = confidence * 100

        if trend == 1:
            return f"{horizon_name}趋势预测：{trend_name}，置信度{confidence_pct:.1f}%，建议关注上涨机会"
        elif trend == -1:
            return f"{horizon_name}趋势预测：{trend_name}，置信度{confidence_pct:.1f}%，建议规避风险"
        else:
            return f"{horizon_name}趋势预测：{trend_name}，置信度{confidence_pct:.1f}%，建议观望等待"

    def generate_multi_horizon_prediction(self,
                                          stock_code: str,
                                          historical_data: List[Dict]) -> Dict[str, Any]:
        """
        生成多时间维度预测

        Args:
            stock_code: 股票代码
            historical_data: 历史数据

        Returns:
            多时间维度预测结果
        """
        self.logger.info(f"生成多时间维度预测: {stock_code}")

        short_pred = self.predict(stock_code, historical_data, time_horizon='short')
        medium_pred = self.predict(stock_code, historical_data, time_horizon='medium')
        long_pred = self.predict(stock_code, historical_data, time_horizon='long')

        # 综合建议
        overall_recommendation = self._generate_overall_recommendation(
            short_pred, medium_pred, long_pred
        )

        return {
            'stock_code': stock_code,
            'short_term': short_pred,
            'medium_term': medium_pred,
            'long_term': long_pred,
            'overall_recommendation': overall_recommendation,
            'timestamp': datetime.now().isoformat()
        }

    def _generate_overall_recommendation(self,
                                        short_pred: Dict,
                                        medium_pred: Dict,
                                        long_pred: Dict) -> str:
        """生成综合投资建议"""
        short_trend = short_pred.get('trend', 0)
        medium_trend = medium_pred.get('trend', 0)
        long_trend = long_pred.get('trend', 0)

        # 计算综合趋势
        total_trend = short_trend + medium_trend + long_trend

        if total_trend >= 2:
            return "多个时间维度显示上涨趋势，建议积极配置"
        elif total_trend >= 1:
            return "整体趋势向好，可适度参与"
        elif total_trend <= -2:
            return "多个时间维度显示下跌趋势，建议规避风险"
        elif total_trend <= -1:
            return "整体趋势偏弱，建议谨慎操作"
        else:
            return "不同时间维度趋势分化，建议观望等待明确信号"
