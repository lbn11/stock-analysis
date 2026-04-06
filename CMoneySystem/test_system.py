#!/usr/bin/env python3
"""系统测试脚本"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("CMoney 股价预测系统 - 功能测试")
print("=" * 60)
print()

# 测试1: 模块导入测试
print("【测试1】模块导入测试")
print("-" * 60)

try:
    from services.analysis_engine import AnalysisEngine
    print("✓ AnalysisEngine 导入成功")
except Exception as e:
    print(f"✗ AnalysisEngine 导入失败: {e}")

try:
    from services.factor_analyzer import FactorAnalyzer
    print("✓ FactorAnalyzer 导入成功")
except Exception as e:
    print(f"✗ FactorAnalyzer 导入失败: {e}")

try:
    from services.prediction_service import PredictionService
    print("✓ PredictionService 导入成功")
except Exception as e:
    print(f"✗ PredictionService 导入失败: {e}")

try:
    from data.collector import DataCollector
    print("✓ DataCollector 导入成功")
except Exception as e:
    print(f"✗ DataCollector 导入失败: {e}")

try:
    from data.processor import DataProcessor
    print("✓ DataProcessor 导入成功")
except Exception as e:
    print(f"✗ DataProcessor 导入失败: {e}")

try:
    from utils.constants import FACTOR_WEIGHTS, TIME_HORIZONS
    print("✓ 常量配置导入成功")
    print(f"  - 因子权重: {len(FACTOR_WEIGHTS)} 个")
    print(f"  - 时间维度: {len(TIME_HORIZONS)} 个")
except Exception as e:
    print(f"✗ 常量配置导入失败: {e}")

print()

# 测试2: 数据收集测试
print("【测试2】数据收集功能测试")
print("-" * 60)

try:
    from data.collector import DataCollector

    collector = DataCollector()

    # 测试股票数据收集
    stock_data = collector.collect_stock_data("000001")
    print(f"✓ 股票数据收集成功")
    print(f"  - 股票代码: {stock_data.get('stock_code')}")
    print(f"  - 历史数据条数: {len(stock_data.get('historical', []))}")
    print(f"  - 基本面指标: {len(stock_data.get('fundamental_data', {}))}")

    # 测试新闻数据收集
    news_data = collector.collect_news_data("000001")
    print(f"✓ 新闻数据收集成功")
    print(f"  - 新闻条数: {len(news_data.get('news_items', []))}")

    # 测试行业数据收集
    industry_data = collector.collect_industry_data("000001")
    print(f"✓ 行业数据收集成功")
    print(f"  - 行业名称: {industry_data.get('industry_info', {}).get('industry_name')}")

except Exception as e:
    print(f"✗ 数据收集测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试3: 因子分析测试
print("【测试3】因子分析功能测试")
print("-" * 60)

try:
    from services.factor_analyzer import FactorAnalyzer
    from data.collector import DataCollector

    analyzer = FactorAnalyzer()
    collector = DataCollector()

    # 收集测试数据
    stock_data = collector.collect_stock_data("000001")
    news_data = collector.collect_news_data("000001")

    # 测试基本面分析
    fundamental_result = analyzer.analyze_fundamental_factors(stock_data, 0.30)
    print(f"✓ 基本面分析成功")
    print(f"  - 综合得分: {fundamental_result['score']:.3f}")
    print(f"  - 摘要: {fundamental_result['summary']}")

    # 测试情绪分析
    sentiment_result = analyzer.analyze_sentiment_factors(news_data, 0.10)
    print(f"✓ 情绪分析成功")
    print(f"  - 情绪得分: {sentiment_result['score']:.3f}")
    print(f"  - 正面新闻: {sentiment_result['details']['positive_count']}")
    print(f"  - 负面新闻: {sentiment_result['details']['negative_count']}")

except Exception as e:
    print(f"✗ 因子分析测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试4: 预测服务测试
print("【测试4】预测服务功能测试")
print("-" * 60)

try:
    from services.prediction_service import PredictionService
    from data.collector import DataCollector

    predictor = PredictionService()
    collector = DataCollector()

    # 收集历史数据
    stock_data = collector.collect_stock_data("000001")
    historical_data = stock_data.get('historical', [])

    # 测试短期预测
    short_pred = predictor.predict("000001", historical_data, time_horizon='short')
    print(f"✓ 短期预测成功")
    print(f"  - 趋势: {short_pred['trend_name']}")
    print(f"  - 置信度: {short_pred['confidence']:.2%}")
    print(f"  - 风险等级: {short_pred['risk_level']}")

    # 测试中期预测
    medium_pred = predictor.predict("000001", historical_data, time_horizon='medium')
    print(f"✓ 中期预测成功")
    print(f"  - 趋势: {medium_pred['trend_name']}")
    print(f"  - 置信度: {medium_pred['confidence']:.2%}")

    # 测试长期预测
    long_pred = predictor.predict("000001", historical_data, time_horizon='long')
    print(f"✓ 长期预测成功")
    print(f"  - 趋势: {long_pred['trend_name']}")
    print(f"  - 置信度: {long_pred['confidence']:.2%}")

except Exception as e:
    print(f"✗ 预测服务测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试5: 完整分析流程测试
print("【测试5】完整分析流程测试")
print("-" * 60)

try:
    from services.analysis_engine import AnalysisEngine

    engine = AnalysisEngine()

    # 执行综合分析
    result = engine.analyze(
        stock_code="000001",
        analysis_type="comprehensive",
        time_horizon="medium"
    )

    print(f"✓ 完整分析流程成功")
    print(f"  - 股票代码: {result['stock_code']}")
    print(f"  - 分析类型: {result['analysis_type']}")
    print(f"  - 时间范围: {result['time_horizon']}")
    print(f"  - 综合得分: {result['comprehensive_score']:.3f}")
    print(f"  - 预测趋势: {result['prediction']['trend_name']}")
    print(f"  - 投资建议: {result['recommendation']}")
    print(f"  - 分析因子: {', '.join(result['factors_considered'])}")

except Exception as e:
    print(f"✗ 完整分析流程测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("测试完成！")
print("=" * 60)
print()
print("提示:")
print("1. 如需安装依赖，请运行: pip install -r requirements.txt")
print("2. 如需启动API服务，请运行: python main.py")
print("3. API文档地址: http://localhost:5000/api/health")
print()
