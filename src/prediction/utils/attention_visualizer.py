"""
TFT 注意力可视化工具

用于可视化 Temporal Fusion Transformer 的注意力权重
帮助理解模型关注哪些时间步和特征
"""

import torch
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib/seaborn not installed. Install with: pip install matplotlib seaborn")


class AttentionVisualizer:
    """
    TFT 注意力可视化工具
    
    可视化 TFT 模型的注意力权重，包括:
    - 编码器注意力 (历史时间步的重要性)
    - 解码器注意力 (预测时间步的依赖)
    - 特征重要性 (哪些特征最关键)
    """
    
    def __init__(self, output_dir: str = "results/attention_viz"):
        """
        初始化可视化工具
        
        参数:
            output_dir: 输出目录
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib and seaborn are required for visualization")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_encoder_attention(
        self,
        attention_weights: torch.Tensor,
        time_idx: Optional[np.ndarray] = None,
        title: str = "Encoder Attention Weights",
        save_path: Optional[str] = None,
    ) -> plt.Figure:
        """
        绘制编码器注意力权重
        
        参数:
            attention_weights: 注意力权重张量 [batch, heads, encoder_length]
            time_idx: 时间索引 (可选)
            title: 图表标题
            save_path: 保存路径 (可选)
            
        返回:
            matplotlib Figure 对象
        """
        # 转换为 numpy 并取平均
        attn = attention_weights.detach().cpu().numpy()
        
        # 平均所有批次和注意力头
        if len(attn.shape) == 3:
            attn_mean = attn.mean(axis=(0, 1))  # [encoder_length]
        else:
            attn_mean = attn.mean(axis=0)
        
        # 创建时间索引
        if time_idx is None:
            time_idx = np.arange(len(attn_mean))
        
        # 绘制
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.bar(time_idx, attn_mean, color='steelblue', alpha=0.7)
        ax.set_xlabel("Time Step (Encoder)", fontsize=12)
        ax.set_ylabel("Attention Weight", fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.grid(True, alpha=0.3)
        
        # 标注最重要的时间步
        top_idx = np.argsort(attn_mean)[-5:][::-1]
        for idx in top_idx:
            ax.annotate(
                f'{attn_mean[idx]:.3f}',
                xy=(time_idx[idx], attn_mean[idx]),
                xytext=(0, 5),
                textcoords='offset points',
                ha='center',
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5)
            )
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Attention plot saved to {save_path}")
        
        return fig
    
    def plot_attention_heatmap(
        self,
        attention_weights: torch.Tensor,
        encoder_labels: Optional[List[str]] = None,
        decoder_labels: Optional[List[str]] = None,
        title: str = "Attention Heatmap",
        save_path: Optional[str] = None,
    ) -> plt.Figure:
        """
        绘制注意力热力图
        
        参数:
            attention_weights: 注意力权重张量 [batch, heads, encoder_len, decoder_len]
            encoder_labels: 编码器时间步标签
            decoder_labels: 解码器时间步标签
            title: 图表标题
            save_path: 保存路径
            
        返回:
            matplotlib Figure 对象
        """
        # 转换为 numpy 并取平均
        attn = attention_weights.detach().cpu().numpy()
        
        # 平均所有批次和注意力头
        if len(attn.shape) == 4:
            attn_mean = attn.mean(axis=(0, 1))  # [encoder_len, decoder_len]
        else:
            attn_mean = attn
        
        # 绘制热力图
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            attn_mean,
            annot=True,
            fmt='.3f',
            cmap='YlOrRd',
            xticklabels=decoder_labels or [f'D{i}' for i in range(attn_mean.shape[1])],
            yticklabels=encoder_labels or [f'E{i}' for i in range(attn_mean.shape[0])],
            ax=ax,
            cbar_kws={'label': 'Attention Weight'}
        )
        
        ax.set_xlabel("Decoder Time Steps", fontsize=12)
        ax.set_ylabel("Encoder Time Steps", fontsize=12)
        ax.set_title(title, fontsize=14)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Attention heatmap saved to {save_path}")
        
        return fig
    
    def plot_feature_importance(
        self,
        feature_names: List[str],
        importance_scores: np.ndarray,
        top_k: int = 20,
        title: str = "Feature Importance",
        save_path: Optional[str] = None,
    ) -> plt.Figure:
        """
        绘制特征重要性
        
        参数:
            feature_names: 特征名称列表
            importance_scores: 重要性分数数组
            top_k: 显示前 K 个特征
            title: 图表标题
            save_path: 保存路径
            
        返回:
            matplotlib Figure 对象
        """
        # 排序
        indices = np.argsort(importance_scores)[::-1][:top_k]
        sorted_names = [feature_names[i] for i in indices]
        sorted_scores = importance_scores[indices]
        
        # 绘制
        fig, ax = plt.subplots(figsize=(10, 8))
        y_pos = np.arange(len(sorted_names))
        
        bars = ax.barh(y_pos, sorted_scores, color='steelblue', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(sorted_names, fontsize=10)
        ax.invert_yaxis()  # 最重要的在顶部
        ax.set_xlabel("Importance Score", fontsize=12)
        ax.set_title(title, fontsize=14)
        
        # 添加数值标签
        for i, (bar, score) in enumerate(zip(bars, sorted_scores)):
            ax.text(
                score + 0.01 * max(sorted_scores),
                bar.get_y() + bar.get_height() / 2,
                f'{score:.4f}',
                va='center',
                fontsize=9
            )
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Feature importance plot saved to {save_path}")
        
        return fig
    
    def plot_prediction_with_attention(
        self,
        actual: np.ndarray,
        predicted: np.ndarray,
        attention_weights: Optional[np.ndarray] = None,
        title: str = "Prediction vs Actual",
        save_path: Optional[str] = None,
    ) -> plt.Figure:
        """
        绘制预测结果与注意力权重
        
        参数:
            actual: 实际值
            predicted: 预测值
            attention_weights: 注意力权重 (可选)
            title: 图表标题
            save_path: 保存路径
            
        返回:
            matplotlib Figure 对象
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                        gridspec_kw={'height_ratios': [2, 1]})
        
        # 上图：预测 vs 实际
        time_steps = np.arange(len(actual))
        ax1.plot(time_steps, actual, 'b-', label='Actual', linewidth=2, alpha=0.7)
        ax1.plot(time_steps, predicted, 'r--', label='Predicted', linewidth=2, alpha=0.7)
        ax1.set_ylabel("Value", fontsize=12)
        ax1.set_title(title, fontsize=14)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # 下图：注意力权重
        if attention_weights is not None:
            attn = attention_weights if len(attention_weights.shape) == 1 else attention_weights.mean(axis=0)
            if len(attn) == len(time_steps):
                ax2.bar(time_steps, attn, color='steelblue', alpha=0.5, label='Attention')
                ax2.set_xlabel("Time Step", fontsize=12)
                ax2.set_ylabel("Attention Weight", fontsize=12)
                ax2.legend(loc='best')
                ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Prediction plot saved to {save_path}")
        
        return fig
    
    def save_all_visualizations(
        self,
        model: Any,
        data_loader: torch.utils.data.DataLoader,
        feature_names: Optional[List[str]] = None,
        prefix: str = "tft",
    ):
        """
        保存所有可视化图表
        
        参数:
            model: TFT 模型实例
            data_loader: 数据加载器
            feature_names: 特征名称列表
            prefix: 文件名前缀
        """
        print("Generating attention visualizations...")
        
        # 获取注意力权重
        try:
            attention = model.get_attention(data_loader)
            
            # 保存编码器注意力
            if isinstance(attention, dict):
                if 'encoder' in attention:
                    self.plot_encoder_attention(
                        attention['encoder'],
                        title=f"{prefix} - Encoder Attention",
                        save_path=str(self.output_dir / f"{prefix}_encoder_attention.png")
                    )
            else:
                self.plot_encoder_attention(
                    attention,
                    title=f"{prefix} - Encoder Attention",
                    save_path=str(self.output_dir / f"{prefix}_encoder_attention.png")
                )
            
            print(f"Visualizations saved to {self.output_dir}")
            
        except Exception as e:
            print(f"Error generating visualizations: {e}")


def visualize_tft_attention(
    model: Any,
    data_loader: torch.utils.data.DataLoader,
    output_dir: str = "results/attention_viz",
    feature_names: Optional[List[str]] = None,
):
    """
    便捷函数：可视化 TFT 模型注意力
    
    参数:
        model: TFT 模型实例
        data_loader: 数据加载器
        output_dir: 输出目录
        feature_names: 特征名称列表
    """
    visualizer = AttentionVisualizer(output_dir=output_dir)
    visualizer.save_all_visualizations(model, data_loader, feature_names)


if __name__ == "__main__":
    # 示例用法
    print("TFT Attention Visualizer")
    print("Usage: Import and use with trained TFT model")
    
    # 创建示例数据
    if MATPLOTLIB_AVAILABLE:
        visualizer = AttentionVisualizer()
        
        # 示例注意力权重
        example_attn = torch.rand(4, 8, 30)  # [batch, heads, encoder_length]
        
        visualizer.plot_encoder_attention(
            example_attn,
            title="Example Encoder Attention",
            save_path="results/attention_viz/example_attention.png"
        )
        
        print("Example visualization created!")
