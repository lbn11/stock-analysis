"""API路由定义"""
from flask import Blueprint, request, jsonify
from services.analysis_engine import AnalysisEngine
from services.factor_analyzer import FactorAnalyzer
from services.prediction_service import PredictionService
from utils.validators import validate_analysis_request
from utils.constants import TIME_HORIZONS
import traceback

bp = Blueprint('api', __name__)

@bp.route('/analyze', methods=['POST'])
def analyze_stock():
    """股票分析接口"""
    try:
        data = request.get_json()

        # 验证请求数据
        validation_result = validate_analysis_request(data)
        if not validation_result['is_valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid input',
                'details': validation_result['errors']
            }), 400

        # 获取参数
        stock_code = data['stock_code']
        analysis_type = data.get('analysis_type', 'comprehensive')
        time_horizon = data.get('time_horizon', 'medium')
        custom_weights = data.get('custom_weights')

        # 执行分析
        engine = AnalysisEngine()
        result = engine.analyze(
            stock_code=stock_code,
            analysis_type=analysis_type,
            time_horizon=time_horizon,
            custom_weights=custom_weights
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        print(f"Error in analyze_stock: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@bp.route('/predict', methods=['POST'])
def predict_stock():
    """股价预测接口"""
    try:
        data = request.get_json()

        # 验证请求数据
        from utils.validators import validate_prediction_params
        validation_result = validate_prediction_params(data)
        if not validation_result['is_valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid input',
                'details': validation_result['errors']
            }), 400

        # 获取参数
        stock_code = data.get('stock_code')
        historical_data = data.get('historical_data', [])
        prediction_days = data.get('prediction_days', 30)
        time_horizon = data.get('time_horizon', 'short')

        # 执行预测
        predictor = PredictionService()
        result = predictor.predict(
            stock_code=stock_code,
            historical_data=historical_data,
            prediction_days=prediction_days,
            time_horizon=time_horizon
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        print(f"Error in predict_stock: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@bp.route('/factors', methods=['GET'])
def get_factors():
    """获取因子权重配置"""
    try:
        from utils.constants import FACTOR_WEIGHTS

        return jsonify({
            'success': True,
            'data': {
                'factor_weights': FACTOR_WEIGHTS,
                'time_horizons': TIME_HORIZONS
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'data': {
            'status': 'healthy',
            'service': 'CMoney System API'
        }
    })