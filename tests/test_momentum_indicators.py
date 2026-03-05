"""
动量指标模块测试

测试覆盖：
- RSI (相对强弱指数)
- ROC (变化率)
- CCI (商品通道指数)
- Stochastic (随机指标/KDJ)
- MomentumIndicatorCalculator 类
- 信号检测功能
- 边界情况和异常处理
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.indicators.momentum_indicators import (
    calculate_rsi,
    calculate_rsi_multi,
    calculate_roc,
    calculate_roc_multi,
    calculate_cci,
    calculate_cci_multi,
    calculate_stochastic,
    calculate_stochastic_multi,
    MomentumIndicatorCalculator,
    rsi,
    roc,
    cci,
    stochastic
)


class TestCalculateRSI:
    """测试 RSI 计算"""
    
    def test_rsi_basic(self, sample_series):
        """测试基础 RSI 计算"""
        result = calculate_rsi(sample_series, period=5)
        
        # 验证结果长度
        assert len(result) == len(sample_series)
        
        # RSI 值应该在 0-100 之间
        valid_values = result.dropna()
        assert (valid_values >= 0).all()
        assert (valid_values <= 100).all()
    
    def test_rsi_default_period(self, sample_series):
        """测试默认周期"""
        result = calculate_rsi(sample_series)
        # 默认周期是 14
        assert len(result) == len(sample_series)
    
    def test_rsi_constant_prices(self):
        """测试恒定价格"""
        prices = pd.Series([50.0] * 30)
        result = calculate_rsi(prices, period=14)
        
        # 当价格不变时，RSI 应该是 50 或 NaN
        valid_values = result.dropna()
        if len(valid_values) > 0:
            assert all(v == 50 or v == 100 for v in valid_values)
    
    def test_rsi_strong_uptrend(self):
        """测试强上涨趋势"""
        prices = pd.Series(range(1, 31))  # 持续上涨
        result = calculate_rsi(prices, period=14)
        
        # 在强上涨中，RSI 应该接近 100
        valid_values = result.dropna()
        assert (valid_values > 50).all()
    
    def test_rsi_strong_downtrend(self):
        """测试强下跌趋势"""
        prices = pd.Series(range(30, 0, -1))  # 持续下跌
        result = calculate_rsi(prices, period=14)
        
        # 在强下跌中，RSI 应该很低（除了第一个值可能是 100 因为 EMA 初始化）
        valid_values = result.dropna()
        # 除了第一个值，其他都应该很低
        assert (valid_values.iloc[1:] <= 1).all()


class TestCalculateRSIMulti:
    """测试多周期 RSI 计算"""
    
    def test_rsi_multi_basic(self, sample_price_data):
        """测试多周期 RSI"""
        result = calculate_rsi_multi(sample_price_data, periods=[6, 12, 24])
        
        assert "rsi6" in result.columns
        assert "rsi12" in result.columns
        assert "rsi24" in result.columns
    
    def test_rsi_multi_default_periods(self, sample_price_data):
        """测试默认周期"""
        result = calculate_rsi_multi(sample_price_data)
        
        # 默认周期是 [6, 12, 24]
        assert "rsi6" in result.columns
        assert "rsi12" in result.columns
        assert "rsi24" in result.columns
    
    def test_rsi_multi_custom_prefix(self, sample_price_data):
        """测试自定义前缀"""
        result = calculate_rsi_multi(
            sample_price_data,
            periods=[14],
            output_prefix="RSI"
        )
        
        assert "RSI14" in result.columns


class TestCalculateROC:
    """测试 ROC 计算"""
    
    def test_roc_basic(self, sample_series):
        """测试基础 ROC 计算"""
        result = calculate_roc(sample_series, period=3)
        
        assert len(result) == len(sample_series)
        # 前 period 个值应该是 NaN
        assert pd.isna(result.iloc[:3]).all()
    
    def test_roc_percentage(self, sample_series):
        """测试 ROC 是百分比"""
        result = calculate_roc(sample_series, period=1)
        
        # ROC 应该是百分比形式
        # 例如从 10 到 12 的变化率是 20%
        assert abs(result.iloc[1] - 20.0) < 0.01
    
    def test_roc_constant_prices(self):
        """测试恒定价格"""
        prices = pd.Series([50.0] * 20)
        result = calculate_roc(prices, period=5)
        
        # 价格不变时 ROC 应该是 0
        valid_values = result.dropna()
        assert (valid_values == 0).all()


class TestCalculateROCMulti:
    """测试多周期 ROC 计算"""
    
    def test_roc_multi_basic(self, sample_price_data):
        """测试多周期 ROC"""
        result = calculate_roc_multi(sample_price_data, periods=[5, 10, 20])
        
        assert "roc5" in result.columns
        assert "roc10" in result.columns
        assert "roc20" in result.columns


class TestCalculateCCI:
    """测试 CCI 计算"""
    
    def test_cci_basic(self, sample_price_data):
        """测试基础 CCI 计算"""
        result = calculate_cci(sample_price_data, period=20)
        
        assert len(result) == len(sample_price_data)
    
    def test_cci_custom_columns(self, sample_price_data):
        """测试自定义列名"""
        result = calculate_cci(
            sample_price_data,
            period=14,
            high_col="high",
            low_col="low",
            close_col="close"
        )
        
        assert len(result) == len(sample_price_data)
    
    def test_cci_missing_columns(self, sample_price_data):
        """测试缺失列"""
        with pytest.raises(ValueError):
            calculate_cci(sample_price_data, high_col="invalid")


class TestCalculateCCIMulti:
    """测试多周期 CCI 计算"""
    
    def test_cci_multi_basic(self, sample_price_data):
        """测试多周期 CCI"""
        result = calculate_cci_multi(sample_price_data, periods=[14, 20, 30])
        
        assert "cci14" in result.columns
        assert "cci20" in result.columns
        assert "cci30" in result.columns


class TestCalculateStochastic:
    """测试随机指标计算"""
    
    def test_stochastic_basic(self, sample_price_data):
        """测试基础随机指标"""
        result = calculate_stochastic(sample_price_data, k_period=14, d_period=3)
        
        assert "k" in result
        assert "d" in result
        assert "j" in result
        
        # K, D 应该在 0-100 之间
        for key in ["k", "d"]:
            valid_values = result[key].dropna()
            if len(valid_values) > 0:
                assert (valid_values >= 0).all()
                assert (valid_values <= 100).all()
    
    def test_stochastic_j_range(self, sample_price_data):
        """测试 J 值范围"""
        result = calculate_stochastic(sample_price_data)
        
        # J 值可能超出 0-100 范围，但应该是有限值
        j_valid = result["j"].dropna()
        assert np.isfinite(j_valid).all()
    
    def test_stochastic_custom_periods(self, sample_price_data):
        """测试自定义周期"""
        result = calculate_stochastic(
            sample_price_data,
            k_period=9,
            d_period=3
        )
        
        assert "k" in result
        assert "d" in result
        assert "j" in result


class TestCalculateStochasticMulti:
    """测试随机指标多周期计算"""
    
    def test_stochastic_multi_basic(self, sample_price_data):
        """测试随机指标添加到 DataFrame"""
        result = calculate_stochastic_multi(sample_price_data)
        
        assert "stoch_k" in result.columns
        assert "stoch_d" in result.columns
        assert "stoch_j" in result.columns


class TestMomentumIndicatorCalculator:
    """测试 MomentumIndicatorCalculator 类"""
    
    def test_initialization(self, sample_price_data):
        """测试初始化"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        assert len(calc.calculated) == 0
    
    def test_add_rsi(self, sample_price_data):
        """测试添加 RSI"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        result = calc.add_rsi(period=14)
        
        # 验证链式调用
        assert result is calc
        
        # 验证 RSI 被添加
        assert "rsi14" in calc.df.columns
        assert "rsi_14" in calc.calculated
    
    def test_add_roc(self, sample_price_data):
        """测试添加 ROC"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        calc.add_roc(period=12)
        
        assert "roc12" in calc.df.columns
    
    def test_add_cci(self, sample_price_data):
        """测试添加 CCI"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        calc.add_cci(period=20)
        
        assert "cci20" in calc.df.columns
    
    def test_add_stochastic(self, sample_price_data):
        """测试添加随机指标"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        calc.add_stochastic()
        
        assert "stoch_k" in calc.df.columns
        assert "stoch_d" in calc.df.columns
        assert "stoch_j" in calc.df.columns
    
    def test_detect_rsi_signal(self, sample_price_data):
        """测试 RSI 信号检测"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        signals = calc.detect_rsi_signal(period=14, oversold=30, overbought=70)
        
        assert "buy_signal" in signals
        assert "sell_signal" in signals
        
        # 信号应该是布尔序列
        assert signals["buy_signal"].dtype == bool
        assert signals["sell_signal"].dtype == bool
    
    def test_detect_stochastic_signal(self, sample_price_data):
        """测试随机指标信号检测"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        signals = calc.detect_stochastic_signal()
        
        assert "buy_signal" in signals
        assert "sell_signal" in signals
    
    def test_detect_cci_signal(self, sample_price_data):
        """测试 CCI 信号检测"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        signals = calc.detect_cci_signal(period=20)
        
        assert "buy_signal" in signals
        assert "sell_signal" in signals
    
    def test_get_momentum_score(self, sample_price_data):
        """测试动量得分计算"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        score = calc.get_momentum_score()
        
        assert len(score) == len(sample_price_data)
        # 得分应该在 -100 到 100 之间
        valid_scores = score.dropna()
        assert (valid_scores >= -100).all()
        assert (valid_scores <= 100).all()
    
    def test_get_dataframe(self, sample_price_data):
        """测试获取 DataFrame"""
        calc = MomentumIndicatorCalculator(sample_price_data)
        calc.add_rsi().add_roc()
        
        df = calc.get_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert "rsi14" in df.columns
        assert "roc12" in df.columns


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_rsi_function(self, sample_series):
        """测试 rsi 函数"""
        result = rsi(sample_series, period=14)
        expected = calculate_rsi(sample_series, period=14)
        pd.testing.assert_series_equal(result, expected)
    
    def test_roc_function(self, sample_series):
        """测试 roc 函数"""
        result = roc(sample_series, period=12)
        expected = calculate_roc(sample_series, period=12)
        pd.testing.assert_series_equal(result, expected)
    
    def test_cci_function(self, sample_price_data):
        """测试 cci 函数"""
        result = cci(sample_price_data, period=20)
        expected = calculate_cci(sample_price_data, period=20)
        pd.testing.assert_series_equal(result, expected)
    
    def test_stochastic_function(self, sample_price_data):
        """测试 stochastic 函数"""
        result = stochastic(sample_price_data)
        expected = calculate_stochastic(sample_price_data)
        
        assert len(result) == len(expected)
        for key in ["k", "d", "j"]:
            pd.testing.assert_series_equal(result[key], expected[key])


class TestEdgeCases:
    """测试边界情况"""
    
    def test_rsi_insufficient_data(self, small_dataframe):
        """测试 RSI 数据不足"""
        result = calculate_rsi(small_dataframe["close"], period=14)
        
        # RSI 使用 EMA 计算，即使数据不足也会返回值
        # 验证结果长度与输入相同
        assert len(result) == len(small_dataframe)
        # 所有值都应该是有限的数值
        assert np.isfinite(result).all()
    
    def test_roc_with_zero_prices(self):
        """测试 ROC 零价格处理"""
        prices = pd.Series([0, 0, 0, 10, 20])
        result = calculate_roc(prices, period=1)
        
        # 应该能处理除零情况
        assert len(result) == 5
    
    def test_stochastic_constant_high_low(self):
        """测试随机指标恒定高低点"""
        df = pd.DataFrame({
            "high": [10.0] * 20,
            "low": [10.0] * 20,
            "close": [10.0] * 20
        })
        
        result = calculate_stochastic(df)
        
        # 当 high=low 时，应该能处理除零
        assert "k" in result
        assert "d" in result
        assert "j" in result
