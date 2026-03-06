#!/usr/bin/env python3
"""
端到端推理流程示例

演示从实时数据到预测结果的完整流程:
1. 实时数据获取
2. 数据预处理
3. 模型加载
4. 预测推理
5. 结果后处理
6. 预测输出

使用方法:
    python examples/predict_end_to_end.py --checkpoint checkpoints/best_model.pt --config config/end_to_end_config.yaml
"""

import argparse
import yaml
import torch
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import time

# 添加项目根目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prediction.data.preprocessing import FeaturePreprocessor
from src.prediction.models.checkpoint import ModelCheckpoint
from src.prediction.models.lstm import LSTMPredictor
from src.prediction.models.transformer import TransformerPredictor


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_model(checkpoint_path: str, device: torch.device) -> tuple:
    """
    加载模型检查点
    
    返回:
        model: 模型实例
        config: 模型配置
    """
    checkpoint_mgr = ModelCheckpoint(Path(checkpoint_path).parent)
    
    # 加载检查点
    checkpoint_data = checkpoint_mgr.load_checkpoint(checkpoint_path)
    
    model_config = checkpoint_data.get("config", {})
    model_type = model_config.get("model_type", "lstm")
    
    # 创建模型
    if model_type == "lstm":
        model = LSTMPredictor(
            input_size=model_config.get("input_size", 25),
            hidden_size=model_config.get("hidden_size", 128),
        )
    elif model_type == "transformer":
        model = TransformerPredictor(
            input_size=model_config.get("input_size", 25),
            d_model=model_config.get("d_model", 128),
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # 加载权重
    model.load_state_dict(checkpoint_data["model_state_dict"])
    model.to(device)
    model.eval()
    
    print(f"  → 模型类型：{model_type}")
    print(f"  → 检查点 epoch: {checkpoint_data.get('epoch', 'N/A')}")
    print(f"  → 检查点指标：{checkpoint_data.get('metric', 'N/A'):.4f}")
    
    return model, model_config


def generate_realtime_features(seq_len: int = 60, n_features: int = 25) -> np.ndarray:
    """
    生成实时特征数据 (模拟)
    
    在实际使用中，这里应该替换为真实的数据获取逻辑
    """
    np.random.seed(int(time.time()) % 10000)
    
    # 生成最新的市场数据特征
    features = np.random.randn(1, seq_len, n_features).astype(np.float32)
    
    return features


def preprocess_features(features: np.ndarray, preprocessor: FeaturePreprocessor) -> np.ndarray:
    """预处理特征"""
    return preprocessor.transform(features)


def predict(model: torch.nn.Module, features: torch.Tensor, device: torch.device, multi_task: bool = True) -> dict:
    """
    执行预测
    
    参数:
        model: 模型
        features: 输入特征
        device: 计算设备
        multi_task: 是否多任务预测
        
    返回:
        预测结果字典
    """
    with torch.no_grad():
        features = features.to(device)
        
        # 前向传播
        features_out = model(features)
        
        if multi_task and hasattr(model, "head"):
            predictions = model.head(features_out)
            
            # 方向预测
            direction_pred = predictions["direction"].argmax(dim=1).cpu().numpy()[0]
            direction_prob = torch.softmax(predictions["direction"], dim=1)[0, direction_pred].item()
            
            # 收益率预测
            return_pred = predictions["return"].cpu().numpy()[0]
            
            # 置信度预测
            confidence_pred = predictions["confidence"].cpu().numpy()[0]
            
            result = {
                "direction": int(direction_pred),
                "direction_label": "上涨" if direction_pred == 1 else "下跌",
                "direction_probability": float(direction_prob),
                "expected_return": float(return_pred),
                "confidence": float(confidence_pred),
            }
        else:
            # 单任务模式
            outputs = model(features)
            direction_pred = outputs.argmax(dim=1).cpu().numpy()[0]
            direction_prob = torch.softmax(outputs, dim=1)[0, direction_pred].item()
            
            result = {
                "direction": int(direction_pred),
                "direction_label": "上涨" if direction_pred == 1 else "下跌",
                "direction_probability": float(direction_prob),
            }
    
    return result


def postprocess_prediction(prediction: dict, config: dict) -> dict:
    """
    后处理预测结果
    
    包括:
    - 平滑处理
    - 阈值过滤
    - 信号生成
    """
    result = prediction.copy()
    
    # 基于置信度生成交易信号
    threshold = config["inference"]["postprocessing"]["threshold"]
    
    if prediction["direction_probability"] >= threshold:
        if prediction["direction"] == 1:
            result["signal"] = "BUY"
            result["signal_strength"] = "STRONG" if prediction["direction_probability"] > 0.7 else "MODERATE"
        else:
            result["signal"] = "SELL"
            result["signal_strength"] = "STRONG" if prediction["direction_probability"] > 0.7 else "MODERATE"
    else:
        result["signal"] = "HOLD"
        result["signal_strength"] = "WEAK"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="端到端推理流程示例")
    parser.add_argument("--checkpoint", type=str, required=True,
                        help="模型检查点路径")
    parser.add_argument("--config", type=str, default="config/end_to_end_config.yaml",
                        help="配置文件路径")
    parser.add_argument("--output", type=str, default="results/predictions",
                        help="输出目录")
    parser.add_argument("--batch", action="store_true",
                        help="批量预测模式")
    parser.add_argument("--n-samples", type=int, default=10,
                        help="批量预测样本数")
    parser.add_argument("--timing", action="store_true",
                        help="显示推理延迟")
    args = parser.parse_args()
    
    # 加载配置
    print("=" * 60)
    print("端到端推理流程示例")
    print("=" * 60)
    print(f"\n[1/5] 加载配置文件: {args.config}")
    config = load_config(args.config)
    
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[2/5] 使用设备：{device}")
    
    # 加载模型
    print(f"\n[3/5] 加载模型检查点：{args.checkpoint}")
    model, model_config = load_model(args.checkpoint, device)
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 数据预处理 (在实际使用中，preprocessor 应该从训练时保存)
    preprocessor = FeaturePreprocessor()
    # 注意：实际使用时应该加载训练时保存的 preprocessor
    
    # 推理
    print(f"\n[4/5] 执行推理...")
    
    seq_len = config["features"]["sequence_length"]
    n_features = config["model"]["lstm"]["input_size"]
    multi_task = config["model"]["multi_task"]["enabled"]
    
    if args.batch:
        # 批量预测
        print(f"  → 批量预测模式：{args.n_samples} 样本")
        predictions = []
        
        total_time = 0
        for i in range(args.n_samples):
            # 生成实时特征
            features = generate_realtime_features(seq_len=seq_len, n_features=n_features)
            features_processed = preprocess_features(features, preprocessor)
            features_tensor = torch.from_numpy(features_processed).float()
            
            # 计时
            start_time = time.time()
            prediction = predict(model, features_tensor, device, multi_task=multi_task)
            inference_time = time.time() - start_time
            total_time += inference_time
            
            # 后处理
            prediction = postprocess_prediction(prediction, config)
            prediction["inference_time_ms"] = inference_time * 1000
            prediction["sample_id"] = i
            predictions.append(prediction)
        
        avg_time = total_time / args.n_samples * 1000
        print(f"  → 平均推理延迟：{avg_time:.2f}ms")
        
        # 保存结果
        results_path = output_dir / "batch_predictions.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "n_samples": args.n_samples,
                "avg_inference_time_ms": avg_time,
                "predictions": predictions,
            }, f, indent=2, ensure_ascii=False)
        print(f"  → 批量预测结果已保存：{results_path}")
        
    else:
        # 单条预测
        print("  → 单条预测模式")
        
        # 生成实时特征
        features = generate_realtime_features(seq_len=seq_len, n_features=n_features)
        features_processed = preprocess_features(features, preprocessor)
        features_tensor = torch.from_numpy(features_processed).float()
        
        # 计时
        if args.timing:
            start_time = time.time()
        
        prediction = predict(model, features_tensor, device, multi_task=multi_task)
        
        if args.timing:
            inference_time = time.time() - start_time
            prediction["inference_time_ms"] = inference_time * 1000
            print(f"  → 推理延迟：{inference_time * 1000:.2f}ms")
        
        # 后处理
        prediction = postprocess_prediction(prediction, config)
        
        # 打印结果
        print(f"\n[5/5] 预测结果:")
        print("-" * 60)
        print(f"  方向：{prediction['direction_label']} (概率：{prediction['direction_probability']:.2%})")
        if "expected_return" in prediction:
            print(f"  预期收益率：{prediction['expected_return']:.4f}")
        if "confidence" in prediction:
            print(f"  置信度：{prediction['confidence']:.4f}")
        print(f"  交易信号：{prediction['signal']} ({prediction['signal_strength']})")
        if "inference_time_ms" in prediction:
            print(f"  推理延迟：{prediction['inference_time_ms']:.2f}ms")
        print("-" * 60)
        
        # 保存结果
        results_path = output_dir / "prediction.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "prediction": prediction,
            }, f, indent=2, ensure_ascii=False)
        print(f"  → 预测结果已保存：{results_path}")
    
    print("\n" + "=" * 60)
    print("端到端推理流程完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
