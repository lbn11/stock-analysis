#!/bin/bash
# 数据源依赖安装脚本

echo "=========================================="
echo "  CMoney 数据源依赖安装"
echo "=========================================="
echo ""

# 检查 Python 版本
echo "【1/5】检查 Python 版本..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python3 未安装，请先安装 Python3"
    exit 1
fi

echo "✓ Python3 已安装"
echo ""

# 更新 pip
echo "【2/5】更新 pip..."
python3 -m pip install --upgrade pip -q

echo "✓ pip 已更新"
echo ""

# 安装 requests（如果未安装）
echo "【3/5】安装 requests..."
python3 -m pip show requests > /dev/null 2>&1

if [ $? -ne 0 ]; then
    python3 -m pip install requests -q
    echo "✓ requests 已安装"
else
    echo "✓ requests 已存在"
fi

echo ""

# 安装 pandas 和 numpy
echo "【4/5】安装 pandas 和 numpy..."
python3 -m pip show pandas > /dev/null 2>&1

if [ $? -ne 0 ]; then
    python3 -m pip install pandas numpy -q
    echo "✓ pandas 和 numpy 已安装"
else
    echo "✓ pandas 和 numpy 已存在"
fi

echo ""

# 安装 AkShare
echo "【5/5】安装 AkShare..."
python3 -m pip show akshare > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "正在安装 AkShare，这可能需要几分钟..."
    python3 -m pip install akshare
    echo "✓ AkShare 已安装"
else
    echo "✓ AkShare 已存在"
fi

echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""

# 验证安装
echo "验证安装..."
python3 -c "import akshare; print('✓ AkShare 版本:', akshare.__version__)" 2>&1
python3 -c "import pandas; print('✓ Pandas 版本:', pandas.__version__)" 2>&1
python3 -c "import numpy; print('✓ NumPy 版本:', numpy.__version__)" 2>&1
python3 -c "import requests; print('✓ Requests 版本:', requests.__version__)" 2>&1

echo ""
echo "现在可以运行测试脚本了："
echo "  python3 test_data_sources.py"
