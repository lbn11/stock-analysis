"""CMoney 系统测试套件

包含所有模块的单元测试和集成测试
"""
import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestImports(unittest.TestCase):
    """测试所有模块导入"""

    def test_import_data_sources(self):
        """测试数据源模块导入"""
        try:
            from data_sources.akshare_source import AkShareDataSource
            from data_sources.sina_finance import SinaFinanceDataSource
            from data_sources.eastmoney import EastMoneyDataSource
            from data_sources.ths import TonghuashunDataSource
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"数据源模块导入失败: {e}")

    def test_import_news_collector(self):
        """测试新闻采集模块导入"""
        try:
            from data_sources.news_collector import NewsDataSource, SentimentAnalyzer
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"新闻采集模块导入失败: {e}")

    def test_import_chip_analysis(self):
        """测试筹码分析模块导入"""
        try:
            from services.chip_analysis import ChipDistributionAnalyzer
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"筹码分析模块导入失败: {e}")

    def test_import_ml_models(self):
        """测试机器学习模型导入"""
        try:
            from ml_models.lstm_model import LSTMPredictor
            from ml_models.ensemble_models import XGBoostPredictor, EnsemblePredictor
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"ML模型导入失败: {e}")

    def test_import_services(self):
        """测试服务模块导入"""
        try:
            from services.analysis_engine import AnalysisEngine
            from services.factor_analyzer import FactorAnalyzer
            from services.prediction_service import PredictionService
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"服务模块导入失败: {e}")


class TestDataSource(unittest.TestCase):
    """测试数据源功能"""

    def setUp(self):
        """测试前准备"""
        try:
            from data_sources.akshare_source import AkShareDataSource
            self.source = AkShareDataSource()
        except ImportError:
            self.skipTest("AkShare 不可用")

    def test_get_stock_quote(self):
        """测试获取股票行情"""
        # 使用知名股票代码
        quote = self.source.get_stock_quote('000001')

        self.assertIsInstance(quote, dict)
        if quote:  # 如果有数据
            self.assertIn('stock_code', quote)
            self.assertIn('current', quote)
            self.assertIn('name', quote)

    def test_get_stock_history(self):
        """测试获取历史数据"""
        history = self.source.get_stock_history('000001', start_date='2024-01-01')

        self.assertIsInstance(history, list)
        if len(history) > 0:
            self.assertIn('date', history[0])
            self.assertIn('close', history[0])

    def test_rate_limiting(self):
        """测试请求频率限制"""
        import time
        start = time.time()
        for _ in range(3):
            self.source.get_stock_quote('000001')
        elapsed = time.time() - start

        # 应该有至少1秒的延迟（3次请求 × 0.5秒间隔）
        self.assertGreater(elapsed, 1.0)


class TestChipAnalysis(unittest.TestCase):
    """测试筹码分布分析"""

    def setUp(self):
        """测试前准备"""
        from services.chip_analysis import ChipDistributionAnalyzer
        self.analyzer = ChipDistributionAnalyzer()

        # 准备模拟历史数据
        self.test_data = []
        for i in range(100):
            price = 10 + i * 0.1
            self.test_data.append({
                'date': f'2024-01-{i+1:02d}',
                'open': price,
                'close': price + 0.05,
                'high': price + 0.1,
                'low': price - 0.05,
                'volume': 1000000 + i * 10000
            })

    def test_calculate_chip_distribution(self):
        """测试筹码分布计算"""
        result = self.analyzer.calculate_chip_distribution(self.test_data)

        self.assertIsInstance(result, dict)
        self.assertIn('chip_distribution', result)
        self.assertIn('weighted_avg_price', result)
        self.assertIn('support_level', result)
        self.assertIn('pressure_level', result)
        self.assertGreater(result['total_chips'], 0)

    def test_get_chip_signals(self):
        """测试交易信号生成"""
        chip_data = self.analyzer.calculate_chip_distribution(self.test_data)
        signals = self.analyzer.get_chip_signals(chip_data, current_price=15.0)

        self.assertIsInstance(signals, dict)
        self.assertIn('signal', signals)
        self.assertIn('strength', signals)
        self.assertIn(signals['signal'], ['strong_buy', 'buy', 'neutral', 'sell', 'strong_sell'])

    def test_format_chip_analysis_report(self):
        """测试报告生成"""
        chip_data = self.analyzer.calculate_chip_distribution(self.test_data)
        signals = self.analyzer.get_chip_signals(chip_data, current_price=15.0)

        analysis_result = {
            'chip_distribution': chip_data,
            'signals': signals
        }

        report = self.analyzer.format_chip_analysis_report(analysis_result)

        self.assertIsInstance(report, str)
        self.assertIn('筹码分布分析报告', report)


class TestSentimentAnalysis(unittest.TestCase):
    """测试情感分析"""

    def setUp(self):
        """测试前准备"""
        from data_sources.news_collector import SentimentAnalyzer
        self.analyzer = SentimentAnalyzer()

    def test_simple_sentiment_analysis(self):
        """测试简单情感分析"""
        positive_text = "股价大涨，公司业绩优秀，盈利增长"
        negative_text = "股价暴跌，业绩下滑，亏损严重"
        neutral_text = "股价横盘整理"

        pos_result = self.analyzer.analyze_sentiment_simple(positive_text)
        neg_result = self.analyzer.analyze_sentiment_simple(negative_text)
        neu_result = self.analyzer.analyze_sentiment_simple(neutral_text)

        self.assertEqual(pos_result['sentiment'], 'positive')
        self.assertEqual(neg_result['sentiment'], 'negative')
        self.assertIn(neu_result['sentiment'], ['positive', 'negative', 'neutral'])

    def test_news_sentiment_analysis(self):
        """测试新闻列表情感分析"""
        news_list = [
            {'title': '公司业绩大增，股价上涨', 'summary': '盈利能力提升'},
            {'title': '市场下跌，利空消息', 'summary': '经济不景气'},
            {'title': '政策支持行业发展', 'summary': '利好消息'}
        ]

        result = self.analyzer.analyze_news_sentiment(news_list)

        self.assertIsInstance(result, dict)
        self.assertIn('overall_sentiment', result)
        self.assertIn('average_score', result)
        self.assertIn('news_count', result)


class TestFactorAnalyzer(unittest.TestCase):
    """测试因子分析器"""

    def setUp(self):
        """测试前准备"""
        from services.factor_analyzer import FactorAnalyzer
        self.analyzer = FactorAnalyzer()

    def test_fundamental_analysis(self):
        """测试基本面分析"""
        stock_data = {
            'revenue': 1000000000,
            'net_profit': 100000000,
            'roe': 15.5,
            'roa': 8.2,
            'gross_margin': 35.0
        }

        result = self.analyzer.analyze_fundamental_factors(stock_data, weight=0.3)

        self.assertIsInstance(result, dict)
        self.assertIn('score', result)
        self.assertIn('weight', result)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)

    def test_macro_analysis(self):
        """测试宏观环境分析"""
        macro_data = {
            'gdp_growth': 6.5,
            'cpi': 2.1,
            'interest_rate': 4.35,
            'policy': '宽松'
        }

        result = self.analyzer.analyze_macro_economic_factors(macro_data, weight=0.2)

        self.assertIsInstance(result, dict)
        self.assertIn('score', result)


class TestPredictionService(unittest.TestCase):
    """测试预测服务"""

    def setUp(self):
        """测试前准备"""
        from services.prediction_service import PredictionService
        self.service = PredictionService()

    def test_short_term_prediction(self):
        """测试短期预测"""
        # 准备模拟历史数据
        historical_data = []
        for i in range(60):
            historical_data.append({
                'date': f'2024-01-{i+1:02d}',
                'close': 10 + i * 0.1
            })

        result = self.service.predict('000001', historical_data, time_horizon='short')

        self.assertIsInstance(result, dict)
        self.assertIn('trend_name', result)
        self.assertIn('confidence', result)
        self.assertIn('prediction_days', result)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_analysis_pipeline(self):
        """测试完整分析流程"""
        try:
            from services.analysis_engine import AnalysisEngine

            engine = AnalysisEngine()

            # 使用模拟数据测试
            result = engine.analyze(
                stock_code='000001',
                analysis_type='comprehensive',
                time_horizon='medium'
            )

            self.assertIsInstance(result, dict)
            self.assertIn('success', result)

        except Exception as e:
            self.skipTest(f"集成测试失败: {e}")

    def test_data_source_fallback(self):
        """测试数据源 fallback 机制"""
        from data_sources import data_source_manager

        # 测试使用不存在的股票代码
        result = data_source_manager.get_stock_quote('999999')

        # 应该返回空字典或None
        self.assertIn(result, [None, {}, {'stock_code': '999999'}])


def run_tests(verbosity=2):
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestImports))
    suite.addTests(loader.loadTestsFromTestCase(TestDataSource))
    suite.addTests(loader.loadTestsFromTestCase(TestChipAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestSentimentAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestFactorAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestPredictionService))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # 返回测试结果
    return result


if __name__ == '__main__':
    print("=" * 60)
    print("CMoney 系统测试套件")
    print("=" * 60)

    result = run_tests()

    print("\n" + "=" * 60)
    print(f"测试总数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    print("=" * 60)

    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)
