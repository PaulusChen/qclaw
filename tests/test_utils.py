"""
工具函数模块测试

测试覆盖：
- setup_logger 日志设置
- validate_dataframe DataFrame 验证
- validate_series Series 验证
- check_numeric_data 数值类型检查
- 边界情况和异常处理
"""

import pytest
import pandas as pd
import numpy as np
import logging
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import (
    setup_logger,
    validate_dataframe,
    validate_series,
    check_numeric_data
)


class TestSetupLogger:
    """测试 setup_logger 函数"""
    
    def test_logger_creation(self):
        """测试 logger 创建"""
        logger = setup_logger("test_logger")
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG
    
    def test_logger_custom_level(self):
        """测试自定义日志级别"""
        logger = setup_logger("test_logger_info", level=logging.INFO)
        
        assert logger.level == logging.INFO
    
    def test_logger_custom_format(self):
        """测试自定义日志格式"""
        custom_format = "%(levelname)s - %(message)s"
        logger = setup_logger("test_logger_format", format_string=custom_format)
        
        assert logger is not None
        # 验证 handler 存在
        assert len(logger.handlers) > 0
    
    def test_logger_singleton(self):
        """测试 logger 单例（重复调用返回同一实例）"""
        logger1 = setup_logger("test_singleton")
        logger2 = setup_logger("test_singleton")
        
        # 应该是同一个 logger 实例
        assert logger1 is logger2
    
    def test_logger_handlers_not_duplicated(self):
        """测试 handler 不重复添加"""
        logger = setup_logger("test_handlers")
        handler_count_1 = len(logger.handlers)
        
        # 再次调用
        logger = setup_logger("test_handlers")
        handler_count_2 = len(logger.handlers)
        
        # handler 数量不应增加
        assert handler_count_1 == handler_count_2
    
    def test_logger_can_log(self, caplog):
        """测试 logger 可以正常记录日志"""
        logger = setup_logger("test_log")
        
        with caplog.at_level(logging.DEBUG):
            logger.debug("Test debug message")
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
        
        assert "Test debug message" in caplog.text
        assert "Test info message" in caplog.text
        assert "Test warning message" in caplog.text
        assert "Test error message" in caplog.text


class TestValidateDataframe:
    """测试 validate_dataframe 函数"""
    
    def test_valid_dataframe(self, sample_price_data):
        """测试有效的 DataFrame"""
        result = validate_dataframe(sample_price_data, ["close", "high", "low"])
        
        assert result is True
    
    def test_missing_columns(self, sample_price_data):
        """测试缺失列"""
        with pytest.raises(ValueError, match="缺少必需的列"):
            validate_dataframe(sample_price_data, ["close", "invalid_column"])
    
    def test_missing_columns_no_raise(self, sample_price_data):
        """测试缺失列但不抛出异常"""
        result = validate_dataframe(
            sample_price_data,
            ["close", "invalid_column"],
            raise_error=False
        )
        
        assert result is False
    
    def test_empty_dataframe(self):
        """测试空 DataFrame"""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="缺少必需的列"):
            validate_dataframe(df, ["close"])
    
    def test_none_dataframe(self):
        """测试 None 输入"""
        with pytest.raises(ValueError, match="不能为空"):
            validate_dataframe(None, ["close"])
    
    def test_none_dataframe_no_raise(self):
        """测试 None 输入但不抛出异常"""
        result = validate_dataframe(None, ["close"], raise_error=False)
        
        assert result is False
    
    def test_not_dataframe_input(self):
        """测试非 DataFrame 输入"""
        with pytest.raises(ValueError, match="必须是 pandas DataFrame"):
            validate_dataframe([1, 2, 3], ["close"])
    
    def test_not_dataframe_no_raise(self):
        """测试非 DataFrame 输入但不抛出异常"""
        result = validate_dataframe([1, 2, 3], ["close"], raise_error=False)
        
        assert result is False
    
    def test_single_column(self, sample_price_data):
        """测试单列验证"""
        result = validate_dataframe(sample_price_data, ["close"])
        
        assert result is True
    
    def test_all_columns_present(self, sample_price_data):
        """测试所有列都存在"""
        result = validate_dataframe(
            sample_price_data,
            ["open", "high", "low", "close", "volume"]
        )
        
        assert result is True


class TestValidateSeries:
    """测试 validate_series 函数"""
    
    def test_valid_series(self, sample_series):
        """测试有效的 Series"""
        result = validate_series(sample_series)
        
        assert result is True
    
    def test_series_with_name(self):
        """测试带名称的 Series"""
        series = pd.Series([1, 2, 3], name="test")
        
        result = validate_series(series, name="test")
        
        assert result is True
    
    def test_series_name_mismatch(self):
        """测试 Series 名称不匹配"""
        series = pd.Series([1, 2, 3], name="test")
        
        with pytest.raises(ValueError, match="名称不匹配"):
            validate_series(series, name="wrong_name")
    
    def test_series_name_mismatch_no_raise(self):
        """测试 Series 名称不匹配但不抛出异常"""
        series = pd.Series([1, 2, 3], name="test")
        
        result = validate_series(series, name="wrong_name", raise_error=False)
        
        assert result is False
    
    def test_none_series(self):
        """测试 None 输入"""
        with pytest.raises(ValueError, match="不能为空"):
            validate_series(None)
    
    def test_none_series_no_raise(self):
        """测试 None 输入但不抛出异常"""
        result = validate_series(None, raise_error=False)
        
        assert result is False
    
    def test_not_series_input(self):
        """测试非 Series 输入"""
        with pytest.raises(ValueError, match="必须是 pandas Series"):
            validate_series([1, 2, 3])
    
    def test_not_series_no_raise(self):
        """测试非 Series 输入但不抛出异常"""
        result = validate_series([1, 2, 3], raise_error=False)
        
        assert result is False
    
    def test_empty_series(self):
        """测试空 Series"""
        series = pd.Series([], dtype=float)
        
        result = validate_series(series)
        
        assert result is True
    
    def test_series_without_name(self, sample_series):
        """测试没有名称的 Series"""
        # sample_series 没有设置 name
        result = validate_series(sample_series)
        
        assert result is True


class TestCheckNumericData:
    """测试 check_numeric_data 函数"""
    
    def test_numeric_series(self, sample_series):
        """测试数值型 Series"""
        result = check_numeric_data(sample_series)
        
        assert result is True
    
    def test_float_series(self):
        """测试浮点数 Series"""
        series = pd.Series([1.5, 2.7, 3.14])
        
        result = check_numeric_data(series)
        
        assert result is True
    
    def test_non_numeric_series(self):
        """测试非数值型 Series"""
        series = pd.Series(["a", "b", "c"])
        
        with pytest.raises(ValueError, match="必须是数值类型"):
            check_numeric_data(series)
    
    def test_non_numeric_no_raise(self):
        """测试非数值型但不抛出异常"""
        series = pd.Series(["a", "b", "c"])
        
        result = check_numeric_data(series, raise_error=False)
        
        assert result is False
    
    def test_series_with_nan(self):
        """测试包含 NaN 的 Series"""
        series = pd.Series([1.0, np.nan, 3.0])
        
        # 默认允许 NaN
        result = check_numeric_data(series)
        
        assert result is True
    
    def test_series_with_nan_not_allowed(self):
        """测试 NaN 不允许的情况"""
        series = pd.Series([1.0, np.nan, 3.0])
        
        with pytest.raises(ValueError, match="包含 NaN 值"):
            check_numeric_data(series, allow_nan=False)
    
    def test_series_with_nan_not_allowed_no_raise(self):
        """测试 NaN 不允许但不抛出异常"""
        series = pd.Series([1.0, np.nan, 3.0])
        
        result = check_numeric_data(series, allow_nan=False, raise_error=False)
        
        assert result is False
    
    def test_series_without_nan(self):
        """测试不包含 NaN 的 Series"""
        series = pd.Series([1.0, 2.0, 3.0])
        
        result = check_numeric_data(series, allow_nan=False)
        
        assert result is True
    
    def test_custom_column_name(self):
        """测试自定义列名"""
        series = pd.Series(["a", "b", "c"])
        
        with pytest.raises(ValueError, match="price 必须是数值类型"):
            check_numeric_data(series, column_name="price")
    
    def test_integer_series(self):
        """测试整数 Series"""
        series = pd.Series([1, 2, 3, 4, 5])
        
        result = check_numeric_data(series)
        
        assert result is True
    
    def test_mixed_numeric(self):
        """测试混合数值类型"""
        series = pd.Series([1, 2.5, 3, 4.7, 5])
        
        result = check_numeric_data(series)
        
        assert result is True


class TestEdgeCases:
    """测试边界情况"""
    
    def test_empty_dataframe_columns(self):
        """测试空列名列表"""
        df = pd.DataFrame({"close": [1, 2, 3]})
        
        # 空列名列表应该通过验证
        result = validate_dataframe(df, [])
        
        assert result is True
    
    def test_duplicate_column_requirements(self, sample_price_data):
        """测试重复的列名要求"""
        result = validate_dataframe(sample_price_data, ["close", "close", "close"])
        
        assert result is True
    
    def test_case_sensitive_columns(self, sample_price_data):
        """测试列名大小写敏感"""
        with pytest.raises(ValueError):
            validate_dataframe(sample_price_data, ["CLOSE"])  # 应该是 "close"
    
    def test_series_with_none_values(self):
        """测试包含 None 值的 Series"""
        series = pd.Series([1, None, 3])
        
        # None 会被视为 NaN
        result = check_numeric_data(series)
        
        assert result is True
    
    def test_series_with_inf(self):
        """测试包含无穷大的 Series"""
        series = pd.Series([1, np.inf, 3])
        
        # inf 是数值类型
        result = check_numeric_data(series)
        
        assert result is True
    
    def test_large_dataframe(self):
        """测试大型 DataFrame"""
        df = pd.DataFrame({
            "close": np.random.randn(10000),
            "volume": np.random.randint(1000, 10000, 10000)
        })
        
        result = validate_dataframe(df, ["close", "volume"])
        
        assert result is True
    
    def test_dataframe_with_multiindex(self):
        """测试 MultiIndex DataFrame"""
        arrays = [
            ["bar", "bar", "baz", "baz"],
            ["one", "two", "one", "two"]
        ]
        index = pd.MultiIndex.from_arrays(arrays, names=["first", "second"])
        df = pd.DataFrame({"close": [1, 2, 3, 4]}, index=index)
        
        result = validate_dataframe(df, ["close"])
        
        assert result is True


class TestIntegration:
    """测试集成场景"""
    
    def test_validate_then_process(self, sample_price_data):
        """测试验证后处理"""
        # 先验证
        assert validate_dataframe(sample_price_data, ["close", "high", "low"])
        
        # 然后处理（这里简单验证数据可用）
        assert len(sample_price_data) > 0
        assert sample_price_data["close"].notna().any()
    
    def test_logger_with_indicator_calc(self, sample_price_data, caplog):
        """测试 logger 与指标计算集成"""
        from src.indicators.moving_average import calculate_ma
        
        logger = setup_logger("test_integration")
        
        with caplog.at_level(logging.DEBUG):
            result = calculate_ma(sample_price_data["close"], period=5)
        
        # 验证计算成功
        assert len(result) == len(sample_price_data)
        
        # 验证日志记录
        assert "MA" in caplog.text or "计算" in caplog.text or len(caplog.text) > 0
