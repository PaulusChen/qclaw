"""
TFT 模型数据适配器

将 qclaw 数据格式转换为 pytorch-forecasting 所需的 TimeSeriesDataSet 格式

核心功能:
- 数据格式转换
- 时间索引生成
- 特征工程
- 数据验证
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path


class QclawDataAdapter:
    """
    qclaw 数据适配器
    
    将原始股票数据转换为 TFT 模型可用的格式
    支持 A 股和美股数据格式
    """
    
    def __init__(
        self,
        target_col: str = "close",
        feature_cols: Optional[List[str]] = None,
        static_categoricals: Optional[List[str]] = None,
        static_reals: Optional[List[str]] = None,
        time_varying_known_categoricals: Optional[List[str]] = None,
        time_varying_known_reals: Optional[List[str]] = None,
        time_varying_unknown_categoricals: Optional[List[str]] = None,
        time_varying_unknown_reals: Optional[List[str]] = None,
    ):
        """
        初始化数据适配器
        
        参数:
            target_col: 目标列名 (默认："close")
            feature_cols: 特征列名列表
            static_categoricals: 静态类别特征 (如：stock_sector, market)
            static_reals: 静态连续特征 (如：market_cap)
            time_varying_known_categoricals: 时变已知类别特征
            time_varying_known_reals: 时变已知连续特征 (如：volume)
            time_varying_unknown_categoricals: 时变未知类别特征
            time_varying_unknown_reals: 时变未知连续特征 (如：close, high, low)
        """
        self.target_col = target_col
        self.feature_cols = feature_cols or []
        self.static_categoricals = static_categoricals or []
        self.static_reals = static_reals or []
        self.time_varying_known_categoricals = time_varying_known_categoricals or []
        self.time_varying_known_reals = time_varying_known_reals or []
        self.time_varying_unknown_categoricals = time_varying_unknown_categoricals or []
        self.time_varying_unknown_reals = time_varying_unknown_reals or []
        
        # 默认时变未知连续特征 (价格相关)
        if not self.time_varying_unknown_reals:
            self.time_varying_unknown_reals = ["close", "open", "high", "low"]
    
    def prepare_data(
        self,
        data: pd.DataFrame,
        stock_id_col: str = "stock_id",
        date_col: str = "date",
        add_technical_indicators: bool = True,
    ) -> pd.DataFrame:
        """
        准备数据用于 TFT 模型训练
        
        参数:
            data: 原始 DataFrame
            stock_id_col: 股票 ID 列名
            date_col: 日期列名
            add_technical_indicators: 是否添加技术指标
        
        返回:
            处理后的 DataFrame，包含 time_idx 列
        """
        # 创建数据副本
        df = data.copy()
        
        # 确保日期列是 datetime 类型
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])
        
        # 按股票和时间排序
        df = df.sort_values([stock_id_col, date_col]).reset_index(drop=True)
        
        # 生成时间索引 (每个股票独立计数)
        df["time_idx"] = df.groupby(stock_id_col).cumcount()
        
        # 确保目标列存在
        if self.target_col not in df.columns:
            if "close" in df.columns:
                df[self.target_col] = df["close"]
            else:
                raise ValueError(f"Target column '{self.target_col}' not found in data")
        
        # 添加技术指标
        if add_technical_indicators:
            df = self._add_technical_indicators(df, date_col)
        
        # 添加时间特征
        df = self._add_time_features(df, date_col)
        
        return df
    
    def _add_technical_indicators(
        self,
        df: pd.DataFrame,
        date_col: str,
    ) -> pd.DataFrame:
        """
        添加技术指标
        
        参数:
            df: 输入 DataFrame
            date_col: 日期列名
        
        返回:
            添加技术指标后的 DataFrame
        """
        # 按股票分组计算指标
        stock_col = "stock_id" if "stock_id" in df.columns else None
        
        if stock_col:
            grouped = df.groupby(stock_col)
        else:
            grouped = df
        
        # 移动平均线
        if "close" in df.columns:
            df["ma_5"] = grouped["close"].transform(lambda x: x.rolling(5, min_periods=1).mean())
            df["ma_10"] = grouped["close"].transform(lambda x: x.rolling(10, min_periods=1).mean())
            df["ma_20"] = grouped["close"].transform(lambda x: x.rolling(20, min_periods=1).mean())
            
            # 价格动量
            df["momentum_5"] = grouped["close"].transform(lambda x: x.pct_change(5))
            df["momentum_10"] = grouped["close"].transform(lambda x: x.pct_change(10))
            
            # 波动率
            df["volatility_5"] = grouped["close"].transform(lambda x: x.rolling(5, min_periods=1).std())
        
        # 填充 NaN 值
        df = df.fillna(method="ffill").fillna(0)
        
        return df
    
    def _add_time_features(
        self,
        df: pd.DataFrame,
        date_col: str,
    ) -> pd.DataFrame:
        """
        添加时间特征
        
        参数:
            df: 输入 DataFrame
            date_col: 日期列名
        
        返回:
            添加时间特征后的 DataFrame
        """
        # 提取日期组件
        df["day_of_week"] = df[date_col].dt.dayofweek
        df["day_of_month"] = df[date_col].dt.day
        df["month"] = df[date_col].dt.month
        df["quarter"] = df[date_col].dt.quarter
        df["year"] = df[date_col].dt.year
        df["week_of_year"] = df[date_col].dt.isocalendar().week.astype(int)
        
        # 周期性编码 (正弦/余弦)
        df["day_of_week_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_of_week_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
        
        return df
    
    def get_dataset_params(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取 TimeSeriesDataSet 参数
        
        参数:
            df: 处理后的 DataFrame
        
        返回:
            参数字典
        """
        return {
            "time_idx": "time_idx",
            "target": self.target_col,
            "group_ids": ["stock_id"],
            "static_categoricals": self.static_categoricals if self.static_categoricals else [],
            "static_reals": self.static_reals if self.static_reals else [],
            "time_varying_known_categoricals": self.time_varying_known_categoricals,
            "time_varying_known_reals": self.time_varying_known_reals,
            "time_varying_unknown_categoricals": self.time_varying_unknown_categoricals,
            "time_varying_unknown_reals": self.time_varying_unknown_reals,
        }
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        验证数据是否满足 TFT 模型要求
        
        参数:
            df: 待验证的 DataFrame
        
        返回:
            (是否有效，错误信息列表)
        """
        errors = []
        
        # 检查必需列
        required_cols = ["stock_id", "date", "time_idx", self.target_col]
        for col in required_cols:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        # 检查时间索引连续性
        if "time_idx" in df.columns and "stock_id" in df.columns:
            for stock_id in df["stock_id"].unique():
                stock_data = df[df["stock_id"] == stock_id]["time_idx"]
                expected = list(range(len(stock_data)))
                if list(stock_data) != expected:
                    errors.append(f"Time index not continuous for stock {stock_id}")
                    break
        
        # 检查目标列是否有有效值
        if self.target_col in df.columns:
            if df[self.target_col].isna().all():
                errors.append(f"Target column '{self.target_col}' has all NaN values")
        
        return len(errors) == 0, errors


# 便捷函数
def create_tft_dataset(
    data: pd.DataFrame,
    max_encoder_length: int = 30,
    max_prediction_length: int = 7,
    target_col: str = "close",
) -> "TimeSeriesDataSet":
    """
    便捷函数：直接从原始数据创建 TimeSeriesDataSet
    
    参数:
        data: 原始 DataFrame
        max_encoder_length: 编码器序列长度
        max_prediction_length: 预测长度
        target_col: 目标列名
    
    返回:
        TimeSeriesDataSet 实例
    """
    from pytorch_forecasting import TimeSeriesDataSet
    
    adapter = QclawDataAdapter(target_col=target_col)
    prepared_data = adapter.prepare_data(data)
    
    dataset = TimeSeriesDataSet(
        prepared_data,
        time_idx="time_idx",
        target=target_col,
        group_ids=["stock_id"],
        max_encoder_length=max_encoder_length,
        max_prediction_length=max_prediction_length,
    )
    
    return dataset
