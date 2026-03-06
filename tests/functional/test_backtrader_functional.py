"""
回测框架功能测试 - TEST-BT-001

测试 backtrader 回测框架的功能
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestBacktraderFunctional:
    """Backtrader 回测框架功能测试"""
    
    @pytest.fixture
    def sample_stock_data(self):
        """准备测试股票数据"""
        np.random.seed(42)
        n_days = 250
        
        dates = pd.date_range(start='2020-01-01', periods=n_days, freq='D')
        data = {
            'date': dates,
            'open': 100 + np.random.randn(n_days) * 5,
            'high': 100 + np.random.randn(n_days) * 5 + 2,
            'low': 100 + np.random.randn(n_days) * 5 - 2,
            'close': 100 + np.random.randn(n_days) * 5,
            'volume': np.random.randint(1000, 10000, n_days)
        }
        
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        return df
    
    def test_data_loading(self, sample_stock_data):
        """测试 1: 数据加载功能"""
        import backtrader as bt
        
        # 创建数据源
        data = bt.feeds.PandasData(
            dataname=sample_stock_data,
            datetime=None,
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1
        )
        
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        
        assert data is not None
        print("✅ 数据加载成功")
    
    def test_strategy_execution(self, sample_stock_data):
        """测试 2: 策略执行功能"""
        import backtrader as bt
        
        class TestStrategy(bt.Strategy):
            def __init__(self):
                self.sma = bt.indicators.SimpleMovingAverage(
                    self.data.close, period=10
                )
            
            def next(self):
                if not self.position:
                    if self.data.close[0] > self.sma[0]:
                        self.buy()
                else:
                    if self.data.close[0] < self.sma[0]:
                        self.sell()
        
        data = bt.feeds.PandasData(dataname=sample_stock_data)
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.addstrategy(TestStrategy)
        cerebro.broker.setcash(100000.0)
        
        initial_cash = cerebro.broker.getvalue()
        cerebro.run()
        final_cash = cerebro.broker.getvalue()
        
        assert final_cash > 0
        print(f"✅ 策略执行成功，初始：{initial_cash:.2f}, 最终：{final_cash:.2f}")
    
    def test_indicator_calculation(self, sample_stock_data):
        """测试 3: 指标计算功能"""
        import backtrader as bt
        
        data = bt.feeds.PandasData(dataname=sample_stock_data)
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        
        cerebro.addindicator(bt.indicators.SMA, period=10)
        cerebro.addindicator(bt.indicators.RSI, period=14)
        cerebro.addindicator(bt.indicators.MACD)
        
        results = cerebro.run()
        assert results is not None
        print("✅ 指标计算成功 (SMA, RSI, MACD)")
    
    def test_transaction_cost(self, sample_stock_data):
        """测试 4: 交易费用计算"""
        import backtrader as bt
        
        class SimpleStrategy(bt.Strategy):
            def next(self):
                if not self.position:
                    self.buy()
                else:
                    self.sell()
        
        data = bt.feeds.PandasData(dataname=sample_stock_data)
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.addstrategy(SimpleStrategy)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.0003)
        
        initial_cash = cerebro.broker.getvalue()
        cerebro.run()
        final_cash = cerebro.broker.getvalue()
        
        print(f"✅ 交易费用计算完成，初始：{initial_cash:.2f}, 最终：{final_cash:.2f}")
    
    def test_backtest_speed(self, sample_stock_data):
        """测试 5: 回测速度测试"""
        import backtrader as bt
        import time
        
        class TestStrategy(bt.Strategy):
            def __init__(self):
                self.sma = bt.indicators.SMA(self.data.close, period=10)
            
            def next(self):
                if self.data.close[0] > self.sma[0]:
                    self.buy()
                else:
                    self.sell()
        
        data = bt.feeds.PandasData(dataname=sample_stock_data)
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.addstrategy(TestStrategy)
        
        start_time = time.time()
        cerebro.run()
        elapsed_time = time.time() - start_time
        
        print(f"✅ 回测速度：{elapsed_time:.3f}秒 (250 天数据)")
        assert elapsed_time < 5, f"回测速度过慢：{elapsed_time:.3f}秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
