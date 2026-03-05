"""
QCLaw 量化分析系统

A 股量化分析工具，基于 qlib 和 AKShare 实现。
"""

__version__ = "0.1.0"
__author__ = "QCLaw Team"

from . import indicators
from .utils import setup_logger, validate_dataframe

__all__ = ["indicators", "utils", "setup_logger", "validate_dataframe"]
