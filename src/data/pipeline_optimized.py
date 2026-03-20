"""
优化数据管道 - CODE-DATA-002

功能:
- LRU 缓存策略 (LRUCache 类)
- 并行化处理 (ThreadPoolExecutor)
- 向量化操作 (NumPy)
- 懒加载 (LazyDataLoader 类)
- 内存优化 (分块处理)

性能目标:
- 数据加载速度提升 50%
- 内存占用降低 30%
- 缓存命中率 > 80%
"""

import time
import threading
from typing import Any, Dict, List, Optional, Callable, Generator, Union
from collections import OrderedDict
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


class LRUCache:
    """
    LRU (Least Recently Used) 缓存实现
    
    特性:
    - 基于 OrderedDict 实现 LRU 淘汰
    - 支持 TTL 过期
    - 支持内存限制
    - 线程安全
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600, max_memory_mb: Optional[float] = None):
        """
        初始化 LRU 缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 默认 TTL (秒)
            max_memory_mb: 最大内存限制 (MB), None 表示无限制
        """
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: OrderedDict = OrderedDict()
        self._sizes: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._max_memory_mb = max_memory_mb
        self._lock = threading.RLock()
        
        # 统计信息
        self._hits = 0
        self._misses = 0
    
    def _get_size(self, value: Any) -> int:
        """获取对象的内存大小 (字节)"""
        if isinstance(value, pd.DataFrame):
            return value.memory_usage(deep=True).sum()
        elif isinstance(value, np.ndarray):
            return value.nbytes
        else:
            import sys
            return sys.getsizeof(value)
    
    def _total_memory(self) -> int:
        """获取当前缓存总内存占用 (字节)"""
        return sum(self._sizes.values())
    
    def _evict_if_needed(self):
        """根据大小和内存限制进行淘汰"""
        # 按大小淘汰
        while len(self._cache) > self._max_size and self._cache:
            # 从 cache 获取最旧的 key（OrderedDict 保证顺序）
            oldest_key = next(iter(self._cache))
            self._cache.pop(oldest_key)
            self._timestamps.pop(oldest_key, None)
            self._sizes.pop(oldest_key, None)
        
        # 按内存淘汰
        if self._max_memory_mb is not None:
            max_bytes = self._max_memory_mb * 1024 * 1024
            while self._total_memory() > max_bytes and self._cache:
                oldest_key = next(iter(self._cache))
                self._cache.pop(oldest_key)
                self._timestamps.pop(oldest_key, None)
                self._sizes.pop(oldest_key, None)
    
    def _is_expired(self, key: str) -> bool:
        """检查条目是否过期"""
        if key not in self._timestamps:
            return True
        return time.time() - self._timestamps[key] > self._ttl_seconds
    
    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        写入缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl_seconds: 自定义 TTL，None 使用默认值
        """
        with self._lock:
            # 如果已存在，先移除
            if key in self._cache:
                self._cache.pop(key)
                self._timestamps.pop(key, None)
                self._sizes.pop(key, None)
            
            # 检查过期并清理
            self._cleanup_expired()
            
            # 写入新值
            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._sizes[key] = self._get_size(value)
            
            # 移动到末尾 (标记为最近使用)
            self._cache.move_to_end(key)
            
            # 淘汰
            self._evict_if_needed()
    
    def get(self, key: str) -> Optional[Any]:
        """
        从缓存读取
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，不存在或已过期返回 None
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # 检查过期
            if self._is_expired(key):
                self._cache.pop(key)
                self._timestamps.pop(key, None)
                self._sizes.pop(key, None)
                self._misses += 1
                return None
            
            # 移动到末尾 (标记为最近使用)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
    
    def _cleanup_expired(self):
        """清理所有过期条目"""
        current_time = time.time()
        expired_keys = [
            key for key, ts in self._timestamps.items()
            if current_time - ts > self._ttl_seconds
        ]
        for key in expired_keys:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            self._sizes.pop(key, None)
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._sizes.clear()
    
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            return {
                "entries": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "total_memory_bytes": self._total_memory(),
                "total_memory_mb": self._total_memory() / (1024 * 1024),
                "max_size": self._max_size,
                "max_memory_mb": self._max_memory_mb,
            }


class LazyDataLoader:
    """
    懒加载器 - 按需加载数据
    
    特性:
    - 延迟加载 (首次访问时才加载)
    - 分块加载 (支持大数据集)
    - 迭代器支持
    """
    
    def __init__(self, data_source: Callable[[], pd.DataFrame], chunk_size: int = 1000):
        """
        初始化懒加载器
        
        Args:
            data_source: 数据源函数，返回 DataFrame
            chunk_size: 分块大小
        """
        self._data_source = data_source
        self._chunk_size = chunk_size
        self._data: Optional[pd.DataFrame] = None
        self._loaded = False
        self._lock = threading.Lock()
    
    def _load(self) -> pd.DataFrame:
        """加载数据 (线程安全)"""
        if not self._loaded:
            with self._lock:
                if not self._loaded:
                    self._data = self._data_source()
                    self._loaded = True
        return self._data
    
    def get_all(self) -> pd.DataFrame:
        """获取全部数据"""
        return self._load()
    
    def get_chunk(self, index: int) -> pd.DataFrame:
        """
        获取指定块
        
        Args:
            index: 块索引 (0-based)
            
        Returns:
            数据块 DataFrame
        """
        data = self._load()
        start = index * self._chunk_size
        end = start + self._chunk_size
        return data.iloc[start:end].copy()
    
    def iter_chunks(self) -> Generator[pd.DataFrame, None, None]:
        """迭代所有数据块"""
        data = self._load()
        total_chunks = (len(data) + self._chunk_size - 1) // self._chunk_size
        for i in range(total_chunks):
            yield self.get_chunk(i)
    
    @property
    def is_loaded(self) -> bool:
        """检查数据是否已加载"""
        return self._loaded


class OptimizedDataPipeline:
    """
    优化数据管道
    
    特性:
    - LRU 缓存
    - 并行数据加载
    - 向量化预处理
    - 懒加载支持
    - 内存优化
    """
    
    def __init__(
        self,
        cache_size: int = 50,
        cache_memory_mb: int = 256,
        max_workers: int = 4,
        chunk_size: int = 100,
    ):
        """
        初始化数据管道
        
        Args:
            cache_size: 缓存最大条目数
            cache_memory_mb: 缓存最大内存 (MB)
            max_workers: 并行工作线程数
            chunk_size: 分块大小
        """
        self._cache = LRUCache(
            max_size=cache_size,
            max_memory_mb=cache_memory_mb,
            ttl_seconds=3600,
        )
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._chunk_size = chunk_size
        
        # 统计信息
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_loads": 0,
            "total_load_time": 0.0,
        }
        self._stats_lock = threading.Lock()
    
    def _make_cache_key(
        self,
        symbol: str,
        start_date: Optional[str],
        end_date: Optional[str],
        period: str,
    ) -> str:
        """生成缓存键"""
        return f"{symbol}:{start_date}:{end_date}:{period}"
    
    def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1mo",
        use_cache: bool = True,
    ) -> Optional[pd.DataFrame]:
        """
        获取单只股票数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 时间周期
            use_cache: 是否使用缓存
            
        Returns:
            股票数据 DataFrame
        """
        cache_key = self._make_cache_key(symbol, start_date, end_date, period)
        
        # 尝试从缓存获取
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                with self._stats_lock:
                    self._stats["cache_hits"] += 1
                return cached.copy()
        
        with self._stats_lock:
            self._stats["cache_misses"] += 1
            self._stats["total_loads"] += 1
        
        # 缓存未命中，加载数据
        start_time = time.time()
        
        # 模拟数据加载 (实际实现应调用数据源)
        # 这里返回 None 表示需要从真实数据源加载
        df = self._load_from_source(symbol, start_date, end_date, period)
        
        load_time = time.time() - start_time
        with self._stats_lock:
            self._stats["total_load_time"] += load_time
        
        # 缓存结果
        if df is not None and not df.empty:
            self._cache.put(cache_key, df)
        
        return df
    
    def _load_from_source(
        self,
        symbol: str,
        start_date: Optional[str],
        end_date: Optional[str],
        period: str,
    ) -> Optional[pd.DataFrame]:
        """
        从数据源加载数据
        
        实际实现应调用 yfinance 或其他数据源
        这里生成模拟数据用于测试
        """
        # 模拟数据加载延迟 (真实场景中网络请求需要时间)
        time.sleep(0.1)
        
        # 生成模拟股票数据
        np.random.seed(hash(symbol) % 2**32)
        n_days = 60  # 1mo 约 60 个交易日
        
        dates = pd.date_range(end=pd.Timestamp.now(), periods=n_days, freq="D")
        df = pd.DataFrame({
            "open": np.random.rand(n_days) * 100 + 50,
            "high": np.random.rand(n_days) * 100 + 50,
            "low": np.random.rand(n_days) * 100 + 40,
            "close": np.random.rand(n_days) * 100 + 50,
            "volume": np.random.randint(100000, 10000000, n_days),
        }, index=dates)
        
        return df
    
    def get_multiple_stocks_parallel(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1mo",
    ) -> Dict[str, pd.DataFrame]:
        """
        并行获取多只股票数据
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            period: 时间周期
            
        Returns:
            股票数据字典 {symbol: DataFrame}
        """
        results = {}
        
        def load_symbol(symbol: str) -> tuple:
            df = self.get_stock_data(symbol, start_date, end_date, period)
            return (symbol, df)
        
        futures = [self._executor.submit(load_symbol, s) for s in symbols]
        
        for future in as_completed(futures):
            try:
                symbol, df = future.result()
                if df is not None and not df.empty:
                    results[symbol] = df
            except Exception as e:
                print(f"Error loading {symbol}: {e}")
        
        return results
    
    def preprocess_data(
        self,
        df: pd.DataFrame,
        operations: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        向量化数据预处理
        
        Args:
            df: 输入 DataFrame
            operations: 预处理操作列表
            
        Returns:
            预处理后的 DataFrame
        """
        if operations is None:
            operations = ["all"]
        
        result = df.copy()
        
        if "all" in operations or "handle_missing" in operations:
            result = self._handle_missing(result)
        
        if "all" in operations or "add_features" in operations:
            result = self._add_features(result)
        
        return result
    
    def _handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值 (向量化)"""
        result = df.copy()
        
        # 前向填充
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        result[numeric_cols] = result[numeric_cols].ffill()
        
        # 剩余缺失值用均值填充
        result[numeric_cols] = result[numeric_cols].fillna(result[numeric_cols].mean())
        
        return result
    
    def _add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加特征 (向量化)"""
        result = df.copy()
        
        if "close" not in result.columns:
            return result
        
        close = result["close"]
        
        # 收益率
        result["returns"] = close.pct_change()
        result["log_returns"] = np.log(close / close.shift(1))
        
        # 动量特征
        result["momentum_5d"] = close / close.shift(5) - 1
        result["momentum_10d"] = close / close.shift(10) - 1
        result["momentum_20d"] = close / close.shift(20) - 1
        
        # 波动率特征
        result["volatility_5d"] = result["returns"].rolling(5).std()
        result["volatility_10d"] = result["returns"].rolling(10).std()
        result["volatility_20d"] = result["returns"].rolling(20).std()
        
        # 移动平均线
        result["ma_5d"] = close.rolling(5).mean()
        result["ma_10d"] = close.rolling(10).mean()
        result["ma_20d"] = close.rolling(20).mean()
        result["ma_60d"] = close.rolling(60).mean()
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """获取管道统计信息"""
        with self._stats_lock:
            cache_stats = self._cache.stats()
            avg_load_time = (
                self._stats["total_load_time"] / self._stats["total_loads"]
                if self._stats["total_loads"] > 0
                else 0.0
            )
            
            return {
                "cache_hits": self._stats["cache_hits"],
                "cache_misses": self._stats["cache_misses"],
                "cache_hit_rate": cache_stats["hit_rate"],
                "total_loads": self._stats["total_loads"],
                "avg_load_time": avg_load_time,
                "cache_details": cache_stats,
            }
    
    def shutdown(self):
        """关闭管道，释放资源"""
        self._executor.shutdown(wait=True)
        self._cache.clear()


# 全局单例
_global_pipeline: Optional[OptimizedDataPipeline] = None
_pipeline_lock = threading.Lock()


def get_optimized_pipeline() -> OptimizedDataPipeline:
    """获取全局优化的数据管道单例"""
    global _global_pipeline
    if _global_pipeline is None:
        with _pipeline_lock:
            if _global_pipeline is None:
                _global_pipeline = OptimizedDataPipeline()
    return _global_pipeline


def get_stock_data_optimized(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "1mo",
    use_cache: bool = True,
) -> Optional[pd.DataFrame]:
    """
    获取股票数据 (使用优化管道)
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        period: 时间周期
        use_cache: 是否使用缓存
        
    Returns:
        股票数据 DataFrame
    """
    pipeline = get_optimized_pipeline()
    return pipeline.get_stock_data(symbol, start_date, end_date, period, use_cache)


def get_multiple_stocks_parallel(
    symbols: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "1mo",
) -> Dict[str, pd.DataFrame]:
    """
    并行获取多只股票数据 (使用优化管道)
    
    Args:
        symbols: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
        period: 时间周期
        
    Returns:
        股票数据字典 {symbol: DataFrame}
    """
    pipeline = get_optimized_pipeline()
    return pipeline.get_multiple_stocks_parallel(symbols, start_date, end_date, period)
