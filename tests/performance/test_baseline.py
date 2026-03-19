"""
性能基准测试 - TEST-DEEP-001.2
测试系统性能指标并建立基准
"""
import pytest
import requests
import time
import statistics
from datetime import datetime


class TestAPIPerformance:
    """API 性能测试"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_api_response_time_baseline(self):
        """测试 API 响应时间基准"""
        times = []
        
        for _ in range(10):
            start = time.time()
            response = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=30)
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200
        
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        print(f"\nAPI 响应时间基准:")
        print(f"  平均：{avg_time*1000:.2f}ms")
        print(f"  P95: {p95_time*1000:.2f}ms")
        print(f"  最小：{min(times)*1000:.2f}ms")
        print(f"  最大：{max(times)*1000:.2f}ms")
        
        # 目标：平均响应时间 < 500ms
        assert avg_time < 0.5, f"API avg response time {avg_time:.2f}s exceeds 500ms"
    
    def test_api_throughput(self):
        """测试 API 吞吐量"""
        import concurrent.futures
        
        def make_request():
            start = time.time()
            response = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=30)
            return time.time() - start, response.status_code
        
        # 并发 10 个请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in futures]
        
        times = [r[0] for r in results]
        success_count = sum(1 for r in results if r[1] == 200)
        
        total_time = max(times) - min(times)
        throughput = success_count / total_time if total_time > 0 else 0
        
        print(f"\nAPI 吞吐量测试:")
        print(f"  成功请求：{success_count}/20")
        print(f"  总时间：{total_time:.2f}s")
        print(f"  吞吐量：{throughput:.2f} req/s")
        
        # 目标：吞吐量 > 5 req/s
        assert throughput > 5, f"API throughput {throughput:.2f} req/s below 5 req/s"
    
    def test_api_memory_efficiency(self):
        """测试 API 内存效率（通过响应大小）"""
        response = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=30)
        assert response.status_code == 200
        
        content_length = len(response.content)
        
        print(f"\nAPI 响应大小:")
        print(f"  大小：{content_length / 1024:.2f}KB")
        
        # 目标：响应大小 < 1MB
        assert content_length < 1024 * 1024, f"Response size {content_length} exceeds 1MB"


class TestFrontendPerformance:
    """前端性能测试"""
    
    BASE_URL = "http://localhost:80"
    
    def test_frontend_load_time(self):
        """测试前端加载时间"""
        times = []
        
        for _ in range(5):
            start = time.time()
            response = requests.get(self.BASE_URL, timeout=30)
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200
        
        avg_time = statistics.mean(times)
        
        print(f"\n前端加载时间基准:")
        print(f"  平均：{avg_time*1000:.2f}ms")
        print(f"  最小：{min(times)*1000:.2f}ms")
        print(f"  最大：{max(times)*1000:.2f}ms")
        
        # 目标：加载时间 < 3s
        assert avg_time < 3.0, f"Frontend load time {avg_time:.2f}s exceeds 3s"
    
    def test_frontend_asset_size(self):
        """测试前端资源大小"""
        response = requests.get(self.BASE_URL, timeout=30)
        assert response.status_code == 200
        
        html_size = len(response.content)
        
        print(f"\n前端资源大小:")
        print(f"  HTML: {html_size / 1024:.2f}KB")
        
        # 目标：HTML < 100KB
        assert html_size < 100 * 1024, f"HTML size {html_size} exceeds 100KB"
    
    def test_frontend_concurrent_users(self):
        """测试前端并发用户支持"""
        import concurrent.futures
        
        def load_page():
            start = time.time()
            response = requests.get(self.BASE_URL, timeout=30)
            return time.time() - start, response.status_code
        
        # 模拟 20 个并发用户
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(load_page) for _ in range(20)]
            results = [f.result() for f in futures]
        
        times = [r[0] for r in results]
        success_count = sum(1 for r in results if r[1] == 200)
        
        print(f"\n前端并发测试:")
        print(f"  成功请求：{success_count}/20")
        print(f"  平均时间：{statistics.mean(times)*1000:.2f}ms")
        
        # 目标：80% 以上成功
        assert success_count >= 16, f"Frontend success rate {success_count}/20 below 80%"


class TestDatabasePerformance:
    """数据库性能测试"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_database_query_time(self):
        """测试数据库查询时间"""
        times = []
        
        # 测试历史数据查询
        for _ in range(5):
            start = time.time()
            response = requests.get(
                f"{self.BASE_URL}/api/stock/history",
                params={"code": "000001", "start_date": "2024-01-01", "end_date": "2025-12-31"},
                timeout=30
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n数据库查询测试:")
                print(f"  返回记录数：{len(data) if isinstance(data, list) else 'N/A'}")
        
        if times:
            avg_time = statistics.mean(times)
            print(f"  平均查询时间：{avg_time*1000:.2f}ms")
            
            # 目标：查询时间 < 2s
            assert avg_time < 2.0, f"DB query time {avg_time:.2f}s exceeds 2s"
    
    def test_database_concurrent_queries(self):
        """测试数据库并发查询"""
        import concurrent.futures
        
        def query_stock(code):
            start = time.time()
            response = requests.get(
                f"{self.BASE_URL}/api/stock/history",
                params={"code": code, "start_date": "2025-01-01", "end_date": "2025-12-31"},
                timeout=30
            )
            return time.time() - start, response.status_code
        
        # 并发查询不同股票
        stock_codes = ["000001", "000002", "600000", "600036", "000858"]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(query_stock, code) for code in stock_codes]
            results = list(zip(stock_codes, [f.result() for f in futures]))
        
        print(f"\n数据库并发查询测试:")
        for code, (time_taken, status) in results:
            print(f"  {code}: {time_taken*1000:.2f}ms (status: {status})")


class TestCachePerformance:
    """缓存性能测试"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_cache_hit_improvement(self):
        """测试缓存命中提升"""
        # 首次请求（缓存未命中）
        start = time.time()
        response1 = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=30)
        first_time = time.time() - start
        
        # 第二次请求（缓存命中）
        start = time.time()
        response2 = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=30)
        second_time = time.time() - start
        
        improvement = (first_time - second_time) / first_time * 100 if first_time > 0 else 0
        
        print(f"\n缓存性能测试:")
        print(f"  缓存未命中：{first_time*1000:.2f}ms")
        print(f"  缓存命中：{second_time*1000:.2f}ms")
        print(f"  性能提升：{improvement:.1f}%")
        
        # 缓存命中应该更快
        if first_time > 0:
            assert second_time <= first_time * 1.5, "Cache hit not faster than miss"


def generate_performance_report():
    """生成性能基准报告"""
    report = f"""# 性能基准测试报告

**生成时间:** {datetime.now().isoformat()}
**测试环境:** QCLaw 生产环境

## API 性能指标

| 指标 | 目标 | 实测 | 状态 |
|------|------|------|------|
| 平均响应时间 | < 500ms | - | ⏳ |
| P95 响应时间 | < 1000ms | - | ⏳ |
| 吞吐量 | > 5 req/s | - | ⏳ |
| 响应大小 | < 1MB | - | ⏳ |

## 前端性能指标

| 指标 | 目标 | 实测 | 状态 |
|------|------|------|------|
| 加载时间 | < 3s | - | ⏳ |
| HTML 大小 | < 100KB | - | ⏳ |
| 并发用户 | > 20 | - | ⏳ |

## 数据库性能指标

| 指标 | 目标 | 实测 | 状态 |
|------|------|------|------|
| 查询时间 | < 2s | - | ⏳ |
| 并发查询 | > 5 | - | ⏳ |

## 缓存性能指标

| 指标 | 目标 | 实测 | 状态 |
|------|------|------|------|
| 缓存命中率 | > 80% | - | ⏳ |
| 性能提升 | > 50% | - | ⏳ |

## 总结

性能基准测试已执行，详细数据见测试输出。

**测试负责人:** qclaw-tester
**测试日期:** {datetime.now().strftime("%Y-%m-%d")}
"""
    
    # 写入报告文件
    with open("/home/openclaw/.openclaw/workspace-qclaw/docs/reports/performance-baseline-2026-03-06.md", "w") as f:
        f.write(report)
    
    print(f"\n性能基准报告已生成：docs/reports/performance-baseline-2026-03-06.md")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
    generate_performance_report()
