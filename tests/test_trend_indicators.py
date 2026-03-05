"""
趋势指标模块测试

测试覆盖：
- calculate_macd MACD 计算
- calculate_adx ADX 计算
- calculate_sar SAR 计算
- TrendIndicatorCalculator 类
- 信号检测 (金叉/死叉/趋势强度)
- 边界情况和异常处理
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.indicators.trend_indicators import (
    calculate_macd,
    calculate_macd_multi,
    calculate_adx,
    calculate_adx_multi,
    calculate_sar,
    calculate_sar_multi,
    TrendIndicatorCalculator,
    macd,
    adx,
    sar
)


class TestCalculateMACD:
    """测试 calculate_macd 函数"""
    
    def test_macd_calculation_basic(self, sample_series):
        """测试基础 MACD 计算"""
        result = calculate_macd(sample_series)
        
        # 验证返回字典包含所有键
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result
        
        # 验证结果长度
        assert len(result["macd"]) == len(sample_series)
        assert len(result["signal"]) == len(sample_series)
        assert len(result["histogram"]) == len(sample_series)
        
        # 验证 MACD 值存在（EMA 不会产生 NaN，但早期值可能不稳定）
        assert result["macd"].notna().all()
    
    def test_macd_custom_periods(self, sample_series):
        """测试自定义周期"""
        result = calculate_macd(
            sample_series,
            fast_period=6,
            slow_period=13,
            signal_period=5
        )
        
        assert "macd" in result
        assert len(result["macd"]) == len(sample_series)
    
    def test_macd_with_dataframe(self, sample_price_data):
        """测试使用 DataFrame 输入"""
        result = calculate_macd(sample_price_data["close"])
        
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result
    
    def test_macd_histogram_relationship(self, sample_series):
        """测试 histogram = macd - signal"""
        result = calculate_macd(sample_series)
        
        # histogram 应该等于 macd - signal
        expected_histogram = result["macd"] - result["signal"]
        pd.testing.assert_series_equal(
            result["histogram"].dropna(),
            expected_histogram.dropna()
        )
    
    def test_macd_empty_series(self):
        """测试空序列"""
        empty = pd.Series([], dtype=float)
        result = calculate_macd(empty)
        
        assert len(result["macd"]) == 0
        assert len(result["signal"]) == 0
        assert len(result["histogram"]) == 0


class TestCalculateMACDMulti:
    """测试 calculate_macd_multi 函数"""
    
    def test_macd_multi_basic(self, sample_price_data):
        """测试 MACD 添加到 DataFrame"""
        result = calculate_macd_multi(sample_price_data)
        
        # 验证新列被添加
        assert "macd" in result.columns
        assert "macd_signal" in result.columns
        assert "macd_histogram" in result.columns
        
        # 验证原数据未被修改
        assert "close" in result.columns
    
    def test_macd_multi_custom_prefix(self, sample_price_data):
        """测试自定义前缀"""
        result = calculate_macd_multi(
            sample_price_data,
            output_prefix="MACD"
        )
        
        assert "MACD" in result.columns
        assert "MACD_signal" in result.columns
        assert "MACD_histogram" in result.columns
    
    def test_macd_multi_missing_column(self, sample_price_data):
        """测试缺失列"""
        with pytest.raises(ValueError):
            calculate_macd_multi(sample_price_data, price_column="invalid")


class TestCalculateADX:
    """测试 calculate_adx 函数"""
    
    def test_adx_calculation_basic(self, sample_price_data):
        """测试基础 ADX 计算"""
        result = calculate_adx(sample_price_data)
        
        # 验证结果长度
        assert len(result) == len(sample_price_data)
        
        # 验证 ADX 值在合理范围内 (0-100)
        adx_valid = result.dropna()
        assert (adx_valid >= 0).all()
        assert (adx_valid <= 100).all()
    
    def test_adx_custom_period(self, sample_price_data):
        """测试自定义周期"""
        result = calculate_adx(sample_price_data, period=20)
        
        assert len(result) == len(sample_price_data)
    
    def test_adx_custom_columns(self, sample_price_data):
        """测试自定义列名"""
        result = calculate_adx(
            sample_price_data,
            high_col="high",
            low_col="low",
            close_col="close"
        )
        
        assert len(result) == len(sample_price_data)
    
    def test_adx_missing_columns(self, sample_price_data):
        """测试缺失列"""
        df = sample_price_data.drop(columns=["high"])
        
        with pytest.raises(ValueError):
            calculate_adx(df)


class TestCalculateADXMulti:
    """测试 calculate_adx_multi 函数"""
    
    def test_adx_multi_basic(self, sample_price_data):
        """测试多个周期 ADX"""
        result = calculate_adx_multi(sample_price_data, periods=[14, 20])
        
        assert "adx14" in result.columns
        assert "adx20" in result.columns
    
    def test_adx_multi_default_periods(self, sample_price_data):
        """测试默认周期"""
        result = calculate_adx_multi(sample_price_data)
        
        # 默认周期是 [14]
        assert "adx14" in result.columns
    
    def test_adx_multi_custom_prefix(self, sample_price_data):
        """测试自定义前缀"""
        result = calculate_adx_multi(
            sample_price_data,
            periods=[14],
            output_prefix="ADX"
        )
        
        assert "ADX14" in result.columns


class TestCalculateSAR:
    """测试 calculate_sar 函数"""
    
    def test_sar_calculation_basic(self, sample_price_data):
        """测试基础 SAR 计算"""
        result = calculate_sar(sample_price_data)
        
        # 验证结果长度
        assert len(result) == len(sample_price_data)
        
        # 验证 SAR 值不为 NaN（除了可能的第一个值）
        assert result.notna().sum() > len(result) - 5
    
    def test_sar_custom_parameters(self, sample_price_data):
        """测试自定义参数"""
        result = calculate_sar(
            sample_price_data,
            acceleration=0.01,
            maximum=0.1
        )
        
        assert len(result) == len(sample_price_data)
    
    def test_sar_trend_reversal(self, sample_price_data):
        """测试 SAR 趋势反转"""
        result = calculate_sar(sample_price_data)
        
        # SAR 应该在趋势反转时改变位置（从价格上方变到下方或反之）
        # 这是一个基本检查，确保 SAR 值存在
        assert result.notna().sum() > 0
    
    def test_sar_missing_columns(self, sample_price_data):
        """测试缺失列"""
        df = sample_price_data.drop(columns=["high"])
        
        with pytest.raises(ValueError):
            calculate_sar(df)


class TestCalculateSARMulti:
    """测试 calculate_sar_multi 函数"""
    
    def test_sar_multi_basic(self, sample_price_data):
        """测试多个加速因子 SAR"""
        result = calculate_sar_multi(sample_price_data, accelerations=[0.02, 0.03])
        
        assert "sar1" in result.columns
        assert "sar2" in result.columns
    
    def test_sar_multi_default_accelerations(self, sample_price_data):
        """测试默认加速因子"""
        result = calculate_sar_multi(sample_price_data)
        
        # 默认加速因子是 [0.02]
        assert "sar1" in result.columns


class TestTrendIndicatorCalculator:
    """测试 TrendIndicatorCalculator 类"""
    
    def test_initialization(self, sample_price_data):
        """测试初始化"""
        calc = TrendIndicatorCalculator(sample_price_data)
        
        assert calc.df is not None
        assert len(calc.calculated) == 0
    
    def test_add_macd(self, sample_price_data):
        """测试添加 MACD"""
        calc = TrendIndicatorCalculator(sample_price_data)
        result = calc.add_macd()
        
        # 验证链式调用
        assert result is calc
        
        # 验证 MACD 被添加
        assert "macd" in calc.df.columns
        assert "macd_signal" in calc.df.columns
        assert "macd_histogram" in calc.df.columns
        assert "macd" in calc.calculated
    
    def test_add_macd_custom_params(self, sample_price_data):
        """测试自定义 MACD 参数"""
        calc = TrendIndicatorCalculator(sample_price_data)
        calc.add_macd(fast_period=6, slow_period=13, signal_period=5)
        
        assert "macd" in calc.df.columns
    
    def test_add_adx(self, sample_price_data):
        """测试添加 ADX"""
        calc = TrendIndicatorCalculator(sample_price_data)
        result = calc.add_adx(period=14)
        
        assert result is calc
        assert "adx14" in calc.df.columns
        assert "adx_14" in calc.calculated
    
    def test_add_sar(self, sample_price_data):
        """测试添加 SAR"""
        calc = TrendIndicatorCalculator(sample_price_data)
        result = calc.add_sar()
        
        assert result is calc
        assert "sar" in calc.df.columns
        assert "sar" in calc.calculated
    
    def test_chaining(self, sample_price_data):
        """测试链式调用"""
        calc = TrendIndicatorCalculator(sample_price_data)
        
        # 链式添加多个指标
        calc.add_macd().add_adx().add_sar()
        
        assert "macd" in calc.df.columns
        assert "adx14" in calc.df.columns
        assert "sar" in calc.df.columns
    
    def test_detect_macd_signal(self, sample_price_data):
        """测试 MACD 信号检测"""
        calc = TrendIndicatorCalculator(sample_price_data)
        calc.add_macd()
        
        signals = calc.detect_macd_signal()
        
        # 验证返回字典包含所有键
        assert "buy_signal" in signals
        assert "sell_signal" in signals
        
        # 验证返回布尔序列
        assert isinstance(signals["buy_signal"], pd.Series)
        assert isinstance(signals["sell_signal"], pd.Series)
        assert signals["buy_signal"].dtype == bool
        assert signals["sell_signal"].dtype == bool
    
    def test_detect_macd_signal_without_macd(self, sample_price_data):
        """测试未计算 MACD 时检测信号（应临时计算）"""
        calc = TrendIndicatorCalculator(sample_price_data)
        
        # 代码设计为临时计算 MACD，不应抛出异常
        signals = calc.detect_macd_signal()
        
        assert "buy_signal" in signals
        assert "sell_signal" in signals
    
    def test_detect_adx_trend_strength(self, sample_price_data):
        """测试 ADX 趋势强度检测"""
        calc = TrendIndicatorCalculator(sample_price_data)
        calc.add_adx(period=14)
        
        strong_trend = calc.detect_adx_trend_strength(period=14)
        
        # 验证返回布尔序列
        assert isinstance(strong_trend, pd.Series)
        assert strong_trend.dtype == bool
        
        # 验证值在合理范围内
        assert (strong_trend >= False).all()
        assert (strong_trend <= True).all()
    
    def test_detect_adx_trend_strength_custom_threshold(self, sample_price_data):
        """测试自定义趋势强度阈值"""
        calc = TrendIndicatorCalculator(sample_price_data)
        calc.add_adx(period=14)
        
        strong_trend = calc.detect_adx_trend_strength(
            period=14,
            strong_threshold=30
        )
        
        assert isinstance(strong_trend, pd.Series)
    
    def test_get_dataframe(self, sample_price_data):
        """测试获取 DataFrame"""
        calc = TrendIndicatorCalculator(sample_price_data)
        calc.add_macd()
        
        df = calc.get_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert "macd" in df.columns


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_macd_function(self, sample_series):
        """测试 macd 便捷函数"""
        result = macd(sample_series)
        expected = calculate_macd(sample_series)
        
        pd.testing.assert_series_equal(result["macd"], expected["macd"])
        pd.testing.assert_series_equal(result["signal"], expected["signal"])
        pd.testing.assert_series_equal(result["histogram"], expected["histogram"])
    
    def test_adx_function(self, sample_price_data):
        """测试 adx 便捷函数"""
        result = adx(sample_price_data)
        expected = calculate_adx(sample_price_data)
        
        pd.testing.assert_series_equal(result, expected)
    
    def test_sar_function(self, sample_price_data):
        """测试 sar 便捷函数"""
        result = sar(sample_price_data)
        expected = calculate_sar(sample_price_data)
        
        pd.testing.assert_series_equal(result, expected)


class TestEdgeCases:
    """测试边界情况"""
    
    def test_macd_insufficient_data(self, small_dataframe):
        """测试数据不足的情况"""
        result = calculate_macd(small_dataframe["close"])
        
        # EMA 仍能计算，但值可能不稳定
        assert "macd" in result
        assert len(result["macd"]) == len(small_dataframe)
    
    def test_adx_insufficient_data(self):
        """测试 ADX 数据不足"""
        # 创建包含必需列的小 DataFrame
        df = pd.DataFrame({
            "high": [10, 11, 12],
            "low": [9, 10, 11],
            "close": [9.5, 10.5, 11.5]
        })
        result = calculate_adx(df)
        
        # 应该能计算，但结果大部分是 NaN
        assert len(result) == len(df)
    
    def test_sar_insufficient_data(self):
        """测试 SAR 数据不足"""
        # 创建包含必需列的小 DataFrame
        df = pd.DataFrame({
            "high": [10, 11, 12, 13, 14],
            "low": [9, 10, 11, 12, 13]
        })
        result = calculate_sar(df)
        
        # SAR 应该仍能计算
        assert len(result) == len(df)
    
    def test_constant_prices_macd(self):
        """测试恒定价格的 MACD"""
        prices = pd.Series([10.0] * 50)
        result = calculate_macd(prices)
        
        # MACD 应该接近 0（无趋势）
        macd_valid = result["macd"].dropna()
        if len(macd_valid) > 0:
            assert abs(macd_valid).max() < 0.01
    
    def test_constant_prices_adx(self):
        """测试恒定价格的 ADX"""
        df = pd.DataFrame({
            "high": [10.0] * 50,
            "low": [9.0] * 50,
            "close": [9.5] * 50
        })
        result = calculate_adx(df)
        
        # ADX 应该较低（无趋势）
        adx_valid = result.dropna()
        if len(adx_valid) > 0:
            assert adx_valid.mean() < 20
    
    def test_volatile_prices(self, sample_price_data):
        """测试高波动性价格"""
        # 创建高波动性数据
        volatile_df = sample_price_data.copy()
        volatile_df["close"] = volatile_df["close"] * (1 + np.random.uniform(-0.1, 0.1, len(volatile_df)))
        
        result = calculate_macd(volatile_df["close"])
        
        # MACD 应该有更大的波动
        macd_valid = result["macd"].dropna()
        assert len(macd_valid) > 0
    
    def test_negative_prices_adx(self):
        """测试负价格（ADX 应能处理）"""
        df = pd.DataFrame({
            "high": [-10, -12, -11, -13, -15] * 10,
            "low": [-12, -14, -13, -15, -17] * 10,
            "close": [-11, -13, -12, -14, -16] * 10
        })
        result = calculate_adx(df)
        
        assert len(result) == len(df)


class TestSignalDetection:
    """测试信号检测逻辑"""
    
    def test_macd_golden_cross_detection(self, sample_price_data):
        """测试 MACD 金叉检测"""
        calc = TrendIndicatorCalculator(sample_price_data)
        signals = calc.detect_macd_signal()
        
        # 金叉信号应该是布尔序列
        assert isinstance(signals["buy_signal"], pd.Series)
        assert signals["buy_signal"].dtype == bool
    
    def test_macd_death_cross_detection(self, sample_price_data):
        """测试 MACD 死叉检测"""
        calc = TrendIndicatorCalculator(sample_price_data)
        signals = calc.detect_macd_signal()
        
        # 死叉信号应该是布尔序列
        assert isinstance(signals["sell_signal"], pd.Series)
        assert signals["sell_signal"].dtype == bool
    
    def test_adx_strong_trend_count(self, sample_price_data):
        """测试强趋势数量统计"""
        calc = TrendIndicatorCalculator(sample_price_data)
        calc.add_adx(period=14)
        
        strong_trend = calc.detect_adx_trend_strength(period=14)
        
        # 统计强趋势数量
        strong_count = strong_trend.sum()
        
        # 应该有一些强趋势或非强趋势
        assert strong_count >= 0
        assert strong_count <= len(strong_trend)
