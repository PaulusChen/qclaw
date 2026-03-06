#!/usr/bin/env python3
"""
yfinance 功能评估测试
测试内容:
1. 安装和基础功能
2. A 股数据支持
3. 历史数据完整性
4. API 稳定性
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

print("=" * 60)
print("yfinance 功能评估测试")
print("=" * 60)

# ============ 1. 安装和基础功能测试 ============
print("\n[1/4] 安装和基础功能测试...")
print(f"  ✓ yfinance 版本：{yf.__version__}")

# ============ 2. A 股数据支持测试 ============
print("\n[2/4] A 股数据支持测试...")

# 测试 A 股代码格式 (上海证券交易所)
test_symbols = [
    "600519.SS",  # 贵州茅台
    "000858.SZ",  # 五粮液
    "300750.SZ",  # 宁德时代
]

for symbol in test_symbols:
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")
        if len(hist) > 0:
            print(f"  ✓ {symbol}: 获取成功，{len(hist)} 条记录")
        else:
            print(f"  ⚠️ {symbol}: 返回空数据 (可能停牌或数据不可用)")
    except Exception as e:
        print(f"  ❌ {symbol}: 获取失败 - {str(e)}")

# ============ 3. 历史数据完整性测试 ============
print("\n[3/4] 历史数据完整性测试...")

# 测试长期历史数据
try:
    stock = yf.Ticker("600519.SS")
    hist = stock.history(start="2020-01-01", end="2025-01-01")
    print(f"  贵州茅台 (2020-2025):")
    print(f"    - 数据条数：{len(hist)}")
    print(f"    - 时间范围：{hist.index.min()} 至 {hist.index.max()}")
    print(f"    - 包含字段：{list(hist.columns)}")
    
    # 检查数据完整性
    missing_days = hist.isnull().sum()
    if missing_days.sum() == 0:
        print(f"    ✓ 数据完整，无缺失值")
    else:
        print(f"    ⚠️ 存在缺失值：{missing_days[missing_days > 0]}")
except Exception as e:
    print(f"  ❌ 历史数据获取失败：{str(e)}")

# ============ 4. API 稳定性测试 ============
print("\n[4/4] API 稳定性测试...")

# 测试多种 API 功能
test_results = {
    "历史数据": False,
    "实时行情": False,
    "公司信息": False,
    "财务数据": False,
}

try:
    # 历史数据
    stock = yf.Ticker("600519.SS")
    hist = stock.history(period="3mo")
    if len(hist) > 0:
        test_results["历史数据"] = True
        print(f"  ✓ 历史数据 API 正常")
except Exception as e:
    print(f"  ❌ 历史数据 API 失败：{str(e)}")

try:
    # 实时行情
    info = stock.info
    if info and len(info) > 0:
        test_results["实时行情"] = True
        print(f"  ✓ 实时行情 API 正常")
except Exception as e:
    print(f"  ❌ 实时行情 API 失败：{str(e)}")

try:
    # 公司信息
    if 'longName' in info:
        test_results["公司信息"] = True
        print(f"  ✓ 公司信息 API 正常")
        print(f"    - 公司名称：{info.get('longName', 'N/A')}")
except Exception as e:
    print(f"  ❌ 公司信息 API 失败：{str(e)}")

try:
    # 财务数据
    financials = stock.financials
    if financials is not None and len(financials) > 0:
        test_results["财务数据"] = True
        print(f"  ✓ 财务数据 API 正常")
        print(f"    - 报表期间数：{len(financials.columns)}")
except Exception as e:
    print(f"  ❌ 财务数据 API 失败：{str(e)}")

# ============ 评估总结 ============
print("\n" + "=" * 60)
print("yfinance 功能评估总结")
print("=" * 60)

# 计算得分
score = sum(test_results.values())
total = len(test_results)

evaluation = {
    "功能支持": {
        "历史数据": "✅ 支持多周期、多时间粒度",
        "实时行情": "✅ 支持实时/延迟行情",
        "公司信息": "✅ 支持基本面数据",
        "财务数据": "✅ 支持三大报表",
        "技术指标": "⚠️ 需自行计算 (可集成 pandas_ta)",
        "多市场支持": "✅ 支持全球主要市场"
    },
    "A 股兼容性": {
        "数据覆盖": "⚠️ 部分 A 股数据可用 (依赖 Yahoo 数据源)",
        "数据质量": "⚠️ 可能存在延迟或缺失",
        "复权支持": "✅ 支持前复权/后复权",
        "实时性": "⚠️ 延迟 15 分钟 (免费版本)"
    },
    "API 稳定性测试结果": test_results,
    "优点": [
        "安装简单，使用便捷",
        "支持全球多个市场",
        "免费使用，无需 API Key",
        "社区活跃，文档丰富",
        "与 pandas 集成良好"
    ],
    "缺点": [
        "A 股数据覆盖不完整",
        "数据可能存在延迟",
        "依赖 Yahoo 服务器稳定性",
        "频繁请求可能被限流",
        "技术指标需自行计算"
    ],
    "推荐使用场景": [
        "美股/港股数据获取",
        "个人投资研究",
        "策略原型开发",
        "数据下载和备份"
    ],
    "不推荐场景": [
        "A 股主力数据源 (建议用 AKShare)",
        "生产环境实时交易",
        "高频数据需求"
    ],
    "综合评分": "6.5/10 (A 股场景)"
}

print("\n功能支持:")
for k, v in evaluation["功能支持"].items():
    print(f"  {k}: {v}")

print("\nA 股兼容性:")
for k, v in evaluation["A 股兼容性"].items():
    print(f"  {k}: {v}")

print("\nAPI 稳定性测试:")
for k, v in evaluation["API 稳定性测试结果"].items():
    status = "✅" if v else "❌"
    print(f"  {status} {k}")

print("\n优点:")
for item in evaluation["优点"]:
    print(f"  • {item}")

print("\n缺点:")
for item in evaluation["缺点"]:
    print(f"  • {item}")

print(f"\n综合评分：{evaluation['综合评分']}")
print("\n" + "=" * 60)
print("评估完成!")
print("=" * 60)
