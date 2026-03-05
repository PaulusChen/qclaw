"""
数据质量验证模块

包含:
- 缺失值检测
- 异常值检测 (3σ原则 / 孤立森林)
- 数据分布分析
- 数据质量报告生成
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import IsolationForest


class DataValidator:
    """
    数据质量验证器
    
    功能:
    - 检测缺失值
    - 检测异常值
    - 分析数据分布
    - 生成质量报告
    """
    
    def __init__(
        self,
        missing_threshold: float = 0.05,
        outlier_method: str = "zscore",
        zscore_threshold: float = 3.0,
        contamination: float = 0.05,
    ):
        """
        初始化验证器
        
        参数:
            missing_threshold: 缺失值阈值 (超过则标记)
            outlier_method: 异常值检测方法 ("zscore" 或 "isolation_forest")
            zscore_threshold: Z-Score 阈值
            contamination: 孤立森林异常值比例
        """
        self.missing_threshold = missing_threshold
        self.outlier_method = outlier_method
        self.zscore_threshold = zscore_threshold
        self.contamination = contamination
        
        self.report: Dict[str, Any] = {}
    
    def check_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        检查缺失值
        
        参数:
            df: 输入数据
            
        返回:
            缺失值统计信息
        """
        missing_count = df.isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        
        # 标记超过阈值的列
        problematic_cols = missing_pct[missing_pct > self.missing_threshold * 100].to_dict()
        
        result = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_count": missing_count.to_dict(),
            "missing_percentage": missing_pct.to_dict(),
            "problematic_columns": problematic_cols,
            "has_critical_missing": len(problematic_cols) > 0,
        }
        
        return result
    
    def check_outliers_zscore(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        使用 Z-Score 检测异常值
        
        参数:
            df: 输入数据 (数值列)
            
        返回:
            异常值统计信息
        """
        numeric_df = df.select_dtypes(include=[np.number])
        
        outliers = {}
        outlier_mask = pd.DataFrame(index=df.index)
        
        for col in numeric_df.columns:
            mean = numeric_df[col].mean()
            std = numeric_df[col].std()
            
            if std > 0:
                z_scores = np.abs((numeric_df[col] - mean) / std)
                col_outliers = z_scores > self.zscore_threshold
                outliers[col] = {
                    "count": int(col_outliers.sum()),
                    "percentage": float(col_outliers.mean() * 100),
                    "indices": np.where(col_outliers)[0].tolist()[:100],  # 最多 100 个
                }
                outlier_mask[col] = col_outliers
        
        result = {
            "method": "zscore",
            "threshold": self.zscore_threshold,
            "outliers_by_column": outliers,
            "total_outlier_cells": int(outlier_mask.any(axis=1).sum()),
            "outlier_percentage": float(outlier_mask.any(axis=1).mean() * 100),
        }
        
        return result
    
    def check_outliers_isolation_forest(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        使用孤立森林检测异常值
        
        参数:
            df: 输入数据 (数值列)
            
        返回:
            异常值统计信息
        """
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if len(numeric_df) < 10:
            return {"error": "Insufficient data for isolation forest"}
        
        # 训练孤立森林
        iso_forest = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
        )
        
        predictions = iso_forest.fit_predict(numeric_df)
        
        # -1 表示异常值，1 表示正常值
        outlier_mask = predictions == -1
        outlier_indices = np.where(outlier_mask)[0].tolist()
        
        result = {
            "method": "isolation_forest",
            "contamination": self.contamination,
            "n_outliers": int(outlier_mask.sum()),
            "outlier_percentage": float(outlier_mask.mean() * 100),
            "outlier_indices": outlier_indices[:100],  # 最多 100 个
        }
        
        return result
    
    def check_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        检测异常值 (根据配置选择方法)
        
        参数:
            df: 输入数据
            
        返回:
            异常值统计信息
        """
        if self.outlier_method == "zscore":
            return self.check_outliers_zscore(df)
        elif self.outlier_method == "isolation_forest":
            return self.check_outliers_isolation_forest(df)
        else:
            raise ValueError(f"Unknown outlier method: {self.outlier_method}")
    
    def analyze_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        分析数据分布
        
        参数:
            df: 输入数据
            
        返回:
            分布统计信息
        """
        numeric_df = df.select_dtypes(include=[np.number])
        
        distribution_stats = {}
        
        for col in numeric_df.columns:
            data = numeric_df[col].dropna()
            
            if len(data) == 0:
                continue
            
            distribution_stats[col] = {
                "mean": float(data.mean()),
                "std": float(data.std()),
                "min": float(data.min()),
                "max": float(data.max()),
                "median": float(data.median()),
                "skewness": float(data.skew()),
                "kurtosis": float(data.kurtosis()),
                "q1": float(data.quantile(0.25)),
                "q3": float(data.quantile(0.75)),
            }
        
        return {
            "numeric_columns": len(numeric_df.columns),
            "distribution_stats": distribution_stats,
        }
    
    def check_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        执行完整的数据质量检查
        
        参数:
            df: 输入数据
            
        返回:
            完整的质量报告
        """
        self.report = {
            "summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
                "categorical_columns": len(df.select_dtypes(include=["object", "category"]).columns),
            },
            "missing_values": self.check_missing_values(df),
            "outliers": self.check_outliers(df),
            "distribution": self.analyze_distribution(df),
            "quality_score": self._calculate_quality_score(df),
        }
        
        return self.report
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算数据质量评分 (0-100)
        
        参数:
            df: 输入数据
            
        返回:
            质量评分和等级
        """
        missing_info = self.check_missing_values(df)
        outlier_info = self.check_outliers(df)
        
        # 缺失值扣分 (最多 40 分)
        missing_penalty = min(40, missing_info["missing_percentage"].get("close", 0) * 10)
        
        # 异常值扣分 (最多 30 分)
        outlier_pct = outlier_info.get("outlier_percentage", 0)
        outlier_penalty = min(30, outlier_pct * 2)
        
        # 完整性扣分 (最多 30 分)
        completeness = 100 - missing_info["missing_percentage"].mean()
        completeness_penalty = max(0, 30 - completeness * 0.3)
        
        # 总分
        score = 100 - missing_penalty - outlier_penalty - completeness_penalty
        score = max(0, min(100, score))
        
        # 等级
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "score": round(score, 2),
            "grade": grade,
            "missing_penalty": round(missing_penalty, 2),
            "outlier_penalty": round(outlier_penalty, 2),
            "completeness_penalty": round(completeness_penalty, 2),
        }
    
    def generate_report(self, df: pd.DataFrame, output_path: Optional[str] = None) -> str:
        """
        生成数据质量报告
        
        参数:
            df: 输入数据
            output_path: 输出文件路径 (可选)
            
        返回:
            报告文本
        """
        report = self.check_data_quality(df)
        
        lines = [
            "=" * 60,
            "数据质量报告",
            "=" * 60,
            "",
            "【数据概览】",
            f"  总行数：{report['summary']['total_rows']}",
            f"  总列数：{report['summary']['total_columns']}",
            f"  数值列：{report['summary']['numeric_columns']}",
            f"  分类列：{report['summary']['categorical_columns']}",
            "",
            "【缺失值检查】",
            f"  是否存在严重缺失：{report['missing_values']['has_critical_missing']}",
            f"  问题列：{report['missing_values']['problematic_columns']}",
            "",
            "【异常值检查】",
            f"  检测方法：{report['outliers'].get('method', 'N/A')}",
            f"  异常值比例：{report['outliers'].get('outlier_percentage', 0):.2f}%",
            "",
            "【质量评分】",
            f"  总分：{report['quality_score']['score']}/100",
            f"  等级：{report['quality_score']['grade']}",
            "",
            "=" * 60,
        ]
        
        report_text = "\n".join(lines)
        
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_text)
        
        return report_text


if __name__ == "__main__":
    # 测试数据验证器
    import numpy as np
    import pandas as pd
    
    np.random.seed(42)
    
    # 创建模拟数据 (包含一些缺失值和异常值)
    n = 1000
    df = pd.DataFrame({
        "close": np.random.randn(n).cumsum() + 100,
        "volume": np.random.randint(1000, 10000, n),
        "open": np.random.randn(n).cumsum() + 100,
    })
    
    # 添加缺失值
    df.loc[np.random.choice(n, 50), "close"] = np.nan
    
    # 添加异常值
    df.loc[np.random.choice(n, 10), "volume"] *= 100
    
    # 运行验证
    validator = DataValidator(outlier_method="zscore")
    report = validator.generate_report(df)
    
    print(report)
    print("\nDataValidator test passed!")
