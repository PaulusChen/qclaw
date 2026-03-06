"""
TFT 模型性能测试 - TEST-DL-001

测试 TFT 模型的性能指标
"""

import pytest
import torch
import pandas as pd
import numpy as np
import time
from pathlib import Path


class TestTFTPerformance:
    """TFT 模型性能测试"""
    
    @pytest.fixture
    def large_dataset(self):
        """准备大型测试数据集"""
        np.random.seed(42)
        n_stocks = 50
        n_days = 500
        
        data = []
        for stock_id in range(n_stocks):
            for day in range(n_days):
                row = {
                    'stock_id': f'STOCK_{stock_id}',
                    'date': pd.Timestamp('2020-01-01') + pd.Timedelta(days=day),
                    'price': 100 + np.random.randn() * 5,
                    'volume': np.random.randint(1000, 10000),
                    'target': np.random.randn()
                }
                data.append(row)
        
        return pd.DataFrame(data)
    
    def test_training_speed(self, large_dataset):
        """测试 1: 训练速度"""
        from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
        from torch.utils.data import DataLoader
        
        # 创建数据集
        training = TimeSeriesDataSet(
            large_dataset,
            time_idx=large_dataset.index,
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        train_dataloader = training.to_dataloader(train=True, batch_size=32)
        
        # 创建模型
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=32,
        )
        
        # 训练速度测试
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        model.train()
        
        start_time = time.time()
        samples_processed = 0
        
        for batch_idx, batch in enumerate(train_dataloader):
            optimizer.zero_grad()
            x, y = model.transform_input(batch)
            output = model(x)
            
            loss = model.criterion(output, y[0].squeeze())
            loss.backward()
            optimizer.step()
            
            samples_processed += len(batch[0])
            
            if batch_idx >= 50:  # 训练 50 个 batch
                break
        
        elapsed_time = time.time() - start_time
        samples_per_sec = samples_processed / elapsed_time
        
        print(f"✅ 训练速度：{samples_per_sec:.1f} samples/sec (目标 > 100)")
        assert samples_per_sec > 100, f"训练速度 {samples_per_sec:.1f} < 100 samples/sec"
    
    def test_inference_latency(self, large_dataset):
        """测试 2: 推理延迟"""
        from pytorch_forecasting import TimeSeriesDataSet
        import torch
        
        # 创建数据集
        training = TimeSeriesDataSet(
            large_dataset,
            time_idx=large_dataset.index,
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        # 创建模型
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=32,
        )
        model.eval()
        
        # 推理延迟测试
        latencies = []
        
        with torch.no_grad():
            for i in range(10):
                batch = next(iter(training.to_dataloader(train=False, batch_size=32)))
                
                start_time = time.time()
                x, _ = model.transform_input(batch)
                output = model(x)
                elapsed_time = time.time() - start_time
                
                latencies.append(elapsed_time * 1000)  # 转换为 ms
        
        avg_latency = np.mean(latencies)
        print(f"✅ 推理延迟：{avg_latency:.2f}ms (目标 < 50ms)")
        assert avg_latency < 50, f"推理延迟 {avg_latency:.2f}ms > 50ms"
    
    def test_prediction_accuracy(self, large_dataset):
        """测试 3: 预测准确率 (MSE)"""
        from pytorch_forecasting import TimeSeriesDataSet
        import torch
        
        # 创建数据集
        training = TimeSeriesDataSet(
            large_dataset,
            time_idx=large_dataset.index,
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        train_dataloader = training.to_dataloader(train=True, batch_size=32)
        
        # 创建模型
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=32,
        )
        
        # 训练模型
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        model.train()
        
        for epoch in range(3):
            for batch in train_dataloader:
                optimizer.zero_grad()
                x, y = model.transform_input(batch)
                output = model(x)
                
                loss = model.criterion(output, y[0].squeeze())
                loss.backward()
                optimizer.step()
        
        # 测试 MSE
        model.eval()
        mse_losses = []
        
        with torch.no_grad():
            for batch in training.to_dataloader(train=False, batch_size=32):
                x, y = model.transform_input(batch)
                output = model(x)
                
                mse = torch.nn.functional.mse_loss(output, y[0].squeeze())
                mse_losses.append(mse.item())
        
        avg_mse = np.mean(mse_losses)
        print(f"✅ MSE: {avg_mse:.6f} (目标 < 0.030)")
        assert avg_mse < 0.030, f"MSE {avg_mse:.6f} > 0.030"
    
    def test_direction_accuracy(self, large_dataset):
        """测试 4: 方向准确率"""
        from pytorch_forecasting import TimeSeriesDataSet
        import torch
        
        # 创建数据集
        training = TimeSeriesDataSet(
            large_dataset,
            time_idx=large_dataset.index,
            target="target",
            group_ids=["stock_id"],
            max_encoder_length=10,
            max_prediction_length=7,
        )
        
        # 创建模型
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.01,
            hidden_size=32,
        )
        model.eval()
        
        # 方向准确率测试
        correct_predictions = 0
        total_predictions = 0
        
        with torch.no_grad():
            for batch in training.to_dataloader(train=False, batch_size=32):
                x, y = model.transform_input(batch)
                output = model(x)
                
                # 比较预测方向和实际方向
                pred_direction = torch.sign(output[:, 0, 0])  # 第一步预测
                actual_direction = torch.sign(y[0][:, 0, 0])  # 实际第一步
                
                correct_predictions += (pred_direction == actual_direction).sum().item()
                total_predictions += len(pred_direction)
        
        direction_accuracy = correct_predictions / total_predictions * 100
        print(f"✅ 方向准确率：{direction_accuracy:.1f}%")
        assert direction_accuracy > 40, f"方向准确率 {direction_accuracy:.1f}% 过低"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
