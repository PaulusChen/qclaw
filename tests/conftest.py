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
