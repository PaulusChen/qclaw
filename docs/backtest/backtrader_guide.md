# Backtrader 回测框架使用指南

**创建日期:** 2026-03-06  
**任务:** CODE-BT-001  
**状态:** ✅ 已完成

---

## 📦 简介

Backtrader 是一个功能强大的 Python 回测框架，支持:

- ✅ 多种市场 (股票、期货、外汇、加密货币)
- ✅ 丰富的技术指标库
- ✅ 灵活的交易策略定义
- ✅ 详细的性能分析报告
- ✅ 实时交易支持

**官方文档:** https://www.backtrader.com  
**GitHub:** https://github.com/mementum/backtrader

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install backtrader pandas numpy
```

### 2. 基础回测示例

```python
from src.backtest import BacktraderWrapper, QclawStrategy, run_backtest

# 方法 1: 使用便捷函数
results = run_backtest(
    data_path="data/stock_data.csv",
    strategy_class=QclawStrategy,
    initial_cash=100000,
    from_date="2023-01-01",
    to_date="2023-12-31",
    output_dir="results/backtest",
    macd_fast=12,
    macd_slow=26,
    rsi_period=14,
)

# 方法 2: 使用包装器 (更灵活)
wrapper = BacktraderWrapper(initial_cash=100000)

# 加载数据
import pandas as pd
df = pd.read_csv("data/stock_data.csv")
wrapper.load_data(df, from_date="2023-01-01", to_date="2023-12-31")

# 添加策略
wrapper.add_strategy(
    QclawStrategy,
    macd_fast=12,
    macd_slow=26,
    take_profit=0.05,
    stop_loss=0.03,
)

# 添加分析器
wrapper.add_analyzer()

# 运行回测
results = wrapper.run()

# 绘制图表
wrapper.plot("results/backtest_chart.png")
```

---

## 📊 数据格式

### 必需列

| 列名 | 说明 | 类型 |
|------|------|------|
| `date` | 日期 (YYYY-MM-DD) | string/datetime |
| `open` | 开盘价 | float |
| `high` | 最高价 | float |
| `low` | 最低价 | float |
| `close` | 收盘价 | float |
| `volume` | 成交量 | int |

### 可选列

| 列名 | 说明 |
|------|------|
| `adj_close` | 复权收盘价 |
| `amount` | 成交额 |
| `turnover` | 换手率 |

### 示例数据

```csv
date,open,high,low,close,volume,adj_close,amount,turnover
2023-01-01,50.5,51.2,49.8,50.0,1000000,50.0,50000000,1.5
2023-01-02,50.2,51.5,50.0,51.0,1200000,51.0,61200000,1.8
```

---

## 🎯 交易策略

### 内置策略：QclawStrategy

基于 MACD + RSI 的趋势跟踪策略:

**买入信号:**
- MACD 金叉 (MACD 线上穿信号线)
- RSI 超卖 (< 30)

**卖出信号:**
- 止盈 (5% 默认)
- 止损 (3% 默认)

**参数配置:**

```python
QclawStrategy(
    # MACD 参数
    macd_fast=12,          # 快线周期
    macd_slow=26,          # 慢线周期
    macd_signal=9,         # 信号线周期
    
    # RSI 参数
    rsi_period=14,         # RSI 周期
    rsi_oversold=30,       # 超卖阈值
    rsi_overbought=70,     # 超买阈值
    
    # 风控参数
    take_profit=0.05,      # 止盈比例 (5%)
    stop_loss=0.03,        # 止损比例 (3%)
    
    # 仓位管理
    position_size=0.1,     # 单次仓位 (10%)
)
```

### 自定义策略

继承 `bt.Strategy` 创建自定义策略:

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (
        ('period', 14),
    )
    
    def __init__(self):
        # 初始化指标
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
    
    def next(self):
        # 每个 bar 执行
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()  # 买入
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()  # 卖出
```

---

## 📈 性能指标

回测完成后，`QclawAnalyzer` 会计算以下指标:

| 指标 | 说明 | 优秀标准 |
|------|------|----------|
| **总收益率** | 整个回测期的总收益 | > 20% |
| **年化收益率** | 年化后的收益率 | > 15% |
| **夏普比率** | 风险调整后收益 | > 1.5 |
| **最大回撤** | 最大亏损幅度 | < 15% |
| **胜率** | 盈利交易占比 | > 55% |
| **盈亏比** | 平均盈利/平均亏损 | > 1.5 |
| **波动率** | 收益波动程度 | < 20% |
| **Calmar 比率** | 收益/最大回撤 | > 2.0 |

---

## ⚙️ 高级配置

### A 股佣金配置

```python
from src.backtest import QclawCommission

# 自定义佣金
commission = QclawCommission(
    commission=0.00025,    # 万分之 2.5
    stamp_duty=0.001,      # 0.1% (卖出收取)
    min_commission=5.0,    # 最低 5 元
    slippage=0.001,        # 0.1% 滑点
)

wrapper.cerebro.broker.addcommissioninfo(commission)
```

### 仓位管理

```python
from src.backtest import QclawSizing

# 自定义仓位
sizer = QclawSizing(
    stake=100,          # 默认 100 股
    stake_perc=0.1,     # 按资金 10% 下单
    roundto=100,        # 100 股整数倍 (A 股一手)
)

wrapper.cerebro.addsizer(sizer)
```

### 添加技术指标

```python
import backtrader as bt

# MACD
macd = bt.indicators.MACD(data.close)

# RSI
rsi = bt.indicators.RSI(data.close, period=14)

# KDJ
kdj = bt.indicators.Stochastic(data.close, period=14)

# 布林带
bollinger = bt.indicators.BollingerBands(data.close, period=20)

# 移动平均线
sma20 = bt.indicators.SMA(data.close, period=20)
sma60 = bt.indicators.SMA(data.close, period=60)
```

---

## 📁 输出文件

运行回测后，会生成以下文件:

```
results/backtest/
├── backtest_results.json    # 回测结果 (JSON)
├── equity_curve.csv         # 权益曲线数据
└── backtest_chart.png       # 回测图表
```

### 回测结果 JSON 示例

```json
{
  "total_return": 0.2534,
  "annual_return": 0.2534,
  "sharpe_ratio": 1.85,
  "max_drawdown": -0.12,
  "win_rate": 0.58,
  "profit_loss_ratio": 1.92,
  "volatility": 0.18,
  "calmar_ratio": 2.11,
  "total_trades": 45,
  "winning_trades": 26,
  "losing_trades": 19,
  "final_equity": 125340.0,
  "initial_equity": 100000.0
}
```

---

## 🔧 常见问题

### Q: 如何优化策略参数？

使用网格搜索:

```python
from itertools import product

best_sharpe = 0
best_params = None

for fast, slow in product([10, 12, 14], [24, 26, 28]):
    wrapper = BacktraderWrapper()
    wrapper.load_data(df)
    wrapper.add_strategy(QclawStrategy, macd_fast=fast, macd_slow=slow)
    wrapper.add_analyzer()
    results = wrapper.run()
    
    if results['sharpe_ratio'] > best_sharpe:
        best_sharpe = results['sharpe_ratio']
        best_params = {'macd_fast': fast, 'macd_slow': slow}

print(f"最佳参数：{best_params}, 夏普比率：{best_sharpe:.2f}")
```

### Q: 如何支持多只股票？

```python
# 添加多个数据源
for stock_code in ['000001', '000002', '600000']:
    df = load_stock_data(stock_code)
    data = QclawDataFeed(dataname=df)
    cerebro.adddata(data)
```

### Q: 如何添加自定义指标？

```python
class MyIndicator(bt.Indicator):
    lines = ('my_line',)
    params = (('period', 14),)
    
    def __init__(self):
        self.lines.my_line = bt.indicators.SMA(
            self.data.close,
            period=self.p.period
        )
```

---

## 📚 参考资料

1. [Backtrader 官方文档](https://www.backtrader.com/docu/)
2. [Backtrader GitHub](https://github.com/mementum/backtrader)
3. [Backtrader 示例代码](https://github.com/mementum/backtrader/tree/master/samples)
4. [qclaw 回测示例](../examples/backtrader_example.py)

---

**最后更新:** 2026-03-06  
**维护者:** qclaw-coder
