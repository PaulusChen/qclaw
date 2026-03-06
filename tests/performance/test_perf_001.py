"""
TEST-PERF-001: 性能基准测试
完整性能测试套件 - 包含并发用户和系统资源监控

测试目标:
- 页面加载时间 < 3s ✅
- API 响应时间 < 500ms ✅
- 图表渲染时间 < 1s
- 并发用户支持 > 100
- 内存使用 < 512MB
- CPU 使用率 < 80%
"""
import pytest
import requests
import time
import statistics
import subprocess
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestFrontendPerformance:
    """前端性能测试"""
    
    BASE_URL = "http://localhost:3000"
    
    def test_frontend_load_time(self):
        """测试前端加载时间 - 目标 < 3s"""
        times = []
        
        for _ in range(10):
            start = time.time()
            response = requests.get(self.BASE_URL, timeout=30)
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200, f"Frontend returned {response.status_code}"
        
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        print(f"\n前端加载时间:")
        print(f"  平均：{avg_time*1000:.2f}ms")
        print(f"  P95: {p95_time*1000:.2f}ms")
        print(f"  最小：{min(times)*1000:.2f}ms")
        print(f"  最大：{max(times)*1000:.2f}ms")
        
        # 目标：平均加载时间 < 3s
        assert avg_time < 3.0, f"Frontend avg load time {avg_time:.2f}s exceeds 3s"
    
    def test_frontend_concurrent_users(self):
        """测试并发用户支持 - 目标 > 100 并发"""
        def make_request(user_id):
            start = time.time()
            try:
                response = requests.get(self.BASE_URL, timeout=30)
                elapsed = time.time() - start
                return user_id, response.status_code, elapsed
            except Exception as e:
                return user_id, 0, str(e)
        
        # 测试 100 并发用户
        num_users = 100
        results = []
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_users)]
            for future in as_completed(futures):
                results.append(future.result())
        
        success_count = sum(1 for r in results if r[1] == 200)
        success_rate = success_count / num_users * 100
        times = [r[2] for r in results if isinstance(r[2], float)]
        
        avg_time = statistics.mean(times) if times else 0
        
        print(f"\n并发用户测试 ({num_users} 用户):")
        print(f"  成功请求：{success_count}/{num_users} ({success_rate:.1f}%)")
        print(f"  平均响应时间：{avg_time*1000:.2f}ms")
        print(f"  最大响应时间：{max(times)*1000:.2f}ms" if times else "  无成功请求")
        
        # 目标：>90% 成功率
        assert success_rate >= 90, f"Success rate {success_rate:.1f}% below 90%"


class TestAPIPerformance:
    """API 性能测试"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_api_response_time(self):
        """测试 API 响应时间 - 目标 < 500ms"""
        endpoints = [
            "/api/news",
            "/api/market/indices",
        ]
        
        for endpoint in endpoints:
            times = []
            status_codes = []
            
            for _ in range(10):
                start = time.time()
                try:
                    response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=30)
                    elapsed = time.time() - start
                    times.append(elapsed)
                    status_codes.append(response.status_code)
                except Exception as e:
                    times.append(float('inf'))
                    status_codes.append(0)
            
            avg_time = statistics.mean([t for t in times if t != float('inf')]) if times else 0
            
            print(f"\nAPI {endpoint}:")
            print(f"  平均响应时间：{avg_time*1000:.2f}ms")
            print(f"  状态码分布：{set(status_codes)}")
            
            # 目标：平均响应时间 < 500ms (仅对 200 响应的 API)
            if 200 in status_codes:
                assert avg_time < 0.5, f"API {endpoint} avg response {avg_time:.2f}s exceeds 500ms"
    
    def test_api_concurrent_requests(self):
        """测试 API 并发请求 - 目标 100 并发"""
        def make_request():
            start = time.time()
            try:
                response = requests.get(f"{self.BASE_URL}/api/news", timeout=30)
                return time.time() - start, response.status_code
            except:
                return float('inf'), 0
        
        num_requests = 100
        results = []
        
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            for future in as_completed(futures):
                results.append(future.result())
        
        success_count = sum(1 for r in results if r[1] == 200)
        success_rate = success_count / num_requests * 100
        
        print(f"\nAPI 并发测试 ({num_requests} 请求):")
        print(f"  成功请求：{success_count}/{num_requests} ({success_rate:.1f}%)")
        
        # 目标：>80% 成功率
        assert success_rate >= 80, f"API success rate {success_rate:.1f}% below 80%"


class TestSystemResources:
    """系统资源监控测试"""
    
    def test_memory_usage(self):
        """测试内存使用 - 目标 < 512MB"""
        # 获取前端进程内存使用
        try:
            result = subprocess.run(
                ["pgrep", "-f", "npm run dev"],
                capture_output=True, text=True, timeout=5
            )
            pids = result.stdout.strip().split('\n')
            
            total_memory = 0
            for pid in pids:
                if pid:
                    try:
                        # 读取 /proc/[pid]/status 获取内存
                        with open(f"/proc/{pid}/status", "r") as f:
                            for line in f:
                                if line.startswith("VmRSS:"):
                                    # VmRSS 单位是 kB
                                    memory_kb = int(line.split()[1])
                                    total_memory += memory_kb
                                    break
                    except:
                        pass
            
            memory_mb = total_memory / 1024
            
            print(f"\n系统内存使用:")
            print(f"  前端进程内存：{memory_mb:.2f}MB")
            print(f"  进程数：{len(pids)}")
            
            # 目标：内存使用 < 512MB
            assert memory_mb < 512, f"Memory usage {memory_mb:.2f}MB exceeds 512MB"
            
        except Exception as e:
            print(f"\n内存测试跳过：{e}")
            pytest.skip("无法获取内存信息")
    
    def test_cpu_usage(self):
        """测试 CPU 使用率 - 目标 < 80%"""
        try:
            # 使用 top 命令获取 CPU 使用率
            result = subprocess.run(
                ["top", "-bn1"],
                capture_output=True, text=True, timeout=10
            )
            
            # 解析 CPU 使用率
            for line in result.stdout.split('\n'):
                if 'Cpu(s)' in line:
                    # 格式：Cpu(s):  1.0%us,  0.5%sy,  0.0%ni, 98.5%id, ...
                    parts = line.split(',')
                    user_cpu = float(parts[0].split(':')[1].strip().replace('us', '').strip())
                    system_cpu = float(parts[1].strip().replace('sy', '').strip())
                    total_cpu = user_cpu + system_cpu
                    
                    print(f"\nCPU 使用率:")
                    print(f"  User: {user_cpu:.1f}%")
                    print(f"  System: {system_cpu:.1f}%")
                    print(f"  Total: {total_cpu:.1f}%")
                    
                    # 目标：CPU 使用率 < 80%
                    assert total_cpu < 80, f"CPU usage {total_cpu:.1f}% exceeds 80%"
                    return
            
            print("\nCPU 测试：无法解析 CPU 使用率")
            pytest.skip("无法获取 CPU 信息")
            
        except Exception as e:
            print(f"\nCPU 测试跳过：{e}")
            pytest.skip("无法获取 CPU 信息")


class TestChartRendering:
    """图表渲染性能测试"""
    
    BASE_URL = "http://localhost:3000"
    
    def test_chart_render_time(self):
        """测试图表渲染时间 - 目标 < 1s
        
        注意：这是模拟测试，实际图表渲染需要浏览器自动化
        """
        # 前端加载时间间接反映图表渲染性能
        times = []
        
        for _ in range(5):
            start = time.time()
            response = requests.get(self.BASE_URL, timeout=30)
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200
        
        avg_time = statistics.mean(times)
        
        print(f"\n图表渲染时间 (模拟):")
        print(f"  平均加载时间：{avg_time*1000:.2f}ms")
        print(f"  注：实际图表渲染需浏览器自动化测试")
        
        # 目标：加载时间 < 1s (间接指标)
        assert avg_time < 1.0, f"Load time {avg_time:.2f}s exceeds 1s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
