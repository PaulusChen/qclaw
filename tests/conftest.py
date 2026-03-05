"""
Pytest 配置文件
定义全局 fixtures 和配置
"""
import pytest
import os
import sys

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def test_config():
    """测试配置 fixture"""
    return {
        "api_url": "http://localhost:8000",
        "frontend_url": "http://localhost:3000",
        "redis_url": "redis://localhost:6379",
        "timeout": 10,
    }


@pytest.fixture
def sample_market_data():
    """示例大盘数据"""
    return {
        "shanghai": {
            "name": "上证指数",
            "code": "000001",
            "current": 3024.56,
            "change": 25.67,
            "changePercent": 0.85,
        },
        "shenzhen": {
            "name": "深证成指",
            "code": "399001",
            "current": 9876.54,
            "change": 120.32,
            "changePercent": 1.23,
        },
        "chinext": {
            "name": "创业板指",
            "code": "399006",
            "current": 2123.45,
            "change": 45.67,
            "changePercent": 2.19,
        },
    }


@pytest.fixture
def sample_technical_data():
    """示例技术指标数据"""
    return {
        "macd": {
            "dif": 0.5,
            "dea": 0.3,
            "macd": 0.2,
        },
        "kdj": {
            "k": 50,
            "d": 45,
            "j": 60,
        },
        "rsi": {
            "rsi_6": 55,
            "rsi_12": 52,
            "rsi_24": 48,
        },
    }


@pytest.fixture
def sample_advice():
    """示例 AI 建议"""
    return {
        "advice": "HOLD",
        "confidence": "MEDIUM",
        "reasons": [
            "大盘震荡整理",
            "技术指标中性",
            "成交量萎缩",
        ],
        "risks": [
            "财报季波动风险",
            "地缘政治不确定性",
        ],
    }


@pytest.fixture
def sample_price_data():
    """示例价格数据 fixture - TEST-UNIT-FIX"""
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    
    dates = pd.date_range('2026-01-01', periods=100, freq='D')
    return pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(3000, 3100, 100),
        'high': np.random.uniform(3100, 3200, 100),
        'low': np.random.uniform(2900, 3000, 100),
        'close': np.random.uniform(3000, 3150, 100),
        'volume': np.random.randint(1000000, 5000000, 100),
    })


@pytest.fixture
def sample_series():
    """示例 Series fixture - TEST-UNIT-FIX
    
    使用固定的测试数据以便测试可重复性
    前几个值设计为便于手动计算：[10, 12, 11, 13, 15, ...]
    """
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    
    fixed_values = [10, 12, 11, 13, 15, 14, 16, 18, 17, 19]
    random_values = np.random.uniform(3000, 3100, 90)
    
    all_values = fixed_values + list(random_values)
    
    return pd.Series(
        all_values,
        name='close',
        index=pd.date_range('2026-01-01', periods=100, freq='D')
    )


@pytest.fixture
def small_dataframe():
    """小型 DataFrame fixture - TEST-UNIT-FIX"""
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range('2026-01-01', periods=5, freq='D')
    return pd.DataFrame({
        'date': dates,
        'close': [100.0, 102.0, 101.5, 103.0, 102.5],
    })
