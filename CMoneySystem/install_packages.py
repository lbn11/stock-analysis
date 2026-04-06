#!/usr/bin/env python3
"""依赖包安装脚本"""
import subprocess
import sys

packages = [
    'numpy',
    'pandas',
    'scikit-learn',
    'flask',
    'flask-sqlalchemy',
    'flask-migrate',
    'requests'
]

print("=" * 60)
print("CMoney系统 - 依赖包安装")
print("=" * 60)
print()

for package in packages:
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功\n")
    except subprocess.CalledProcessError as e:
        print(f"✗ {package} 安装失败: {e}\n")

print("=" * 60)
print("安装完成！")
print("=" * 60)
