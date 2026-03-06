"""
市场数据 API 单元测试
"""

import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

class TestMarketAPI:
    """市场数据 API 测试"""
    
    def test_get_market_indices(self):
        """测试获取大盘指标"""
        response = client.get("/api/market/indices")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "indices" in data
        assert "shanghai" in data["indices"]
        assert "shenzhen" in data["indices"]
        assert "chinext" in data["indices"]
        
        shanghai = data["indices"]["shanghai"]
        assert "name" in shanghai
        assert "value" in shanghai
        assert "change" in shanghai
        assert "changePercent" in shanghai
    
    def test_get_index_detail(self):
        """测试获取指数详情"""
        response = client.get("/api/market/indices/000001")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "index" in data
        assert data["index"]["name"] == "上证指数"
    
    def test_get_index_detail_not_found(self):
        """测试获取不存在的指数"""
        response = client.get("/api/market/indices/999999")
        assert response.status_code == 404
