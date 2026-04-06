#!/usr/bin/env python
"""安装依赖包脚本"""
import subprocess
import sys

packages = [
    'pandas',
    'numpy',
    'scikit-learn',
    'akshare',
    'flask-sqlalchemy',
    'flask-migrate',
]

print("正在安装依赖包...")
for package in packages:
    print(f"  安装 {package}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"  ✓ {package} 安装成功")
    except Exception as e:
        print(f"  ✗ {package} 安装失败: {e}")

print("\n安装完成!")
