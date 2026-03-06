#!/usr/bin/env python3
"""
Backtrader 回测示例

演示如何使用 backtrader 框架进行回测:
1. 加载历史数据
2. 配置交易策略
3. 运行回测
4. 分析结果

使用方法:
    python examples/backtrader_example.py --data data/stock_data.csv --output results/backtrader_demo
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backtest import BacktraderWrapper, QclawStrategy, run_backtest


def generate_sample_data(n_days: int = 500) -> pd.DataFrame:
    """
    生成示例 A 股数据
    
    参数:
        n_days: 数据天数
        
    返回:
        pandas DataFrame
    """
    np.random.seed(42)
    
    # 生成日期 (跳过周末)
    start_date = datetime(2023, 1, 1)
    dates = []
    current = start_date
    while len(dates) < n_days:
        if current.weekday() < 5:  # 周一至周五
            dates.append(current)
        current += timedelta(days=1)
    
    # 生成 OHLCV 数据 (随机游走)
    base_price = 50.0
    returns = np.random.randn(n_days) * 0.02
    
    # 价格序列
    prices = base_price * np.cumprod(1 + returns)
    
    # OHLCV
    open_prices = prices * (1 + np.random.randn(n_days) * 0.005)
    high_prices = np.maximum(open_prices, prices) * (1 + np.random.rand(n_days) * 0.01)
    low_prices = np.minimum(open_prices, prices) * (1 - np.random.rand(n_days) * 0.01)
    volumes = np.random.randint(1000000, 10000000, n_days)
    
    # 成交额和换手率
    amounts = volumes * prices
    turnover = volumes / 10000000 * 100  # 假设总股本 1000 万股
    
    df = pd.DataFrame({
        'date': [d.strftime('%Y-%m-%d') for d in dates],
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': prices,
        'volume': volumes,
        'adj_close': prices,  # 简化处理
        'amount': amounts,
        'turnover': turnover,
    })
    
    return df


def run_demo_backtest(data_path: str, output_dir: str):
    """
    运行演示回测
    
    参数:
        data_path: 数据文件路径
        output_dir: 输出目录
    """
    print("=" * 60)
    print("Backtrader 回测示例")
    print("=" * 60)
    
    # 加载数据
    print(f"\n[1/4] 加载数据：{data_path}")
    df = pd.read_csv(data_path)
    print(f"  → 数据范围：{df['date'].min()} 至 {df['date'].max()}")
    print(f"  → 数据条数：{len(df)}")
    
    # 创建回测包装器
    print(f"\n[2/4] 配置回测参数")
    wrapper = BacktraderWrapper(
        initial_cash=100000.0,  # 10 万初始资金
        commission=0.00025,      # 万分之 2.5 佣金
        stamp_duty=0.001,        # 0.1% 印花税
        slippage=0.001,          # 0.1% 滑点
    )
    
    # 加载数据
    wrapper.load_data(
        df,
        from_date='2023-01-01',
        to_date='2023-12-31',
    )
    
    # 添加策略
    print(f"\n[3/4] 添加交易策略")
    wrapper.add_strategy(
        QclawStrategy,
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        rsi_period=14,
        rsi_oversold=30,
        rsi_overbought=70,
        take_profit=0.05,   # 5% 止盈
        stop_loss=0.03,     # 3% 止损
        position_size=0.1,  # 10% 仓位
    )
    
    # 添加分析器
    wrapper.add_analyzer()
    
    # 运行回测
    print(f"\n[4/4] 运行回测...")
    results = wrapper.run()
    
    # 保存结果
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存图表
    wrapper.plot(str(output_path / 'backtest_chart.png'))
    
    # 保存权益曲线
    if 'equity_curve' in results:
        equity_df = pd.DataFrame({
            'equity': results['equity_curve'],
        })
        equity_df.to_csv(output_path / 'equity_curve.csv', index=False)
    
    print(f"\n结果已保存到：{output_dir}")
    print(f"  → 图表：{output_path / 'backtest_chart.png'}")
    print(f"  → 权益曲线：{output_path / 'equity_curve.csv'}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Backtrader 回测示例")
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="数据文件路径 (CSV)，不提供则生成示例数据"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/backtrader_demo",
        help="输出目录"
    )
    parser.add_argument(
        "--generate-sample",
        action="store_true",
        help="生成示例数据并保存"
    )
    args = parser.parse_args()
    
    # 如果未提供数据文件，生成示例数据
    if args.data is None:
        print("\n未提供数据文件，生成示例数据...")
        df = generate_sample_data(n_days=500)
        
        # 保存示例数据
        sample_path = Path("data/sample_stock_data.csv")
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(sample_path, index=False)
        print(f"示例数据已保存到：{sample_path}")
        
        args.data = str(sample_path)
    
    # 运行回测
    run_demo_backtest(args.data, args.output)


if __name__ == "__main__":
    main()
