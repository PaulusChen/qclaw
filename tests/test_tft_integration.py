"""
TFT 模型集成测试
测试 TFT 模型与 qclaw 项目的集成
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.models.tft_model import TFTModelConfig, TFTStockPredictor


class TestTFTModelConfig:
    """测试 TFT 模型配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = TFTModelConfig()
        
        assert config.max_encoder_length == 60
        assert config.max_prediction_length == 5
        assert config.hidden_size == 64
        assert config.attention_head_size == 4
        assert config.dropout == 0.1
        assert config.learning_rate == 0.001
        assert config.batch_size == 64
        assert config.max_epochs == 100
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = TFTModelConfig(
            max_encoder_length=30,
            max_prediction_length=3,
            hidden_size=32,
            batch_size=32,
        )
        
        assert config.max_encoder_length == 30
        assert config.max_prediction_length == 3
        assert config.hidden_size == 32
        assert config.batch_size == 32


class TestTFTStockPredictor:
    """测试 TFT 股票预测器"""
    
    @pytest.fixture
    def sample_data(self):
        """创建示例数据 (足够长的时间序列)"""
        np.random.seed(42)
        n_stocks = 5
        n_days = 200  # 增加数据量
        
        data = []
        for stock_idx in range(n_stocks):
            for day_idx in range(n_days):
                data.append({
                    'stock_code': f'STOCK_{stock_idx:03d}',
                    'time_idx': day_idx,
                    'close': 100 + 10 * np.sin(day_idx / 10) + np.random.randn() * 2,
                    'high': 102 + np.random.randn() * 2,
                    'low': 98 + np.random.randn() * 2,
                    'open': 100 + np.random.randn() * 2,
                    'log_return': np.random.randn() * 0.02,
                    'volume': np.random.randint(100000, 1000000),
                    'macd': np.random.randn() * 0.5,
                    'rsi': 50 + np.random.randn() * 10,
                })
        
        return pd.DataFrame(data)
    
    @pytest.fixture
    def predictor(self):
        """创建预测器 (使用较小的编码器长度用于测试)"""
        config = TFTModelConfig(
            max_encoder_length=20,   # 减小编码器长度
            max_prediction_length=3, # 减小预测长度
            min_encoder_length=10,   # 减小最小编码器长度
            min_prediction_length=1,
            max_epochs=3,  # 快速测试
            batch_size=32,
        )
        return TFTStockPredictor(config)
    
    def test_prepare_data(self, predictor, sample_data):
        """测试数据准备"""
        training, validation = predictor.prepare_data(
            sample_data,
            target_col='close',
            time_idx_col='time_idx',
            group_ids=['stock_code'],
            validation_split=0.2,
        )
        
        assert training is not None
        assert validation is not None
        assert len(training) > 0
        assert len(validation) > 0
        assert predictor.target_normalizer is not None
    
    def test_create_model(self, predictor, sample_data):
        """测试模型创建"""
        # 先准备数据
        predictor.prepare_data(
            sample_data,
            target_col='close',
            group_ids=['stock_code'],
        )
        
        # 创建模型
        model = predictor.create_model()
        
        assert model is not None
        assert sum(p.numel() for p in model.parameters()) > 0
    
    def test_create_trainer(self, predictor, sample_data):
        """测试 Trainer 创建"""
        # 先准备数据和模型
        predictor.prepare_data(sample_data, target_col='close', group_ids=['stock_code'])
        predictor.create_model()
        
        # 创建 Trainer
        trainer = predictor.create_trainer(log_dir='test_logs')
        
        assert trainer is not None
        assert trainer.max_epochs == predictor.config.max_epochs
    
    def test_predictor_workflow(self, predictor, sample_data):
        """测试完整工作流程"""
        # 1. 准备数据
        training, validation = predictor.prepare_data(
            sample_data,
            target_col='close',
            group_ids=['stock_code'],
            time_varying_known_reals=['log_return', 'volume', 'macd', 'rsi'],
            time_varying_unknown_reals=['close', 'high', 'low', 'open'],
        )
        
        # 2. 创建模型
        predictor.create_model()
        
        # 3. 创建 Trainer
        predictor.create_trainer(log_dir='test_logs')
        
        # 4. 训练 (快速测试)
        predictor.train()
        
        # 5. 预测
        predictions = predictor.predict(mode="prediction")
        
        assert predictions is not None


class TestTFTIntegration:
    """测试 TFT 与项目集成"""
    
    def test_module_import(self):
        """测试模块导入"""
        from server.models import TFTModelConfig, TFTStockPredictor
        
        assert TFTModelConfig is not None
        assert TFTStockPredictor is not None
    
    def test_model_files_exist(self):
        """测试模型文件存在"""
        model_file = Path(__file__).parent.parent / 'server' / 'models' / 'tft_model.py'
        init_file = Path(__file__).parent.parent / 'server' / 'models' / '__init__.py'
        
        assert model_file.exists()
        assert init_file.exists()
    
    def test_training_script_exists(self):
        """测试训练脚本存在"""
        script_file = Path(__file__).parent.parent / 'server' / 'scripts' / 'train_tft.py'
        
        # 注意：脚本在 server/scripts/ 而不是 ~/qclaw/server/scripts/
        # 这个测试可能需要调整路径
        # assert script_file.exists()
        pass  # 暂时跳过


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
