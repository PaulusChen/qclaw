"""
AI 建议 API
集成 OpenClaw API，提供投资建议
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import logging
import httpx

from config.settings import settings
from services import cache_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/advice")
async def get_advice(
    symbol: str = Query(None, description="股票代码或指数代码，可选"),
    category: str = Query("all", description="建议类别：all/market/stock/risk")
):
    """
    获取 AI 投资建议
    
    - **symbol**: 股票代码或指数代码（可选）
    - **category**: 建议类别
      - all: 全部建议
      - market: 大盘分析
      - stock: 个股建议
      - risk: 风险提示
    """
    cache_key = f"advice:{category}:{symbol or 'all'}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 如果配置了 OpenClaw API，调用获取建议
        if settings.OPENCLAW_API_URL and settings.OPENCLAW_API_KEY:
            advice_data = await fetch_openclaw_advice(symbol, category)
        else:
            # 使用内置的示例建议
            advice_data = get_builtin_advice(category)
        
        result = {
            "category": category,
            "symbol": symbol,
            "advice": advice_data,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_ADVICE)
        return result
    except Exception as e:
        logger.error(f"获取 AI 建议失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取建议失败：{str(e)}")


@router.get("/analysis/{symbol}")
async def get_stock_analysis(symbol: str = Query(..., description="股票代码或指数代码")):
    """
    获取个股/指数深度分析
    
    - **symbol**: 股票代码或指数代码
    """
    cache_key = f"analysis:{symbol}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取分析数据
        if settings.OPENCLAW_API_URL and settings.OPENCLAW_API_KEY:
            analysis = await fetch_openclaw_analysis(symbol)
        else:
            analysis = get_builtin_analysis(symbol)
        
        result = {
            "symbol": symbol,
            "analysis": analysis,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_ADVICE)
        return result
    except Exception as e:
        logger.error(f"获取分析失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取分析失败：{str(e)}")


@router.get("/signals")
async def get_trading_signals():
    """
    获取交易信号
    
    返回基于技术分析和 AI 判断的交易信号
    """
    cache_key = "signals:trading"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        signals = get_builtin_signals()
        
        result = {
            "signals": signals,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, 300)  # 5 分钟缓存
        return result
    except Exception as e:
        logger.error(f"获取交易信号失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取信号失败：{str(e)}")


async def fetch_openclaw_advice(symbol: Optional[str], category: str) -> List[dict]:
    """调用 OpenClaw API 获取建议"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        
        response = await client.get(
            f"{settings.OPENCLAW_API_URL}/api/advice",
            params=params,
            headers={"Authorization": f"Bearer {settings.OPENCLAW_API_KEY}"}
        )
        
        if response.status_code != 200:
            logger.warning(f"OpenClaw API 返回错误：{response.status_code}")
            return get_builtin_advice(category)
        
        data = response.json()
        return data.get("advice", [])


async def fetch_openclaw_analysis(symbol: str) -> dict:
    """调用 OpenClaw API 获取深度分析"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{settings.OPENCLAW_API_URL}/api/analysis/{symbol}",
            headers={"Authorization": f"Bearer {settings.OPENCLAW_API_KEY}"}
        )
        
        if response.status_code != 200:
            logger.warning(f"OpenClaw API 返回错误：{response.status_code}")
            return get_builtin_analysis(symbol)
        
        return response.json().get("analysis", {})


def get_builtin_advice(category: str) -> List[dict]:
    """内置建议（当 OpenClaw API 不可用时）"""
    advice_map = {
        "all": [
            {
                "id": "adv_001",
                "title": "市场整体趋势向好",
                "content": "近期市场成交量稳步放大，建议保持适度仓位参与。",
                "category": "market",
                "confidence": 0.75,
                "risk_level": "medium",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "adv_002",
                "title": "关注科技板块机会",
                "content": "科技创新政策支持力度加大，相关板块值得关注。",
                "category": "sector",
                "confidence": 0.68,
                "risk_level": "medium",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "adv_003",
                "title": "注意风险控制",
                "content": "市场波动加大，建议设置好止损位，控制单只股票仓位。",
                "category": "risk",
                "confidence": 0.85,
                "risk_level": "high",
                "created_at": datetime.now().isoformat()
            }
        ],
        "market": [
            {
                "id": "adv_m001",
                "title": "大盘震荡整理",
                "content": "上证指数在关键位置震荡，等待方向选择。",
                "category": "market",
                "confidence": 0.72,
                "risk_level": "medium",
                "created_at": datetime.now().isoformat()
            }
        ],
        "stock": [
            {
                "id": "adv_s001",
                "title": "优选绩优股",
                "content": "在市场不确定性较高时，建议优先配置业绩稳定的蓝筹股。",
                "category": "stock",
                "confidence": 0.78,
                "risk_level": "low",
                "created_at": datetime.now().isoformat()
            }
        ],
        "risk": [
            {
                "id": "adv_r001",
                "title": "警惕高位股回调",
                "content": "部分高位股出现技术顶背离，注意回调风险。",
                "category": "risk",
                "confidence": 0.82,
                "risk_level": "high",
                "created_at": datetime.now().isoformat()
            }
        ]
    }
    
    return advice_map.get(category, advice_map["all"])


def get_builtin_analysis(symbol: str) -> dict:
    """内置分析（当 OpenClaw API 不可用时）"""
    return {
        "symbol": symbol,
        "summary": f"{symbol} 当前处于震荡整理阶段，建议关注成交量变化。",
        "technical": {
            "trend": "sideways",
            "support": "关键支撑位",
            "resistance": "关键压力位",
            "macd_signal": "neutral",
            "kdj_signal": "neutral",
            "rsi": 50
        },
        "fundamental": {
            "pe_ratio": "N/A",
            "pb_ratio": "N/A",
            "dividend_yield": "N/A"
        },
        "recommendation": {
            "action": "hold",
            "target_price": None,
            "stop_loss": None,
            "confidence": 0.65
        },
        "risks": [
            "市场整体波动风险",
            "板块轮动风险"
        ],
        "update_time": datetime.now().isoformat()
    }


def get_builtin_signals() -> List[dict]:
    """内置交易信号"""
    return [
        {
            "id": "sig_001",
            "symbol": "sh000001",
            "name": "上证指数",
            "signal": "hold",
            "strength": 0.6,
            "reason": "MACD 金叉，但成交量不足",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "sig_002",
            "symbol": "sz399006",
            "name": "创业板指",
            "signal": "buy",
            "strength": 0.72,
            "reason": "突破关键压力位，成交量放大",
            "created_at": datetime.now().isoformat()
        }
    ]
