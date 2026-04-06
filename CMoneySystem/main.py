from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
import os

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    from api.routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV'))
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))