"""
Pytest 配置文件
"""

import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture
def sample_stock_data():
    """示例股票数据"""
    return {
        "symbol": "600519",
        "name": "贵州茅台",
        "price": 1402.00,
        "change": 1.25,
        "changePercent": 0.09
    }
