"""预测数据模型"""
from datetime import datetime
from main import db


class PredictionResult(db.Model):
    """预测结果表"""
    __tablename__ = 'prediction_result'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_code = db.Column(db.String(20), nullable=False, index=True)
    time_horizon = db.Column(db.String(20), nullable=False)  # short/medium/long
    horizon_name = db.Column(db.String(50))  # 短期/中期/长期
    horizon_days = db.Column(db.Integer)  # 预测天数

    # 预测结果
    trend = db.Column(db.Integer, nullable=False)  # 1: 上涨, 0: 横盘, -1: 下跌
    trend_name = db.Column(db.String(20))  # 上涨/横盘/下跌
    confidence = db.Column(db.Float, nullable=False)  # 置信度 0-1
    price_change_pct = db.Column(db.Float)  # 预测价格变化百分比

    # 风险评估
    risk_level = db.Column(db.String(20))  # 低/中/高

    # 关键因素
    key_factors = db.Column(db.JSON)  # 影响因素列表

    # 摘要
    summary = db.Column(db.Text)

    # 详细预测数据 (JSON格式)
    prediction_details = db.Column(db.JSON)

    # 时间戳
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PredictionResult {self.stock_code} - {self.time_horizon} - {self.trend_name}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'time_horizon': self.time_horizon,
            'horizon_name': self.horizon_name,
            'horizon_days': self.horizon_days,
            'trend': self.trend,
            'trend_name': self.trend_name,
            'confidence': self.confidence,
            'price_change_pct': self.price_change_pct,
            'risk_level': self.risk_level,
            'key_factors': self.key_factors,
            'summary': self.summary,
            'prediction_details': self.prediction_details,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StockPriceHistory(db.Model):
    """股票价格历史数据表"""
    __tablename__ = 'stock_price_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_code = db.Column(db.String(20), nullable=False, index=True)
    trade_date = db.Column(db.Date, nullable=False, index=True)

    # OHLCV数据
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    turnover = db.Column(db.Float)  # 成交额

    # 涨跌幅
    change_pct = db.Column(db.Float)  # 涨跌幅
    change_amount = db.Column(db.Float)  # 涨跌额

    # 技术指标
    ma5 = db.Column(db.Float)  # 5日均线
    ma10 = db.Column(db.Float)  # 10日均线
    ma20 = db.Column(db.Float)  # 20日均线
    ma60 = db.Column(db.Float)  # 60日均线
    ema12 = db.Column(db.Float)  # 12日EMA
    ema26 = db.Column(db.Float)  # 26日EMA
    macd = db.Column(db.Float)  # MACD
    signal = db.Column(db.Float)  # Signal线
    histogram = db.Column(db.Float)  # MACD柱状图
    rsi = db.Column(db.Float)  # RSI指标
    bollinger_upper = db.Column(db.Float)  # 布林带上轨
    bollinger_middle = db.Column(db.Float)  # 布林带中轨
    bollinger_lower = db.Column(db.Float)  # 布林带下轨

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('stock_code', 'trade_date', name='uq_stock_date'),
    )

    def __repr__(self):
        return f'<StockPriceHistory {self.stock_code} - {self.trade_date}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'trade_date': self.trade_date.isoformat() if self.trade_date else None,
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume,
            'turnover': self.turnover,
            'change_pct': self.change_pct,
            'change_amount': self.change_amount,
            'technical_indicators': {
                'ma5': self.ma5,
                'ma10': self.ma10,
                'ma20': self.ma20,
                'ma60': self.ma60,
                'ema12': self.ema12,
                'ema26': self.ema26,
                'macd': self.macd,
                'signal': self.signal,
                'histogram': self.histogram,
                'rsi': self.rsi,
                'bollinger_upper': self.bollinger_upper,
                'bollinger_middle': self.bollinger_middle,
                'bollinger_lower': self.bollinger_lower
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AnalysisTask(db.Model):
    """分析任务表"""
    __tablename__ = 'analysis_task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    stock_code = db.Column(db.String(20), nullable=False, index=True)
    analysis_type = db.Column(db.String(50), nullable=False)
    time_horizon = db.Column(db.String(20))

    # 任务状态
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending/running/completed/failed
    progress = db.Column(db.Integer, default=0)  # 进度 0-100

    # 任务参数
    parameters = db.Column(db.JSON)

    # 任务结果
    result = db.Column(db.JSON)
    error_message = db.Column(db.Text)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AnalysisTask {self.task_id} - {self.status}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'stock_code': self.stock_code,
            'analysis_type': self.analysis_type,
            'time_horizon': self.time_horizon,
            'status': self.status,
            'progress': self.progress,
            'parameters': self.parameters,
            'result': self.result,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class User(db.Model):
    """用户表"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # 用户信息
    full_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))

    # 权限和状态
    role = db.Column(db.String(20), default='user')  # admin/user/guest
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'full_name': self.full_name,
            'phone': self.phone if include_sensitive else None,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        return {k: v for k, v in data.items() if v is not None or include_sensitive}
