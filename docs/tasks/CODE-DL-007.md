# CODE-DL-007: TFT 模型实现与集成

**优先级:** P0 (最高)  
**创建日期:** 2026-03-06  
**负责人:** qclaw-coder  
**依赖:** 
- CODE-DL-005 (训练层) 完成 ✅
- 先进模型架构调研完成 ✅  
**状态:** ⏳ 待开始

---

## 📋 任务描述

实现 Temporal Fusion Transformer (TFT) 模型并集成到 qclaw 项目中。TFT 是 2024-2025 年最成熟的时间序列预测架构，在多步预测和可解释性方面优于传统 Transformer 和 LSTM。

**调研依据:** `docs/research/advanced-model-architectures-2024-2026.md`

---

## ⚠️ 重要原则：优先复用开源项目

**🔄 P0 设计原则:**
1. **第一选择:** 使用 `pytorch-forecasting` 库的 TFT 实现
   - GitHub: https://github.com/jdb78/pytorch-forecasting
   - 文档：https://pytorch-forecasting.readthedocs.io/en/stable/api/pytorch_forecasting.models.temporal_fusion_transformer.html
   
2. **第二选择:** 在开源实现基础上定制 (添加 qclaw 特定功能)

3. **第三选择:** 自研实现 (仅在开源项目无法满足需求时)

**评估标准:**
- ✅ `pytorch-forecasting` 是否支持我们的数据格式？
- ✅ 是否支持多步预测 (7/14/30 天)？
- ✅ 是否支持注意力可视化？
- ✅ 许可证是否兼容 (MIT/Apache)？

**如果开源项目满足 80% 需求 → 使用开源项目 + 定制开发**

---

## 🎯 实现目标

### 核心目标
1. 实现 TFT 模型架构
2. 集成到训练管道
3. 实现注意力可视化
4. 支持多步预测 (7/14/30 天)
5. 性能对比验证

### 性能目标
| 指标 | 当前 (Transformer) | TFT 目标 | 提升 |
|------|-------------------|---------|------|
| MSE | 0.045 | **0.023** | +49% |
| Sharpe Ratio | 1.8 | **2.1** | +17% |
| 最大回撤 | -18% | **-12%** | +33% |

---

## 📦 交付物清单

### 1. 模型实现

**文件结构:**
```
src/models/
├── tft/
│   ├── __init__.py
│   ├── model.py              # TFT 核心架构
│   ├── components.py         # TFT 组件 (编码器、注意力等)
│   ├── config.py             # TFT 配置类
│   └── utils.py              # TFT 工具函数
```

**核心组件:**
- [ ] `StaticCovariateEncoder` - 静态协变量编码器
- [ ] `VariableSequenceEncoder` - 序列变量编码器
- [ ] `InterpretableMultiHeadAttention` - 可解释多头注意力
- [ ] `GatedLinearUnit` - 门控线性单元
- [ ] `TemporalFusionTransformer` - TFT 主模型

### 2. 训练集成

**文件结构:**
```
src/training/
├── train_tft.py            # TFT 训练脚本
└── tft_trainer.py          # TFT 训练器封装
```

**功能要求:**
- [ ] 支持多步预测训练
- [ ] 实现分位数损失 (quantile loss)
- [ ] 添加梯度裁剪
- [ ] 学习率预热和调度
- [ ] 早停机制

### 3. 推理集成

**文件结构:**
```
src/inference/
├── tft_predictor.py        # TFT 推理器
└── tft_visualizer.py       # TFT 注意力可视化
```

**功能要求:**
- [ ] 加载训练好的 TFT 模型
- [ ] 支持单步和多步预测
- [ ] 实现注意力权重可视化
- [ ] 输出预测不确定性 (分位数)

### 4. 配置文件

**文件结构:**
```
config/models/
├── tft_config.yaml         # TFT 模型配置
config/training/
├── tft_training.yaml       # TFT 训练配置
```

**配置内容:**
```yaml
# tft_config.yaml
model:
  type: TemporalFusionTransformer
  hidden_size: 160
  dropout: 0.1
  num_heads: 4
  output_size: 7  # 预测 7 天
  static_features:
    - sector
    - market_cap
    - volatility_regime
  known_future_inputs:
    - day_of_week
    - month
    - is_holiday
  observed_inputs:
    - open
    - high
    - low
    - close
    - volume
    - technical_indicators
```

### 5. 测试用例

**文件结构:**
```
tests/unit/models/
├── test_tft_components.py   # TFT 组件测试
├── test_tft_model.py        # TFT 模型测试
└── test_tft_integration.py  # TFT 集成测试
```

**测试覆盖:**
- [ ] 组件单元测试
- [ ] 模型前向传播测试
- [ ] 训练流程测试
- [ ] 推理流程测试
- [ ] 可视化功能测试

### 6. 文档

**文件结构:**
```
docs/models/
├── tft_architecture.md     # TFT 架构说明
├── tft_training_guide.md   # TFT 训练指南
└── tft_visualization.md    # 注意力可视化指南
```

---

## 🔄 任务拆解 (Coder 自行细化)

### 任务 7.1: pytorch-forecasting 评估 (4 小时)
**预计工时:** 4 小时  
**依赖:** 无  
**交付物:** `docs/research/pytorch-forecasting-evaluation.md`

**执行步骤:**
1. 安装 pytorch-forecasting
   ```bash
   pip install pytorch-forecasting
   ```

2. 阅读官方文档
   - TFT 模型文档
   - 数据格式要求
   - 训练配置示例

3. 功能验证
   - [ ] 是否支持我们的数据格式？
   - [ ] 是否支持多步预测 (7/14/30 天)？
   - [ ] 是否支持注意力可视化？
   - [ ] 许可证是否兼容 (MIT)？

4. 编写评估报告
   - 功能匹配度分析
   - 优缺点评估
   - 推荐使用建议

**验收标准:**
- [ ] 完成安装和文档阅读
- [ ] 完成功能验证清单
- [ ] 输出评估报告

---

### 任务 7.2: 数据适配器实现 (4 小时)
**预计工时:** 4 小时  
**依赖:** 任务 7.1  
**交付物:** `src/data/tft_dataset.py`

**执行步骤:**
1. 研究 pytorch-forecasting 数据格式
   - TimeSeriesDataSet 要求
   - 静态协变量格式
   - 动态输入格式

2. 实现数据适配器
   ```python
   class TFTDataset(TimeSeriesDataSet):
       def __init__(self, df, config):
           # 适配 qclaw 数据格式
           pass
   ```

3. 测试数据加载
   - [ ] 加载历史数据
   - [ ] 验证数据格式
   - [ ] 测试批量加载

**验收标准:**
- [ ] 数据适配器可正常运行
- [ ] 支持静态协变量
- [ ] 支持动态输入
- [ ] 单元测试通过

---

### 任务 7.3: TFT 模型配置 (2 小时)
**预计工时:** 2 小时  
**依赖:** 任务 7.2  
**交付物:** `config/models/tft_config.yaml`

**执行步骤:**
1. 创建配置文件
   ```yaml
   model:
     type: TemporalFusionTransformer
     hidden_size: 160
     dropout: 0.1
     num_heads: 4
     output_size: 7
   ```

2. 配置静态协变量
   ```yaml
   static_features:
     - sector
     - market_cap
     - volatility_regime
   ```

3. 配置输入特征
   ```yaml
   observed_inputs:
     - open
     - high
     - low
     - close
     - volume
     - technical_indicators
   ```

**验收标准:**
- [ ] 配置文件完整
- [ ] 参数配置合理
- [ ] 通过配置验证

---

### 任务 7.4: 训练脚本实现 (4 小时)
**预计工时:** 4 小时  
**依赖:** 任务 7.3  
**交付物:** `src/training/train_tft.py`

**执行步骤:**
1. 实现训练脚本框架
   ```python
   def train_tft(config):
       # 加载数据
       # 创建模型
       # 训练循环
       pass
   ```

2. 集成到训练管道
   - [ ] 使用现有 Trainer 类
   - [ ] 添加 TFT 支持
   - [ ] 配置优化器

3. 实现训练功能
   - [ ] 分位数损失
   - [ ] 梯度裁剪
   - [ ] 学习率调度
   - [ ] 早停机制

**验收标准:**
- [ ] 训练脚本可运行
- [ ] 模型收敛正常
- [ ] 损失函数下降

---

### 任务 7.5: 推理器实现 (4 小时)
**预计工时:** 4 小时  
**依赖:** 任务 7.4  
**交付物:** `src/inference/tft_predictor.py`

**执行步骤:**
1. 实现推理器类
   ```python
   class TFTPredictor:
       def __init__(self, model_path, config):
           # 加载模型
           pass
       
       def predict(self, data, horizon=7):
           # 执行预测
           pass
   ```

2. 集成到推理管道
   - [ ] 加载训练好的模型
   - [ ] 支持单步预测
   - [ ] 支持多步预测 (7/14/30 天)

3. 实现分位数输出
   - [ ] 输出中位数预测
   - [ ] 输出不确定性范围

**验收标准:**
- [ ] 推理器可正常运行
- [ ] 支持多步预测
- [ ] 输出格式正确

---

### 任务 7.6: 注意力可视化 (4 小时)
**预计工时:** 4 小时  
**依赖:** 任务 7.5  
**交付物:** `src/viz/tft_attention.py`

**执行步骤:**
1. 提取注意力权重
   ```python
   def extract_attention(model, data):
       # 获取注意力权重
       pass
   ```

2. 实现可视化函数
   - [ ] 特征重要性热力图
   - [ ] 时间注意力图
   - [ ] 保存为图表

3. 生成示例图表
   - [ ] 选择典型样本
   - [ ] 生成可视化
   - [ ] 保存到文档

**验收标准:**
- [ ] 注意力权重可提取
- [ ] 可视化图表清晰
- [ ] 至少生成 3 个示例图

---

### 任务 7.7: 性能对比测试 (4 小时)
**预计工时:** 4 小时  
**依赖:** 任务 7.6  
**交付物:** `docs/reports/tft-performance-report.md`

**执行步骤:**
1. 准备测试数据集
   - 沪深 300 成分股
   - 时间跨度：2020-2025

2. 执行对比测试
   - [ ] TFT 模型测试
   - [ ] Transformer 基线测试
   - [ ] LSTM 基线测试

3. 计算评估指标
   - [ ] MSE、MAE、RMSE
   - [ ] Sharpe Ratio
   - [ ] Max Drawdown
   - [ ] 方向准确率

4. 编写性能报告
   - 对比结果分析
   - 性能提升统计
   - 优化建议

**验收标准:**
- [ ] 完成所有对比测试
- [ ] MSE < 0.030 (目标 0.023)
- [ ] Sharpe Ratio > 2.0
- [ ] 输出性能报告

---

### 任务 7.8: 文档完善 (2 小时)
**预计工时:** 2 小时  
**依赖:** 任务 7.7  
**交付物:** `docs/models/tft_usage.md`

**执行步骤:**
1. 编写使用指南
   - 安装说明
   - 快速开始
   - 配置说明

2. 编写 API 文档
   - 类和方法说明
   - 参数说明
   - 使用示例

3. 编写最佳实践
   - 超参数调优建议
   - 常见问题解答
   - 性能优化技巧

**验收标准:**
- [ ] 文档完整清晰
- [ ] 示例代码可运行
- [ ] 常见问题覆盖

---

## ✅ 验收标准

### 代码质量
- [ ] 所有模块导入成功
- [ ] 代码符合项目规范
- [ ] 必要的文档字符串
- [ ] 错误处理完善

### 功能完整
- [ ] TFT 模型可训练
- [ ] TFT 模型可推理
- [ ] 支持多步预测 (7/14/30 天)
- [ ] 注意力可视化正常
- [ ] 配置文件完善

### 测试覆盖
- [ ] 单元测试覆盖率 >90%
- [ ] 集成测试通过
- [ ] 训练流程测试通过
- [ ] 推理流程测试通过

### 性能达标
- [ ] MSE < 0.030 (对比 Transformer 的 0.045)
- [ ] Sharpe Ratio > 2.0
- [ ] 训练速度 > 100 samples/sec
- [ ] 推理延迟 < 50ms (单样本)

### 文档完整
- [ ] 架构说明文档
- [ ] 训练指南
- [ ] 可视化指南
- [ ] API 文档更新

---

## 📊 性能基准测试

### 对比实验设计

**基线模型:**
- Transformer (当前主力)
- LSTM (传统基线)

**测试数据集:**
- 沪深 300 成分股 (300 只股票)
- 时间跨度：2020-2025 (5 年)
- 特征：25 个技术指标 + 静态协变量

**评估指标:**
- MSE、MAE、RMSE
- Sharpe Ratio、Max Drawdown
- 方向准确率 (Direction Accuracy)

### 预期结果

| 模型 | MSE | Sharpe | MaxDD | 方向准确率 |
|------|-----|--------|-------|-----------|
| LSTM | 0.052 | 1.5 | -22% | 52% |
| Transformer | 0.045 | 1.8 | -18% | 56% |
| **TFT (目标)** | **0.023** | **2.1** | **-12%** | **62%** |

---

## 🔧 技术要点

### 1. 分位数损失

```python
def quantile_loss(y_true, y_pred, quantiles=[0.1, 0.5, 0.9]):
    losses = []
    for q in quantiles:
        loss = torch.max((q-1)*(y_true-y_pred), q*(y_true-y_pred))
        losses.append(loss.mean())
    return torch.stack(losses).sum()
```

### 2. 注意力可视化

```python
def visualize_attention(attention_weights, feature_names, save_path):
    # 绘制注意力权重热力图
    # 展示模型关注哪些特征和时间步
    pass
```

### 3. 多步预测

```python
# 预测未来 7 天
predictions = model.predict(
    past_inputs=past_data,
    future_inputs=known_future,
    horizon=7
)
```

---

## ⚠️ 风险与缓解

### 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| TFT 训练不稳定 | 中 | 梯度裁剪、学习率预热、权重初始化 |
| 显存不足 | 中 | 梯度累积、混合精度训练、减小 batch size |
| 过拟合 | 低 | Dropout、早停、数据增强、正则化 |
| 性能不达标 | 中 | 超参数调优、特征工程优化 |

### 实施挑战

1. **TFT 复杂度高** - 需要深入理解论文
   - 缓解：参考官方实现、详细阅读论文
   
2. **超参数调优** - 需要大量实验
   - 缓解：使用 Optuna 自动调参
   
3. **与现有代码集成** - 需要重构部分模块
   - 缓解：设计清晰的接口、逐步迁移

---

## 📚 参考资料

### 核心论文
1. Lim, B. et al. (2021). Temporal Fusion Transformers for interpretable multi-horizon time series forecasting. *International Journal of Forecasting*.
2. Wu, H. et al. (2024). iTransformer: Inverted Transformers Are Effective for Time Series Forecasting. *ICLR 2024*.

### 开源实现
1. https://github.com/google-research/google-research/tree/master/tft
2. https://github.com/jdb78/pytorch-forecasting (TFT 实现)

### 文档
- `docs/research/advanced-model-architectures-2024-2026.md` - 先进模型架构调研

---

## 🎯 下一步

**TFT 完成后:**
- CODE-DL-008: iTransformer 模型实现
- CODE-DL-009: 混合模型探索 (TFT-GNN、CNN-LSTM-TFT)
- CODE-DL-010: 模型集成与部署优化

---

**立即开始实施！**
