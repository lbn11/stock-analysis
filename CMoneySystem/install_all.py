#!/usr/bin/env python3
import subprocess
import sys

packages = [
    'flask-cors',
    'pandas',
    'numpy',
    'scikit-learn',
    'snownlp',
    'python-dotenv',
    'pyyaml',
    'gunicorn',
    'akshare',
    'flask-sqlalchemy',
    'flask-migrate'
]

print("开始安装依赖包...")
success_count = 0

for pkg in packages:
    print(f"\n正在安装 {pkg}...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', pkg],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ {pkg} 安装成功")
            success_count += 1
        else:
            print(f"✗ {pkg} 安装失败")
            print(result.stderr)
    except Exception as e:
        print(f"✗ {pkg} 安装异常: {e}")

print(f"\n\n安装完成！成功: {success_count}/{len(packages)}")

# 验证安装
print("\n验证安装...")
for pkg in packages:
    try:
        if pkg == 'flask-sqlalchemy':
            import flask_sqlalchemy
        elif pkg == 'flask-migrate':
            import flask_migrate
        elif pkg == 'python-dotenv':
            import dotenv
        elif pkg == 'pyyaml':
            import yaml
        else:
            __import__(pkg.replace('-', '_'))
        print(f"✓ {pkg}")
    except ImportError:
        print(f"✗ {pkg} 未安装")
