"""
趋势类算法模块

实现 MACD, ADX, SAR 等趋势跟踪指标。
使用 pandas/numpy 实现，遵循与 moving_average 模块一致的设计风格。
"""

import logging
from typing import Union, Optional, Dict, Any
import pandas as pd
import numpy as np

from ..utils import setup_logger, validate_dataframe

logger = setup_logger(__name__)


# =============================================================================
# MACD (Moving Average Convergence Divergence)
# =============================================================================

def calculate_macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict[str, pd.Series]:
    """
    计算 MACD 指标
    
    Args:
        prices: 价格序列（收盘价）
        fast_period: 快线 EMA 周期，默认 12
        slow_period: 慢线 EMA 周期，默认 26
        signal_period: 信号线 EMA 周期，默认 9
        
    Returns:
        包含 MACD, signal, histogram 的字典
    """
    # 计算 EMA
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
    
    # MACD 线 = 快 EMA - 慢 EMA
    macd_line = ema_fast - ema_slow
    
    # 信号线 = MACD 的 EMA
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # 柱状图 = MACD 线 - 信号线
    histogram = macd_line - signal_line
    
    logger.debug(f"MACD 计算完成，有效数据点：{macd_line.notna().sum()}")
    
    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram
    }


def calculate_macd_multi(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_column: str = "close",
    output_prefix: str = "macd"
) -> pd.DataFrame:
    """
    计算 MACD 并添加到 DataFrame
    
    Args:
        df: 包含价格数据的 DataFrame
        fast_period: 快线周期
        slow_period: 慢线周期
        signal_period: 信号线周期
        price_column: 价格列名
        output_prefix: 输出列前缀
        
    Returns:
        添加 MACD 列的 DataFrame
    """
    validate_dataframe(df, [price_column])
    
    result = df.copy()
    macd_data = calculate_macd(result[price_column], fast_period, slow_period, signal_period)
    
    result[f"{output_prefix}"] = macd_data["macd"]
    result[f"{output_prefix}_signal"] = macd_data["signal"]
    result[f"{output_prefix}_histogram"] = macd_data["histogram"]
    
    logger.info(f"MACD 计算完成，添加到 DataFrame")
    
    return result


# =============================================================================
# ADX (Average Directional Index)
# =============================================================================

def calculate_adx(
    df: pd.DataFrame,
    period: int = 14,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close"
) -> pd.Series:
    """
    计算 ADX 指标（平均趋向指数）
    
    Args:
        df: 包含 OHLC 数据的 DataFrame
        period: ADX 计算周期，默认 14
        high_col: 最高价列名
        low_col: 最低价列名
        close_col: 收盘价列名
        
    Returns:
        ADX 值序列
    """
    validate_dataframe(df, [high_col, low_col, close_col])
    
    high = df[high_col]
    low = df[low_col]
    close = df[close_col]
    
    # 计算 +DM 和 -DM
    plus_dm = high.diff()
    minus_dm = -low.diff()
    
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    
    # 当趋势方向相反时设为 0
    plus_dm[(plus_dm > 0) & (plus_dm <= -minus_dm)] = 0
    minus_dm[(minus_dm > 0) & (minus_dm <= plus_dm)] = 0
    
    # 计算 TR (True Range)
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 平滑计算
    plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / 
                     tr.ewm(span=period, adjust=False).mean())
    minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / 
                      tr.ewm(span=period, adjust=False).mean())
    
    # 计算 DX 和 ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.ewm(span=period, adjust=False).mean()
    
    logger.debug(f"ADX({period}) 计算完成，有效数据点：{adx.notna().sum()}")
    
    return adx


def calculate_adx_multi(
    df: pd.DataFrame,
    periods: Optional[list[int]] = None,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    output_prefix: str = "adx"
) -> pd.DataFrame:
    """
    计算多个周期的 ADX 并添加到 DataFrame
    
    Args:
        df: 包含 OHLC 数据的 DataFrame
        periods: ADX 周期列表，默认 [14]
        high_col: 最高价列名
        low_col: 最低价列名
        close_col: 收盘价列名
        output_prefix: 输出列前缀
        
    Returns:
        添加 ADX 列的 DataFrame
    """
    if periods is None:
        periods = [14]
    
    result = df.copy()
    
    for period in periods:
        col_name = f"{output_prefix}{period}"
        result[col_name] = calculate_adx(result, period, high_col, low_col, close_col)
    
    logger.info(f"完成 {len(periods)} 个 ADX 指标计算")
    
    return result


# =============================================================================
# SAR (Parabolic Stop and Reverse)
# =============================================================================

def calculate_sar(
    df: pd.DataFrame,
    acceleration: float = 0.02,
    maximum: float = 0.2,
    high_col: str = "high",
    low_col: str = "low"
) -> pd.Series:
    """
    计算 SAR 指标（抛物线转向指标）
    
    Args:
        df: 包含 OHLC 数据的 DataFrame
        acceleration: 加速因子，默认 0.02
        maximum: 最大加速因子，默认 0.2
        high_col: 最高价列名
        low_col: 最低价列名
        
    Returns:
        SAR 值序列
    """
    validate_dataframe(df, [high_col, low_col])
    
    high = df[high_col].values
    low = df[low_col].values
    n = len(high)
    
    sar = np.zeros(n)
    
    # 初始化：假设上升趋势
    uptrend = True
    ep = high[0]  # 极端点
    af = acceleration
    sar[0] = low[0]
    
    for i in range(1, n):
        if uptrend:
            sar[i] = sar[i-1] + af * (ep - sar[i-1])
            if high[i] > ep:
                ep = high[i]
                af = min(af + acceleration, maximum)
            if low[i] < sar[i]:
                # 趋势反转
                uptrend = False
                sar[i] = ep
                ep = low[i]
                af = acceleration
        else:
            sar[i] = sar[i-1] + af * (ep - sar[i-1])
            if low[i] < ep:
                ep = low[i]
                af = min(af + acceleration, maximum)
            if high[i] > sar[i]:
                # 趋势反转
                uptrend = True
                sar[i] = ep
                ep = high[i]
                af = acceleration
    
    result = pd.Series(sar, index=df.index)
    
    logger.debug(f"SAR 计算完成，有效数据点：{result.notna().sum()}")
    
    return result


def calculate_sar_multi(
    df: pd.DataFrame,
    accelerations: Optional[list[float]] = None,
    high_col: str = "high",
    low_col: str = "low",
    output_prefix: str = "sar"
) -> pd.DataFrame:
    """
    计算多个加速因子的 SAR 并添加到 DataFrame
    
    Args:
        df: 包含 OHLC 数据的 DataFrame
        accelerations: 加速因子列表，默认 [0.02]
        high_col: 最高价列名
        low_col: 最低价列名
        output_prefix: 输出列前缀
        
    Returns:
        添加 SAR 列的 DataFrame
    """
    if accelerations is None:
        accelerations = [0.02]
    
    result = df.copy()
    
    for i, acc in enumerate(accelerations):
        col_name = f"{output_prefix}{i+1}"
        result[col_name] = calculate_sar(result, acc, high_col=high_col, low_col=low_col)
    
    logger.info(f"完成 {len(accelerations)} 个 SAR 指标计算")
    
    return result


# =============================================================================
# 趋势指标计算器类
# =============================================================================

class TrendIndicatorCalculator:
    """
    趋势指标计算器
    
    提供 MACD, ADX, SAR 等趋势指标的计算和信号检测。
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化计算器
        
        Args:
            df: 包含 OHLC 数据的 DataFrame
        """
        self.df = df.copy()
        self.calculated = set()
        
        logger.debug("TrendIndicatorCalculator 初始化完成")
    
    def add_macd(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        price_column: str = "close"
    ) -> 'TrendIndicatorCalculator':
        """
        添加 MACD 指标
        
        Args:
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            price_column: 价格列名
            
        Returns:
            self (支持链式调用)
        """
        macd_data = calculate_macd(
            self.df[price_column], fast_period, slow_period, signal_period
        )
        
        self.df["macd"] = macd_data["macd"]
        self.df["macd_signal"] = macd_data["signal"]
        self.df["macd_histogram"] = macd_data["histogram"]
        
        self.calculated.add("macd")
        logger.debug("添加 MACD 指标")
        
        return self
    
    def add_adx(
        self,
        period: int = 14,
        high_col: str = "high",
        low_col: str = "low",
        close_col: str = "close"
    ) -> 'TrendIndicatorCalculator':
        """
        添加 ADX 指标
        
        Args:
            period: ADX 周期
            high_col: 最高价列名
            low_col: 最低价列名
            close_col: 收盘价列名
            
        Returns:
            self (支持链式调用)
        """
        col_name = f"adx{period}"
        self.df[col_name] = calculate_adx(self.df, period, high_col, low_col, close_col)
        self.calculated.add(f"adx_{period}")
        
        logger.debug(f"添加 ADX({period}) 指标")
        
        return self
    
    def add_sar(
        self,
        acceleration: float = 0.02,
        maximum: float = 0.2,
        high_col: str = "high",
        low_col: str = "low"
    ) -> 'TrendIndicatorCalculator':
        """
        添加 SAR 指标
        
        Args:
            acceleration: 加速因子
            maximum: 最大加速因子
            high_col: 最高价列名
            low_col: 最低价列名
            
        Returns:
            self (支持链式调用)
        """
        self.df["sar"] = calculate_sar(self.df, acceleration, maximum, high_col, low_col)
        self.calculated.add("sar")
        
        logger.debug("添加 SAR 指标")
        
        return self
    
    def detect_macd_signal(self) -> Dict[str, pd.Series]:
        """
        检测 MACD 交易信号
        
        Returns:
            包含 buy_signal, sell_signal 的字典
        """
        if "macd" not in self.calculated:
            self.add_macd()
        
        macd = self.df["macd"]
        signal = self.df["macd_signal"]
        
        # 金叉买入：MACD 线上穿信号线
        buy_signal = (macd > signal) & (macd.shift(1) <= signal.shift(1))
        
        # 死叉卖出：MACD 线下穿信号线
        sell_signal = (macd < signal) & (macd.shift(1) >= signal.shift(1))
        
        buy_count = buy_signal.sum()
        sell_count = sell_signal.sum()
        
        logger.info(f"MACD 信号：{buy_count} 个买入，{sell_count} 个卖出")
        
        return {
            "buy_signal": buy_signal,
            "sell_signal": sell_signal
        }
    
    def detect_adx_trend_strength(
        self,
        period: int = 14,
        strong_threshold: float = 25
    ) -> pd.Series:
        """
        检测趋势强度
        
        Args:
            period: ADX 周期
            strong_threshold: 强趋势阈值
            
        Returns:
            趋势强度布尔序列（True 表示强趋势）
        """
        if f"adx_{period}" not in self.calculated:
            self.add_adx(period)
        
        adx = self.df[f"adx{period}"]
        strong_trend = adx > strong_threshold
        
        strong_count = strong_trend.sum()
        logger.info(f"ADX 强趋势信号：{strong_count} 个")
        
        return strong_trend
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        获取包含所有指标的 DataFrame
        
        Returns:
            包含指标数据的 DataFrame
        """
        return self.df


# =============================================================================
# 便捷函数
# =============================================================================

def macd(prices: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
    """计算 MACD（默认参数）"""
    return calculate_macd(prices, fast_period, slow_period, signal_period)


def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算 ADX（默认周期 14）"""
    return calculate_adx(df, period)


def sar(df: pd.DataFrame, acceleration: float = 0.02, maximum: float = 0.2) -> pd.Series:
    """计算 SAR（默认参数）"""
    return calculate_sar(df, acceleration, maximum)
