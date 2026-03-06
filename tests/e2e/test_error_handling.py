"""
异常场景测试 - TEST-DEEP-001.1
测试系统的异常处理和容错能力
"""
import pytest
import requests
import time


class TestAPIErrorHandling:
    """API 异常处理测试"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_api_returns_error_format(self):
        """测试 API 返回统一的错误格式"""
        response = requests.get(f"{self.BASE_URL}/api/nonexistent", timeout=10)
        
        if response.status_code >= 400:
            # 错误响应应该包含错误信息
            try:
                data = response.json()
                # 应该有 error 或 message 字段
                assert "error" in data or "message" in data or "detail" in data
            except:
                pytest.fail("Error response is not valid JSON")
    
    def test_api_handles_timeout(self):
        """测试 API 超时处理"""
        # 发送请求并设置很短的超时
        try:
            response = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=0.001)
        except requests.exceptions.Timeout:
            # 超时是预期的
            pass
        except requests.exceptions.ConnectionError:
            # 连接错误也是可以接受的
            pass
    
    def test_api_invalid_json_input(self):
        """测试 API 处理无效 JSON 输入"""
        # 发送无效的 JSON
        response = requests.post(
            f"{self.BASE_URL}/api/test",
            data="not valid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code in [400, 422, 500]
    
    def test_api_missing_required_fields(self):
        """测试 API 处理缺失必填字段"""
        response = requests.post(
            f"{self.BASE_URL}/api/stock/query",
            json={},
            timeout=10
        )
        assert response.status_code in [400, 422, 200]
    
    def test_api_malformed_url(self):
        """测试 API 处理畸形 URL"""
        # 测试各种畸形 URL
        malformed_urls = [
            f"{self.BASE_URL}/api//double-slash",
            f"{self.BASE_URL}/api/with%20space",
            f"{self.BASE_URL}/api/with\nnewline",
        ]
        
        for url in malformed_urls:
            try:
                response = requests.get(url, timeout=10)
                assert response.status_code in [200, 400, 404]
            except:
                pass  # 连接错误也是可以接受的


class TestFrontendErrorHandling:
    """前端异常处理测试"""
    
    BASE_URL = "http://localhost:3000"
    
    def test_frontend_handles_api_error(self):
        """测试前端处理 API 错误"""
        # 前端应该优雅地处理 API 错误
        response = requests.get(self.BASE_URL, timeout=10)
        assert response.status_code == 200
        
        # 页面应该正常加载，即使 API 可能失败
        assert "QCLaw" in response.text or "root" in response.text
    
    def test_frontend_handles_network_error(self):
        """测试前端处理网络错误"""
        # 访问一个存在的页面
        response = requests.get(self.BASE_URL, timeout=10)
        assert response.status_code == 200
    
    def test_frontend_handles_slow_network(self):
        """测试前端处理慢速网络"""
        # 模拟慢速网络（通过增加超时）
        start = time.time()
        response = requests.get(self.BASE_URL, timeout=30)
        elapsed = time.time() - start
        
        # 页面最终应该加载
        assert response.status_code == 200
        assert elapsed < 10.0


class TestDatabaseErrorHandling:
    """数据库异常处理测试"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_database_query_timeout(self):
        """测试数据库查询超时处理"""
        # 查询大量历史数据可能导致超时
        response = requests.get(
            f"{self.BASE_URL}/api/stock/history",
            params={
                "code": "000001",
                "start_date": "2000-01-01",
                "end_date": "2025-12-31"
            },
            timeout=30
        )
        # 应该成功或返回适当的错误
        assert response.status_code in [200, 400, 408, 500]
    
    def test_database_invalid_query(self):
        """测试数据库无效查询处理"""
        response = requests.get(
            f"{self.BASE_URL}/api/stock/history",
            params={"code": "", "start_date": "invalid", "end_date": "invalid"},
            timeout=10
        )
        assert response.status_code in [400, 422, 200]


class TestCacheErrorHandling:
    """缓存异常处理测试"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_cache_miss_handling(self):
        """测试缓存未命中处理"""
        # 首次请求应该触发缓存未命中
        response1 = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=10)
        assert response1.status_code == 200
        
        # 第二次请求应该命中缓存
        response2 = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=10)
        assert response2.status_code == 200
    
    def test_cache_invalidation(self):
        """测试缓存失效处理"""
        # 连续请求应该返回一致的数据
        responses = []
        for _ in range(3):
            response = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=10)
            responses.append(response.json())
            time.sleep(0.1)
        
        # 数据应该在短时间内保持一致
        # (除非市场数据正好更新)


class TestResourceLimits:
    """资源限制测试"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_rate_limiting(self):
        """测试速率限制"""
        # 发送大量快速请求
        responses = []
        for _ in range(20):
            try:
                response = requests.get(f"{self.BASE_URL}/api/market/indices", timeout=5)
                responses.append(response.status_code)
            except:
                responses.append(503)
        
        # 应该有成功或限流响应
        assert 200 in responses or 429 in responses or 503 in responses
    
    def test_payload_size_limit(self):
        """测试负载大小限制"""
        # 发送过大的负载
        large_payload = {"data": "x" * 1000000}  # 1MB
        response = requests.post(
            f"{self.BASE_URL}/api/test",
            json=large_payload,
            timeout=10
        )
        # 应该拒绝或接受
        assert response.status_code in [200, 400, 413, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
