"""
PyTorch 数据集类

用于加载和批处理股票预测数据
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import Optional, Dict, Any, Tuple
import numpy as np


class StockDataset(Dataset):
    """
    股票预测数据集
    
    支持:
    - 序列数据加载
    - 多任务标签
    - 数据增强 (可选)
    """
    
    def __init__(
        self,
        features: np.ndarray,
        targets: Optional[Dict[str, np.ndarray]] = None,
        transform=None,
    ):
        """
        初始化数据集
        
        参数:
            features: 特征数组 (n_samples, seq_len, n_features)
            targets: 目标字典 (可选)
                - direction: (n_samples,) 涨跌标签
                - return: (n_samples, 1) 收益率
                - confidence: (n_samples, 1) 置信度
            transform: 数据变换 (可选)
        """
        self.features = torch.FloatTensor(features)
        self.targets = {}
        
        if targets is not None:
            for key, value in targets.items():
                if value is not None:
                    if len(value.shape) == 1:
                        value = value.reshape(-1, 1)
                    self.targets[key] = torch.FloatTensor(value)
        
        self.transform = transform
        self.n_samples = len(features)
    
    def __len__(self) -> int:
        return self.n_samples
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        获取单个样本
        
        参数:
            idx: 样本索引
            
        返回:
            包含特征和目标的字典
        """
        feature = self.features[idx]
        
        if self.transform:
            feature = self.transform(feature)
        
        sample = {"features": feature}
        
        for key, target in self.targets.items():
            sample[key] = target[idx]
        
        return sample
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据集统计信息"""
        stats = {
            "n_samples": self.n_samples,
            "feature_shape": tuple(self.features.shape),
        }
        
        for key, target in self.targets.items():
            stats[f"{key}_mean"] = target.mean().item()
            stats[f"{key}_std"] = target.std().item()
            if key == "direction":
                stats[f"{key}_distribution"] = torch.bincount(target.squeeze().long()).tolist()
        
        return stats


def create_dataloader(
    dataset: StockDataset,
    batch_size: int = 64,
    shuffle: bool = True,
    num_workers: int = 4,
    pin_memory: bool = True,
    persistent_workers: bool = True,
) -> DataLoader:
    """
    创建数据加载器
    
    参数:
        dataset: 数据集
        batch_size: 批次大小
        shuffle: 是否打乱
        num_workers: 数据加载 worker 数
        pin_memory: 是否锁定内存 (GPU 加速)
        persistent_workers: 是否保持 worker 持久化
        
    返回:
        DataLoader
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
        drop_last=True,
    )


def create_data_loaders(
    dataset_dict: Dict[str, Tuple[np.ndarray, Optional[np.ndarray]]],
    batch_size: int = 64,
    num_workers: int = 4,
) -> Dict[str, DataLoader]:
    """
    为 train/val/test 创建数据加载器
    
    参数:
        dataset_dict: 包含 train/val/test 数据的字典
        batch_size: 批次大小
        num_workers: worker 数
        
    返回:
        包含 train/val/test DataLoader 的字典
    """
    loaders = {}
    
    for split, (features, targets) in dataset_dict.items():
        # 准备目标
        target_dict = None
        if targets is not None:
            target_dict = {"direction": targets}
        
        # 创建数据集
        dataset = StockDataset(features, target_dict)
        
        # 创建 DataLoader
        shuffle = (split == "train")
        loaders[split] = create_dataloader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
        )
    
    return loaders


if __name__ == "__main__":
    # 测试数据集
    import numpy as np
    
    np.random.seed(42)
    
    # 创建模拟数据
    n_samples = 1000
    seq_len = 60
    n_features = 25
    
    features = np.random.randn(n_samples, seq_len, n_features)
    targets = {
        "direction": np.random.randint(0, 2, n_samples),
        "return": np.random.randn(n_samples, 1),
        "confidence": np.random.rand(n_samples, 1),
    }
    
    # 创建数据集
    dataset = StockDataset(features, targets)
    
    print(f"Dataset size: {len(dataset)}")
    print(f"Feature shape: {dataset.features.shape}")
    print(f"Statistics: {dataset.get_statistics()}")
    
    # 创建 DataLoader
    loader = create_dataloader(dataset, batch_size=32, num_workers=2)
    
    # 测试批量加载
    batch = next(iter(loader))
    print(f"\nBatch keys: {batch.keys()}")
    print(f"Features batch shape: {batch['features'].shape}")
    print(f"Direction batch shape: {batch['direction'].shape}")
    
    print("\nStockDataset test passed!")
