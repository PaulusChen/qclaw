"""
Redis 缓存服务
提供数据缓存功能
"""

import json
import logging
from typing import Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


async def get(key: str) -> Optional[Any]:
    """
    从缓存获取数据
    
    Args:
        key: 缓存键
        
    Returns:
        缓存的数据，如果不存在则返回 None
    """
    from main import app
    
    redis = getattr(app.state, 'redis', None)
    if not redis:
        logger.debug(f"Redis 未连接，跳过缓存读取：{key}")
        return None
    
    try:
        data = await redis.get(key)
        if data:
            logger.debug(f"缓存命中：{key}")
            return json.loads(data)
        logger.debug(f"缓存未命中：{key}")
        return None
    except Exception as e:
        logger.error(f"读取缓存失败 {key}: {e}")
        return None


async def set(key: str, value: Any, ttl: int = 300) -> bool:
    """
    设置缓存
    
    Args:
        key: 缓存键
        value: 缓存值
        ttl: 过期时间（秒），默认 5 分钟
        
    Returns:
        是否设置成功
    """
    from main import app
    
    redis = getattr(app.state, 'redis', None)
    if not redis:
        logger.debug(f"Redis 未连接，跳过缓存写入：{key}")
        return False
    
    try:
        data = json.dumps(value, ensure_ascii=False, default=str)
        await redis.setex(key, ttl, data)
        logger.debug(f"缓存设置成功：{key} (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.error(f"设置缓存失败 {key}: {e}")
        return False


async def delete(key: str) -> bool:
    """
    删除缓存
    
    Args:
        key: 缓存键
        
    Returns:
        是否删除成功
    """
    from main import app
    
    redis = getattr(app.state, 'redis', None)
    if not redis:
        return False
    
    try:
        await redis.delete(key)
        logger.debug(f"缓存删除成功：{key}")
        return True
    except Exception as e:
        logger.error(f"删除缓存失败 {key}: {e}")
        return False


async def exists(key: str) -> bool:
    """
    检查缓存是否存在
    
    Args:
        key: 缓存键
        
    Returns:
        是否存在
    """
    from main import app
    
    redis = getattr(app.state, 'redis', None)
    if not redis:
        return False
    
    try:
        result = await redis.exists(key)
        return bool(result)
    except Exception as e:
        logger.error(f"检查缓存失败 {key}: {e}")
        return False


async def clear_pattern(pattern: str) -> int:
    """
    清除匹配模式的缓存
    
    Args:
        pattern: 键模式，支持通配符 *
        
    Returns:
        删除的键数量
    """
    from main import app
    
    redis = getattr(app.state, 'redis', None)
    if not redis:
        return 0
    
    try:
        keys = []
        async for key in redis.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            deleted = await redis.delete(*keys)
            logger.info(f"清除缓存模式 {pattern}: {deleted} 个键")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"清除缓存失败 {pattern}: {e}")
        return 0


async def get_stats() -> dict:
    """
    获取缓存统计信息
    
    Returns:
        统计信息字典
    """
    from main import app
    
    redis = getattr(app.state, 'redis', None)
    if not redis:
        return {"connected": False}
    
    try:
        info = await redis.info("stats")
        keys_count = await redis.dbsize()
        
        return {
            "connected": True,
            "keys_count": keys_count,
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": calculate_hit_rate(info),
            "memory_used": await get_memory_usage()
        }
    except Exception as e:
        logger.error(f"获取缓存统计失败：{e}")
        return {"connected": False, "error": str(e)}


def calculate_hit_rate(info: dict) -> float:
    """计算缓存命中率"""
    hits = info.get("keyspace_hits", 0)
    misses = info.get("keyspace_misses", 0)
    total = hits + misses
    
    if total == 0:
        return 0.0
    
    return round(hits / total * 100, 2)


async def get_memory_usage() -> dict:
    """获取 Redis 内存使用情况"""
    from main import app
    
    redis = getattr(app.state, 'redis', None)
    if not redis:
        return {}
    
    try:
        info = await redis.info("memory")
        return {
            "used_memory": info.get("used_memory_human", "N/A"),
            "used_memory_peak": info.get("used_memory_peak_human", "N/A"),
            "used_memory_lua": info.get("used_memory_lua_human", "N/A")
        }
    except Exception as e:
        logger.error(f"获取内存使用失败：{e}")
        return {}
