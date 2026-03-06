"""
AI 建议 API 单元测试
"""

import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

class TestAdviceAPI:
    """AI 建议 API 测试"""
    
    def test_get_ai_advice(self):
        """测试获取 AI 建议"""
        response = client.get("/api/advice")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "advice" in data
        
        advice = data["advice"]
        assert "type" in advice
        assert advice["type"] in ["买入", "持有", "卖出"]
        assert "confidence" in advice
        assert 0 <= advice["confidence"] <= 1
        assert "reasons" in advice
        assert isinstance(advice["reasons"], list)
        assert "risks" in advice
        assert isinstance(advice["risks"], list)
        assert "targets" in advice
        assert isinstance(advice["targets"], list)
