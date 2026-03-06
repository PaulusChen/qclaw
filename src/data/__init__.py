"""
数据模块

提供 A 股数据获取、处理和存储功能。
支持多种数据源：Qlib, YFinance, AKShare
"""

from .qlib_data import QlibDataManager
from .yfinance_data import YFinanceDataManager, get_stock_data

__all__ = ["QlibDataManager", "YFinanceDataManager", "get_stock_data"]
