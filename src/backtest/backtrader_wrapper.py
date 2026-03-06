"""
Backtrader 回测框架集成

基于 backtrader 库实现 qclaw 的回测功能
文档：https://www.backtrader.com
GitHub: https://github.com/mementum/backtrader

核心优势:
- 成熟的回测框架，支持多种市场
- 丰富的技术指标库
- 灵活的交易策略定义
- 详细的性能分析报告
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json


class QclawDataFeed(bt.feeds.PandasData):
    """
    qclaw 数据源适配器
    
    将 qclaw 数据格式转换为 backtrader 可用的数据源
    支持 A 股市场数据
    
    注意：backtrader 默认列：datetime, open, high, low, close, volume, openinterest
    额外列需要在 lines 中定义
    """
    
    # 定义额外数据列
    lines = ('adj_close', 'amount', 'turnover')
    
    # 参数配置
    params = (
        ('datetime', None),      # 使用 DataFrame 索引
        ('open', -1),            # -1 表示自动检测
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('openinterest', -1),
        ('adj_close', -1),
        ('amount', -1),
        ('turnover', -1),
    )


class QclawCommission(bt.CommissionInfo):
    """
    A 股佣金配置
    
    参数:
        commission: 佣金比率 (默认万分之 2.5)
        stamp_duty: 印花税 (默认 0.1%，仅卖出收取)
        min_commission: 最低佣金 (默认 5 元)
        slippage: 滑点 (默认 0.001)
    """
    
    params = (
        ('commission', 0.00025),  # 万分之 2.5
        ('stamp_duty', 0.001),    # 0.1% (卖出)
        ('min_commission', 5.0),  # 最低 5 元
        ('slippage', 0.001),      # 0.1% 滑点
        ('mult', 1.0),
        ('margin', 1.0),
    )
    
    def _getcommission(self, size, price, pseudoexec):
        """计算佣金"""
        if size > 0:  # 买入
            commission = abs(size) * price * self.p.commission
            commission = max(commission, self.p.min_commission)
            return commission
        elif size < 0:  # 卖出
            commission = abs(size) * price * self.p.commission
            commission = max(commission, self.p.min_commission)
            stamp_duty = abs(size) * price * self.p.stamp_duty
            return commission + stamp_duty
        return 0


class QclawSizing(bt.Sizer):
    """
    A 股仓位管理器
    
    支持:
    - 按资金比例下单
    - 按固定数量下单
    - 100 股整数倍 (A 股一手=100 股)
    """
    
    params = (
        ('stake', 100),        # 默认 100 股 (1 手)
        ('stake_perc', 0.1),   # 按资金 10% 下单
        ('roundto', 100),      # 100 股整数倍
    )
    
    def _getsizing(self, comminfo, cash, data, isbuy):
        """计算下单数量"""
        if self.p.stake_perc > 0:
            # 按资金比例
            price = data.close[0]
            stake = int(cash * self.p.stake_perc / price)
        else:
            # 固定数量
            stake = self.p.stake
        
        # 100 股整数倍
        if self.p.roundto:
            stake = (stake // self.p.roundto) * self.p.roundto
        
        # 最小 100 股
        if stake > 0 and stake < 100:
            stake = 100
        
        return stake


class MACDIndicator(bt.indicators.MACD):
    """
    MACD 指标 (复用 backtrader 内置)
    """
    pass


class KDJIndicator(bt.indicators.Stochastic):
    """
    KDJ 指标 (基于 Stochastic)
    """
    lines = ('k', 'd', 'j')
    
    params = (
        ('period', 14),
        ('smoothk', 3),
        ('smoothd', 3),
    )
    
    def __init__(self):
        self.lines.k = self.lines.percK
        self.lines.d = self.lines.percD
        self.lines.j = 3 * self.lines.k - 2 * self.lines.d


class RSIIIndicator(bt.indicators.RSI):
    """
    RSI 指标 (复用 backtrader 内置)
    """
    pass


class QclawStrategy(bt.Strategy):
    """
    qclaw 基础交易策略
    
    支持:
    - 多指标信号融合
    - 仓位管理
    - 止盈止损
    """
    
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('rsi_period', 14),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('take_profit', 0.05),    # 5% 止盈
        ('stop_loss', 0.03),      # 3% 止损
        ('position_size', 0.1),   # 10% 仓位
    )
    
    def __init__(self):
        """初始化指标"""
        # MACD
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal,
        )
        
        # RSI
        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.p.rsi_period,
        )
        
        # 订单跟踪
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        
    def log(self, txt, dt=None):
        """日志记录"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, '
                    f'Comm: {order.executed.comm:.2f}'
                )
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
            else:  # SELL
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, '
                    f'Comm: {order.executed.comm:.2f}'
                )
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易完成通知"""
        if not trade.isclosed:
            return
        
        self.log(f'TRADE PROFIT, Gross {trade.pnl:.2f}, Net {trade.pnlcomm:.2f}')
    
    def next(self):
        """每个 bar 执行"""
        if self.order:
            return  # 等待订单完成
        
        # 检查止盈止损
        if self.position:
            if self.check_take_profit():
                self.log('Take profit triggered')
                self.order = self.close()
                return
            
            if self.check_stop_loss():
                self.log('Stop loss triggered')
                self.order = self.close()
                return
        
        # 开仓信号
        if not self.position:
            if self.check_buy_signal():
                self.log(f'BUY CREATE, Close: {self.data.close[0]:.2f}')
                self.order = self.buy(size=self.get_position_size())
    
    def check_buy_signal(self) -> bool:
        """检查买入信号"""
        # MACD 金叉 + RSI 超卖
        macd_crossed_up = self.macd.macd[0] > self.macd.signal[0] and \
                         self.macd.macd[-1] <= self.macd.signal[-1]
        
        rsi_oversold = self.rsi[0] < self.p.rsi_oversold
        
        return macd_crossed_up or rsi_oversold
    
    def check_take_profit(self) -> bool:
        """检查止盈"""
        if self.buy_price is None:
            return False
        
        current_price = self.data.close[0]
        profit_pct = (current_price - self.buy_price) / self.buy_price
        
        return profit_pct >= self.p.take_profit
    
    def check_stop_loss(self) -> bool:
        """检查止损"""
        if self.buy_price is None:
            return False
        
        current_price = self.data.close[0]
        loss_pct = (self.buy_price - current_price) / self.buy_price
        
        return loss_pct >= self.p.stop_loss
    
    def get_position_size(self) -> int:
        """获取仓位大小"""
        cash = self.broker.getcash()
        price = self.data.close[0]
        
        stake = int(cash * self.p.position_size / price)
        stake = (stake // 100) * 100  # 100 股整数倍
        
        return max(stake, 100) if stake > 0 else 0


class QclawAnalyzer(bt.Analyzer):
    """
    qclaw 性能分析器
    
    计算关键性能指标:
    - 总收益率
    - 年化收益率
    - 夏普比率
    - 最大回撤
    - 胜率
    """
    
    def __init__(self):
        self.returns = []
        self.trades = []
        self.equity_curve = []
        self.trade_log = []  # 通过 notify_trade 收集
    
    def start(self):
        """初始化"""
        self.equity_curve.append(self.strategy.broker.getvalue())
    
    def next(self):
        """记录每个 bar 的净值"""
        self.equity_curve.append(self.strategy.broker.getvalue())
    
    def notify_trade(self, trade):
        """接收交易完成通知"""
        if trade.isclosed:
            self.trade_log.append({
                'pnl': trade.pnl,
                'pnlcomm': trade.pnlcomm,
                'long': trade.long,
                'size': trade.size,
                'price': trade.price,
            })
    
    def stop(self):
        """计算最终指标"""
        # 计算收益率序列
        self.returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        
        # 使用收集的交易记录
        self.trades = self.trade_log
    
    def get_analysis(self) -> Dict[str, Any]:
        """返回分析结果"""
        if len(self.returns) == 0:
            return {}
        
        returns = np.array(self.returns)
        
        # 总收益率
        total_return = (self.equity_curve[-1] - self.equity_curve[0]) / self.equity_curve[0]
        
        # 年化收益率 (假设 252 个交易日)
        n_days = len(returns)
        annual_return = (1 + total_return) ** (252 / n_days) - 1 if n_days > 0 else 0
        
        # 夏普比率 (假设无风险利率 3%)
        risk_free_rate = 0.03
        excess_returns = returns - risk_free_rate / 252
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
        
        # 最大回撤
        equity = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdowns = (equity - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        # 胜率
        winning_trades = [t for t in self.trades if t['pnlcomm'] > 0]
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        # 盈亏比
        if winning_trades and len(self.trades) > len(winning_trades):
            avg_win = np.mean([t['pnlcomm'] for t in winning_trades])
            losing_trades = [t for t in self.trades if t['pnlcomm'] <= 0]
            avg_loss = abs(np.mean([t['pnlcomm'] for t in losing_trades]))
            profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf')
        else:
            profit_loss_ratio = 0
        
        # 波动率
        volatility = np.std(returns) * np.sqrt(252)
        
        # Calmar 比率
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_loss_ratio': profit_loss_ratio,
            'volatility': volatility,
            'calmar_ratio': calmar_ratio,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(self.trades) - len(winning_trades),
            'final_equity': self.equity_curve[-1],
            'initial_equity': self.equity_curve[0],
            'equity_curve': self.equity_curve,
        }


class BacktraderWrapper:
    """
    Backtrader 回测包装器
    
    提供简化的 API 用于 qclaw 回测
    """
    
    def __init__(
        self,
        initial_cash: float = 100000.0,
        commission: float = 0.00025,
        stamp_duty: float = 0.001,
        slippage: float = 0.001,
    ):
        """
        初始化回测包装器
        
        参数:
            initial_cash: 初始资金
            commission: 佣金比率
            stamp_duty: 印花税
            slippage: 滑点
        """
        self.initial_cash = initial_cash
        self.commission = commission
        self.stamp_duty = stamp_duty
        self.slippage = slippage
        
        self.cerebro = None
        self.data = None
        self.strategy = None
        self.analyzer = None
        self.results = None
    
    def load_data(
        self,
        df: pd.DataFrame,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ):
        """
        加载数据
        
        参数:
            df: pandas DataFrame，包含 OHLCV 数据
            from_date: 开始日期 (YYYY-MM-DD)
            to_date: 结束日期 (YYYY-MM-DD)
        """
        self.cerebro = bt.Cerebro()
        
        # 数据过滤
        if from_date:
            df = df[df['date'] >= from_date]
        if to_date:
            df = df[df['date'] <= to_date]
        
        # 设置日期索引 (backtrader 需要 datetime 作为索引)
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # 确保所有必需的列存在
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # 添加数据源
        self.data = QclawDataFeed(dataname=df)
        self.cerebro.adddata(self.data)
        
        # 设置初始资金
        self.cerebro.broker.setcash(self.initial_cash)
        
        # 设置佣金
        self.cerebro.broker.addcommissioninfo(
            QclawCommission(
                commission=self.commission,
                stamp_duty=self.stamp_duty,
            )
        )
        
        # 设置滑点
        self.cerebro.broker.set_slippage_perc(self.slippage)
        
        print(f"初始资金：¥{self.initial_cash:,.0f}")
        print(f"数据范围：{df.index.min()} 至 {df.index.max()}")
    
    def add_strategy(
        self,
        strategy_class: type = QclawStrategy,
        **kwargs
    ):
        """
        添加交易策略
        
        参数:
            strategy_class: 策略类
            **kwargs: 策略参数
        """
        self.cerebro.addstrategy(strategy_class, **kwargs)
        self.strategy = strategy_class
        print(f"策略：{strategy_class.__name__}")
    
    def add_analyzer(self):
        """添加性能分析器"""
        self.analyzer = QclawAnalyzer
        self.cerebro.addanalyzer(self.analyzer, _name='qclaw_analyzer')
    
    def run(self) -> Dict[str, Any]:
        """
        运行回测
        
        返回:
            回测结果字典
        """
        if self.cerebro is None:
            raise RuntimeError("请先加载数据和策略")
        
        print("\n开始回测...")
        print(f"初始资金：¥{self.cerebro.broker.getvalue():,.0f}")
        
        self.results = self.cerebro.run()
        
        final_value = self.cerebro.broker.getvalue()
        print(f"最终资金：¥{final_value:,.0f}")
        
        # 获取分析结果
        if self.analyzer:
            analysis = self.results[0].analyzers.qclaw_analyzer.get_analysis()
            self._print_analysis(analysis)
            return analysis
        
        return {}
    
    def _print_analysis(self, analysis: Dict[str, Any]):
        """打印分析结果"""
        print("\n" + "=" * 60)
        print("回测结果分析")
        print("=" * 60)
        print(f"总收益率：    {analysis.get('total_return', 0):.2%}")
        print(f"年化收益率：  {analysis.get('annual_return', 0):.2%}")
        print(f"夏普比率：    {analysis.get('sharpe_ratio', 0):.2f}")
        print(f"最大回撤：    {analysis.get('max_drawdown', 0):.2%}")
        print(f"胜率：        {analysis.get('win_rate', 0):.2%}")
        print(f"盈亏比：      {analysis.get('profit_loss_ratio', 0):.2f}")
        print(f"波动率：      {analysis.get('volatility', 0):.2%}")
        print(f"Calmar 比率：  {analysis.get('calmar_ratio', 0):.2f}")
        print(f"交易次数：    {analysis.get('total_trades', 0)}")
        print(f"盈利次数：    {analysis.get('winning_trades', 0)}")
        print(f"亏损次数：    {analysis.get('losing_trades', 0)}")
        print("=" * 60)
    
    def plot(self, filename: Optional[str] = None):
        """
        绘制回测结果
        
        参数:
            filename: 保存文件名 (可选)
        """
        if self.cerebro is None:
            raise RuntimeError("请先运行回测")
        
        print("\n生成图表...")
        
        try:
            # 使用非交互式后端
            import matplotlib
            matplotlib.use('Agg')  # 非交互式后端
            
            if filename:
                # 保存到文件
                self.cerebro.plot(style='candlestick', filename=filename)
                print(f"图表已保存到：{filename}")
            else:
                # 显示图表 (如果环境支持)
                self.cerebro.plot(style='candlestick')
        except Exception as e:
            print(f"图表生成失败：{e}")
            print("提示：在无 GUI 环境中，请指定 filename 参数保存图表")


def run_backtest(
    data_path: str,
    strategy_class: type = QclawStrategy,
    initial_cash: float = 100000.0,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    output_dir: Optional[str] = None,
    **strategy_params
) -> Dict[str, Any]:
    """
    便捷函数：运行回测
    
    参数:
        data_path: 数据文件路径 (CSV)
        strategy_class: 策略类
        initial_cash: 初始资金
        from_date: 开始日期
        to_date: 结束日期
        output_dir: 输出目录
        **strategy_params: 策略参数
        
    返回:
        回测结果字典
    """
    # 加载数据
    df = pd.read_csv(data_path)
    
    # 创建回测包装器
    wrapper = BacktraderWrapper(initial_cash=initial_cash)
    
    # 加载数据
    wrapper.load_data(df, from_date=from_date, to_date=to_date)
    
    # 添加策略
    wrapper.add_strategy(strategy_class, **strategy_params)
    
    # 添加分析器
    wrapper.add_analyzer()
    
    # 运行回测
    results = wrapper.run()
    
    # 保存结果
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存 JSON 结果
        results_copy = {k: v for k, v in results.items() if k != 'equity_curve'}
        with open(output_path / 'backtest_results.json', 'w') as f:
            json.dump(results_copy, f, indent=2)
        
        # 保存权益曲线
        if 'equity_curve' in results:
            equity_df = pd.DataFrame({
                'date': pd.date_range(start=from_date or df['date'].min(), 
                                     periods=len(results['equity_curve'])),
                'equity': results['equity_curve'],
            })
            equity_df.to_csv(output_path / 'equity_curve.csv', index=False)
        
        # 保存图表
        wrapper.plot(str(output_path / 'backtest_chart.png'))
        
        print(f"\n结果已保存到：{output_dir}")
    
    return results


if __name__ == "__main__":
    # 示例用法
    print("Backtrader 回测框架集成示例")
    print("=" * 60)
    
    # 注意：需要提供实际数据文件
    # results = run_backtest(
    #     data_path="data/stock_data.csv",
    #     strategy_class=QclawStrategy,
    #     initial_cash=100000,
    #     from_date="2023-01-01",
    #     to_date="2023-12-31",
    #     output_dir="results/backtest",
    #     macd_fast=12,
    #     macd_slow=26,
    #     rsi_period=14,
    # )
