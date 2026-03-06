"""
API 路由模块
"""

from .market import router as market_router
from .health import router as health_router
from .advice import router as advice_router
from .dl.models import router as dl_models_router
from .dl.predict import router as dl_predict_router

__all__ = [
    'market_router',
    'health_router', 
    'advice_router',
    'dl_models_router',
    'dl_predict_router'
]
