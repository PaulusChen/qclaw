"""
移动平均线算法模块

实现各类移动平均线指标：MA5, MA10, MA20, MA60, MA120, MA250
使用 pandas/numpy 实现，支持多种 MA 计算方法。
"""

import logging
from typing import Union, Optional
import pandas as pd
import numpy as np

from ..utils import setup_logger, validate_dataframe

logger = setup_logger(__name__)


def calculate_ma(
    prices: pd.Series,
    period: int = 5,
    price_type: str = "close"
) -> pd.Series:
    """
    计算单条移动平均线
    
    Args:
        prices: 价格序列（或包含价格数据的 DataFrame）
        period: MA 周期，默认 5
        price_type: 价格类型，如果使用 DataFrame 则指定列名
        
    Returns:
        MA 值序列
    """
    # 如果传入的是 DataFrame，提取指定列
    if isinstance(prices, pd.DataFrame):
        if price_type not in prices.columns:
            raise ValueError(f"DataFrame 中不存在列：{price_type}")
        prices = prices[price_type]
    
    # 使用 pandas 的 rolling 计算简单移动平均
    ma = prices.rolling(window=period).mean()
    
    logger.debug(f"计算 MA{period} 完成，有效数据点：{ma.notna().sum()}")
    
    return ma


def calculate_ma_multi(
    df: pd.DataFrame,
    periods: Optional[list[int]] = None,
    price_column: str = "close",
    output_prefix: str = "ma"
) -> pd.DataFrame:
    """
    计算多条移动平均线
    
    Args:
        df: 包含价格数据的 DataFrame
        periods: MA 周期列表，默认 [5, 10, 20, 60]
        price_column: 价格列名
        output_prefix: 输出列前缀
        
    Returns:
        添加 MA 列的 DataFrame
    """
    if periods is None:
        periods = [5, 10, 20, 60]
    
    # 验证必需列存在
    validate_dataframe(df, [price_column])
    
    # 创建副本避免修改原数据
    result = df.copy()
    
    for period in periods:
        col_name = f"{output_prefix}{period}"
        result[col_name] = result[price_column].rolling(window=period).mean()
        logger.debug(f"计算 {col_name} 完成")
    
    logger.info(f"完成 {len(periods)} 条移动平均线计算")
    
    return result


class MovingAverageCalculator:
    """
    移动平均线计算器
    
    提供多种 MA 计算方法和交叉信号检测。
    """
    
    def __init__(self, df: pd.DataFrame, price_column: str = "close"):
        """
        初始化计算器
        
        Args:
            df: 包含价格数据的 DataFrame
            price_column: 价格列名
        """
        self.df = df.copy()
        self.price_column = price_column
        self.ma_columns = {}
        
        validate_dataframe(df, [price_column])
        logger.debug("MovingAverageCalculator 初始化完成")
    
    def add_ma(self, period: int, column_name: Optional[str] = None) -> 'MovingAverageCalculator':
        """
        添加一条移动平均线
        
        Args:
            period: MA 周期
            column_name: 自定义列名，默认 "MA{period}"
            
        Returns:
            self (支持链式调用)
        """
        if column_name is None:
            column_name = f"MA{period}"
        
        self.df[column_name] = self.df[self.price_column].rolling(window=period).mean()
        self.ma_columns[period] = column_name
        
        logger.debug(f"添加 {column_name} (周期={period})")
        
        return self
    
    def add_common_mas(self) -> 'MovingAverageCalculator':
        """
        添加常用的移动平均线 (MA5, MA10, MA20, MA60, MA120, MA250)
        
        Returns:
            self (支持链式调用)
        """
        common_periods = [5, 10, 20, 60, 120, 250]
        
        for period in common_periods:
            self.add_ma(period)
        
        logger.info("添加常用移动平均线完成")
        
        return self
    
    def get_ma(self, period: int) -> Optional[pd.Series]:
        """
        获取指定周期的 MA 数据
        
        Args:
            period: MA 周期
            
        Returns:
            MA 数据序列，不存在则返回 None
        """
        column = self.ma_columns.get(period)
        if column and column in self.df.columns:
            return self.df[column]
        
        # 如果未预先计算，临时计算
        logger.debug(f"临时计算 MA{period}")
        return self.df[self.price_column].rolling(window=period).mean()
    
    def detect_golden_cross(
        self,
        short_period: int = 5,
        long_period: int = 20,
        lookback: int = 1
    ) -> pd.Series:
        """
        检测金叉信号（短期 MA 上穿长期 MA）
        
        Args:
            short_period: 短期 MA 周期
            long_period: 长期 MA 周期
            lookback: 回看周期数，默认 1（检测前一天）
            
        Returns:
            金叉信号布尔序列
        """
        ma_short = self.get_ma(short_period)
        ma_long = self.get_ma(long_period)
        
        if ma_short is None or ma_long is None:
            raise ValueError(f"MA{short_period} 或 MA{long_period} 未计算")
        
        # 金叉条件：今天短期 MA > 长期 MA，且昨天短期 MA <= 长期 MA
        current_cross = ma_short > ma_long
        prev_cross = ma_short.shift(lookback) <= ma_long.shift(lookback)
        
        golden_cross = current_cross & prev_cross
        
        cross_count = golden_cross.sum()
        logger.info(f"检测到 {cross_count} 个金叉信号 (MA{short_period} vs MA{long_period})")
        
        return golden_cross
    
    def detect_death_cross(
        self,
        short_period: int = 5,
        long_period: int = 20,
        lookback: int = 1
    ) -> pd.Series:
        """
        检测死叉信号（短期 MA 下穿长期 MA）
        
        Args:
            short_period: 短期 MA 周期
            long_period: 长期 MA 周期
            lookback: 回看周期数
            
        Returns:
            死叉信号布尔序列
        """
        ma_short = self.get_ma(short_period)
        ma_long = self.get_ma(long_period)
        
        if ma_short is None or ma_long is None:
            raise ValueError(f"MA{short_period} 或 MA{long_period} 未计算")
        
        # 死叉条件：今天短期 MA < 长期 MA，且昨天短期 MA >= 长期 MA
        current_cross = ma_short < ma_long
        prev_cross = ma_short.shift(lookback) >= ma_long.shift(lookback)
        
        death_cross = current_cross & prev_cross
        
        cross_count = death_cross.sum()
        logger.info(f"检测到 {cross_count} 个死叉信号 (MA{short_period} vs MA{long_period})")
        
        return death_cross
    
    def get_ma_alignment(
        self,
        periods: Optional[list[int]] = None,
        direction: str = "bullish"
    ) -> pd.Series:
        """
        检测 MA 多头/空头排列
        
        Args:
            periods: MA 周期列表，按从短到长排序
            direction: 排列方向，"bullish"(多头) 或 "bearish"(空头)
            
        Returns:
            排列信号布尔序列
        """
        if periods is None:
            periods = [5, 10, 20, 60]
        
        # 获取所有 MA
        mas = []
        for period in periods:
            ma = self.get_ma(period)
            if ma is None:
                raise ValueError(f"MA{period} 未计算")
            mas.append(ma)
        
        if direction == "bullish":
            # 多头排列：短周期 MA > 中周期 MA > 长周期 MA
            signal = pd.Series(True, index=self.df.index)
            for i in range(len(mas) - 1):
                signal = signal & (mas[i] > mas[i + 1])
        elif direction == "bearish":
            # 空头排列：短周期 MA < 中周期 MA < 长周期 MA
            signal = pd.Series(True, index=self.df.index)
            for i in range(len(mas) - 1):
                signal = signal & (mas[i] < mas[i + 1])
        else:
            raise ValueError(f"无效的排列方向：{direction}")
        
        signal_count = signal.sum()
        logger.info(f"检测到 {signal_count} 个{direction}排列信号")
        
        return signal
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        获取包含所有 MA 的 DataFrame
        
        Returns:
            包含 MA 数据的 DataFrame
        """
        return self.df


# 便捷函数
def ma5(prices: Union[pd.Series, pd.DataFrame]) -> pd.Series:
    """计算 5 日均线"""
    return calculate_ma(prices, period=5)


def ma10(prices: Union[pd.Series, pd.DataFrame]) -> pd.Series:
    """计算 10 日均线"""
    return calculate_ma(prices, period=10)


def ma20(prices: Union[pd.Series, pd.DataFrame]) -> pd.Series:
    """计算 20 日均线"""
    return calculate_ma(prices, period=20)


def ma60(prices: Union[pd.Series, pd.DataFrame]) -> pd.Series:
    """计算 60 日均线"""
    return calculate_ma(prices, period=60)
