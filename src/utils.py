"""
工具函数模块

提供日志设置、数据验证等通用工具函数。
"""

import logging
from typing import List, Optional
import pandas as pd
import sys


def setup_logger(
    name: str,
    level: int = logging.DEBUG,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置并返回 logger
    
    Args:
        name: logger 名称
        level: 日志级别
        format_string: 日志格式字符串
        
    Returns:
        配置好的 logger 实例
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已经有 handler，不再添加
    if logger.handlers:
        return logger
    
    # 创建控制台 handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # 设置格式
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str],
    raise_error: bool = True
) -> bool:
    """
    验证 DataFrame 是否包含必需的列
    
    Args:
        df: 要验证的 DataFrame
        required_columns: 必需的列名列表
        raise_error: 是否抛出异常
        
    Returns:
        验证是否通过
        
    Raises:
        ValueError: 当缺少必需列且 raise_error=True 时
    """
    if df is None:
        if raise_error:
            raise ValueError("DataFrame 不能为空")
        return False
    
    if not isinstance(df, pd.DataFrame):
        if raise_error:
            raise ValueError("输入必须是 pandas DataFrame")
        return False
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        if raise_error:
            raise ValueError(f"DataFrame 中缺少必需的列：{missing_columns}")
        return False
    
    return True


def validate_series(
    series: pd.Series,
    name: Optional[str] = None,
    raise_error: bool = True
) -> bool:
    """
    验证 Series 是否有效
    
    Args:
        series: 要验证的 Series
        name: 期望的 Series 名称（可选）
        raise_error: 是否抛出异常
        
    Returns:
        验证是否通过
    """
    if series is None:
        if raise_error:
            raise ValueError("Series 不能为空")
        return False
    
    if not isinstance(series, pd.Series):
        if raise_error:
            raise ValueError("输入必须是 pandas Series")
        return False
    
    if name is not None and series.name != name:
        if raise_error:
            raise ValueError(f"Series 名称不匹配：期望 '{name}'，实际 '{series.name}'")
        return False
    
    return True


def check_numeric_data(
    data: pd.Series,
    column_name: str = "data",
    allow_nan: bool = True,
    raise_error: bool = True
) -> bool:
    """
    检查数据是否为数值类型
    
    Args:
        data: 要检查的数据
        column_name: 列名（用于错误信息）
        allow_nan: 是否允许 NaN 值
        raise_error: 是否抛出异常
        
    Returns:
        检查是否通过
    """
    if not pd.api.types.is_numeric_dtype(data):
        if raise_error:
            raise ValueError(f"{column_name} 必须是数值类型")
        return False
    
    if not allow_nan and data.isna().any():
        if raise_error:
            raise ValueError(f"{column_name} 包含 NaN 值")
        return False
    
    return True
