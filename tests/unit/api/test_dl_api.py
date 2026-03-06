"""
深度学习 API 单元测试
"""

import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

class TestDLAPI:
    """深度学习 API 测试"""
    
    def test_list_models(self):
        """测试获取模型列表"""
        response = client.get("/api/v1/dl/models")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "models" in data
        assert "count" in data
        assert isinstance(data["models"], list)
    
    def test_predict_stock_price(self):
        """测试股价预测"""
        request_data = {
            "model_id": "lstm_real_600519",
            "symbol": "600519",
            "days": 5
        }
        response = client.post("/api/v1/dl/predict", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "model_id" in data
        assert "symbol" in data
        assert "prediction" in data
        assert "confidence" in data
        assert "disclaimer" in data
        
        predictions = data["prediction"]
        assert len(predictions) == 5
        for pred in predictions:
            assert "day" in pred
            assert "price" in pred
            assert "change" in pred
            assert "changePercent" in pred
    
    def test_predict_not_found_model(self):
        """测试不存在的模型"""
        request_data = {
            "model_id": "nonexistent_model",
            "symbol": "600519",
            "days": 5
        }
        response = client.post("/api/v1/dl/predict", json=request_data)
        assert response.status_code == 404
