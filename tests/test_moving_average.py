"""
移动平均线模块测试

测试覆盖：
- calculate_ma 单条 MA 计算
- calculate_ma_multi 多条 MA 计算
- MovingAverageCalculator 类
- 金叉/死叉信号检测
- MA 排列检测
- 边界情况和异常处理
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.indicators.moving_average import (
    calculate_ma,
    calculate_ma_multi,
    MovingAverageCalculator,
    ma5,
    ma10,
    ma20,
    ma60
)


class TestCalculateMA:
    """测试 calculate_ma 函数"""
    
    def test_ma_calculation_basic(self, sample_series):
        """测试基础 MA 计算"""
        result = calculate_ma(sample_series, period=3)
        
        # 验证结果长度
        assert len(result) == len(sample_series)
        
        # 验证前两个值为 NaN（周期为 3）
        assert pd.isna(result.iloc[0])
        assert pd.isna(result.iloc[1])
        
        # 验证第三个值是前三个的平均
        expected = (10 + 12 + 11) / 3
        assert abs(result.iloc[2] - expected) < 0.001
    
    def test_ma_with_dataframe(self, sample_price_data):
        """测试使用 DataFrame 输入"""
        result = calculate_ma(sample_price_data, period=5, price_type="close")
        
        assert len(result) == len(sample_price_data)
        assert result.name == "close"
    
    def test_ma_invalid_column(self, sample_price_data):
        """测试无效的列名"""
        with pytest.raises(ValueError, match="不存在列"):
            calculate_ma(sample_price_data, period=5, price_type="invalid")
    
    def test_ma_different_periods(self, sample_series):
        """测试不同周期的 MA"""
        for period in [3, 5, 10]:
            result = calculate_ma(sample_series, period=period)
            # 前 period-1 个值应该是 NaN
            assert pd.isna(result.iloc[:period-1]).all()
            assert not pd.isna(result.iloc[period-1])
    
    def test_ma_empty_series(self):
        """测试空序列"""
        empty = pd.Series([], dtype=float)
        result = calculate_ma(empty, period=5)
        assert len(result) == 0


class TestCalculateMAMulti:
    """测试 calculate_ma_multi 函数"""
    
    def test_multi_ma_basic(self, sample_price_data):
        """测试多条 MA 计算"""
        result = calculate_ma_multi(sample_price_data, periods=[5, 10, 20])
        
        # 验证新列被添加
        assert "ma5" in result.columns
        assert "ma10" in result.columns
        assert "ma20" in result.columns
        
        # 验证原数据未被修改
        assert "close" in result.columns
    
    def test_multi_ma_default_periods(self, sample_price_data):
        """测试默认周期"""
        result = calculate_ma_multi(sample_price_data)
        
        # 默认周期是 [5, 10, 20, 60]
        assert "ma5" in result.columns
        assert "ma10" in result.columns
        assert "ma20" in result.columns
        assert "ma60" in result.columns
    
    def test_multi_ma_custom_prefix(self, sample_price_data):
        """测试自定义前缀"""
        result = calculate_ma_multi(
            sample_price_data,
            periods=[5, 10],
            output_prefix="MA"
        )
        
        assert "MA5" in result.columns
        assert "MA10" in result.columns
    
    def test_multi_ma_missing_column(self, sample_price_data):
        """测试缺失列"""
        with pytest.raises(ValueError):
            calculate_ma_multi(sample_price_data, price_column="invalid")


class TestMovingAverageCalculator:
    """测试 MovingAverageCalculator 类"""
    
    def test_initialization(self, sample_price_data):
        """测试初始化"""
        calc = MovingAverageCalculator(sample_price_data)
        assert calc.price_column == "close"
        assert len(calc.ma_columns) == 0
    
    def test_add_ma(self, sample_price_data):
        """测试添加单条 MA"""
        calc = MovingAverageCalculator(sample_price_data)
        result = calc.add_ma(5)
        
        # 验证链式调用
        assert result is calc
        
        # 验证 MA 被添加
        assert "MA5" in calc.df.columns
        assert 5 in calc.ma_columns
    
    def test_add_ma_custom_name(self, sample_price_data):
        """测试自定义 MA 列名"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_ma(5, column_name="my_ma5")
        
        assert "my_ma5" in calc.df.columns
    
    def test_add_common_mas(self, sample_price_data):
        """测试添加常用 MA"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_common_mas()
        
        # 验证常用 MA 都被添加
        for period in [5, 10, 20, 60, 120, 250]:
            assert f"MA{period}" in calc.df.columns
    
    def test_get_ma(self, sample_price_data):
        """测试获取 MA"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_ma(5)
        
        ma = calc.get_ma(5)
        assert ma is not None
        assert len(ma) == len(sample_price_data)
    
    def test_get_ma_not_calculated(self, sample_price_data):
        """测试获取未计算的 MA"""
        calc = MovingAverageCalculator(sample_price_data)
        
        # 应该临时计算并返回
        ma = calc.get_ma(5)
        assert ma is not None
    
    def test_detect_golden_cross(self, sample_price_data):
        """测试金叉检测"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_common_mas()
        
        signals = calc.detect_golden_cross(short_period=5, long_period=20)
        
        # 验证返回布尔序列
        assert isinstance(signals, pd.Series)
        assert signals.dtype == bool
        assert len(signals) == len(sample_price_data)
    
    def test_detect_death_cross(self, sample_price_data):
        """测试死叉检测"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_common_mas()
        
        signals = calc.detect_death_cross(short_period=5, long_period=20)
        
        assert isinstance(signals, pd.Series)
        assert signals.dtype == bool
    
    def test_detect_cross_without_ma(self, sample_price_data):
        """测试未计算 MA 时检测交叉（应临时计算）"""
        calc = MovingAverageCalculator(sample_price_data)
        
        # 代码设计为临时计算 MA，不应抛出异常
        signals = calc.detect_golden_cross()
        
        # 应返回布尔序列
        assert isinstance(signals, pd.Series)
        assert signals.dtype == bool
    
    def test_ma_alignment_bullish(self, sample_price_data):
        """测试多头排列检测"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_common_mas()
        
        signals = calc.get_ma_alignment(periods=[5, 10, 20], direction="bullish")
        
        assert isinstance(signals, pd.Series)
        assert signals.dtype == bool
    
    def test_ma_alignment_bearish(self, sample_price_data):
        """测试空头排列检测"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_common_mas()
        
        signals = calc.get_ma_alignment(periods=[5, 10, 20], direction="bearish")
        
        assert isinstance(signals, pd.Series)
    
    def test_ma_alignment_invalid_direction(self, sample_price_data):
        """测试无效排列方向"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_common_mas()
        
        with pytest.raises(ValueError, match="无效的排列方向"):
            calc.get_ma_alignment(direction="invalid")
    
    def test_get_dataframe(self, sample_price_data):
        """测试获取 DataFrame"""
        calc = MovingAverageCalculator(sample_price_data)
        calc.add_ma(5)
        
        df = calc.get_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert "MA5" in df.columns


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_ma5(self, sample_series):
        """测试 ma5 函数"""
        result = ma5(sample_series)
        expected = calculate_ma(sample_series, period=5)
        pd.testing.assert_series_equal(result, expected)
    
    def test_ma10(self, sample_series):
        """测试 ma10 函数"""
        result = ma10(sample_series)
        expected = calculate_ma(sample_series, period=10)
        pd.testing.assert_series_equal(result, expected)
    
    def test_ma20(self, sample_series):
        """测试 ma20 函数"""
        result = ma20(sample_series)
        expected = calculate_ma(sample_series, period=20)
        pd.testing.assert_series_equal(result, expected)
    
    def test_ma60(self, sample_series):
        """测试 ma60 函数"""
        result = ma60(sample_series)
        expected = calculate_ma(sample_series, period=60)
        pd.testing.assert_series_equal(result, expected)


class TestEdgeCases:
    """测试边界情况"""
    
    def test_insufficient_data(self, small_dataframe):
        """测试数据不足的情况"""
        result = calculate_ma_multi(small_dataframe, periods=[5, 10])
        
        # 应该能计算，但结果大部分是 NaN
        # MA5 需要 5 个数据点，所以前 4 个是 NaN，第 5 个有值
        # MA10 需要 10 个数据点，所以全部是 NaN（只有 5 行数据）
        assert "ma5" in result.columns
        assert "ma10" in result.columns
        assert pd.isna(result["ma5"]).iloc[:4].all()  # 前 4 个是 NaN
        assert not pd.isna(result["ma5"]).iloc[4]     # 第 5 个有值
        assert pd.isna(result["ma10"]).all()          # MA10 全部是 NaN
    
    def test_constant_prices(self):
        """测试恒定价格"""
        prices = pd.Series([10.0] * 20)
        result = calculate_ma(prices, period=5)
        
        # MA 应该也是恒定的
        assert result.iloc[4:].std() == 0
    
    def test_negative_prices(self):
        """测试负价格（虽然不现实，但应该能处理）"""
        prices = pd.Series([-10, -12, -11, -13, -15])
        result = calculate_ma(prices, period=3)
        
        assert len(result) == 5
        assert not pd.isna(result.iloc[2])
