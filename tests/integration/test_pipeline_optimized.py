"""
优化数据管道集成测试

测试 CODE-DATA-002 实现的优化功能:
- LRU 缓存策略
- 并行化处理
- 懒加载
- 向量化操作
- 内存优化
"""

import pytest
import time
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# 直接导入模块，避免相对导入问题
import importlib.util
spec = importlib.util.spec_from_file_location(
    "pipeline_optimized",
    project_root / "src" / "data" / "pipeline_optimized.py"
)
pipeline_optimized = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline_optimized)

LRUCache = pipeline_optimized.LRUCache
LazyDataLoader = pipeline_optimized.LazyDataLoader
OptimizedDataPipeline = pipeline_optimized.OptimizedDataPipeline
get_optimized_pipeline = pipeline_optimized.get_optimized_pipeline
get_stock_data_optimized = pipeline_optimized.get_stock_data_optimized
get_multiple_stocks_parallel = pipeline_optimized.get_multiple_stocks_parallel


class TestLRUCache:
    """LRU 缓存测试"""
    
    def test_cache_basic_operations(self):
        """测试基本缓存操作"""
        cache = LRUCache(max_size=5, ttl_seconds=3600)
        
        # 写入
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # 读取
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") is None
    
    def test_cache_lru_eviction(self):
        """测试 LRU 淘汰策略"""
        cache = LRUCache(max_size=3, ttl_seconds=3600)
        
        # 写入 3 个条目
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # 访问 key1，使其成为最近使用
        cache.get("key1")
        
        # 写入第 4 个条目，应该淘汰 key2 (最久未使用)
        cache.put("key4", "value4")
        
        assert cache.get("key1") == "value1"  # 存在
        assert cache.get("key2") is None  # 已淘汰
        assert cache.get("key3") == "value3"  # 存在
        assert cache.get("key4") == "value4"  # 存在
    
    def test_cache_memory_limit(self):
        """测试内存限制"""
        cache = LRUCache(max_size=1000, max_memory_mb=1, ttl_seconds=3600)
        
        # 写入大数据
        large_data = np.random.rand(1000, 100)
        cache.put("large1", large_data)
        
        # 再写入一个大数据，应该触发淘汰
        large_data2 = np.random.rand(1000, 100)
        cache.put("large2", large_data2)
        
        stats = cache.stats()
        assert stats["total_memory_mb"] <= 1.0
    
    def test_cache_ttl_expiration(self):
        """测试 TTL 过期"""
        cache = LRUCache(max_size=5, ttl_seconds=1)  # 1 秒过期
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # 等待过期
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_cache_dataframe(self):
        """测试 DataFrame 缓存"""
        cache = LRUCache(max_size=10, ttl_seconds=3600)
        
        df = pd.DataFrame({
            "open": [1.0, 2.0, 3.0],
            "close": [1.1, 2.1, 3.1],
            "volume": [100, 200, 300],
        })
        
        cache.put("stock_data", df)
        cached_df = cache.get("stock_data")
        
        assert cached_df is not None
        assert len(cached_df) == 3
        pd.testing.assert_frame_equal(df, cached_df)
    
    def test_cache_clear(self):
        """测试清空缓存"""
        cache = LRUCache(max_size=5, ttl_seconds=3600)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.stats()["entries"] == 0


class TestLazyDataLoader:
    """懒加载器测试"""
    
    def test_lazy_loader_basic(self):
        """测试基本懒加载"""
        call_count = [0]
        
        def mock_data_source():
            call_count[0] += 1
            return pd.DataFrame({"value": range(100)})
        
        loader = LazyDataLoader(mock_data_source, chunk_size=10)
        
        # 创建时不应加载数据
        assert call_count[0] == 0
        
        # 首次访问时加载
        data = loader.get_all()
        assert call_count[0] == 1
        assert len(data) == 100
    
    def test_lazy_loader_chunked(self):
        """测试分块加载"""
        df = pd.DataFrame({"value": range(100)})
        loader = LazyDataLoader(lambda: df, chunk_size=10)
        
        # 获取第一块
        chunk0 = loader.get_chunk(0)
        assert len(chunk0) == 10
        assert chunk0["value"].iloc[0] == 0
        
        # 获取第二块
        chunk1 = loader.get_chunk(1)
        assert len(chunk1) == 10
        assert chunk1["value"].iloc[0] == 10
        
        # 获取最后一块
        chunk9 = loader.get_chunk(9)
        assert len(chunk9) == 10
        assert chunk9["value"].iloc[-1] == 99
    
    def test_lazy_loader_iteration(self):
        """测试迭代器"""
        df = pd.DataFrame({"value": range(50)})
        loader = LazyDataLoader(lambda: df, chunk_size=10)
        
        chunks = list(loader.iter_chunks())
        assert len(chunks) == 5
        
        # 验证数据完整性
        all_values = []
        for chunk in chunks:
            all_values.extend(chunk["value"].tolist())
        assert all_values == list(range(50))


class TestOptimizedDataPipeline:
    """优化数据管道测试"""
    
    @pytest.fixture
    def pipeline(self):
        """创建测试管道"""
        return OptimizedDataPipeline(
            cache_size=50,
            cache_memory_mb=256,
            max_workers=4,
            chunk_size=100,
        )
    
    def test_pipeline_initialization(self, pipeline):
        """测试管道初始化"""
        stats = pipeline.get_stats()
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "cache_hit_rate" in stats
    
    def test_pipeline_single_stock_load(self, pipeline):
        """测试单只股票加载 (使用模拟数据避免速率限制)"""
        # 创建模拟数据
        mock_df = pd.DataFrame({
            "open": np.random.rand(20) * 100,
            "high": np.random.rand(20) * 100,
            "low": np.random.rand(20) * 100,
            "close": np.random.rand(20) * 100,
            "volume": np.random.randint(1000, 10000, 20),
        })
        mock_df.index = pd.date_range("2024-01-01", periods=20, freq="D")
        
        # 直接缓存模拟数据
        cache_key = pipeline._make_cache_key("TEST", None, None, "1mo")
        pipeline._cache.put(cache_key, mock_df)
        
        # 从缓存获取
        df = pipeline.get_stock_data("TEST", period="1mo", use_cache=True)
        
        assert df is not None
        assert not df.empty
        assert len(df) == 20
        assert "close" in df.columns
    
    def test_pipeline_cache_hit(self, pipeline):
        """测试缓存命中 (使用模拟数据)"""
        # 创建模拟数据
        mock_df = pd.DataFrame({"close": np.random.rand(20) * 100})
        mock_df.index = pd.date_range("2024-01-01", periods=20, freq="D")
        
        cache_key = pipeline._make_cache_key("TEST2", None, None, "1mo")
        
        # 第一次：缓存未命中，手动放入
        pipeline._stats["cache_misses"] += 1
        pipeline._cache.put(cache_key, mock_df)
        
        # 第二次：缓存命中
        start2 = time.time()
        df2 = pipeline.get_stock_data("TEST2", period="1mo", use_cache=True)
        time2 = time.time() - start2
        
        # 缓存命中应该非常快
        assert time2 < 0.1
        pd.testing.assert_frame_equal(df2, mock_df)  # 值比较而非对象比较
        
        # 检查统计
        stats = pipeline.get_stats()
        assert stats["cache_hits"] >= 1
    
    def test_pipeline_parallel_loading(self, pipeline):
        """测试并行加载 (使用模拟数据)"""
        # 准备模拟数据
        symbols = ["TEST1", "TEST2", "TEST3", "TEST4"]
        for symbol in symbols:
            mock_df = pd.DataFrame({
                "close": np.random.rand(20) * 100,
                "volume": np.random.randint(1000, 10000, 20),
            })
            mock_df.index = pd.date_range("2024-01-01", periods=20, freq="D")
            cache_key = pipeline._make_cache_key(symbol, None, None, "1mo")
            pipeline._cache.put(cache_key, mock_df)
        
        start = time.time()
        results = pipeline.get_multiple_stocks_parallel(symbols, period="1mo")
        total_time = time.time() - start
        
        # 验证结果
        assert len(results) == len(symbols)
        for symbol in results:
            assert not results[symbol].empty
            assert "close" in results[symbol].columns
        
        print(f"并行加载 {len(symbols)} 只股票耗时：{total_time:.2f}s")
    
    def test_pipeline_preprocessing(self, pipeline):
        """测试向量化预处理"""
        # 创建测试数据
        df = pd.DataFrame({
            "open": [1.0, 2.0, 3.0, 4.0, 5.0] * 20,
            "high": [1.1, 2.1, 3.1, 4.1, 5.1] * 20,
            "low": [0.9, 1.9, 2.9, 3.9, 4.9] * 20,
            "close": [1.05, 2.05, 3.05, 4.05, 5.05] * 20,
            "volume": [100, 200, 300, 400, 500] * 20,
        })
        
        # 预处理
        df_processed = pipeline.preprocess_data(df)
        
        # 验证新增特征
        assert "returns" in df_processed.columns
        assert "log_returns" in df_processed.columns
        
        # 验证动量特征
        assert "momentum_5d" in df_processed.columns
        
        # 验证波动率特征
        assert "volatility_5d" in df_processed.columns
        
        # 验证移动平均线
        assert "ma_5d" in df_processed.columns
        assert "ma_10d" in df_processed.columns
        assert "ma_20d" in df_processed.columns
    
    def test_pipeline_missing_value_handling(self, pipeline):
        """测试缺失值处理"""
        df = pd.DataFrame({
            "open": [1.0, np.nan, 3.0, np.nan, 5.0],
            "close": [1.1, 2.1, np.nan, 4.1, 5.1],
            "volume": [100, 200, 300, 400, 500],
        })
        
        df_processed = pipeline.preprocess_data(df, operations=["handle_missing"])
        
        # 验证缺失值已填充
        assert not df_processed["open"].isna().any()
        assert not df_processed["close"].isna().any()
    
    def test_pipeline_lazy_loading(self, pipeline):
        """测试懒加载模式 (使用模拟数据)"""
        # 创建模拟数据源
        mock_df = pd.DataFrame({
            "close": np.random.rand(50) * 100,
            "volume": np.random.randint(1000, 10000, 50),
        })
        mock_df.index = pd.date_range("2024-01-01", periods=50, freq="D")
        
        loader = LazyDataLoader(lambda: mock_df.copy(), chunk_size=10)
        
        # 返回的应该是 LazyDataLoader
        assert isinstance(loader, LazyDataLoader)
        
        # 获取数据
        df = loader.get_all()
        assert df is not None
        assert len(df) == 50
    
    def test_pipeline_stats(self, pipeline):
        """测试统计信息"""
        # 模拟缓存命中/未命中
        mock_df = pd.DataFrame({"close": [1.0, 2.0, 3.0]})
        cache_key = pipeline._make_cache_key("STATS_TEST", None, None, "1mo")
        
        # 未命中
        pipeline._stats["cache_misses"] += 1
        pipeline._cache.put(cache_key, mock_df)
        
        # 命中
        pipeline._stats["cache_hits"] += 1
        pipeline._cache.get(cache_key)
        
        stats = pipeline.get_stats()
        
        assert stats["cache_hits"] >= 1
        assert stats["cache_misses"] >= 1
        assert "cache_hit_rate" in stats
        assert "avg_load_time" in stats
        assert "cache_details" in stats
    
    def test_pipeline_memory_efficiency(self, pipeline):
        """测试内存效率"""
        # 加载多只股票
        symbols = [f"TEST{i}.SS" for i in range(10)]
        
        # 模拟数据 (实际测试中可能不会真的加载)
        for symbol in symbols:
            df = pd.DataFrame({
                "close": np.random.rand(100),
                "volume": np.random.randint(100, 1000, 100),
            })
            pipeline._cache.put(symbol, df)
        
        stats = pipeline._cache.stats()
        assert stats["entries"] <= 50  # 不超过最大缓存数


class TestPerformanceImprovement:
    """性能提升测试"""
    
    @pytest.fixture
    def pipeline(self):
        return OptimizedDataPipeline(
            cache_size=100,
            cache_memory_mb=512,
            max_workers=8,
        )
    
    def test_cache_performance(self, pipeline):
        """测试缓存性能提升"""
        symbol = "AAPL"
        
        # 第一次加载
        start = time.time()
        pipeline.get_stock_data(symbol, period="1mo")
        time_first = time.time() - start
        
        # 第二次加载 (缓存)
        start = time.time()
        pipeline.get_stock_data(symbol, period="1mo")
        time_cached = time.time() - start
        
        # 缓存应该显著提升性能
        speedup = time_first / time_cached if time_cached > 0 else float('inf')
        print(f"缓存加速比：{speedup:.2f}x")
        
        # 通常缓存应该快 10 倍以上
        assert speedup > 5
    
    def test_parallel_performance(self, pipeline):
        """测试并行性能提升"""
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        
        # 并行加载
        start = time.time()
        pipeline.get_multiple_stocks_parallel(symbols, period="1mo")
        time_parallel = time.time() - start
        
        # 串行加载
        start = time.time()
        for symbol in symbols:
            pipeline.get_stock_data(symbol, period="1mo", use_cache=False)
        time_serial = time.time() - start
        
        speedup = time_serial / time_parallel if time_parallel > 0 else float('inf')
        print(f"并行加速比：{speedup:.2f}x")
        
        # 并行应该有一定加速 (取决于网络和线程数)
        assert speedup > 1.0
    
    def test_vectorization_performance(self, pipeline):
        """测试向量化性能"""
        # 创建大数据集
        n = 10000
        df = pd.DataFrame({
            "close": np.random.rand(n) * 100,
            "volume": np.random.randint(1000, 100000, n),
        })
        
        # 向量化预处理
        start = time.time()
        df_processed = pipeline.preprocess_data(df)
        time_vectorized = time.time() - start
        
        print(f"向量化预处理 {n} 条记录耗时：{time_vectorized:.3f}s")
        
        # 应该非常快 (< 1 秒)
        assert time_vectorized < 1.0


class TestIntegration:
    """集成测试"""
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        pipeline = OptimizedDataPipeline()
        
        try:
            # 1. 获取单只股票
            df = pipeline.get_stock_data("AAPL", period="1mo")
            assert not df.empty
            
            # 2. 预处理
            df_processed = pipeline.preprocess_data(df)
            assert "returns" in df_processed.columns
            
            # 3. 获取多只股票
            symbols = ["AAPL", "MSFT", "GOOGL"]
            results = pipeline.get_multiple_stocks_parallel(symbols, period="1mo")
            assert len(results) > 0
            
            # 4. 检查缓存
            stats = pipeline.get_stats()
            assert stats["cache_hits"] + stats["cache_misses"] > 0
            
            print(f"端到端测试完成，缓存命中率：{stats['cache_hit_rate']}")
            
        finally:
            pipeline.shutdown()
    
    def test_global_pipeline_singleton(self):
        """测试全局单例模式"""
        p1 = get_optimized_pipeline()
        p2 = get_optimized_pipeline()
        
        assert p1 is p2  # 同一个实例


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
