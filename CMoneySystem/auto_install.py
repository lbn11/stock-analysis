#!/usr/bin/env python3
"""
数据源依赖自动安装脚本
"""
import subprocess
import sys
import os

def install_package(package_name):
    """安装单个包"""
    try:
        __import__(package_name)
        print(f"✓ {package_name} 已安装")
        return True
    except ImportError:
        print(f"→ 安装 {package_name}...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package_name
            ])
            print(f"✓ {package_name} 安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ {package_name} 安装失败: {e}")
            return False

def main():
    print("=" * 60)
    print("  CMoney 数据源依赖自动安装")
    print("=" * 60)
    print()

    packages = ['akshare', 'pandas', 'numpy', 'requests']

    print(f"准备安装 {len(packages)} 个包...")
    print()

    success_count = 0
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] {package}")
        if install_package(package):
            success_count += 1
        print()

    print("=" * 60)
    print(f"安装完成！成功: {success_count}/{len(packages)}")
    print("=" * 60)
    print()

    # 验证安装
    print("验证安装...")
    print()

    for package in packages:
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✓ {package}: {version}")
        except ImportError:
            print(f"✗ {package}: 未安装")

    print()
    print("=" * 60)
    print("下一步：运行测试脚本")
    print("  python3 test_data_sources.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
