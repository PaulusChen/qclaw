"""
技术指标模块

包含各类量化分析指标：
- moving_average: 移动平均线 (MA5/10/20/60)
- trend_indicators: 趋势跟踪指标 (MACD, ADX, SAR)
- momentum_indicators: 动量指标 (RSI, ROC, CCI, Stochastic)
"""

from .moving_average import (
    calculate_ma,
    calculate_ma_multi,
    MovingAverageCalculator,
    ma5,
    ma10,
    ma20,
    ma60
)

from .trend_indicators import (
    calculate_macd,
    calculate_macd_multi,
    calculate_adx,
    calculate_adx_multi,
    calculate_sar,
    calculate_sar_multi,
    TrendIndicatorCalculator,
    macd,
    adx,
    sar
)

from .momentum_indicators import (
    calculate_rsi,
    calculate_rsi_multi,
    calculate_roc,
    calculate_roc_multi,
    calculate_cci,
    calculate_cci_multi,
    calculate_stochastic,
    calculate_stochastic_multi,
    MomentumIndicatorCalculator,
    rsi,
    roc,
    cci,
    stochastic
)

__all__ = [
    # Moving Average
    "calculate_ma",
    "calculate_ma_multi",
    "MovingAverageCalculator",
    "ma5",
    "ma10",
    "ma20",
    "ma60",
    
    # Trend Indicators
    "calculate_macd",
    "calculate_macd_multi",
    "calculate_adx",
    "calculate_adx_multi",
    "calculate_sar",
    "calculate_sar_multi",
    "TrendIndicatorCalculator",
    "macd",
    "adx",
    "sar",
    
    # Momentum Indicators
    "calculate_rsi",
    "calculate_rsi_multi",
    "calculate_roc",
    "calculate_roc_multi",
    "calculate_cci",
    "calculate_cci_multi",
    "calculate_stochastic",
    "calculate_stochastic_multi",
    "MomentumIndicatorCalculator",
    "rsi",
    "roc",
    "cci",
    "stochastic"
]
