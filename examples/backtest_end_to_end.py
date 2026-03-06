#!/usr/bin/env python3
"""
端到端回测流程示例

演示从历史数据到回测报告的完整流程:
1. 历史数据加载
2. 特征工程
3. 模型加载
4. 逐日预测
5. 模拟交易
6. 性能评估
7. 回测报告生成

使用方法:
    python examples/backtest_end_to_end.py --checkpoint checkpoints/best_model.pt --config config/end_to_end_config.yaml
"""

import argparse
import yaml
import torch
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd

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
    """加载模型检查点"""
    checkpoint_mgr = ModelCheckpoint(Path(checkpoint_path).parent)
    checkpoint_data = checkpoint_mgr.load_checkpoint(checkpoint_path)
    
    model_config = checkpoint_data.get("config", {})
    model_type = model_config.get("model_type", "lstm")
    
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
    
    model.load_state_dict(checkpoint_data["model_state_dict"])
    model.to(device)
    model.eval()
    
    return model, model_config


def generate_historical_data(n_days: int = 250, seq_len: int = 60, n_features: int = 25):
    """
    生成历史数据 (模拟)
    
    实际使用中应替换为真实历史数据加载
    """
    np.random.seed(42)
    
    # 生成 OHLCV 数据
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(n_days)]
    
    # 生成价格序列 (随机游走)
    base_price = 100
    returns = np.random.randn(n_days) * 0.02
    prices = base_price * np.cumprod(1 + returns)
    
    # 生成特征
    features = np.random.randn(n_days, seq_len, n_features).astype(np.float32)
    
    # 生成真实涨跌标签
    actual_direction = (returns > 0).astype(np.int64)
    
    return {
        "dates": dates,
        "prices": prices,
        "returns": returns,
        "features": features,
        "actual_direction": actual_direction,
    }


def predict_daily(model: torch.nn.Module, features: np.ndarray, device: torch.device, 
                  multi_task: bool = True) -> dict:
    """执行单日预测"""
    with torch.no_grad():
        features_tensor = torch.from_numpy(features).float().unsqueeze(0).to(device)
        features_out = model(features_tensor)
        
        if multi_task and hasattr(model, "head"):
            predictions = model.head(features_out)
            direction_pred = predictions["direction"].argmax(dim=1).cpu().numpy()[0]
            direction_prob = torch.softmax(predictions["direction"], dim=1)[0, direction_pred].item()
            return_pred = predictions["return"].cpu().numpy()[0]
            confidence_pred = predictions["confidence"].cpu().numpy()[0]
            
            return {
                "direction": int(direction_pred),
                "probability": float(direction_prob),
                "expected_return": float(return_pred),
                "confidence": float(confidence_pred),
            }
        else:
            outputs = model(features_tensor)
            direction_pred = outputs.argmax(dim=1).cpu().numpy()[0]
            direction_prob = torch.softmax(outputs, dim=1)[0, direction_pred].item()
            
            return {
                "direction": int(direction_pred),
                "probability": float(direction_prob),
            }


def simulate_trading(predictions: List[dict], actual_returns: np.ndarray, 
                     config: dict) -> Dict[str, Any]:
    """
    模拟交易
    
    基于预测结果执行模拟交易，计算收益
    """
    initial_capital = config["backtest"]["initial_capital"]
    commission_rate = config["backtest"]["trading"]["commission_rate"]
    position_limit = config["backtest"]["trading"]["position_limit"]
    
    capital = initial_capital
    position = 0.0  # 当前持仓比例
    trades = []
    portfolio_values = [initial_capital]
    
    for i, (pred, actual_return) in enumerate(zip(predictions, actual_returns)):
        # 获取预测信号
        direction = pred.get("direction", 0)
        confidence = pred.get("confidence", pred.get("probability", 0.5))
        
        # 交易决策
        if direction == 1 and confidence > 0.6:  # 预测上涨，买入
            target_position = position_limit
        elif direction == 0 and confidence > 0.6:  # 预测下跌，卖出
            target_position = 0.0
        else:
            target_position = position  # 保持当前仓位
        
        # 计算交易
        position_change = target_position - position
        trade_amount = abs(position_change) * capital
        
        # 手续费
        commission = trade_amount * commission_rate
        
        # 更新持仓
        position = target_position
        
        # 计算当日收益
        daily_return = position * actual_return
        capital = capital * (1 + daily_return - commission / capital if capital > 0 else 1)
        
        portfolio_values.append(capital)
        
        if abs(position_change) > 0.01:  # 记录交易
            trades.append({
                "day": i,
                "action": "BUY" if position_change > 0 else "SELL",
                "position_change": position_change,
                "commission": commission,
            })
    
    return {
        "final_capital": capital,
        "total_return": (capital - initial_capital) / initial_capital,
        "portfolio_values": portfolio_values,
        "trades": trades,
        "n_trades": len(trades),
    }


def calculate_metrics(trading_result: dict, actual_returns: np.ndarray, 
                      predictions: List[dict], config: dict) -> Dict[str, float]:
    """
    计算回测评估指标
    """
    portfolio_values = np.array(trading_result["portfolio_values"])
    
    # 计算每日收益率
    daily_returns = np.diff(portfolio_values) / portfolio_values[:-1]
    
    # 年化收益率 (假设 252 个交易日)
    n_days = len(daily_returns)
    annual_return = (1 + trading_result["total_return"]) ** (252 / n_days) - 1
    
    # 夏普比率 (假设无风险利率为 3%)
    risk_free_rate = 0.03
    excess_returns = daily_returns - risk_free_rate / 252
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
    
    # 最大回撤
    cum_returns = np.cumprod(1 + daily_returns)
    running_max = np.maximum.accumulate(cum_returns)
    drawdowns = (cum_returns - running_max) / running_max
    max_drawdown = np.min(drawdowns)
    
    # 胜率
    correct_predictions = sum(
        1 for pred, actual in zip(predictions, actual_returns)
        if pred["direction"] == (1 if actual > 0 else 0)
    )
    win_rate = correct_predictions / len(predictions) if len(predictions) > 0 else 0
    
    # 盈亏比
    winning_trades = [t for t in trading_result["trades"] if t["action"] == "BUY"]
    losing_trades = [t for t in trading_result["trades"] if t["action"] == "SELL"]
    
    avg_win = np.mean([t["position_change"] for t in winning_trades]) if winning_trades else 0
    avg_loss = np.mean([t["position_change"] for t in losing_trades]) if losing_trades else 0
    profit_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
    
    # 波动率
    volatility = np.std(daily_returns) * np.sqrt(252)
    
    # Calmar 比率
    calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    return {
        "total_return": trading_result["total_return"],
        "annual_return": annual_return,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "profit_loss_ratio": profit_loss_ratio,
        "volatility": volatility,
        "calmar_ratio": calmar_ratio,
        "final_capital": trading_result["final_capital"],
        "initial_capital": config["backtest"]["initial_capital"],
        "n_trades": trading_result["n_trades"],
    }


def generate_report(metrics: dict, trading_result: dict, output_dir: Path):
    """生成回测报告"""
    report = {
        "report_type": "Backtest Report",
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "initial_capital": metrics["initial_capital"],
            "final_capital": metrics["final_capital"],
            "total_return": f"{metrics['total_return']:.2%}",
            "annual_return": f"{metrics['annual_return']:.2%}",
            "sharpe_ratio": f"{metrics['sharpe_ratio']:.2f}",
            "max_drawdown": f"{metrics['max_drawdown']:.2%}",
            "win_rate": f"{metrics['win_rate']:.2%}",
            "profit_loss_ratio": f"{metrics['profit_loss_ratio']:.2f}",
            "volatility": f"{metrics['volatility']:.2%}",
            "calmar_ratio": f"{metrics['calmar_ratio']:.2f}",
            "total_trades": metrics["n_trades"],
        },
        "trading_details": {
            "n_trades": trading_result["n_trades"],
            "sample_trades": trading_result["trades"][:10],  # 只显示前 10 笔交易
        },
    }
    
    # 保存 JSON 报告
    report_path = output_dir / "backtest_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 生成 Markdown 报告
    md_report = f"""# 回测报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 核心指标

| 指标 | 数值 |
|------|------|
| 初始资金 | ¥{metrics['initial_capital']:,.0f} |
| 最终资金 | ¥{metrics['final_capital']:,.0f} |
| **总收益率** | **{metrics['total_return']:.2%}** |
| **年化收益率** | **{metrics['annual_return']:.2%}** |
| 夏普比率 | {metrics['sharpe_ratio']:.2f} |
| 最大回撤 | {metrics['max_drawdown']:.2%} |
| 胜率 | {metrics['win_rate']:.2%} |
| 盈亏比 | {metrics['profit_loss_ratio']:.2f} |
| 波动率 | {metrics['volatility']:.2%} |
| Calmar 比率 | {metrics['calmar_ratio']:.2f} |
| 交易次数 | {metrics['n_trades']} |

---

## 📈 交易统计

- **总交易次数:** {trading_result['n_trades']}
- **平均每日交易:** {trading_result['n_trades'] / len(trading_result['portfolio_values']) * 252:.1f} (年化)

---

## 💡 评估

"""
    
    # 添加评估意见
    if metrics["sharpe_ratio"] > 1.5:
        md_report += "**夏普比率优秀!** 风险调整后收益表现良好。\n\n"
    elif metrics["sharpe_ratio"] > 1.0:
        md_report += "**夏普比率良好.** 风险调整后收益不错。\n\n"
    else:
        md_report += "**夏普比率一般.** 可能需要优化策略。\n\n"
    
    if abs(metrics["max_drawdown"]) < 0.15:
        md_report += "**最大回撤控制良好.** 风险控制有效。\n\n"
    else:
        md_report += "**最大回撤较大.** 建议加强风险控制。\n\n"
    
    if metrics["win_rate"] > 0.55:
        md_report += "**胜率较高.** 预测准确性不错。\n\n"
    else:
        md_report += "**胜率一般.** 可能需要改进预测模型。\n\n"
    
    md_report += "---\n\n*本报告由端到端回测流程自动生成.*\n"
    
    md_path = output_dir / "backtest_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    
    return report_path, md_path


def main():
    parser = argparse.ArgumentParser(description="端到端回测流程示例")
    parser.add_argument("--checkpoint", type=str, required=True,
                        help="模型检查点路径")
    parser.add_argument("--config", type=str, default="config/end_to_end_config.yaml",
                        help="配置文件路径")
    parser.add_argument("--output", type=str, default="results/backtest",
                        help="输出目录")
    parser.add_argument("--n-days", type=int, default=250,
                        help="回测天数")
    args = parser.parse_args()
    
    # 加载配置
    print("=" * 60)
    print("端到端回测流程示例")
    print("=" * 60)
    print(f"\n[1/6] 加载配置文件：{args.config}")
    config = load_config(args.config)
    
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[2/6] 使用设备：{device}")
    
    # 加载模型
    print(f"\n[3/6] 加载模型检查点：{args.checkpoint}")
    model, model_config = load_model(args.checkpoint, device)
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载历史数据
    print(f"\n[4/6] 加载历史数据...")
    seq_len = config["features"]["sequence_length"]
    n_features = config["model"]["lstm"]["input_size"]
    multi_task = config["model"]["multi_task"]["enabled"]
    
    data = generate_historical_data(n_days=args.n_days, seq_len=seq_len, n_features=n_features)
    print(f"  → 回测天数：{args.n_days}")
    print(f"  → 日期范围：{data['dates'][0].strftime('%Y-%m-%d')} 至 {data['dates'][-1].strftime('%Y-%m-%d')}")
    
    # 数据预处理
    preprocessor = FeaturePreprocessor()
    
    # 逐日预测
    print(f"\n[5/6] 执行逐日预测...")
    predictions = []
    for i in range(len(data["features"])):
        pred = predict_daily(model, data["features"][i], device, multi_task=multi_task)
        predictions.append(pred)
        
        if (i + 1) % 50 == 0:
            print(f"  → 已完成 {i + 1}/{len(data['features'])} 天")
    
    print(f"  → 预测完成：{len(predictions)} 天")
    
    # 模拟交易
    print(f"\n[6/6] 执行模拟交易...")
    trading_result = simulate_trading(predictions, data["returns"], config)
    
    # 计算评估指标
    metrics = calculate_metrics(trading_result, data["returns"], predictions, config)
    
    # 打印结果
    print("\n" + "-" * 60)
    print("回测结果摘要:")
    print("-" * 60)
    print(f"  初始资金：¥{metrics['initial_capital']:,.0f}")
    print(f"  最终资金：¥{metrics['final_capital']:,.0f}")
    print(f"  总收益率：{metrics['total_return']:.2%}")
    print(f"  年化收益率：{metrics['annual_return']:.2%}")
    print(f"  夏普比率：{metrics['sharpe_ratio']:.2f}")
    print(f"  最大回撤：{metrics['max_drawdown']:.2%}")
    print(f"  胜率：{metrics['win_rate']:.2%}")
    print(f"  交易次数：{metrics['n_trades']}")
    print("-" * 60)
    
    # 生成报告
    report_path, md_path = generate_report(metrics, trading_result, output_dir)
    print(f"\n  → JSON 报告：{report_path}")
    print(f"  → Markdown 报告：{md_path}")
    
    print("\n" + "=" * 60)
    print("端到端回测流程完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
