"""
市场数据 API
提供大盘指标、个股行情等市场数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/indices")
async def get_market_indices() -> Dict[str, Any]:
    """
    获取大盘指标数据
    
    返回上证指数、深证成指、创业板指的实时数据
    """
    try:
        # TODO: 接入真实数据源 (AKShare/yfinance)
        # 当前使用模拟数据（包含完整的 OHLC 数据）
        return {
            "timestamp": datetime.now().isoformat(),
            "indices": {
                "shanghai": {
                    "name": "上证指数",
                    "code": "000001",
                    "current": 3400.50,
                    "change": 1.25,
                    "changePercent": 0.37,
                    "open": 3395.00,
                    "high": 3410.80,
                    "low": 3388.50,
                    "previousClose": 3399.25,
                    "volume": 285000000000,
                    "turnover": 320000000000
                },
                "shenzhen": {
                    "name": "深证成指",
                    "code": "399001",
                    "current": 11200.80,
                    "change": -0.85,
                    "changePercent": -0.08,
                    "open": 11215.50,
                    "high": 11228.00,
                    "low": 11185.20,
                    "previousClose": 11201.65,
                    "volume": 350000000000,
                    "turnover": 450000000000
                },
                "chinext": {
                    "name": "创业板指",
                    "code": "399006",
                    "current": 2350.20,
                    "change": 2.10,
                    "changePercent": 0.09,
                    "open": 2345.00,
                    "high": 2358.50,
                    "low": 2340.80,
                    "previousClose": 2348.10,
                    "volume": 120000000000,
                    "turnover": 180000000000
                }
            },
            "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"获取大盘指标失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取大盘指标失败：{str(e)}")

@router.get("/indices/{index_code}")
async def get_index_detail(index_code: str) -> Dict[str, Any]:
    """
    获取单个指数详情
    
    Args:
        index_code: 指数代码 (000001, 399001, 399006)
    """
    indices_data = {
        "000001": {"name": "上证指数", "value": 3400.50},
        "399001": {"name": "深证成指", "value": 11200.80},
        "399006": {"name": "创业板指", "value": 2350.20}
    }
    
    if index_code not in indices_data:
        raise HTTPException(status_code=404, detail=f"指数 {index_code} 不存在")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "index": indices_data[index_code]
    }
