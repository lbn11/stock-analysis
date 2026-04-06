"""分析引擎服务"""
from typing import Dict, Any, List
from datetime import datetime
from data.collector import DataCollector
from services.factor_analyzer import FactorAnalyzer
from services.prediction_service import PredictionService
from utils.constants import FACTOR_WEIGHTS, TIME_HORIZONS, PREDICTION_MAP
from utils.helpers import calculate_time_weight


class AnalysisEngine:
    """主分析引擎"""

    def __init__(self):
        self.data_collector = DataCollector()
        self.factor_analyzer = FactorAnalyzer()
        self.prediction_service = PredictionService()

    def analyze(self,
                stock_code: str,
                analysis_type: str = 'comprehensive',
                time_horizon: str = 'medium',
                custom_weights: Dict[str, float] = None) -> Dict[str, Any]:
        """
        执行股票综合分析

        Args:
            stock_code: 股票代码
            analysis_type: 分析类型
            time_horizon: 时间范围
            custom_weights: 自定义因子权重

        Returns:
            分析结果
        """
        # 使用自定义权重或默认权重
        weights = custom_weights if custom_weights else FACTOR_WEIGHTS

        # 收集数据
        stock_data = self.data_collector.collect_stock_data(stock_code)
        news_data = self.data_collector.collect_news_data(stock_code)
        industry_data = self.data_collector.collect_industry_data(stock_code)

        # 执行不同类型的分析
        analysis_results = {}

        if analysis_type in ['comprehensive', 'fundamental']:
            analysis_results['fundamental'] = self._analyze_fundamental(
                stock_data, weights.get('fundamental', 0.30)
            )

        if analysis_type in ['comprehensive', 'technical']:
            analysis_results['technical'] = self._analyze_technical(
                stock_data, weights.get('technical', 0.15)
            )

        if analysis_type in ['comprehensive', 'sentiment']:
            analysis_results['sentiment'] = self._analyze_sentiment(
                news_data, weights.get('sentiment', 0.10)
            )

        # 综合分析
        comprehensive_score = self._calculate_comprehensive_score(
            analysis_results, weights
        )

        # 预测结果
        prediction = self.prediction_service.predict(
            stock_code=stock_code,
            historical_data=stock_data.get('historical', []),
            time_horizon=time_horizon
        )

        return {
            'stock_code': stock_code,
            'analysis_type': analysis_type,
            'time_horizon': time_horizon,
            'analysis_results': analysis_results,
            'comprehensive_score': comprehensive_score,
            'prediction': prediction,
            'factors_considered': list(weights.keys()),
            'analysis_timestamp': datetime.now().isoformat(),
            'recommendation': self._generate_recommendation(comprehensive_score, prediction)
        }

    def _analyze_fundamental(self, stock_data: Dict, weight: float) -> Dict[str, Any]:
        """基本面分析"""
        return self.factor_analyzer.analyze_fundamental_factors(stock_data, weight)

    def _analyze_technical(self, stock_data: Dict, weight: float) -> Dict[str, Any]:
        """技术面分析"""
        return self.factor_analyzer.analyze_technical_factors(stock_data, weight)

    def _analyze_sentiment(self, news_data: Dict, weight: float) -> Dict[str, Any]:
        """情绪面分析"""
        return self.factor_analyzer.analyze_sentiment_factors(news_data, weight)

    def _calculate_comprehensive_score(self, analysis_results: Dict, weights: Dict) -> float:
        """计算综合得分"""
        total_score = 0
        total_weight = 0

        for factor_type, result in analysis_results.items():
            if 'score' in result:
                weight = weights.get(factor_type, 0)
                total_score += result['score'] * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0

    def _generate_recommendation(self, score: float, prediction: Dict) -> str:
        """生成投资建议"""
        if score > 0.5:
            recommendation = "强烈推荐买入"
        elif score > 0.2:
            recommendation = "推荐买入"
        elif score < -0.5:
            recommendation = "强烈推荐卖出"
        elif score < -0.2:
            recommendation = "建议卖出"
        else:
            recommendation = "持有观望"

        return recommendation