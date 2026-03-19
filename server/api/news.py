"""
财经新闻 API
提供财经新闻、政策解读等资讯
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List
from datetime import datetime
import logging
import httpx

from config.settings import settings
from server.services import cache_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/news")
async def get_news(
    category: str = Query("all", description="新闻类别：all/finance/policy/market/company"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量", ge=1, le=100)
):
    """
    获取财经新闻列表
    
    - **category**: 新闻类别
      - all: 全部
      - finance: 财经
      - policy: 政策
      - market: 市场
      - company: 公司
    - **page**: 页码
    - **page_size**: 每页数量
    """
    cache_key = f"news:{category}:{page}:{page_size}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取新闻数据
        news_data = await fetch_news(category, page, page_size)
        
        result = {
            "category": category,
            "page": page,
            "page_size": page_size,
            "total": news_data.get("total", 0),
            "news": news_data.get("news", []),
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_NEWS)
        return result
    except Exception as e:
        logger.error(f"获取新闻失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取新闻失败：{str(e)}")


@router.get("/news/{news_id}")
async def get_news_detail(news_id: str = Path(..., description="新闻 ID")):
    """
    获取新闻详情
    
    - **news_id**: 新闻 ID
    """
    cache_key = f"news:detail:{news_id}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取新闻详情
        detail = await fetch_news_detail(news_id)
        
        result = {
            "news_id": news_id,
            "detail": detail,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_NEWS)
        return result
    except Exception as e:
        logger.error(f"获取新闻详情失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取详情失败：{str(e)}")


@router.get("/news/search")
async def search_news(
    keyword: str = Query(..., description="搜索关键词"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量", ge=1, le=100)
):
    """
    搜索新闻
    
    - **keyword**: 搜索关键词
    - **page**: 页码
    - **page_size**: 每页数量
    """
    cache_key = f"news:search:{keyword}:{page}:{page_size}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 搜索新闻
        news_data = await search_news_by_keyword(keyword, page, page_size)
        
        result = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "total": news_data.get("total", 0),
            "news": news_data.get("news", []),
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, settings.CACHE_TTL_NEWS)
        return result
    except Exception as e:
        logger.error(f"搜索新闻失败：{e}")
        raise HTTPException(status_code=500, detail=f"搜索失败：{str(e)}")


@router.get("/news/hot")
async def get_hot_news(limit: int = Query(10, description="返回数量", ge=1, le=50)):
    """
    获取热门新闻
    
    - **limit**: 返回数量
    """
    cache_key = f"news:hot:{limit}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取热门新闻
        hot_news = get_builtin_hot_news(limit)
        
        result = {
            "limit": limit,
            "news": hot_news,
            "update_time": datetime.now().isoformat()
        }
        
        await cache_service.set(cache_key, result, 300)  # 5 分钟缓存
        return result
    except Exception as e:
        logger.error(f"获取热门新闻失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取热门新闻失败：{str(e)}")


async def fetch_news(category: str, page: int, page_size: int) -> dict:
    """获取新闻列表"""
    # 如果有外部新闻源，可以在这里调用
    # 目前使用内置数据
    return get_builtin_news(category, page, page_size)


async def fetch_news_detail(news_id: str) -> dict:
    """获取新闻详情"""
    # 如果有外部新闻源，可以在这里调用
    # 目前使用内置数据
    return get_builtin_news_detail(news_id)


async def search_news_by_keyword(keyword: str, page: int, page_size: int) -> dict:
    """搜索新闻"""
    # 如果有外部新闻源，可以在这里调用
    # 目前使用内置数据
    return search_builtin_news(keyword, page, page_size)


def get_builtin_news(category: str, page: int, page_size: int) -> dict:
    """内置新闻数据"""
    all_news = [
        {
            "id": "news_001",
            "title": "央行：保持流动性合理充裕",
            "summary": "央行表示将继续实施稳健的货币政策，保持流动性合理充裕。",
            "category": "policy",
            "source": "央行官网",
            "author": "央行记者",
            "publish_time": "2026-03-05T10:00:00",
            "sentiment": "positive",
            "sentiment_score": 0.75,
            "tags": ["货币政策", "流动性", "央行"],
            "url": "https://example.com/news/001"
        },
        {
            "id": "news_002",
            "title": "科技股持续走强，多只股票涨停",
            "summary": "今日科技板块表现强势，多只龙头股票涨停。",
            "category": "market",
            "source": "财经日报",
            "author": "市场分析师",
            "publish_time": "2026-03-05T14:30:00",
            "sentiment": "positive",
            "sentiment_score": 0.82,
            "tags": ["科技股", "涨停", "板块"],
            "url": "https://example.com/news/002"
        },
        {
            "id": "news_003",
            "title": "某上市公司发布业绩预告",
            "summary": "该公司预计一季度净利润同比增长 50%-80%。",
            "category": "company",
            "source": "公司公告",
            "author": "公司",
            "publish_time": "2026-03-05T16:00:00",
            "sentiment": "positive",
            "sentiment_score": 0.88,
            "tags": ["业绩预告", "增长", "财报"],
            "url": "https://example.com/news/003"
        },
        {
            "id": "news_004",
            "title": "国际市场波动加剧",
            "summary": "受多重因素影响，国际市场波动性明显上升。",
            "category": "finance",
            "source": "国际金融报",
            "author": "国际记者",
            "publish_time": "2026-03-05T09:00:00",
            "sentiment": "negative",
            "sentiment_score": 0.35,
            "tags": ["国际市场", "波动", "风险"],
            "url": "https://example.com/news/004"
        },
        {
            "id": "news_005",
            "title": "新能源汽车销量创新高",
            "summary": "2 月份新能源汽车销量同比增长 120%，创历史新高。",
            "category": "market",
            "source": "汽车周刊",
            "author": "行业分析师",
            "publish_time": "2026-03-05T11:00:00",
            "sentiment": "positive",
            "sentiment_score": 0.90,
            "tags": ["新能源汽车", "销量", "增长"],
            "url": "https://example.com/news/005"
        }
    ]
    
    # 按类别过滤
    if category != "all":
        filtered = [n for n in all_news if n["category"] == category]
    else:
        filtered = all_news
    
    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    return {
        "total": len(filtered),
        "news": paginated
    }


def get_builtin_news_detail(news_id: str) -> dict:
    """内置新闻详情"""
    details = {
        "news_001": {
            "id": "news_001",
            "title": "央行：保持流动性合理充裕",
            "content": """
央行今日召开新闻发布会，表示将继续实施稳健的货币政策，保持流动性合理充裕。

主要要点：
1. 保持货币供应量和社会融资规模增速与名义经济增速基本匹配
2. 引导金融机构加大对实体经济的支持力度
3. 保持人民币汇率在合理均衡水平上的基本稳定

分析师认为，这一政策表态有利于稳定市场预期，为经济发展创造良好的货币金融环境。
            """,
            "category": "policy",
            "source": "央行官网",
            "author": "央行记者",
            "publish_time": "2026-03-05T10:00:00",
            "sentiment": "positive",
            "sentiment_score": 0.75,
            "tags": ["货币政策", "流动性", "央行"],
            "url": "https://example.com/news/001",
            "related_news": ["news_002", "news_004"]
        }
    }
    
    return details.get(news_id, {"error": "新闻不存在"})


def search_builtin_news(keyword: str, page: int, page_size: int) -> dict:
    """搜索内置新闻"""
    all_news = [
        {
            "id": "news_001",
            "title": "央行：保持流动性合理充裕",
            "summary": "央行表示将继续实施稳健的货币政策，保持流动性合理充裕。",
            "category": "policy",
            "publish_time": "2026-03-05T10:00:00",
            "sentiment": "positive",
            "url": "https://example.com/news/001"
        },
        {
            "id": "news_002",
            "title": "科技股持续走强，多只股票涨停",
            "summary": "今日科技板块表现强势，多只龙头股票涨停。",
            "category": "market",
            "publish_time": "2026-03-05T14:30:00",
            "sentiment": "positive",
            "url": "https://example.com/news/002"
        }
    ]
    
    # 简单关键词匹配
    filtered = [
        n for n in all_news
        if keyword.lower() in n["title"].lower() or keyword.lower() in n["summary"].lower()
    ]
    
    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    return {
        "total": len(filtered),
        "news": paginated
    }


def get_builtin_hot_news(limit: int) -> List[dict]:
    """内置热门新闻"""
    return [
        {
            "id": "news_005",
            "title": "新能源汽车销量创新高",
            "summary": "2 月份新能源汽车销量同比增长 120%，创历史新高。",
            "category": "market",
            "hot_score": 95,
            "publish_time": "2026-03-05T11:00:00"
        },
        {
            "id": "news_002",
            "title": "科技股持续走强，多只股票涨停",
            "summary": "今日科技板块表现强势，多只龙头股票涨停。",
            "category": "market",
            "hot_score": 88,
            "publish_time": "2026-03-05T14:30:00"
        },
        {
            "id": "news_001",
            "title": "央行：保持流动性合理充裕",
            "summary": "央行表示将继续实施稳健的货币政策，保持流动性合理充裕。",
            "category": "policy",
            "hot_score": 82,
            "publish_time": "2026-03-05T10:00:00"
        }
    ][:limit]
