"""
应用配置
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    
    # CORS 配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # 缓存过期时间 (秒)
    CACHE_TTL_MARKET: int = 60  # 行情数据 1 分钟
    CACHE_TTL_INDICATOR: int = 300  # 指标数据 5 分钟
    CACHE_TTL_ADVICE: int = 3600  # AI 建议 1 小时
    CACHE_TTL_NEWS: int = 600  # 新闻数据 10 分钟
    
    # OpenClaw API 配置
    OPENCLAW_API_URL: str | None = None
    OPENCLAW_API_KEY: str | None = None
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
