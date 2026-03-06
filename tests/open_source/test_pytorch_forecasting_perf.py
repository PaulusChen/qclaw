#!/usr/bin/env python3
"""
pytorch-forecasting 性能测试 - OPEN-001.2
测试性能指标：训练速度、推理延迟、显存占用、模型大小、预测准确率
"""

import numpy as np
import pandas as pd
import torch
import time
import os
from pytorch_forecasting import (
    TemporalFusionTransformer,
    TimeSeriesDataSet,
)
from pytorch_forecasting.metrics import RMSE, MAE
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("pytorch-forecasting 性能测试 - OPEN-001.2")
print("=" * 60)

# ============================================================
# 1. 准备性能测试数据集
# ============================================================
print("\n[1/5] 准备性能测试数据集...")

np.random.seed(42)
n_stocks = 50  # 50 股票
n_days = 500   # 500 天 (~2 年)
n_features = 15

data_list = []
for stock_id in range(n_stocks):
    for day in range(n_days):
        row = {
            'stock_id': f'stock_{stock_id}',
            'time_idx': day,
            'date': pd.Timestamp('2023-01-01') + pd.Timedelta(days=day),
            'target': np.random.randn() * 0.02 + 0.0005 * day,  # 收益率
        }
        for i in range(5):
            row[f'static_feat_{i}'] = np.random.randn()
        for i in range(n_features):
            row[f'feat_{i}'] = np.random.randn()
        data_list.append(row)

data = pd.DataFrame(data_list)
print(f"✅ 数据集大小：{len(data):,} 行 ({n_stocks} 股票 × {n_days} 天)")

# 创建数据集
max_encoder_length = 60
max_prediction_length = 14

training = TimeSeriesDataSet(
    data[lambda x: x.time_idx < 400],
    time_idx='time_idx',
    target='target',
    group_ids=['stock_id'],
    static_reals=[f'static_feat_{i}' for i in range(5)],
    time_varying_known_reals=[f'feat_{i}' for i in range(n_features)],
    time_varying_unknown_reals=['target'],
    max_encoder_length=max_encoder_length,
    max_prediction_length=max_prediction_length,
    allow_missing_timesteps=True,
)

validation = TimeSeriesDataSet.from_dataset(
    training,
    data[lambda x: x.time_idx >= 400],
    predict=True,
)

batch_size = 64
train_dataloader = training.to_dataloader(train=True, batch_size=batch_size)
val_dataloader = validation.to_dataloader(train=False, batch_size=batch_size)

print(f"✅ 训练集：{len(training):,} samples")
print(f"✅ 验证集：{len(validation):,} samples")

# ============================================================
# 2. 训练速度测试
# ============================================================
print("\n[2/5] 训练速度测试...")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"   设备：{device}")

model = TemporalFusionTransformer.from_dataset(
    training,
    learning_rate=0.001,
    hidden_size=64,
    attention_head_size=8,
    dropout=0.1,
    hidden_continuous_size=32,
    output_size=1,
    loss=RMSE(),
)
model = model.to(device)

# 训练速度测试
print("   开始训练速度测试 (5 epochs)...")
trainer = torch.optim.Adam(model.parameters(), lr=0.001)

total_samples = 0
start_time = time.time()

for epoch in range(5):
    model.train()
    epoch_samples = 0
    for batch in train_dataloader:
        x, y = batch
        x = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in x.items()}
        target = y[0].to(device) if isinstance(y, tuple) else y.to(device)
        
        output = model(x)
        pred = output.prediction.squeeze(-1)
        loss = torch.mean((pred - target) ** 2)
        
        trainer.zero_grad()
        loss.backward()
        trainer.step()
        epoch_samples += target.shape[0]
    
    total_samples += epoch_samples
    elapsed = time.time() - start_time
    samples_per_sec = total_samples / elapsed
    print(f"   Epoch {epoch+1}/5 - Samples: {epoch_samples:,}, 速度：{samples_per_sec:.1f} samples/sec")

training_speed = total_samples / (time.time() - start_time)
print(f"\n✅ 训练速度：{training_speed:.1f} samples/sec (目标：>100)")

# ============================================================
# 3. 推理延迟测试
# ============================================================
print("\n[3/5] 推理延迟测试...")

model.eval()
latencies = []

with torch.no_grad():
    for i, batch in enumerate(val_dataloader):
        if i >= 10:  # 测试 10 个批次
            break
        x, y = batch
        x = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in x.items()}
        
        start = time.time()
        output = model(x)
        elapsed = time.time() - start
        latencies.append(elapsed * 1000)  # ms

avg_latency = np.mean(latencies)
std_latency = np.std(latencies)
samples_per_batch = batch_size
latency_per_sample = avg_latency / samples_per_batch * 1000  # ms/sample

print(f"✅ 平均推理延迟：{avg_latency:.2f} ms/batch")
print(f"✅ 单样本延迟：{latency_per_sample:.3f} ms/sample (目标：<50ms)")

# ============================================================
# 4. 模型大小测试
# ============================================================
print("\n[4/5] 模型大小测试...")

# 保存模型
model_path = '/tmp/tft_model.pth'
torch.save(model.state_dict(), model_path)
model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
print(f"✅ 模型大小：{model_size_mb:.2f} MB")

# 计算参数量
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"✅ 总参数量：{total_params:,}")
print(f"✅ 可训练参数：{trainable_params:,}")

os.remove(model_path)

# ============================================================
# 5. 预测准确率测试
# ============================================================
print("\n[5/5] 预测准确率测试...")

model.eval()
all_predictions = []
all_targets = []

with torch.no_grad():
    for batch in val_dataloader:
        x, y = batch
        x = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in x.items()}
        target = y[0].cpu() if isinstance(y, tuple) else y.cpu()
        
        output = model(x)
        pred = output.prediction.squeeze(-1).cpu()
        
        all_predictions.append(pred)
        all_targets.append(target)

all_predictions = torch.cat(all_predictions, dim=0)
all_targets = torch.cat(all_targets, dim=0)

# 计算指标
mse = torch.mean((all_predictions - all_targets) ** 2).item()
rmse = np.sqrt(mse)
mae = torch.mean(torch.abs(all_predictions - all_targets)).item()

print(f"✅ MSE: {mse:.6f} (目标：<0.030)")
print(f"✅ RMSE: {rmse:.6f}")
print(f"✅ MAE: {mae:.6f}")

# 方向准确率
pred_direction = torch.sign(all_predictions)
target_direction = torch.sign(all_targets)
direction_accuracy = (pred_direction == target_direction).float().mean().item()
print(f"✅ 方向准确率：{direction_accuracy:.2%}")

# ============================================================
# 性能评估总结
# ============================================================
print("\n" + "=" * 60)
print("性能测试结果汇总")
print("=" * 60)

results = {
    "训练速度": f"{training_speed:.1f} samples/sec",
    "推理延迟": f"{latency_per_sample:.3f} ms/sample",
    "模型大小": f"{model_size_mb:.2f} MB",
    "参数量": f"{total_params:,}",
    "MSE": f"{mse:.6f}",
    "RMSE": f"{rmse:.6f}",
    "MAE": f"{mae:.6f}",
    "方向准确率": f"{direction_accuracy:.2%}",
}

for metric, value in results.items():
    print(f"  {metric}: {value}")

# 评估结论
print("\n" + "=" * 60)
print("评估结论")
print("=" * 60)

pass_training = training_speed > 100
pass_latency = latency_per_sample < 50
pass_mse = mse < 0.030

print(f"  训练速度 (>100 samples/sec): {'✅ 通过' if pass_training else '❌ 未通过'}")
print(f"  推理延迟 (<50ms/sample): {'✅ 通过' if pass_latency else '❌ 未通过'}")
print(f"  MSE (<0.030): {'✅ 通过' if pass_mse else '❌ 未通过'}")

overall = pass_training and pass_latency and pass_mse
print(f"\n  总体评估：{'✅ 推荐使用' if overall else '⚠️ 需要优化'}")

print("\n" + "=" * 60)
print("✅ OPEN-001.2 性能测试完成")
print("=" * 60)
