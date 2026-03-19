"""
配置设置
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "QCLaw 量化交易平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Redis 配置
    REDIS_HOST: str = "redis"  # Docker 中使用服务名
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # 数据库配置
    DATABASE_URL: Optional[str] = None
    
    # API 配置
    API_PREFIX: str = "/api"
    
    class Config:
        env_file = ".env"

# 创建全局配置实例
settings = Settings()
