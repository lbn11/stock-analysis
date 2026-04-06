#!/bin/bash
# 安装依赖包脚本

echo "开始安装依赖包..."
python3 -m pip install numpy pandas scikit-learn flask flask-sqlalchemy flask-migrate requests
echo "依赖包安装完成！"
