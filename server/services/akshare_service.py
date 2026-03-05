"""
AKShare 数据服务
提供股票、指数行情数据获取
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

# 服务初始化状态
_initialized = False


async def init() -> bool:
    """
    初始化 AKShare 服务
    
    Returns:
        是否初始化成功
    """
    global _initialized
    
    try:
        # 测试导入 AKShare
        import akshare as ak
        logger.info("AKShare 导入成功")
        _initialized = True
        return True
    except ImportError as e:
        logger.warning(f"AKShare 未安装：{e}")
        _initialized = False
        return False
    except Exception as e:
        logger.error(f"AKShare 初始化失败：{e}")
        _initialized = False
        return False


async def get_index_data(
    index_id: str,
    period: str = "daily"
) -> Dict[str, Any]:
    """
    获取指数历史行情数据
    
    Args:
        index_id: 指数代码，如 sh000001, sz399001, sz399006
        period: 周期 daily/weekly/monthly
        
    Returns:
        指数数据字典
    """
    try:
        import akshare as ak
        
        # 映射指数代码
        symbol_map = {
            "sh000001": "上证指数",
            "sz399001": "深证成指",
            "sz399006": "创业板指",
            "sh000016": "上证 50",
            "sh000300": "沪深 300",
            "sh000905": "中证 500"
        }
        
        symbol = symbol_map.get(index_id, index_id)
        
        # 获取历史行情
        df = await asyncio.to_thread(
            ak.stock_zh_index_daily,
            symbol=index_id
        )
        
        # 转换数据格式
        data = []
        for _, row in df.iterrows():
            data.append({
                "date": str(row.get("date", "")),
                "open": float(row.get("open", 0)),
                "high": float(row.get("high", 0)),
                "low": float(row.get("low", 0)),
                "close": float(row.get("close", 0)),
                "volume": float(row.get("volume", 0))
            })
        
        return {
            "name": symbol,
            "code": index_id,
            "data": data[-250:]  # 返回最近 250 个交易日
        }
        
    except Exception as e:
        logger.error(f"获取指数数据失败 {index_id}: {e}")
        # 返回模拟数据用于测试
        return get_mock_index_data(index_id)


async def get_stock_data(
    symbol: str,
    period: str = "daily"
) -> Dict[str, Any]:
    """
    获取个股历史行情数据
    
    Args:
        symbol: 股票代码，如 600519, 000001
        period: 周期 daily/weekly/monthly
        
    Returns:
        股票数据字典
    """
    try:
        import akshare as ak
        
        # 确定市场前缀
        if symbol.startswith("6"):
            market = "sh"
        else:
            market = "sz"
        
        full_symbol = f"{market}{symbol}"
        
        # 获取历史行情
        df = await asyncio.to_thread(
            ak.stock_zh_a_hist,
            symbol=symbol,
            period="daily",
            start_date="20250101",
            end_date=datetime.now().strftime("%Y%m%d")
        )
        
        # 转换数据格式
        data = []
        for _, row in df.iterrows():
            data.append({
                "date": str(row.get("日期", "")),
                "open": float(row.get("开盘", 0)),
                "high": float(row.get("最高", 0)),
                "low": float(row.get("最低", 0)),
                "close": float(row.get("收盘", 0)),
                "volume": float(row.get("成交量", 0)),
                "amount": float(row.get("成交额", 0))
            })
        
        return {
            "name": f"{symbol}",
            "code": full_symbol,
            "data": data[-250:]
        }
        
    except Exception as e:
        logger.error(f"获取股票数据失败 {symbol}: {e}")
        return get_mock_stock_data(symbol)


async def get_realtime_quote(symbol: str) -> Dict[str, Any]:
    """
    获取实时行情
    
    Args:
        symbol: 股票代码或指数代码
        
    Returns:
        实时行情数据
    """
    try:
        import akshare as ak
        
        # 判断是指数还是股票
        if symbol.startswith("sh") or symbol.startswith("sz"):
            if symbol.startswith("sh00") or symbol.startswith("sz39"):
                # 指数
                df = await asyncio.to_thread(
                    ak.stock_zh_index_spot
                )
                row = df[df['代码'] == symbol].iloc[0] if len(df) > 0 else None
            else:
                # 股票
                df = await asyncio.to_thread(
                    ak.stock_zh_a_spot_em
                )
                row = df[df['代码'] == symbol[2:]].iloc[0] if len(df) > 0 else None
            
            if row is not None:
                return {
                    "symbol": symbol,
                    "current": float(row.get("最新价", 0)),
                    "change": float(row.get("涨跌幅", 0)),
                    "change_percent": float(row.get("涨跌幅", 0)),
                    "open": float(row.get("今开", 0)),
                    "high": float(row.get("最高", 0)),
                    "low": float(row.get("最低", 0)),
                    "pre_close": float(row.get("昨收", 0)),
                    "volume": float(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0))
                }
        
        # 返回模拟数据
        return get_mock_realtime_quote(symbol)
        
    except Exception as e:
        logger.error(f"获取实时行情失败 {symbol}: {e}")
        return get_mock_realtime_quote(symbol)


# ============ 模拟数据（用于 AKShare 不可用时） ============

def get_mock_index_data(index_id: str) -> Dict[str, Any]:
    """生成模拟指数数据"""
    symbol_map = {
        "sh000001": "上证指数",
        "sz399001": "深证成指",
        "sz399006": "创业板指"
    }
    
    base_prices = {
        "sh000001": 3400,
        "sz399001": 11000,
        "sz399006": 2300
    }
    
    base = base_prices.get(index_id, 3000)
    data = []
    
    # 生成 250 天模拟数据
    current = base * 0.9
    for i in range(250):
        date = (datetime.now() - timedelta(days=250-i)).strftime("%Y-%m-%d")
        change = (hash(f"{index_id}{i}") % 100 - 45) / 1000  # -4.5% to +5.5%
        current = current * (1 + change)
        
        high = current * (1 + abs(hash(f"h{i}") % 20) / 1000)
        low = current * (1 - abs(hash(f"l{i}") % 20) / 1000)
        open_price = current * (1 + (hash(f"o{i}") % 10 - 5) / 1000)
        
        data.append({
            "date": date,
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(current, 2),
            "volume": int(abs(hash(f"v{i}") % 100000000) + 10000000)
        })
    
    return {
        "name": symbol_map.get(index_id, "未知指数"),
        "code": index_id,
        "data": data
    }


def get_mock_stock_data(symbol: str) -> Dict[str, Any]:
    """生成模拟股票数据"""
    base = 50 + (hash(symbol) % 200)
    data = []
    
    current = base * 0.8
    for i in range(250):
        date = (datetime.now() - timedelta(days=250-i)).strftime("%Y-%m-%d")
        change = (hash(f"{symbol}{i}") % 100 - 45) / 1000
        current = current * (1 + change)
        
        high = current * (1 + abs(hash(f"h{i}") % 30) / 1000)
        low = current * (1 - abs(hash(f"l{i}") % 30) / 1000)
        open_price = current * (1 + (hash(f"o{i}") % 10 - 5) / 1000)
        
        data.append({
            "date": date,
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(current, 2),
            "volume": int(abs(hash(f"v{i}") % 50000000) + 1000000),
            "amount": round(current * hash(f"a{i}") % 100000000, 2)
        })
    
    return {
        "name": f"{symbol}",
        "code": f"sz{symbol}" if symbol[0] != '6' else f"sh{symbol}",
        "data": data
    }


def get_mock_realtime_quote(symbol: str) -> Dict[str, Any]:
    """生成模拟实时行情"""
    base = 3400 if "000001" in symbol else 50 + (hash(symbol) % 200)
    change = (hash(f"{symbol}rt") % 100 - 45) / 10
    
    return {
        "symbol": symbol,
        "current": round(base, 2),
        "change": round(change, 2),
        "change_percent": round(change / base * 100, 2),
        "open": round(base * 0.99, 2),
        "high": round(base * 1.02, 2),
        "low": round(base * 0.98, 2),
        "pre_close": round(base * 0.99, 2),
        "volume": int(hash(f"{symbol}v") % 100000000) + 10000000,
        "amount": round(hash(f"{symbol}a") % 1000000000, 2)
    }


async def get_market_status() -> Dict[str, Any]:
    """
    获取市场状态
    
    Returns:
        市场状态信息
    """
    now = datetime.now()
    
    # 判断是否在交易时间
    is_trading_day = now.weekday() < 5  # 周一至周五
    is_trading_time = (
        (now.hour == 9 and now.minute >= 30) or
        (now.hour == 10) or
        (now.hour == 11) or
        (now.hour == 13) or
        (now.hour == 14) or
        (now.hour == 15 and now.minute <= 0)
    )
    
    return {
        "is_trading_day": is_trading_day,
        "is_trading_time": is_trading_day and is_trading_time,
        "current_time": now.isoformat(),
        "next_open": get_next_trading_time().isoformat() if not is_trading_time else None
    }


def get_next_trading_time() -> datetime:
    """获取下一个交易时间"""
    now = datetime.now()
    
    if now.hour < 9 or (now.hour == 9 and now.minute < 30):
        return now.replace(hour=9, minute=30, second=0, microsecond=0)
    elif now.hour < 13:
        return now.replace(hour=13, minute=0, second=0, microsecond=0)
    else:
        # 下一个交易日
        next_day = now + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        return next_day.replace(hour=9, minute=30, second=0, microsecond=0)
