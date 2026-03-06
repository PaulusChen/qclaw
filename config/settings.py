"""
配置设置
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    APP_NAME: str = "QCLaw 量化交易平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    DATABASE_URL: Optional[str] = None
    API_PREFIX: str = "/api"
    
    class Config:
        env_file = ".env"

settings = Settings()
