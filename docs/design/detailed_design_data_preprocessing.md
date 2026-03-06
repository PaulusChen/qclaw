<!-- ARCHIVED: 已压缩至 check-history-summary.md -->

# 数据预处理模块详细设计

**文档 ID:** DESIGN-DL-002-DATA  
**创建日期:** 2026-03-06  
**版本:** v1.0  
**状态:** 设计中  
**关联任务:** CODE-DL-004 (实现特征工程和数据预处理)

---

## 1. 模块概述

### 1.1 职责

数据预处理模块负责将原始行情数据和技术指标转换为深度学习模型可用的特征矩阵，包括：

- 数据清洗和缺失值处理
- 特征计算和衍生
- 特征标准化/归一化
- 序列样本构建
- 数据集划分

### 1.2 输入输出

```
输入:
  - 原始行情数据 (OHLCV)
  - 技术指标数据 (MA, MACD, RSI, etc.)
  - 配置参数 (序列长度、特征列表等)

输出:
  - 标准化特征矩阵 (numpy array / torch tensor)
  - 标签数据 (方向、收益率、置信度)
  - 数据划分索引 (train/val/test)
```

### 1.3 处理流程

```
原始数据 → 数据清洗 → 特征计算 → 缺失值处理 → 异常值处理 
    → 标准化 → 序列构建 → 标签生成 → 数据集划分 → 输出
```

---

## 2. 特征工程详细设计

### 2.1 特征列表 (共 38 个特征)

#### 基础价格特征 (9 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `open` | 原始值 | 开盘价 |
| `high` | 原始值 | 最高价 |
| `low` | 原始值 | 最低价 |
| `close` | 原始值 | 收盘价 |
| `volume` | 原始值 | 成交量 |
| `price_change` | close - close.shift(1) | 价格变化 |
| `price_change_pct` | price_change / close.shift(1) | 价格变化率 |
| `high_low_range` | high - low | 日内波幅 |
| `open_close_diff` | close - open | 开盘收盘差 |

#### 移动平均线特征 (4 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `ma5` | close.rolling(5).mean() | 5 日均线 |
| `ma10` | close.rolling(10).mean() | 10 日均线 |
| `ma20` | close.rolling(20).mean() | 20 日均线 |
| `ma60` | close.rolling(60).mean() | 60 日均线 |

#### 趋势指标特征 (5 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `macd` | EMA(12) - EMA(26) | MACD 线 |
| `macd_signal` | macd.ewm(span=9).mean() | 信号线 |
| `macd_histogram` | macd - macd_signal | MACD 柱状图 |
| `adx14` | ADX(14) | 平均趋向指数 |
| `sar` | SAR(accel=0.02, max=0.2) | 抛物线转向 |

#### 动量指标特征 (6 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `rsi14` | RSI(14) | 相对强弱指数 |
| `roc12` | ROC(12) | 变化率 |
| `cci20` | CCI(20) | 商品通道指数 |
| `stoch_k` | Stochastic K(14,3) | 随机指标 K 线 |
| `stoch_d` | Stochastic D(14,3) | 随机指标 D 线 |
| `stoch_j` | 3*K - 2*D | 随机指标 J 线 |

#### 波动率指标特征 (2 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `atr14` | ATR(14) | 平均真实波幅 |
| `volatility_20` | close.pct_change().rolling(20).std() | 20 日收益率标准差 |

#### 成交量指标特征 (1 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `volume_ratio` | volume / volume.rolling(5).mean() | 量比 |

#### 布林带指标特征 (2 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `boll_width` | (upper - lower) / middle | 布林带宽度 |
| `close_vs_boll` | (close - lower) / (upper - lower) | 价格相对位置 |

#### 位置特征 (2 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `close_vs_ma20` | (close - ma20) / ma20 | 价格相对 MA20 |
| `close_vs_ma60` | (close - ma60) / ma60 | 价格相对 MA60 |

#### 滞后特征 (6 个)

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `close_lag_1` | close.shift(1) | 1 日前收盘价 |
| `close_lag_5` | close.shift(5) | 5 日前收盘价 |
| `close_lag_10` | close.shift(10) | 10 日前收盘价 |
| `return_lag_1` | close.pct_change().shift(1) | 1 日前收益率 |
| `return_lag_5` | close.pct_change().shift(5) | 5 日前收益率 |
| `return_lag_10` | close.pct_change().shift(10) | 10 日前收益率 |

#### 目标特征 (3 个) - 用于标签

| 特征名 | 计算方式 | 说明 |
|--------|---------|------|
| `future_return_1` | close.shift(-1) / close - 1 | T+1 收益率 |
| `future_return_5` | close.shift(-5) / close - 1 | T+5 收益率 |
| `future_direction` | np.sign(future_return_1) | T+1 涨跌方向 |

---

### 2.2 特征计算伪代码

```python
import pandas as pd
import numpy as np
import talib  # 或使用 pandas-ta

class FeatureEngineer:
    def __init__(self, config: dict):
        self.config = config
        self.feature_columns = []
    
    def compute_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有特征"""
        df = df.copy()
        
        # 1. 基础价格特征
        df = self._compute_price_features(df)
        
        # 2. 移动平均线
        df = self._compute_ma_features(df)
        
        # 3. 趋势指标
        df = self._compute_trend_indicators(df)
        
        # 4. 动量指标
        df = self._compute_momentum_indicators(df)
        
        # 5. 波动率指标
        df = self._compute_volatility_indicators(df)
        
        # 6. 成交量指标
        df = self._compute_volume_indicators(df)
        
        # 7. 布林带
        df = self._compute_bollinger_bands(df)
        
        # 8. 位置特征
        df = self._compute_position_features(df)
        
        # 9. 滞后特征
        df = self._compute_lag_features(df)
        
        # 10. 目标特征 (标签)
        df = self._compute_target_features(df)
        
        # 删除 NaN 行 (由于滞后和滚动计算产生)
        df = df.dropna().reset_index(drop=True)
        
        return df
    
    def _compute_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """基础价格特征"""
        df['price_change'] = df['close'] - df['close'].shift(1)
        df['price_change_pct'] = df['price_change'] / df['close'].shift(1)
        df['high_low_range'] = df['high'] - df['low']
        df['open_close_diff'] = df['close'] - df['open']
        return df
    
    def _compute_ma_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """移动平均线特征"""
        for period in [5, 10, 20, 60]:
            df[f'ma{period}'] = df['close'].rolling(period).mean()
        return df
    
    def _compute_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """趋势指标"""
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # ADX (使用 talib 或自定义实现)
        # df['adx14'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
        
        # SAR
        # df['sar'] = talib.SAR(df['high'], df['low'], acceleration=0.02, maximum=0.2)
        
        return df
    
    def _compute_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """动量指标"""
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi14'] = 100 - (100 / (1 + rs))
        
        # ROC
        df['roc12'] = df['close'].pct_change(periods=12) * 100
        
        # CCI
        tp = (df['high'] + df['low'] + df['close']) / 3
        df['cci20'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())
        
        # Stochastic
        lowest_low = df['low'].rolling(window=14).min()
        highest_high = df['high'].rolling(window=14).max()
        df['stoch_k'] = 100 * (df['close'] - lowest_low) / (highest_high - lowest_low)
        df['stoch_d'] = df['stoch_k'].rolling(3).mean()
        df['stoch_j'] = 3 * df['stoch_k'] - 2 * df['stoch_d']
        
        return df
    
    def _compute_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """波动率指标"""
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr14'] = true_range.rolling(14).mean()
        
        # Volatility
        df['volatility_20'] = df['close'].pct_change().rolling(20).std()
        
        return df
    
    def _compute_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """成交量指标"""
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(5).mean()
        return df
    
    def _compute_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """布林带指标"""
        df['boll_middle'] = df['close'].rolling(20).mean()
        boll_std = df['close'].rolling(20).std()
        df['boll_upper'] = df['boll_middle'] + 2 * boll_std
        df['boll_lower'] = df['boll_middle'] - 2 * boll_std
        df['boll_width'] = (df['boll_upper'] - df['boll_lower']) / df['boll_middle']
        df['close_vs_boll'] = (df['close'] - df['boll_lower']) / (df['boll_upper'] - df['boll_lower'])
        
        return df
    
    def _compute_position_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """位置特征"""
        df['close_vs_ma20'] = (df['close'] - df['ma20']) / df['ma20']
        df['close_vs_ma60'] = (df['close'] - df['ma60']) / df['ma60']
        return df
    
    def _compute_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """滞后特征"""
        for lag in [1, 5, 10]:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'return_lag_{lag}'] = df['close'].pct_change().shift(lag)
        return df
    
    def _compute_target_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """目标特征 (标签)"""
        # T+1 收益率
        df['future_return_1'] = df['close'].shift(-1) / df['close'] - 1
        # T+5 收益率
        df['future_return_5'] = df['close'].shift(-5) / df['close'] - 1
        # T+1 涨跌方向 (1=涨，0=跌)
        df['future_direction'] = (df['future_return_1'] > 0).astype(int)
        return df
    
    def get_feature_columns(self) -> list:
        """获取特征列名 (不包括目标列)"""
        return [col for col in self.feature_columns if not col.startswith('future_')]
    
    def get_target_columns(self) -> list:
        """获取目标列名"""
        return [col for col in self.feature_columns if col.startswith('future_')]
```

---

## 3. 数据清洗和预处理

### 3.1 缺失值处理策略

```python
class DataCleaner:
    def __init__(self, strategy: str = 'ffill'):
        """
        缺失值处理策略:
        - ffill: 前向填充
        - bfill: 后向填充
        - interpolate: 线性插值
        - drop: 删除含缺失值的行
        """
        self.strategy = strategy
    
    def handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        df = df.copy()
        
        if self.strategy == 'ffill':
            df = df.fillna(method='ffill')
        elif self.strategy == 'bfill':
            df = df.fillna(method='bfill')
        elif self.strategy == 'interpolate':
            df = df.interpolate(method='linear')
        elif self.strategy == 'drop':
            df = df.dropna()
        
        # 最后仍有缺失值则删除
        df = df.dropna()
        
        return df
```

### 3.2 异常值检测和处理

```python
class OutlierHandler:
    def __init__(self, method: str = 'zscore', threshold: float = 3.0):
        """
        异常值检测方法:
        - zscore: Z-Score 方法 (3σ原则)
        - iqr: 四分位距方法
        - isolation_forest: 孤立森林
        """
        self.method = method
        self.threshold = threshold
    
    def detect_and_handle(self, df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
        """检测并处理异常值"""
        df = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
        
        if self.method == 'zscore':
            df = self._handle_zscore(df, columns)
        elif self.method == 'iqr':
            df = self._handle_iqr(df, columns)
        
        return df
    
    def _handle_zscore(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Z-Score 方法"""
        from scipy import stats
        
        for col in columns:
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers = z_scores > self.threshold
            
            # 用中位数替换异常值
            median = df[col].median()
            df.loc[df.index[outliers], col] = median
        
        return df
    
    def _handle_iqr(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """IQR 方法"""
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # 用边界值截断 (winsorization)
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df
```

---

## 4. 特征标准化

### 4.1 标准化方法选择

| 方法 | 公式 | 适用场景 |
|------|------|---------|
| **Z-Score** | (x - μ) / σ | 特征近似正态分布 |
| **Min-Max** | (x - min) / (max - min) | 特征有明确边界 |
| **Robust** | (x - median) / IQR | 存在异常值 |
| **RankGauss** | 秩变换 + 高斯化 | 任意分布，深度学习推荐 |

### 4.2 标准化实现

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.preprocessing import QuantileTransformer
import joblib

class FeatureNormalizer:
    def __init__(self, method: str = 'zscore'):
        """
        标准化方法:
        - zscore: Z-Score 标准化
        - minmax: Min-Max 归一化
        - robust: Robust 标准化
        - rankgauss: RankGauss 变换
        """
        self.method = method
        self.scaler = self._get_scaler()
        self.fitted = False
    
    def _get_scaler(self):
        if self.method == 'zscore':
            return StandardScaler()
        elif self.method == 'minmax':
            return MinMaxScaler(feature_range=(-1, 1))
        elif self.method == 'robust':
            return RobustScaler()
        elif self.method == 'rankgauss':
            return QuantileTransformer(output_distribution='normal')
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def fit(self, X: np.ndarray) -> 'FeatureNormalizer':
        """拟合标准化器"""
        self.scaler.fit(X)
        self.fitted = True
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """转换数据"""
        if not self.fitted:
            raise RuntimeError("Normalizer not fitted. Call fit() first.")
        return self.scaler.transform(X)
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """拟合并转换"""
        return self.scaler.fit_transform(X)
    
    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """逆变换 (用于还原预测结果)"""
        return self.scaler.inverse_transform(X)
    
    def save(self, path: str):
        """保存标准化器"""
        joblib.dump(self.scaler, path)
    
    def load(self, path: str) -> 'FeatureNormalizer':
        """加载标准化器"""
        self.scaler = joblib.load(path)
        self.fitted = True
        return self
```

### 4.3 标准化配置

```yaml
# config/normalization.yaml
normalization:
  method: zscore  # zscore | minmax | robust | rankgauss
  
  # 按特征类型分组标准化
  groups:
    price_features:
      columns: [open, high, low, close, volume]
      method: robust  # 价格数据用 Robust 标准化
  
    indicator_features:
      columns: [ma5, ma10, ma20, ma60, macd, rsi14, ...]
      method: zscore  # 技术指标用 Z-Score
    
    lag_features:
      columns: [close_lag_1, close_lag_5, return_lag_1, ...]
      method: zscore
  
  # 特殊处理
  clip_outliers: true  # 标准化前截断异常值
  clip_threshold: 5.0  # 截断阈值 (标准差倍数)
```

---

## 5. 序列样本构建

### 5.1 序列构建策略

```
输入: 时间序列数据 (T 天, F 个特征)
参数: sequence_length = 60 (使用 60 天历史数据预测)
输出: 样本矩阵 (T - sequence_length + 1, sequence_length, F)

示例:
原始数据: [day_0, day_1, ..., day_T]
样本 1: [day_0, day_1, ..., day_59] → 预测 day_60
样本 2: [day_1, day_2, ..., day_60] → 预测 day_61
...
```

### 5.2 序列构建实现

```python
import numpy as np
from typing import Tuple, Dict

class SequenceBuilder:
    def __init__(self, sequence_length: int = 60, prediction_horizon: int = 1):
        """
        参数:
            sequence_length: 输入序列长度 (历史天数)
            prediction_horizon: 预测 horizon (T+1, T+5, etc.)
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
    
    def build_sequences(
        self, 
        features: np.ndarray, 
        targets: np.ndarray = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        构建序列样本
        
        参数:
            features: 特征矩阵 (T, F)
            targets: 目标向量 (T,) 或 None
        
        返回:
            X: 输入序列 (num_samples, sequence_length, F)
            y: 目标值 (num_samples,) 或 None
        """
        num_samples = len(features) - self.sequence_length + 1
        
        if num_samples <= 0:
            raise ValueError(
                f"Not enough data. Have {len(features)} samples, "
                f"need at least {self.sequence_length}"
            )
        
        # 构建输入序列
        X = np.zeros((num_samples, self.sequence_length, features.shape[1]))
        for i in range(num_samples):
            X[i] = features[i : i + self.sequence_length]
        
        # 构建目标值
        if targets is not None:
            # 目标值对应序列的最后一个时间点的未来值
            y = targets[self.sequence_length - 1 + self.prediction_horizon - 1 : 
                       len(targets) + self.prediction_horizon - 1]
            # 截断到与 X 相同长度
            y = y[:num_samples]
            return X, y
        
        return X, None
    
    def build_multi_horizon_sequences(
        self,
        features: np.ndarray,
        targets: Dict[str, np.ndarray],
        horizons: list = [1, 5, 10]
    ) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        构建多 horizon 序列样本
        
        参数:
            features: 特征矩阵 (T, F)
            targets: 目标字典 {horizon_name: target_array}
            horizons: 预测 horizon 列表
        
        返回:
            X: 输入序列 (num_samples, sequence_length, F)
            y_dict: 目标字典 {horizon_name: target_array}
        """
        X, _ = self.build_sequences(features, None)
        
        y_dict = {}
        for horizon in horizons:
            if horizon in targets:
                _, y = self.build_sequences(features, targets[horizon])
                y_dict[f'target_h{horizon}'] = y
        
        return X, y_dict
```

---

## 6. 数据集划分

### 6.1 划分策略

```
时间序列数据划分 (不能随机打乱!):

┌─────────────────────────────────────────────────────────────┐
│                     完整时间序列                              │
├──────────────┬──────────────┬──────────────┤
│   Train 70%  │   Val 15%    │   Test 15%   │
│  (训练集)     │  (验证集)     │  (测试集)     │
│  2020-2024    │  2024-2025   │  2025-2026   │
└──────────────┴──────────────┴──────────────┘
```

### 6.2 数据集划分实现

```python
from typing import Tuple, List

class DatasetSplitter:
    def __init__(
        self, 
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ):
        """
        时间序列数据集划分
        
        参数:
            train_ratio: 训练集比例
            val_ratio: 验证集比例
            test_ratio: 测试集比例
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
    
    def split(
        self, 
        X: np.ndarray, 
        y: np.ndarray = None
    ) -> Tuple[Tuple[np.ndarray, np.ndarray], 
               Tuple[np.ndarray, np.ndarray], 
               Tuple[np.ndarray, np.ndarray]]:
        """
        划分数据集
        
        返回:
            (X_train, y_train), (X_val, y_val), (X_test, y_test)
        """
        n_samples = len(X)
        
        train_end = int(n_samples * self.train_ratio)
        val_end = int(n_samples * (self.train_ratio + self.val_ratio))
        
        X_train = X[:train_end]
        X_val = X[train_end:val_end]
        X_test = X[val_end:]
        
        if y is not None:
            y_train = y[:train_end]
            y_val = y[train_end:val_end]
            y_test = y[val_end:]
            return (X_train, y_train), (X_val, y_val), (X_test, y_test)
        
        return (X_train, None), (X_val, None), (X_test, None)
    
    def get_split_indices(self, n_samples: int) -> Dict[str, Tuple[int, int]]:
        """获取各数据集的起止索引"""
        train_end = int(n_samples * self.train_ratio)
        val_end = int(n_samples * (self.train_ratio + self.val_ratio))
        
        return {
            'train': (0, train_end),
            'val': (train_end, val_end),
            'test': (val_end, n_samples)
        }
```

### 6.3 PyTorch Dataset 实现

```python
import torch
from torch.utils.data import Dataset, DataLoader

class StockPredictionDataset(Dataset):
    def __init__(
        self, 
        X: np.ndarray, 
        y: np.ndarray,
        transform=None
    ):
        """
        PyTorch Dataset for stock prediction
        
        参数:
            X: 输入序列 (num_samples, seq_len, features)
            y: 目标值 (num_samples,)
            transform: 可选的变换
        """
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y) if y is not None else None
        self.transform = transform
    
    def __len__(self) -> int:
        return len(self.X)
    
    def __getitem__(self, idx: int) -> dict:
        x = self.X[idx]
        y = self.y[idx] if self.y is not None else None
        
        if self.transform:
            x = self.transform(x)
        
        return {'features': x, 'target': y}


def create_dataloaders(
    X_train: np.ndarray, y_train: np.ndarray,
    X_val: np.ndarray, y_val: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
    batch_size: int = 64,
    num_workers: int = 4
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """创建 DataLoader"""
    
    train_dataset = StockPredictionDataset(X_train, y_train)
    val_dataset = StockPredictionDataset(X_val, y_val)
    test_dataset = StockPredictionDataset(X_test, y_test)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,  # 训练集打乱
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=True if num_workers > 0 else False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return train_loader, val_loader, test_loader
```

---

## 7. 完整数据处理流水线

### 7.1 流水线实现

```python
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class DataConfig:
    sequence_length: int = 60
    prediction_horizon: int = 1
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    normalization_method: str = 'zscore'
    missing_value_strategy: str = 'ffill'
    outlier_method: str = 'iqr'
    batch_size: int = 64
    num_workers: int = 4


class DataPipeline:
    def __init__(self, config: DataConfig):
        self.config = config
        self.feature_engineer = FeatureEngineer({})
        self.cleaner = DataCleaner(strategy=config.missing_value_strategy)
        self.outlier_handler = OutlierHandler(method=config.outlier_method)
        self.normalizer = FeatureNormalizer(method=config.normalization_method)
        self.sequence_builder = SequenceBuilder(
            sequence_length=config.sequence_length,
            prediction_horizon=config.prediction_horizon
        )
        self.splitter = DatasetSplitter(
            train_ratio=config.train_ratio,
            val_ratio=config.val_ratio,
            test_ratio=config.test_ratio
        )
    
    def process(
        self, 
        raw_data: pd.DataFrame,
        save_dir: str = None
    ) -> dict:
        """
        完整数据处理流水线
        
        参数:
            raw_data: 原始数据 DataFrame
            save_dir: 保存目录 (可选)
        
        返回:
            包含处理结果和数据统计的字典
        """
        print("🔄 开始数据处理流水线...")
        
        # Step 1: 特征工程
        print("  [1/6] 计算特征...")
        data = self.feature_engineer.compute_all_features(raw_data)
        
        # Step 2: 数据清洗
        print("  [2/6] 处理缺失值...")
        data = self.cleaner.handle_missing(data)
        
        # Step 3: 异常值处理
        print("  [3/6] 处理异常值...")
        feature_cols = self.feature_engineer.get_feature_columns()
        data = self.outlier_handler.detect_and_handle(data, feature_cols)
        
        # Step 4: 提取特征和标签
        print("  [4/6] 提取特征和标签...")
        features = data[feature_cols].values
        target_col = 'future_direction'  # 或 'future_return_1'
        targets = data[target_col].values
        
        # Step 5: 标准化
        print("  [5/6] 标准化特征...")
        features_normalized = self.normalizer.fit_transform(features)
        
        # Step 6: 序列构建
        print("  [6/6] 构建序列样本...")
        X, y = self.sequence_builder.build_sequences(features_normalized, targets)
        
        # Step 7: 数据集划分
        print("  [7/7] 划分数据集...")
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = self.splitter.split(X, y)
        
        # 统计信息
        stats = {
            'total_samples': len(X),
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'test_samples': len(X_test),
            'num_features': len(feature_cols),
            'sequence_length': self.config.sequence_length,
            'feature_columns': feature_cols
        }
        
        print(f"\n✅ 数据处理完成!")
        print(f"  总样本数：{stats['total_samples']}")
        print(f"  训练集：{stats['train_samples']} ({stats['train_samples']/stats['total_samples']*100:.1f}%)")
        print(f"  验证集：{stats['val_samples']} ({stats['val_samples']/stats['total_samples']*100:.1f}%)")
        print(f"  测试集：{stats['test_samples']} ({stats['test_samples']/stats['total_samples']*100:.1f}%)")
        
        result = {
            'X_train': X_train, 'y_train': y_train,
            'X_val': X_val, 'y_val': y_val,
            'X_test': X_test, 'y_test': y_test,
            'stats': stats,
            'feature_columns': feature_cols
        }
        
        # 保存数据
        if save_dir:
            self._save_data(result, save_dir)
        
        return result
    
    def _save_data(self, data: dict, save_dir: str):
        """保存处理后的数据"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # 保存 numpy 数组
        np.savez_compressed(
            save_path / 'processed_data.npz',
            X_train=data['X_train'], y_train=data['y_train'],
            X_val=data['X_val'], y_val=data['y_val'],
            X_test=data['X_test'], y_test=data['y_test']
        )
        
        # 保存统计信息
        with open(save_path / 'stats.json', 'w') as f:
            json.dump(data['stats'], f, indent=2, default=str)
        
        # 保存标准化器
        self.normalizer.save(save_path / 'normalizer.pkl')
        
        # 保存特征列名
        with open(save_path / 'feature_columns.json', 'w') as f:
            json.dump(data['feature_columns'], f, indent=2)
        
        print(f"💾 数据已保存至：{save_dir}")
    
    def load_data(self, data_dir: str) -> dict:
        """加载已处理的数据"""
        data_path = Path(data_dir)
        
        # 加载 numpy 数组
        data = np.load(data_path / 'processed_data.npz')
        
        # 加载统计信息
        with open(data_path / 'stats.json', 'r') as f:
            stats = json.load(f)
        
        # 加载特征列名
        with open(data_path / 'feature_columns.json', 'r') as f:
            feature_columns = json.load(f)
        
        # 加载标准化器
        self.normalizer.load(data_path / 'normalizer.pkl')
        
        return {
            'X_train': data['X_train'], 'y_train': data['y_train'],
            'X_val': data['X_val'], 'y_val': data['y_val'],
            'X_test': data['X_test'], 'y_test': data['y_test'],
            'stats': stats,
            'feature_columns': feature_columns
        }
```

---

## 8. 配置示例

### 8.1 配置文件

```yaml
# config/data_pipeline.yaml
data_pipeline:
  # 序列参数
  sequence_length: 60          # 输入序列长度 (天)
  prediction_horizon: 1        # 预测 horizon (T+1)
  
  # 数据集划分
  split:
    train_ratio: 0.7
    val_ratio: 0.15
    test_ratio: 0.15
  
  # 预处理
  preprocessing:
    missing_value_strategy: ffill  # ffill | bfill | interpolate | drop
    outlier_method: iqr            # zscore | iqr | isolation_forest
    outlier_threshold: 1.5         # IQR 倍数
  
  # 标准化
  normalization:
    method: zscore                 # zscore | minmax | robust | rankgauss
    clip_outliers: true
    clip_threshold: 5.0
  
  # DataLoader
  dataloader:
    batch_size: 64
    num_workers: 4
    pin_memory: true
    prefetch_factor: 2
  
  # 数据源
  data_source:
    type: parquet                  # parquet | csv | database
    path: data/raw/stock_data.parquet
    columns: [date, open, high, low, close, volume]
  
  # 输出
  output:
    save_dir: data/processed
    save_raw_features: false
    save_stats: true
```

---

## 9. 验收标准

### 9.1 功能验收

- [ ] 支持 38 个特征的计算
- [ ] 缺失值处理正确，无 NaN 泄露
- [ ] 异常值检测和处理有效
- [ ] 标准化器可保存和加载
- [ ] 序列构建正确 (shape 验证)
- [ ] 数据集划分符合时间顺序 (无未来数据泄露)
- [ ] DataLoader 可正常迭代

### 9.2 性能验收

- [ ] 10 年数据处理时间 < 30 秒
- [ ] 内存占用 < 2GB (10 年数据)
- [ ] DataLoader 吞吐量 > 1000 样本/秒

### 9.3 质量验收

- [ ] 单元测试覆盖率 > 90%
- [ ] 代码通过 type checking (mypy)
- [ ] 代码通过 linting (flake8, black)

---

## 10. 依赖和接口

### 10.1 上游依赖

- `src/data/` - 原始行情数据获取
- `src/indicators/` - 技术指标计算 (可复用)

### 10.2 下游接口

- `src/prediction/models/` - 模型训练
- `src/prediction/inference/` - 推理服务

### 10.3 外部依赖

```requirements.txt
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
torch>=2.0.0
talib-binary>=0.4.25  # 或 pandas-ta>=0.3.14b
```

---

## 11. 风险与注意事项

| 风险 | 说明 | 缓解措施 |
|------|------|---------|
| 未来数据泄露 | 标准化时使用未来数据 | 只在训练集上 fit，验证/测试集用 transform |
| 序列边界问题 | 滞后特征导致数据丢失 | 明确记录有效数据范围 |
| 内存溢出 | 长序列大数据集 | 使用 generator 或分块处理 |
| 指标计算依赖 | TA-Lib 安装复杂 | 提供 pandas-ta 备选方案 |

---

**文档结束**
