#!/usr/bin/env python3
"""测试真实数据源获取"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("测试真实数据源")
print("=" * 60)
print()

# 测试1: 检查依赖
print("【测试1】检查依赖")
print("-" * 60)

try:
    import akshare as ak
    print("✓ AkShare 已安装")
    print(f"  版本: {ak.__version__}")
except ImportError:
    print("✗ AkShare 未安装")
    print()
    print("请运行以下命令安装:")
    print("  pip install akshare")
    sys.exit(1)

try:
    import requests
    print("✓ requests 已安装")
except ImportError:
    print("✗ requests 未安装")
    print()
    print("请运行以下命令安装:")
    print("  pip install requests")
    sys.exit(1)

print()

# 测试2: 导入数据源
print("【测试2】导入数据源模块")
print("-" * 60)

try:
    from data_sources.akshare_source import AkShareDataSource
    print("✓ AkShareDataSource 导入成功")
except Exception as e:
    print(f"✗ AkShareDataSource 导入失败: {e}")
    sys.exit(1)

try:
    from data_sources.sina_finance import SinaFinanceDataSource
    print("✓ SinaFinanceDataSource 导入成功")
except Exception as e:
    print(f"✗ SinaFinanceDataSource 导入失败: {e}")

print()

# 测试3: AkShare 获取实时行情
print("【测试3】AkShare 获取实时行情")
print("-" * 60)

akshare_source = AkShareDataSource()

test_stocks = ['000001', '000002', '600000', '600036']

for stock_code in test_stocks[:2]:  # 只测试前2个
    print(f"\n获取 {stock_code} 实时行情...")
    quote = akshare_source.get_stock_quote(stock_code)

    if quote:
        print(f"  ✓ 成功!")
        print(f"  名称: {quote.get('name', 'N/A')}")
        print(f"  最新价: {quote.get('current', 'N/A')}")
        print(f"  涨跌幅: {quote.get('change_pct', 0)*100:.2f}%")
        print(f"  成交量: {quote.get('volume', 0):,}")
    else:
        print(f"  ✗ 失败")

print()

# 测试4: AkShare 获取历史数据
print("【测试4】AkShare 获取历史数据")
print("-" * 60)

stock_code = '000001'
print(f"\n获取 {stock_code} 历史数据...")

history = akshare_source.get_stock_history(
    stock_code=stock_code,
    start_date='2024-01-01',
    end_date='2024-12-31'
)

if history:
    print(f"  ✓ 成功! 获取 {len(history)} 条记录")
    if len(history) > 0:
        latest = history[-1]
        print(f"  最新日期: {latest.get('date', 'N/A')}")
        print(f"  收盘价: {latest.get('close', 'N/A')}")
        print(f"  涨跌幅: {latest.get('change_pct', 0)*100:.2f}%")
else:
    print(f"  ✗ 失败")

print()

# 测试5: AkShare 获取宏观经济数据
print("【测试5】AkShare 获取宏观经济数据")
print("-" * 60)

print("\n获取宏观经济数据...")
macro_data = akshare_source.get_macro_data()

if macro_data:
    print("  ✓ 成功!")
    if 'gdp' in macro_data:
        gdp = macro_data['gdp']
        print(f"  GDP: {gdp.get('period', 'N/A')} - 增长 {gdp.get('growth_rate', 0):.2f}%")
    if 'cpi' in macro_data:
        cpi = macro_data['cpi']
        print(f"  CPI: {cpi.get('period', 'N/A')} - 同比 {cpi.get('value', 0):.2f}%")
    if 'pmi' in macro_data:
        pmi = macro_data['pmi']
        print(f"  PMI: 制造业 {pmi.get('manufacturing', 0):.1f}")
else:
    print("  ✗ 失败")

print()

# 测试6: 新浪财经获取实时行情
print("【测试6】新浪财经获取实时行情")
print("-" * 60)

sina_source = SinaFinanceDataSource()

for stock_code in test_stocks[:2]:  # 只测试前2个
    print(f"\n获取 {stock_code} 实时行情...")
    quote = sina_source.get_stock_quote(stock_code)

    if quote:
        print(f"  ✓ 成功!")
        print(f"  名称: {quote.get('name', 'N/A')}")
        print(f"  最新价: {quote.get('current', 'N/A')}")
        print(f"  涨跌幅: {quote.get('change_pct', 0)*100:.2f}%")
    else:
        print(f"  ✗ 失败")

print()
print("=" * 60)
print("测试完成!")
print("=" * 60)
print()
print("如果所有测试都通过，说明数据源集成成功！")
print("你可以在系统中使用真实数据了。")
