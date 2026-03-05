"""
QCLaw 深度学习预测模块

提供基于 LSTM 和 Transformer 的股价预测功能
支持多任务学习：涨跌方向、收益率、置信度
"""

__version__ = "0.1.0"
__author__ = "QCLaw Team"

from .models.lstm import LSTMPredictor
from .models.transformer import TransformerPredictor
from .data.dataset import StockDataset
from .data.preprocessing import FeaturePreprocessor

__all__ = [
    "LSTMPredictor",
    "TransformerPredictor",
    "StockDataset",
    "FeaturePreprocessor",
]
