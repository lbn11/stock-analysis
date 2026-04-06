#!/bin/bash
# CMoney系统快速启动脚本

echo "======================================"
echo "  CMoney 股价预测系统 - 快速启动"
echo "======================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✓ Python3 已安装: $(python3 --version)"
echo ""

# 检查依赖
echo "【步骤1】检查依赖包..."
if pip3 list | grep -q "flask"; then
    echo "✓ Flask 已安装"
else
    echo "⚠️ Flask 未安装"
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
fi

echo ""

# 运行测试
echo "【步骤2】运行系统测试..."
echo ""
python3 test_system.py

echo ""
echo "======================================"
echo "启动完成！"
echo "======================================"
echo ""
echo "下一步操作："
echo "1. 查看测试结果，确认所有模块正常"
echo "2. 如需启动API服务: python3 main.py"
echo "3. 访问 http://localhost:5000/api/health 测试API"
echo ""
