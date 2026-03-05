"""
动量类算法模块

实现 RSI, ROC, CCI, Stochastic 等动量类指标。
使用 pandas/numpy 实现，遵循与 moving_average 模块一致的设计风格。
"""

import logging
from typing import Union, Optional, Dict, Any
import pandas as pd
import numpy as np

from ..utils import setup_logger, validate_dataframe

logger = setup_logger(__name__)


# =============================================================================
# RSI (Relative Strength Index)
# =============================================================================

def calculate_rsi(
    prices: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    计算 RSI 指标（相对强弱指数）
    
    Args:
        prices: 价格序列（收盘价）
        period: RSI 计算周期，默认 14
        
    Returns:
        RSI 值序列 (0-100)
    """
    # 计算价格变化
    delta = prices.diff()
    
    # 分离上涨和下跌
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # 计算平均涨幅和跌幅（使用 EMA 平滑）
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    
    # 计算 RS 和 RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # 处理除零情况
    rsi[avg_loss == 0] = 100
    
    logger.debug(f"RSI({period}) 计算完成，有效数据点：{rsi.notna().sum()}")
    
    return rsi


def calculate_rsi_multi(
    df: pd.DataFrame,
    periods: Optional[list[int]] = None,
    price_column: str = "close",
    output_prefix: str = "rsi"
) -> pd.DataFrame:
    """
    计算多个周期的 RSI 并添加到 DataFrame
    
    Args:
        df: 包含价格数据的 DataFrame
        periods: RSI 周期列表，默认 [6, 12, 24]
        price_column: 价格列名
        output_prefix: 输出列前缀
        
    Returns:
        添加 RSI 列的 DataFrame
    """
    if periods is None:
        periods = [6, 12, 24]
    
    validate_dataframe(df, [price_column])
    
    result = df.copy()
    
    for period in periods:
        col_name = f"{output_prefix}{period}"
        result[col_name] = calculate_rsi(result[price_column], period)
        logger.debug(f"计算 {col_name} 完成")
    
    logger.info(f"完成 {len(periods)} 个 RSI 指标计算")
    
    return result


# =============================================================================
# ROC (Rate of Change)
# =============================================================================

def calculate_roc(
    prices: pd.Series,
    period: int = 12
) -> pd.Series:
    """
    计算 ROC 指标（变化率）
    
    Args:
        prices: 价格序列
        period: 周期，默认 12
        
    Returns:
        ROC 值序列（百分比）
    """
    roc = ((prices - prices.shift(period)) / prices.shift(period)) * 100
    
    logger.debug(f"ROC({period}) 计算完成，有效数据点：{roc.notna().sum()}")
    
    return roc


def calculate_roc_multi(
    df: pd.DataFrame,
    periods: Optional[list[int]] = None,
    price_column: str = "close",
    output_prefix: str = "roc"
) -> pd.DataFrame:
    """
    计算多个周期的 ROC 并添加到 DataFrame
    
    Args:
        df: 包含价格数据的 DataFrame
        periods: ROC 周期列表，默认 [5, 10, 20]
        price_column: 价格列名
        output_prefix: 输出列前缀
        
    Returns:
        添加 ROC 列的 DataFrame
    """
    if periods is None:
        periods = [5, 10, 20]
    
    validate_dataframe(df, [price_column])
    
    result = df.copy()
    
    for period in periods:
        col_name = f"{output_prefix}{period}"
        result[col_name] = calculate_roc(result[price_column], period)
    
    logger.info(f"完成 {len(periods)} 个 ROC 指标计算")
    
    return result


# =============================================================================
# CCI (Commodity Channel Index)
# =============================================================================

def calculate_cci(
    df: pd.DataFrame,
    period: int = 20,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close"
) -> pd.Series:
    """
    计算 CCI 指标（商品通道指数）
    
    Args:
        df: 包含 OHLC 数据的 DataFrame
        period: CCI 计算周期，默认 20
        high_col: 最高价列名
        low_col: 最低价列名
        close_col: 收盘价列名
        
    Returns:
        CCI 值序列
    """
    validate_dataframe(df, [high_col, low_col, close_col])
    
    high = df[high_col]
    low = df[low_col]
    close = df[close_col]
    
    # 计算典型价格
    tp = (high + low + close) / 3
    
    # 计算典型价格的移动平均
    tp_sma = tp.rolling(window=period).mean()
    
    # 计算平均偏差
    mean_deviation = tp.rolling(window=period).apply(
        lambda x: np.abs(x - x.mean()).mean(),
        raw=True
    )
    
    # 计算 CCI
    cci = (tp - tp_sma) / (0.015 * mean_deviation)
    
    logger.debug(f"CCI({period}) 计算完成，有效数据点：{cci.notna().sum()}")
    
    return cci


def calculate_cci_multi(
    df: pd.DataFrame,
    periods: Optional[list[int]] = None,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    output_prefix: str = "cci"
) -> pd.DataFrame:
    """
    计算多个周期的 CCI 并添加到 DataFrame
    
    Args:
        df: 包含 OHLC 数据的 DataFrame
        periods: CCI 周期列表，默认 [14, 20, 30]
        high_col: 最高价列名
        low_col: 最低价列名
        close_col: 收盘价列名
        output_prefix: 输出列前缀
        
    Returns:
        添加 CCI 列的 DataFrame
    """
    if periods is None:
        periods = [14, 20, 30]
    
    result = df.copy()
    
    for period in periods:
        col_name = f"{output_prefix}{period}"
        result[col_name] = calculate_cci(result, period, high_col, low_col, close_col)
    
    logger.info(f"完成 {len(periods)} 个 CCI 指标计算")
    
    return result


# =============================================================================
# Stochastic Oscillator (KDJ)
# =============================================================================

def calculate_stochastic(
    df: pd.DataFrame,
    k_period: int = 14,
    d_period: int = 3,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close"
) -> Dict[str, pd.Series]:
    """
    计算随机指标（KDJ）
    
    Args:
        df: 包含 OHLC 数据的 DataFrame
        k_period: %K 周期，默认 14
        d_period: %D 周期（%K 的平滑），默认 3
        high_col: 最高价列名
        low_col: 最低价列名
        close_col: 收盘价列名
        
    Returns:
        包含 K, D, J 的字典
    """
    validate_dataframe(df, [high_col, low_col, close_col])
    
    high = df[high_col]
    low = df[low_col]
    close = df[close_col]
    
    # 计算 %K
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    
    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    
    # 计算 %D（%K 的平滑）
    d = k.rolling(window=d_period).mean()
    
    # 计算 %J
    j = 3 * k - 2 * d
    
    logger.debug(f"Stochastic 计算完成，有效数据点：{k.notna().sum()}")
    
    return {
        "k": k,
        "d": d,
        "j": j
    }


def calculate_stochastic_multi(
    df: pd.DataFrame,
    k_period: int = 14,
    d_period: int = 3,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    output_prefix: str = "stoch"
) -> pd.DataFrame:
    """
    计算随机指标并添加到 DataFrame
    
    Args:
        df: 包含 OHLC 数据的 DataFrame
        k_period: %K 周期
        d_period: %D 周期
        high_col: 最高价列名
        low_col: 最低价列名
        close_col: 收盘价列名
        output_prefix: 输出列前缀
        
    Returns:
        添加 KDJ 列的 DataFrame
    """
    result = df.copy()
    stoch_data = calculate_stochastic(
        result, k_period, d_period, high_col, low_col, close_col
    )
    
    result[f"{output_prefix}_k"] = stoch_data["k"]
    result[f"{output_prefix}_d"] = stoch_data["d"]
    result[f"{output_prefix}_j"] = stoch_data["j"]
    
    logger.info(f"Stochastic 计算完成，添加到 DataFrame")
    
    return result


# =============================================================================
# 动量指标计算器类
# =============================================================================

class MomentumIndicatorCalculator:
    """
    动量指标计算器
    
    提供 RSI, ROC, CCI, Stochastic 等动量指标的计算和信号检测。
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化计算器
        
        Args:
            df: 包含 OHLC 数据的 DataFrame
        """
        self.df = df.copy()
        self.calculated = set()
        
        logger.debug("MomentumIndicatorCalculator 初始化完成")
    
    def add_rsi(
        self,
        period: int = 14,
        price_column: str = "close"
    ) -> 'MomentumIndicatorCalculator':
        """
        添加 RSI 指标
        
        Args:
            period: RSI 周期
            price_column: 价格列名
            
        Returns:
            self (支持链式调用)
        """
        col_name = f"rsi{period}"
        self.df[col_name] = calculate_rsi(self.df[price_column], period)
        self.calculated.add(f"rsi_{period}")
        
        logger.debug(f"添加 RSI({period}) 指标")
        
        return self
    
    def add_roc(
        self,
        period: int = 12,
        price_column: str = "close"
    ) -> 'MomentumIndicatorCalculator':
        """
        添加 ROC 指标
        
        Args:
            period: ROC 周期
            price_column: 价格列名
            
        Returns:
            self (支持链式调用)
        """
        col_name = f"roc{period}"
        self.df[col_name] = calculate_roc(self.df[price_column], period)
        self.calculated.add(f"roc_{period}")
        
        logger.debug(f"添加 ROC({period}) 指标")
        
        return self
    
    def add_cci(
        self,
        period: int = 20,
        high_col: str = "high",
        low_col: str = "low",
        close_col: str = "close"
    ) -> 'MomentumIndicatorCalculator':
        """
        添加 CCI 指标
        
        Args:
            period: CCI 周期
            high_col: 最高价列名
            low_col: 最低价列名
            close_col: 收盘价列名
            
        Returns:
            self (支持链式调用)
        """
        col_name = f"cci{period}"
        self.df[col_name] = calculate_cci(self.df, period, high_col, low_col, close_col)
        self.calculated.add(f"cci_{period}")
        
        logger.debug(f"添加 CCI({period}) 指标")
        
        return self
    
    def add_stochastic(
        self,
        k_period: int = 14,
        d_period: int = 3,
        high_col: str = "high",
        low_col: str = "low",
        close_col: str = "close"
    ) -> 'MomentumIndicatorCalculator':
        """
        添加随机指标
        
        Args:
            k_period: %K 周期
            d_period: %D 周期
            high_col: 最高价列名
            low_col: 最低价列名
            close_col: 收盘价列名
            
        Returns:
            self (支持链式调用)
        """
        stoch_data = calculate_stochastic(
            self.df, k_period, d_period, high_col, low_col, close_col
        )
        
        self.df["stoch_k"] = stoch_data["k"]
        self.df["stoch_d"] = stoch_data["d"]
        self.df["stoch_j"] = stoch_data["j"]
        
        self.calculated.add("stochastic")
        logger.debug("添加 Stochastic 指标")
        
        return self
    
    def detect_rsi_signal(
        self,
        period: int = 14,
        oversold: float = 30,
        overbought: float = 70
    ) -> Dict[str, pd.Series]:
        """
        检测 RSI 交易信号
        
        Args:
            period: RSI 周期
            oversold: 超卖阈值
            overbought: 超买阈值
            
        Returns:
            包含 buy_signal, sell_signal 的字典
        """
        if f"rsi_{period}" not in self.calculated:
            self.add_rsi(period)
        
        rsi = self.df[f"rsi{period}"]
        
        # 超卖买入信号：RSI 从下方上穿 oversold
        buy_signal = (rsi > oversold) & (rsi.shift(1) <= oversold)
        
        # 超买卖出信号：RSI 从上方下穿 overbought
        sell_signal = (rsi < overbought) & (rsi.shift(1) >= overbought)
        
        buy_count = buy_signal.sum()
        sell_count = sell_signal.sum()
        
        logger.info(f"RSI 信号：{buy_count} 个买入（超卖反弹），{sell_count} 个卖出（超买回落）")
        
        return {
            "buy_signal": buy_signal,
            "sell_signal": sell_signal
        }
    
    def detect_stochastic_signal(
        self,
        oversold: float = 20,
        overbought: float = 80
    ) -> Dict[str, pd.Series]:
        """
        检测随机指标交易信号
        
        Args:
            oversold: 超卖阈值
            overbought: 超买阈值
            
        Returns:
            包含 buy_signal, sell_signal 的字典
        """
        if "stochastic" not in self.calculated:
            self.add_stochastic()
        
        k = self.df["stoch_k"]
        d = self.df["stoch_d"]
        
        # 金叉买入：K 线上穿 D 线，且在超卖区
        buy_signal = (k > d) & (k.shift(1) <= d.shift(1)) & (k < oversold)
        
        # 死叉卖出：K 线下穿 D 线，且在超买区
        sell_signal = (k < d) & (k.shift(1) >= d.shift(1)) & (k > overbought)
        
        buy_count = buy_signal.sum()
        sell_count = sell_signal.sum()
        
        logger.info(f"Stochastic 信号：{buy_count} 个买入，{sell_count} 个卖出")
        
        return {
            "buy_signal": buy_signal,
            "sell_signal": sell_signal
        }
    
    def detect_cci_signal(
        self,
        period: int = 20,
        oversold: float = -100,
        overbought: float = 100
    ) -> Dict[str, pd.Series]:
        """
        检测 CCI 交易信号
        
        Args:
            period: CCI 周期
            oversold: 超卖阈值
            overbought: 超买阈值
            
        Returns:
            包含 buy_signal, sell_signal 的字典
        """
        if f"cci_{period}" not in self.calculated:
            self.add_cci(period)
        
        cci = self.df[f"cci{period}"]
        
        # 买入信号：CCI 从超卖区回升
        buy_signal = (cci > oversold) & (cci.shift(1) <= oversold)
        
        # 卖出信号：CCI 从超买区回落
        sell_signal = (cci < overbought) & (cci.shift(1) >= overbought)
        
        buy_count = buy_signal.sum()
        sell_count = sell_signal.sum()
        
        logger.info(f"CCI 信号：{buy_count} 个买入，{sell_count} 个卖出")
        
        return {
            "buy_signal": buy_signal,
            "sell_signal": sell_signal
        }
    
    def get_momentum_score(
        self,
        rsi_period: int = 14,
        roc_period: int = 12
    ) -> pd.Series:
        """
        计算综合动量得分（-100 到 100）
        
        Args:
            rsi_period: RSI 周期
            roc_period: ROC 周期
            
        Returns:
            动量得分序列
        """
        if f"rsi_{rsi_period}" not in self.calculated:
            self.add_rsi(rsi_period)
        if f"roc_{roc_period}" not in self.calculated:
            self.add_roc(roc_period)
        
        rsi = self.df[f"rsi{rsi_period}"]
        roc = self.df[f"roc{roc_period}"]
        
        # RSI 得分：0-100 映射到 -50 到 50
        rsi_score = rsi - 50
        
        # ROC 得分：标准化到 -50 到 50（假设 ROC 在 -100 到 100 之间）
        roc_score = roc.clip(-100, 100) / 2
        
        # 综合得分
        momentum_score = rsi_score + roc_score
        
        logger.debug("综合动量得分计算完成")
        
        return momentum_score
    
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

def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """计算 RSI（默认周期 14）"""
    return calculate_rsi(prices, period)


def roc(prices: pd.Series, period: int = 12) -> pd.Series:
    """计算 ROC（默认周期 12）"""
    return calculate_roc(prices, period)


def cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """计算 CCI（默认周期 20）"""
    return calculate_cci(df, period)


def stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
    """计算 Stochastic（默认参数）"""
    return calculate_stochastic(df, k_period, d_period)
