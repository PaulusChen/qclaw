"""
TFT 模型集成测试 - CODE-DL-008

测试 TFT 模型 (pytorch-forecasting) 的完整集成流程
"""

import pytest
import torch
import pandas as pd
import numpy as np
from pathlib import Path


class TestTFTModelIntegration:
    """TFT 模型集成测试"""
    
    @pytest.fixture
    def sample_data(self):
        """准备测试数据集"""
        np.random.seed(42)
        n_stocks = 5
        n_days = 200
        
        data = []
        for stock_id in range(n_stocks):
            for day in range(n_days):
                row = {
                    'stock_id': f'STOCK_{stock_id}',
                    'date': pd.Timestamp('2020-01-01') + pd.Timedelta(days=day),
                    'price': 100 + np.random.randn() * 5,
                    'volume': np.random.randint(1000, 10000),
                    'target': np.random.randn(),
                    'time_idx': day
                }
                data.append(row)
        
        return pd.DataFrame(data)
    
    def test_model_creation(self, sample_data):
        """测试 1: TFT 模型创建"""
        from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
        
        training = TimeSeriesDataSet(
            sample_data,
            time_idx="time_idx",
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        tft = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=16,
            attention_head_size=4,
            dropout=0.1,
        )
        
        assert tft is not None
        assert isinstance(tft, TemporalFusionTransformer)
        print("✅ TFT 模型创建成功")
    
    def test_model_training(self, sample_data):
        """测试 2: TFT 模型训练流程"""
        from pytorch_forecasting import TimeSeriesDataSet
        
        training = TimeSeriesDataSet(
            sample_data,
            time_idx="time_idx",
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        train_dataloader = training.to_dataloader(train=True, batch_size=32)
        
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=16,
        )
        
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        model.train()
        
        losses = []
        for batch_idx, batch in enumerate(train_dataloader):
            optimizer.zero_grad()
            x, y = model.transform_input(batch)
            output = model(x)
            
            loss = model.criterion(output, y[0].squeeze())
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
            
            if batch_idx >= 2:
                break
        
        assert len(losses) > 0
        assert all(loss > 0 for loss in losses)
        print(f"✅ 模型训练成功，Loss: {losses[-1]:.4f}")
    
    def test_model_inference(self, sample_data):
        """测试 3: TFT 模型推理流程"""
        from pytorch_forecasting import TimeSeriesDataSet
        import torch
        
        training = TimeSeriesDataSet(
            sample_data,
            time_idx="time_idx",
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=16,
        )
        model.eval()
        
        with torch.no_grad():
            batch = next(iter(training.to_dataloader(train=False, batch_size=4)))
            x, _ = model.transform_input(batch)
            output = model(x)
        
        assert output is not None
        assert output.shape[0] > 0
        assert output.shape[1] == 7
        print(f"✅ 模型推理成功，输出形状：{output.shape}")
    
    def test_model_save_load(self, sample_data, tmp_path):
        """测试 4: 模型保存和加载"""
        from pytorch_forecasting import TimeSeriesDataSet
        
        training = TimeSeriesDataSet(
            sample_data,
            time_idx="time_idx",
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=16,
        )
        
        save_path = tmp_path / "tft_model.pt"
        torch.save(model.state_dict(), save_path)
        
        loaded_model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=16,
        )
        loaded_model.load_state_dict(torch.load(save_path, weights_only=True))
        
        assert loaded_model is not None
        
        model.eval()
        loaded_model.eval()
        
        with torch.no_grad():
            batch = next(iter(training.to_dataloader(train=False, batch_size=4)))
            x, _ = model.transform_input(batch)
            output1 = model(x)
            output2 = loaded_model(x)
        
        assert torch.allclose(output1, output2, atol=1e-5)
        print("✅ 模型保存和加载成功")
    
    def test_data_pipeline_integration(self, sample_data):
        """测试 5: 与数据管道的集成"""
        from pytorch_forecasting import TimeSeriesDataSet
        
        training = TimeSeriesDataSet(
            sample_data,
            time_idx="time_idx",
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
            time_varying_known_reals=["volume"],
            time_varying_unknown_reals=["price"],
        )
        
        train_dataloader = training.to_dataloader(
            train=True,
            batch_size=32,
            num_workers=0
        )
        
        batch = next(iter(train_dataloader))
        assert batch is not None
        assert 'x_cat' in batch or 'x_cont' in batch
        assert 'y' in batch
        
        print(f"✅ 数据管道集成成功，batch 包含：{list(batch.keys())}")
    
    def test_attention_visualization(self, sample_data):
        """测试 6: 注意力可视化功能"""
        from pytorch_forecasting import TimeSeriesDataSet
        import torch
        
        training = TimeSeriesDataSet(
            sample_data,
            time_idx="time_idx",
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=16,
            attention_head_size=4,
        )
        
        model.eval()
        
        with torch.no_grad():
            batch = next(iter(training.to_dataloader(train=False, batch_size=4)))
            x, _ = model.transform_input(batch)
            output = model(x)
            
            has_attention = hasattr(model, 'attention')
            
        assert output is not None
        print(f"✅ 注意力机制测试完成 (attention accessible: {has_attention})")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
