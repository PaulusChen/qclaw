"""
行情数据 API
提供股票、指数行情数据
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
from datetime import datetime
import logging

from config.settings import settings
from services import akshare_service, cache_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/index/{index_id}")
async def get_index_data(
    index_id: str = Path(..., description="指数代码，如：sh000001, sz399001, sz399006"),
    period: str = Query("daily", description="周期：daily/weekly/monthly")
):
    """
    获取指数行情数据
    
    - **index_id**: 指数代码
      - sh000001: 上证指数
      - sz399001: 深证成指
      - sz399006: 创业板指
    - **period**: 数据周期
    """
    cache_key = f"market:index:{index_id}:{period}"
    
    # 尝试从缓存获取
    cached = await cache_service.get(cache_key)
    if cached:
        logger.info(f"缓存命中：{cache_key}")
        return cached
    
    try:
        # 从 AKShare 获取数据
        data = await akshare_service.get_index_data(index_id, period)
        
        # 缓存数据
        await cache_service.set(cache_key, data, settings.CACHE_TTL_MARKET)
        
        return {
            "code": index_id,
            "name": data.get("name", ""),
            "data": data.get("data", []),
            "update_time": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取指数数据失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败：{str(e)}")


@router.get("/stock/{symbol}")
async def get_stock_data(
    symbol: str = Path(..., description="股票代码，如：600519, 000001"),
    period: str = Query("daily", description="周期：daily/weekly/monthly")
):
    """
    获取个股行情数据
    
    - **symbol**: 股票代码
    - **period**: 数据周期
    """
    cache_key = f"market:stock:{symbol}:{period}"
    
    # 尝试从缓存获取
    cached = await cache_service.get(cache_key)
    if cached:
        logger.info(f"缓存命中：{cache_key}")
        return cached
    
    try:
        # 从 AKShare 获取数据
        data = await akshare_service.get_stock_data(symbol, period)
        
        # 缓存数据
        await cache_service.set(cache_key, data, settings.CACHE_TTL_MARKET)
        
        return {
            "symbol": symbol,
            "name": data.get("name", ""),
            "data": data.get("data", []),
            "update_time": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取股票数据失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败：{str(e)}")


@router.get("/realtime/{symbol}")
async def get_realtime_quote(symbol: str = Path(..., description="股票代码或指数代码")):
    """
    获取实时行情
    
    - **symbol**: 股票代码或指数代码
    """
    cache_key = f"market:realtime:{symbol}"
    
    # 尝试从缓存获取（实时数据缓存时间较短）
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 从 AKShare 获取实时数据
        data = await akshare_service.get_realtime_quote(symbol)
        
        # 缓存 30 秒
        await cache_service.set(cache_key, data, 30)
        
        return data
    except Exception as e:
        logger.error(f"获取实时行情失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败：{str(e)}")


@router.get("/market/overview")
async def get_market_overview():
    """
    获取市场概览
    
    返回主要指数的实时行情概览
    """
    cache_key = "market:overview"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取主要指数
        indices = [
            {"id": "sh000001", "name": "上证指数"},
            {"id": "sz399001", "name": "深证成指"},
            {"id": "sz399006", "name": "创业板指"}
        ]
        
        overview = []
        for index in indices:
            try:
                data = await akshare_service.get_realtime_quote(index["id"])
                overview.append({
                    "code": index["id"],
                    "name": index["name"],
                    "current": data.get("current", 0),
                    "change": data.get("change", 0),
                    "change_percent": data.get("change_percent", 0),
                    "volume": data.get("volume", 0),
                    "amount": data.get("amount", 0)
                })
            except Exception as e:
                logger.warning(f"获取 {index['name']} 数据失败：{e}")
                overview.append({
                    "code": index["id"],
                    "name": index["name"],
                    "error": str(e)
                })
        
        result = {
            "indices": overview,
            "update_time": datetime.now().isoformat()
        }
        
        # 缓存 1 分钟
        await cache_service.set(cache_key, result, 60)
        
        return result
    except Exception as e:
        logger.error(f"获取市场概览失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败：{str(e)}")
