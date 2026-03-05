"""
特征工程和数据预处理

包含:
- 技术指标特征计算
- 特征标准化 (Z-Score)
- 序列构建 (滑动窗口)
- 数据集划分
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional, Dict, Any
from sklearn.preprocessing import StandardScaler


class FeaturePreprocessor:
    """
    特征预处理器
    
    将原始 OHLCV 数据转换为深度学习模型可用的特征序列
    """
    
    def __init__(
        self,
        feature_columns: Optional[List[str]] = None,
        sequence_length: int = 60,
        target_column: str = "close",
    ):
        """
        初始化预处理器
        
        参数:
            feature_columns: 特征列名列表
            sequence_length: 序列长度 (滑动窗口大小)
            target_column: 目标列名
        """
        self.feature_columns = feature_columns or self._get_default_features()
        self.sequence_length = sequence_length
        self.target_column = target_column
        
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def _get_default_features(self) -> List[str]:
        """获取默认特征列表 (25 个特征)"""
        return [
            # 基础价格 (5)
            "open", "high", "low", "close", "volume",
            # 价格衍生 (4)
            "price_change", "price_change_pct", "high_low_range", "open_close_diff",
            # 移动平均 (4)
            "ma5", "ma10", "ma20", "ma60",
            # MACD (3)
            "macd", "macd_signal", "macd_histogram",
            # RSI (1)
            "rsi14",
            # KDJ (3)
            "stoch_k", "stoch_d", "stoch_j",
            # CCI (1)
            "cci20",
            # ROC (1)
            "roc12",
            # ADX (1)
            "adx14",
            # SAR (1)
            "sar",
        ]
    
    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有特征
        
        参数:
            df: 原始数据 (包含 ohlcv 列)
            
        返回:
            包含所有特征的数据框
        """
        df = df.copy()
        
        # 基础价格衍生特征
        df["price_change"] = df["close"].diff()
        df["price_change_pct"] = df["close"].pct_change()
        df["high_low_range"] = df["high"] - df["low"]
        df["open_close_diff"] = df["close"] - df["open"]
        
        # 移动平均
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma10"] = df["close"].rolling(10).mean()
        df["ma20"] = df["close"].rolling(20).mean()
        df["ma60"] = df["close"].rolling(60).mean()
        
        # MACD
        exp1 = df["close"].ewm(span=12, adjust=False).mean()
        exp2 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = exp1 - exp2
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]
        
        # RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["rsi14"] = 100 - (100 / (1 + rs))
        
        # KDJ
        low_14 = df["low"].rolling(14).min()
        high_14 = df["high"].rolling(14).max()
        df["stoch_k"] = 100 * (df["close"] - low_14) / (high_14 - low_14)
        df["stoch_d"] = df["stoch_k"].rolling(3).mean()
        df["stoch_j"] = 3 * df["stoch_k"] - 2 * df["stoch_d"]
        
        # CCI
        tp = (df["high"] + df["low"] + df["close"]) / 3
        cci_ma = tp.rolling(20).mean()
        cci_mad = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean())
        df["cci20"] = (tp - cci_ma) / (0.015 * cci_mad)
        
        # ROC
        df["roc12"] = df["close"].pct_change(12) * 100
        
        # ADX (简化版本)
        df["adx14"] = df["close"].rolling(14).std() / df["close"].rolling(14).mean() * 100
        
        # SAR (简化版本)
        df["sar"] = df["close"].rolling(10).min()
        
        return df
    
    def fit(self, df: pd.DataFrame) -> "FeaturePreprocessor":
        """
        拟合标准化器
        
        参数:
            df: 训练数据
            
        返回:
            self
        """
        # 计算特征
        df_features = self.compute_features(df)
        
        # 删除 NaN
        df_features = df_features.dropna()
        
        # 拟合标准化器
        self.scaler.fit(df_features[self.feature_columns])
        self.is_fitted = True
        
        return self
    
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        转换数据
        
        参数:
            df: 输入数据
            
        返回:
            标准化后的特征数组
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit() first.")
        
        # 计算特征
        df_features = self.compute_features(df)
        
        # 删除 NaN
        df_features = df_features.dropna()
        
        # 标准化
        features_scaled = self.scaler.transform(df_features[self.feature_columns])
        
        return features_scaled
    
    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """拟合并转换数据"""
        return self.fit(df).transform(df)
    
    def create_sequences(
        self,
        features: np.ndarray,
        targets: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        创建序列数据 (滑动窗口)
        
        参数:
            features: 特征数组 (n_samples, n_features)
            targets: 目标数组 (n_samples,) 或 None
            
        返回:
            X: 序列特征 (n_sequences, sequence_length, n_features)
            y: 序列目标 (n_sequences,) 或 None
        """
        X, y = [], []
        
        for i in range(len(features) - self.sequence_length):
            X.append(features[i : i + self.sequence_length])
            if targets is not None:
                y.append(targets[i + self.sequence_length])
        
        X = np.array(X)
        y = np.array(y) if targets is not None else None
        
        return X, y
    
    def create_dataset(
        self,
        df: pd.DataFrame,
        target_type: str = "direction",
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
    ) -> Dict[str, Tuple[np.ndarray, Optional[np.ndarray]]]:
        """
        创建完整的数据集
        
        参数:
            df: 原始数据
            target_type: 目标类型 ("direction", "return", "both")
            train_ratio: 训练集比例
            val_ratio: 验证集比例
            
        返回:
            包含 train/val/test 数据集的字典
        """
        # 计算特征
        df_features = self.compute_features(df)
        df_features = df_features.dropna()
        
        # 准备目标变量
        if target_type == "direction":
            # 涨跌方向 (1=涨，0=跌)
            targets = (df_features["close"].shift(-1) > df_features["close"]).astype(int)
        elif target_type == "return":
            # 收益率
            targets = df_features["close"].pct_change().shift(-1)
        else:
            targets = None
        
        # 删除最后的 NaN
        df_features = df_features.iloc[:-1]
        if targets is not None:
            targets = targets.iloc[:-1].values
        
        # 标准化特征
        features_scaled = self.fit_transform(df_features)
        
        # 创建序列
        X, y = self.create_sequences(features_scaled, targets)
        
        # 划分数据集
        n_samples = len(X)
        train_end = int(n_samples * train_ratio)
        val_end = int(n_samples * (train_ratio + val_ratio))
        
        dataset = {
            "train": (X[:train_end], y[:train_end] if y is not None else None),
            "val": (X[train_end:val_end], y[train_end:val_end] if y is not None else None),
            "test": (X[val_end:], y[val_end:] if y is not None else None),
        }
        
        return dataset
    
    def get_feature_names(self) -> List[str]:
        """获取特征名称列表"""
        return self.feature_columns
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return {
            "feature_columns": self.feature_columns,
            "sequence_length": self.sequence_length,
            "target_column": self.target_column,
            "is_fitted": self.is_fitted,
        }


if __name__ == "__main__":
    # 测试预处理器
    import pandas as pd
    import numpy as np
    
    # 创建模拟数据
    np.random.seed(42)
    n_days = 500
    
    df = pd.DataFrame({
        "open": np.random.randn(n_days).cumsum() + 100,
        "high": np.random.randn(n_days).cumsum() + 101,
        "low": np.random.randn(n_days).cumsum() + 99,
        "close": np.random.randn(n_days).cumsum() + 100,
        "volume": np.random.randint(1000, 10000, n_days),
    })
    
    # 测试预处理器
    preprocessor = FeaturePreprocessor(sequence_length=60)
    dataset = preprocessor.create_dataset(df, target_type="direction")
    
    print("Dataset shapes:")
    for split, (X, y) in dataset.items():
        print(f"  {split}: X={X.shape}, y={y.shape if y is not None else None}")
    
    print(f"\nFeature count: {len(preprocessor.get_feature_names())}")
    print(f"Config: {preprocessor.get_config()}")
    
    print("\nFeaturePreprocessor test passed!")
