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

## 🔄 实施步骤

### 阶段 1: 核心架构实现 (预计 3-4 天)

**Day 1-2: 组件实现**
- [ ] 实现 `StaticCovariateEncoder`
- [ ] 实现 `VariableSequenceEncoder`
- [ ] 实现 `GatedLinearUnit`
- [ ] 实现 `InterpretableMultiHeadAttention`
- [ ] 编写组件单元测试

**Day 3-4: 主模型实现**
- [ ] 实现 `TemporalFusionTransformer` 主类
- [ ] 实现前向传播逻辑
- [ ] 实现分位数输出
- [ ] 编写模型单元测试

### 阶段 2: 训练集成 (预计 2-3 天)

**Day 1: 训练脚本**
- [ ] 实现 `train_tft.py`
- [ ] 集成到训练管道
- [ ] 配置训练参数

**Day 2-3: 训练验证**
- [ ] 在小数据集上训练验证
- [ ] 对比 Transformer 基线
- [ ] 调优超参数

### 阶段 3: 推理与可视化 (预计 2 天)

**Day 1: 推理器**
- [ ] 实现 `tft_predictor.py`
- [ ] 集成到推理管道
- [ ] 支持多步预测

**Day 2: 可视化**
- [ ] 实现注意力权重提取
- [ ] 实现可视化函数
- [ ] 生成示例图表

### 阶段 4: 测试与文档 (预计 1-2 天)

**Day 1: 测试**
- [ ] 完善单元测试
- [ ] 编写集成测试
- [ ] 确保测试覆盖率 >90%

**Day 2: 文档**
- [ ] 编写架构说明文档
- [ ] 编写训练指南
- [ ] 编写可视化指南
- [ ] 更新 README

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
