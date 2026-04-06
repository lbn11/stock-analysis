"""数据验证器"""
from typing import Dict, Any, Union
from utils.constants import TIME_HORIZONS
from utils.helpers import validate_stock_code


def validate_analysis_request(data: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
    """
    验证分析请求数据

    Args:
        data: 请求数据

    Returns:
        Dict: 验证结果
    """
    errors = []

    # 验证股票代码
    stock_code = data.get('stock_code')
    if not stock_code:
        errors.append("股票代码不能为空")
    elif not validate_stock_code(str(stock_code)):
        errors.append(f"股票代码格式不正确: {stock_code}")

    # 验证分析类型
    analysis_type = data.get('analysis_type', 'comprehensive')
    valid_types = ['comprehensive', 'fundamental', 'technical', 'sentiment']
    if analysis_type not in valid_types:
        errors.append(f"分析类型无效: {analysis_type}. 有效类型: {valid_types}")

    # 验证时间范围
    time_horizon = data.get('time_horizon', 'medium')
    if time_horizon not in TIME_HORIZONS:
        errors.append(f"时间范围无效: {time_horizon}. 有效范围: {list(TIME_HORIZONS.keys())}")

    # 验证自定义因子权重
    custom_weights = data.get('custom_weights')
    if custom_weights:
        if not isinstance(custom_weights, dict):
            errors.append("自定义因子权重必须是字典格式")
        else:
            total_weight = sum(custom_weights.values())
            if abs(total_weight - 1.0) > 0.001:
                errors.append(f"自定义因子权重总和必须为1.0，当前为: {total_weight}")

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


def validate_prediction_params(params: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
    """
    验证预测参数

    Args:
        params: 预测参数

    Returns:
        Dict: 验证结果
    """
    errors = []

    # 验证历史数据长度
    historical_data = params.get('historical_data', [])
    if len(historical_data) < 30:
        errors.append("历史数据长度至少需要30天")

    # 验证预测天数
    prediction_days = params.get('prediction_days', 0)
    if prediction_days <= 0 or prediction_days > 365:
        errors.append("预测天数必须在1-365之间")

    # 验证置信度阈值
    confidence_threshold = params.get('confidence_threshold', 0.5)
    if confidence_threshold < 0 or confidence_threshold > 1:
        errors.append("置信度阈值必须在0-1之间")

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


def validate_factor_data(factor_data: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
    """
    验证因子数据

    Args:
        factor_data: 因子数据

    Returns:
        Dict: 验证结果
    """
    errors = []

    required_fields = ['timestamp', 'factor_type', 'value', 'weight']
    for field in required_fields:
        if field not in factor_data:
            errors.append(f"缺少必要字段: {field}")

    # 验证权重范围
    weight = factor_data.get('weight', 0)
    if weight < 0 or weight > 1:
        errors.append(f"因子权重必须在0-1之间，当前为: {weight}")

    # 验证数值
    value = factor_data.get('value', 0)
    if not isinstance(value, (int, float)):
        errors.append(f"因子值必须是数字，当前类型: {type(value)}")

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }