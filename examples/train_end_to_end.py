#!/usr/bin/env python3
"""
端到端训练流程示例

演示从数据加载到模型训练的完整流程:
1. 数据加载与预处理
2. 特征工程
3. 数据集创建
4. 模型训练
5. 模型保存
6. 训练日志记录

使用方法:
    python examples/train_end_to_end.py --config config/end_to_end_config.yaml
"""

import argparse
import yaml
import torch
import torch.nn as nn
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
import json

# 添加项目根目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prediction.data.dataset import StockDataset, create_dataloader
from src.prediction.data.preprocessing import FeaturePreprocessor
from src.prediction.train import Trainer, create_trainer
from src.prediction.models.lstm import LSTMPredictor
from src.prediction.models.transformer import TransformerPredictor


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_synthetic_data(n_samples: int = 5000, seq_len: int = 60, n_features: int = 25):
    """
    生成合成数据用于演示
    
    在实际使用中，这里应该替换为真实的数据加载逻辑
    """
    np.random.seed(42)
    
    # 生成 OHLCV 基础数据
    n_ohlcv = 5
    base_features = np.random.randn(n_samples, seq_len, n_ohlcv).astype(np.float32)
    
    # 模拟价格序列 (确保价格为正且连续)
    close_prices = np.cumsum(np.abs(base_features[:, :, 0]) + 10, axis=1).astype(np.float32)
    open_prices = close_prices + np.random.randn(n_samples, seq_len).astype(np.float32) * 0.1
    high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.randn(n_samples, seq_len).astype(np.float32)) * 0.05
    low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.randn(n_samples, seq_len).astype(np.float32)) * 0.05
    volume = np.abs(np.random.randn(n_samples, seq_len).astype(np.float32)) * 1000000
    
    # 生成标签 (涨跌方向)
    direction = (close_prices[:, -1] > close_prices[:, -2]).astype(np.int64)
    
    # 生成收益率标签
    returns = (close_prices[:, -1] - close_prices[:, -2]) / close_prices[:, -2]
    
    # 生成置信度标签
    confidence = np.random.uniform(0.5, 1.0, n_samples).astype(np.float32)
    
    # 构建特征数组 (n_samples, seq_len, n_features)
    # 使用 OHLCV + 一些额外特征填充到 n_features
    features = np.stack([
        open_prices, high_prices, low_prices, close_prices, volume
    ], axis=-1)  # (n_samples, seq_len, 5)
    
    # 如果 n_features > 5，添加额外的随机特征
    if n_features > 5:
        extra_features = np.random.randn(n_samples, seq_len, n_features - 5).astype(np.float32)
        features = np.concatenate([features, extra_features], axis=-1)
    
    targets = {
        "direction": direction,
        "return": returns,
        "confidence": confidence,
    }
    
    return features, targets, n_samples, seq_len


def main():
    parser = argparse.ArgumentParser(description="端到端训练流程示例")
    parser.add_argument("--config", type=str, default="config/end_to_end_config.yaml",
                        help="配置文件路径")
    parser.add_argument("--output", type=str, default="results/training",
                        help="输出目录")
    parser.add_argument("--epochs", type=int, default=None,
                        help="训练轮数 (覆盖配置文件)")
    parser.add_argument("--demo", action="store_true",
                        help="使用合成数据进行快速演示")
    args = parser.parse_args()
    
    # 加载配置
    print("=" * 60)
    print("端到端训练流程示例")
    print("=" * 60)
    print(f"\n[1/6] 加载配置文件: {args.config}")
    config = load_config(args.config)
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[2/6] 输出目录：{output_dir}")
    
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[3/6] 使用设备：{device}")
    
    # 数据准备
    print(f"\n[4/6] 准备数据...")
    if args.demo:
        # 使用合成数据进行快速演示
        print("  → 使用合成数据 (演示模式)")
        seq_len = config["features"]["sequence_length"]
        n_features = config["model"]["lstm"]["input_size"]
        features, targets, n_samples, seq_len = generate_synthetic_data(n_samples=1000, seq_len=seq_len, n_features=n_features)
    else:
        # TODO: 实现真实数据加载
        print("  → 真实数据加载待实现")
        print("  → 切换到演示模式")
        seq_len = config["features"]["sequence_length"]
        n_features = config["model"]["lstm"]["input_size"]
        features, targets, n_samples, seq_len = generate_synthetic_data(n_samples=1000, seq_len=seq_len, n_features=n_features)
    
    # 数据预处理
    # 构建 DataFrame (预处理器需要 OHLCV 列名)
    # features shape: (n_samples, seq_len, n_features)
    # 假设前 5 列是 OHLCV
    df_data = pd.DataFrame({
        'open': features[:, :, 0].reshape(-1),
        'high': features[:, :, 1].reshape(-1),
        'low': features[:, :, 2].reshape(-1),
        'close': features[:, :, 3].reshape(-1),
        'volume': features[:, :, 4].reshape(-1),
    })
    
    # 添加额外特征列
    for i in range(5, n_features):
        df_data[f"feature_{i}"] = features[:, :, i].reshape(-1)
    
    feature_names = list(df_data.columns)
    
    preprocessor = FeaturePreprocessor(feature_columns=feature_names)
    preprocessor.fit(df_data)
    features_processed_df = preprocessor.transform(df_data)
    
    # 转换回 numpy 数组
    # 预处理器会添加衍生特征，并且可能会改变样本数 (由于 diff() 等操作)
    features_processed = np.array(features_processed_df)
    actual_n_features = features_processed.shape[1]
    total_rows = features_processed.shape[0]
    # 重新计算实际可用的样本数 (总行数 / 序列长度)
    actual_n_samples = total_rows // seq_len
    # 截断到完整的样本数
    features_processed = features_processed[:actual_n_samples * seq_len].reshape(actual_n_samples, seq_len, actual_n_features)
    print(f"  → 实际特征数：{actual_n_features} (预处理器衍生)")
    print(f"  → 实际样本数：{actual_n_samples} (原始：{len(features)})")
    
    # 数据集划分
    n_samples = actual_n_samples
    train_size = int(n_samples * config["training"]["split"]["train"])
    val_size = int(n_samples * config["training"]["split"]["validation"])
    test_size = n_samples - train_size - val_size
    
    train_features = features_processed[:train_size]
    val_features = features_processed[train_size:train_size + val_size]
    test_features = features_processed[train_size + val_size:]
    
    # 调整 targets 以匹配实际样本数 (由于预处理器可能改变样本数)
    targets_adjusted = {k: v[:n_samples] for k, v in targets.items()}
    train_targets = {k: v[:train_size] for k, v in targets_adjusted.items()}
    val_targets = {k: v[train_size:train_size + val_size] for k, v in targets_adjusted.items()}
    test_targets = {k: v[train_size + val_size:] for k, v in targets_adjusted.items()}
    
    print(f"  → 训练集：{len(train_features)} 样本")
    print(f"  → 验证集：{len(val_features)} 样本")
    print(f"  → 测试集：{len(test_features)} 样本")
    
    # 创建数据加载器
    train_dataset = StockDataset(train_features, train_targets)
    val_dataset = StockDataset(val_features, val_targets)
    
    train_loader = create_dataloader(
        train_dataset,
        batch_size=config["training"]["batch_size"],
        shuffle=True,
        num_workers=config["common"]["num_workers"]
    )
    val_loader = create_dataloader(
        val_dataset,
        batch_size=config["training"]["batch_size"],
        shuffle=False,
        num_workers=config["common"]["num_workers"]
    )
    
    # 创建训练器
    print(f"\n[5/6] 创建训练器...")
    epochs = args.epochs or config["training"]["epochs"]
    
    trainer = create_trainer(
        model_type=config["model"]["type"],
        input_size=actual_n_features,  # 使用实际特征数
        hidden_size=config["model"]["lstm"]["hidden_size"],
        learning_rate=config["training"]["learning_rate"],
        weight_decay=config["training"]["weight_decay"],
        multi_task=config["model"]["multi_task"]["enabled"],
        device=device,
        checkpoint_dir=str(output_dir / "checkpoints"),
    )
    
    print(f"  → 模型类型：{config['model']['type']}")
    print(f"  → 隐藏层维度：{config['model']['lstm']['hidden_size']}")
    print(f"  → 多任务学习：{config['model']['multi_task']['enabled']}")
    print(f"  → 训练轮数：{epochs}")
    
    # 开始训练
    print(f"\n[6/6] 开始训练...")
    print("-" * 60)
    
    start_time = datetime.now()
    result = trainer.train(
        train_loader,
        val_loader,
        epochs=epochs,
        log_interval=config["training"]["log_interval"]
    )
    end_time = datetime.now()
    
    print("-" * 60)
    print(f"\n训练完成!")
    print(f"  → 最佳验证准确率：{result['best_metric']:.4f}")
    print(f"  → 总训练轮数：{result['total_epochs']}")
    print(f"  → 总训练时间：{result['total_time']:.1f}秒 ({(end_time - start_time).total_seconds() / 60:.1f}分钟)")
    
    # 保存训练日志
    log_path = output_dir / "training_log.json"
    trainer.save_training_log(str(log_path))
    print(f"  → 训练日志已保存：{log_path}")
    
    # 保存训练摘要
    summary = {
        "timestamp": datetime.now().isoformat(),
        "config_file": args.config,
        "model_type": config["model"]["type"],
        "epochs": epochs,
        "best_metric": result["best_metric"],
        "total_epochs": result["total_epochs"],
        "total_time_seconds": result["total_time"],
        "device": str(device),
    }
    
    summary_path = output_dir / "training_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  → 训练摘要已保存：{summary_path}")
    
    print("\n" + "=" * 60)
    print("端到端训练流程完成!")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    main()
