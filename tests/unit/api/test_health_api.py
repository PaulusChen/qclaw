"""
健康检查 API 单元测试
"""

import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

class TestHealthAPI:
    """健康检查 API 测试"""
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "services" in data
        assert "api" in data["services"]
        assert "database" in data["services"]
        assert "redis" in data["services"]
    
    def test_health_check_version(self):
        """测试版本号"""
        response = client.get("/api/health")
        data = response.json()
        assert data["version"] == "1.0.0"
