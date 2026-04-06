import os
from datetime import timedelta


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cmoney_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # API配置
    API_TIMEOUT = 30
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 分析配置
    DEFAULT_SHORT_TERM_DAYS = 90  # 短期预测天数
    DEFAULT_MEDIUM_TERM_DAYS = 365  # 中期预测天数
    DEFAULT_LONG_TERM_DAYS = 1095  # 长期预测天数

    # 模型配置
    MODEL_VERSION = "v1.0.0"
    CONFIDENCE_THRESHOLD = 0.6  # 置信度阈值

    # 数据源配置
    FINANCIAL_NEWS_API = os.environ.get('FINANCIAL_NEWS_API')
    STOCK_DATA_API = os.environ.get('STOCK_DATA_API')

    # 调度配置
    ANALYSIS_SCHEDULER_INTERVAL = timedelta(hours=1)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///cmoney_dev.db'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}