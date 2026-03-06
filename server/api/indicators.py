"""
技术指标 API
提供 MACD、KDJ、RSI 等技术指标计算
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List
from datetime import datetime
import logging

from config.settings import settings
from services import akshare_service, cache_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/macd/{symbol}")
async def get_macd(
    symbol: str = Path(..., description="股票代码或指数代码"),
    period: str = Query("daily", description="周期：daily/weekly/monthly")
):
    """
    获取 MACD 指标
    
    MACD (Moving Average Convergence Divergence)
    - DIF: 快线
    - DEA: 慢线
    - MACD: 柱状图
    """
    cache_key = f"indicator:macd:{symbol}:{period}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取历史数据
        data = await akshare_service.get_index_data(symbol, period)
        close_prices = [item["close"] for item in data.get("data", [])]
        
        # 计算 MACD
        macd_data = calculate_macd(close_prices)
        
        result = {
            "symbol": symbol,
            "indicator": "MACD",
            "data": macd_data,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_INDICATOR)
        return result
    except Exception as e:
        logger.error(f"计算 MACD 失败：{e}")
        raise HTTPException(status_code=500, detail=f"计算失败：{str(e)}")


@router.get("/kdj/{symbol}")
async def get_kdj(
    symbol: str = Path(..., description="股票代码或指数代码"),
    period: str = Query("daily", description="周期：daily/weekly/monthly")
):
    """
    获取 KDJ 指标
    
    KDJ (随机指标)
    - K: 快线
    - D: 慢线
    - J: 超快线
    """
    cache_key = f"indicator:kdj:{symbol}:{period}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取历史数据
        data = await akshare_service.get_index_data(symbol, period)
        price_data = data.get("data", [])
        
        # 计算 KDJ
        kdj_data = calculate_kdj(price_data)
        
        result = {
            "symbol": symbol,
            "indicator": "KDJ",
            "data": kdj_data,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_INDICATOR)
        return result
    except Exception as e:
        logger.error(f"计算 KDJ 失败：{e}")
        raise HTTPException(status_code=500, detail=f"计算失败：{str(e)}")


@router.get("/rsi/{symbol}")
async def get_rsi(
    symbol: str = Path(..., description="股票代码或指数代码"),
    period: str = Query("daily", description="周期：daily/weekly/monthly"),
    n: int = Query(14, description="RSI 周期，默认 14")
):
    """
    获取 RSI 指标
    
    RSI (Relative Strength Index, 相对强弱指标)
    - RSI > 70: 超买
    - RSI < 30: 超卖
    """
    cache_key = f"indicator:rsi:{symbol}:{period}:{n}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取历史数据
        data = await akshare_service.get_index_data(symbol, period)
        close_prices = [item["close"] for item in data.get("data", [])]
        
        # 计算 RSI
        rsi_data = calculate_rsi(close_prices, n)
        
        result = {
            "symbol": symbol,
            "indicator": "RSI",
            "period": n,
            "data": rsi_data,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_INDICATOR)
        return result
    except Exception as e:
        logger.error(f"计算 RSI 失败：{e}")
        raise HTTPException(status_code=500, detail=f"计算失败：{str(e)}")


@router.get("/ma/{symbol}")
async def get_ma(
    symbol: str = Path(..., description="股票代码或指数代码"),
    period: str = Query("daily", description="周期：daily/weekly/monthly"),
    windows: List[int] = Query([5, 10, 20], description="均线周期列表")
):
    """
    获取移动平均线
    
    MA (Moving Average)
    - MA5: 5 日均线
    - MA10: 10 日均线
    - MA20: 20 日均线
    """
    cache_key = f"indicator:ma:{symbol}:{period}:{','.join(map(str, windows))}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取历史数据
        data = await akshare_service.get_index_data(symbol, period)
        close_prices = [item["close"] for item in data.get("data", [])]
        
        # 计算均线
        ma_data = calculate_ma(close_prices, windows)
        
        result = {
            "symbol": symbol,
            "indicator": "MA",
            "windows": windows,
            "data": ma_data,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_INDICATOR)
        return result
    except Exception as e:
        logger.error(f"计算均线失败：{e}")
        raise HTTPException(status_code=500, detail=f"计算失败：{str(e)}")


@router.get("/boll/{symbol}")
async def get_boll(
    symbol: str = Path(..., description="股票代码或指数代码"),
    period: str = Query("daily", description="周期：daily/weekly/monthly"),
    n: int = Query(20, description="布林带周期")
):
    """
    获取布林带指标
    
    BOLL (Bollinger Bands)
    - UPPER: 上轨
    - MID: 中轨
    - LOWER: 下轨
    """
    cache_key = f"indicator:boll:{symbol}:{period}:{n}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取历史数据
        data = await akshare_service.get_index_data(symbol, period)
        close_prices = [item["close"] for item in data.get("data", [])]
        
        # 计算布林带
        boll_data = calculate_boll(close_prices, n)
        
        result = {
            "symbol": symbol,
            "indicator": "BOLL",
            "period": n,
            "data": boll_data,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_INDICATOR)
        return result
    except Exception as e:
        logger.error(f"计算布林带失败：{e}")
        raise HTTPException(status_code=500, detail=f"计算失败：{str(e)}")


# ============ 指标计算函数 ============

def calculate_macd(prices: List[float], short: int = 12, long: int = 26, signal: int = 9) -> List[dict]:
    """计算 MACD 指标"""
    if len(prices) < long + signal:
        return []
    
    # 计算 EMA
    ema_short = calculate_ema(prices, short)
    ema_long = calculate_ema(prices, long)
    
    # DIF = EMA(short) - EMA(long)
    dif = [s - l for s, l in zip(ema_short, ema_long)]
    
    # DEA = EMA(DIF, signal)
    dea = calculate_ema(dif, signal)
    
    # MACD = 2 * (DIF - DEA)
    macd = [2 * (d - e) for d, e in zip(dif, dea)]
    
    return [
        {"dif": dif[i], "dea": dea[i], "macd": macd[i]}
        for i in range(len(macd))
    ]


def calculate_kdj(price_data: List[dict], n: int = 9, m1: int = 3, m2: int = 3) -> List[dict]:
    """计算 KDJ 指标"""
    if len(price_data) < n:
        return []
    
    result = []
    prev_k = 50.0
    prev_d = 50.0
    
    for i in range(n - 1, len(price_data)):
        window = price_data[i - n + 1:i + 1]
        high = max(p["high"] for p in window)
        low = min(p["low"] for p in window)
        close = price_data[i]["close"]
        
        if high == low:
            rsv = 0.0
        else:
            rsv = (close - low) / (high - low) * 100
        
        k = (m1 - 1) / m1 * prev_k + 1 / m1 * rsv
        d = (m2 - 1) / m2 * prev_d + 1 / m2 * k
        j = 3 * k - 2 * d
        
        result.append({"k": k, "d": d, "j": j})
        prev_k = k
        prev_d = d
    
    return result


def calculate_rsi(prices: List[float], n: int = 14) -> List[float]:
    """计算 RSI 指标"""
    if len(prices) < n + 1:
        return []
    
    result = []
    
    for i in range(n, len(prices)):
        gains = []
        losses = []
        
        for j in range(i - n + 1, i + 1):
            change = prices[j] - prices[j - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / n
        avg_loss = sum(losses) / n
        
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        result.append(rsi)
    
    return result


def calculate_ma(prices: List[float], windows: List[int]) -> dict:
    """计算移动平均线"""
    result = {}
    
    for window in windows:
        ma_values = []
        for i in range(window - 1, len(prices)):
            ma = sum(prices[i - window + 1:i + 1]) / window
            ma_values.append(ma)
        result[f"ma{window}"] = ma_values
    
    return result


def calculate_boll(prices: List[float], n: int = 20, k: float = 2.0) -> List[dict]:
    """计算布林带"""
    if len(prices) < n:
        return []
    
    result = []
    
    for i in range(n - 1, len(prices)):
        window = prices[i - n + 1:i + 1]
        mid = sum(window) / n
        
        variance = sum((p - mid) ** 2 for p in window) / n
        std = variance ** 0.5
        
        upper = mid + k * std
        lower = mid - k * std
        
        result.append({"upper": upper, "mid": mid, "lower": lower})
    
    return result


def calculate_ema(prices: List[float], n: int) -> List[float]:
    """计算指数移动平均"""
    if len(prices) < n:
        return []
    
    multiplier = 2 / (n + 1)
    
    # 第一个 EMA 使用 SMA
    ema = [sum(prices[:n]) / n]
    
    for i in range(n, len(prices)):
        ema.append((prices[i] - ema[-1]) * multiplier + ema[-1])
    
    # 前面填充 None 以保持长度一致
    return [None] * (n - 1) + ema
