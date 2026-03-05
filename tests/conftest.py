"""
Pytest 配置文件

提供共享的测试夹具 (fixtures)
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_price_data():
    """
    生成模拟的股票价格数据
    
    Returns:
        包含 OHLCV 数据的 DataFrame
    """
    np.random.seed(42)
    
    # 生成 100 个交易日的模拟数据
    dates = pd.date_range(start="2025-01-01", periods=100, freq="D")
    
    # 模拟价格走势（随机游走）
    base_price = 100
    returns = np.random.normal(0.001, 0.02, 100)
    close_prices = base_price * np.cumprod(1 + returns)
    
    # 生成 OHLC 数据
    df = pd.DataFrame({
        "date": dates,
        "open": close_prices * (1 + np.random.uniform(-0.01, 0.01, 100)),
        "high": close_prices * (1 + np.random.uniform(0, 0.03, 100)),
        "low": close_prices * (1 + np.random.uniform(-0.03, 0, 100)),
        "close": close_prices,
        "volume": np.random.randint(1000000, 10000000, 100)
    })
    
    df.set_index("date", inplace=True)
    
    return df


@pytest.fixture
def sample_series():
    """
    生成简单的价格序列用于基础测试
    
    Returns:
        pandas Series
    """
    return pd.Series([10, 12, 11, 13, 15, 14, 16, 18, 17, 19, 20, 22, 21, 23, 25])


@pytest.fixture
def empty_dataframe():
    """
    空 DataFrame 用于边界测试
    
    Returns:
        空的 DataFrame
    """
    return pd.DataFrame()


@pytest.fixture
def small_dataframe():
    """
    小型 DataFrame 用于边界测试（少于 MA 周期）
    
    Returns:
        小型 DataFrame
    """
    return pd.DataFrame({
        "close": [10, 12, 11]
    })
