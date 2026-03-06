<!-- ARCHIVED: 已压缩至 check-history-summary.md -->

# 深度学习量化预测技术调研报告

**任务 ID:** DESIGN-DL-001  
**负责人:** qclaw-designer  
**创建日期:** 2026-03-06  
**状态:** ✅ 已完成  
**限制说明:** ⚠️ Brave Search API 未配置，本报告基于 established best practices 和已有知识编写

---

## 📋 执行摘要

本报告调研深度学习在量化预测领域的技术应用，验证当前技术选型 (LSTM/Transformer) 的合理性，并提供技术实施建议。

**核心结论:**
- ✅ LSTM 和 Transformer 选型合理，是时间序列预测的主流选择
- ✅ 25 个技术指标特征覆盖全面，符合行业实践
- ✅ RTX 2070 8GB 可满足中等规模模型训练需求
- ⚠️ 建议添加混合精度训练和梯度累积优化
- ⚠️ 建议考虑添加 Temporal Fusion Transformer 作为对比模型

---

## 1. 深度学习在量化预测领域的应用现状

### 1.1 主流技术路线

| 技术路线 | 适用场景 | 优势 | 劣势 |
|---------|---------|------|------|
| **LSTM/GRU** | 中短期序列预测 | 捕捉长期依赖，训练稳定 | 序列较长时梯度消失 |
| **Transformer** | 多因子/长序列 | 并行计算，注意力机制强大 | 需要大量数据，训练成本高 |
| **Temporal Fusion Transformer (TFT)** | 多变量时间序列 | 可解释性强，处理静态/动态特征 | 实现复杂 |
| **N-BEATS** | 纯时间序列预测 | 无需特征工程，端到端 | 可解释性较弱 |
| **DeepAR** | 概率预测 | 输出预测分布，不确定性量化 | 需要概率分布假设 |

### 1.2 行业趋势 (2024-2026)

基于已知研究和行业实践:

1. **混合模型兴起:** LSTM+Attention、Transformer+CNN 等混合架构成为研究热点
2. **多模态融合:** 结合价格数据、新闻情绪、宏观经济指标的多模态模型
3. **可解释性增强:** SHAP、Attention 可视化等技术用于模型解释
4. **在线学习:** 适应市场变化的增量学习和模型更新策略
5. **不确定性量化:** 分位数回归、蒙特卡洛 Dropout 等方法评估预测置信度

---

## 2. 技术选型验证

### 2.1 LSTM vs Transformer 对比

| 维度 | LSTM | Transformer | 推荐 |
|------|------|-------------|------|
| **序列长度** | 适合中等长度 (50-200) | 适合长序列 (200+) | 根据数据选择 |
| **训练速度** | 较慢 (序列依赖) | 较快 (并行计算) | Transformer |
| **数据需求** | 中等 | 较大 | LSTM (小数据场景) |
| **捕捉依赖** | 短期+中期依赖 | 长距离依赖 | Transformer |
| **实现复杂度** | 低 | 中 | LSTM |
| **GPU 内存** | 较低 | 较高 | LSTM |

**结论:** 当前选型 (LSTM + Transformer 对比实验) 合理，建议:
- 初期使用 LSTM 快速验证 baseline
- 数据充足时尝试 Transformer 获取更好性能
- 考虑添加 LSTM+Attention 作为中间方案

### 2.2 模型参数建议

基于行业实践和硬件约束 (RTX 2070 8GB):

```yaml
# LSTM 推荐配置
lstm:
  hidden_size: [64, 128, 256]  # 从大到小尝试
  num_layers: [2, 3]           # 避免过深
  dropout: 0.2-0.5             # 正则化
  sequence_length: 60          # 60 天窗口

# Transformer 推荐配置
transformer:
  d_model: [64, 128]           # 受限于 GPU 内存
  nhead: 4-8                   # 注意力头数
  num_encoder_layers: 2-4      # 避免过深
  dim_feedforward: 256-512
  dropout: 0.1-0.3
  sequence_length: 60-120

# Temporal Fusion Transformer (可选)
tft:
  hidden_size: 128
  attention_head_size: 4
  dropout: 0.1
  sequence_length: 60
```

### 2.3 特征工程验证

**当前 25 个特征评估:**

| 类别 | 特征数量 | 评估 | 建议 |
|------|---------|------|------|
| 移动平均线 | 5 | ✅ 充分 | 保持 |
| 动量指标 | 5 | ✅ 充分 | 保持 |
| 波动率指标 | 4 | ✅ 充分 | 保持 |
| 成交量指标 | 4 | ✅ 充分 | 保持 |
| 趋势指标 | 4 | ✅ 充分 | 保持 |
| 价格衍生 | 3 | ✅ 充分 | 保持 |

**建议添加的特征 (可选):**
- 📊 **波动率特征:** Parkinson 波动率、Garman-Klass 波动率 (需要 OHLC 数据)
- 📊 **流动性指标:** 买卖价差、Amihud 非流动性指标
- 📊 **市场情绪:** 融资融券余额、换手率异常
- 📊 **宏观因子:** 无风险利率、市场风险溢价 (低频)

**特征标准化建议:**
```python
# 推荐方案: RobustScaler (对异常值不敏感)
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)

# 备选: Z-Score 标准化
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

---

## 3. 开源项目参考

### 3.1 知名量化预测项目

| 项目 | 框架 | 特点 | 参考价值 |
|------|------|------|---------|
| **qlib** (Microsoft) | PyTorch | 完整量化 AI 平台，多模型支持 | ⭐⭐⭐⭐⭐ |
| **finrl** | TensorFlow/PyTorch | 强化学习量化交易 | ⭐⭐⭐⭐ |
| **vectorbt** | NumPy/Pandas | 向量化回测，快速原型 | ⭐⭐⭐⭐ |
| **backtrader** | Python | 经典回测框架 | ⭐⭐⭐ |
| **stable-baselines3** | PyTorch | 强化学习基线 | ⭐⭐⭐ |

### 3.2 推荐参考实现

**Microsoft Qlib (强烈推荐):**
- GitHub: https://github.com/microsoft/qlib
- 包含 LSTM、Transformer、TabNet 等模型实现
- 提供完整的数据处理、训练、回测流程
- 支持 A 股市场数据

**关键代码参考:**
```python
# QLib LSTM 模型示例
from qlib.contrib.model.pytorch_lstm import LSTMModel

model = LSTMModel(
    d_feat=6,           # 特征维度
    hidden_size=64,     # 隐藏层大小
    num_layers=2,       # LSTM 层数
    dropout=0.3,        # Dropout
    n_epochs=200,       # 训练轮数
    lr=0.001,           # 学习率
    early_stop=10,      # 早停
    batch_size=2048,    # 批次大小
    metric="ic"         # 评估指标
)
```

---

## 4. GPU 训练优化建议

### 4.1 RTX 2070 8GB 配置建议

| 优化技术 | 说明 | 预期收益 | 实施难度 |
|---------|------|---------|---------|
| **混合精度训练 (AMP)** | 使用 FP16+FP32 混合精度 | 内存 -50%, 速度 +30% | 低 |
| **梯度累积** | 多批次累积后更新权重 | 等效更大 batch size | 低 |
| **梯度裁剪** | 防止梯度爆炸 | 训练稳定性 | 低 |
| **学习率调度** | ReduceLROnPlateau/Cosine | 收敛更好 | 低 |
| **数据预取** | DataLoader 多进程加载 | 减少 GPU 等待 | 中 |

### 4.2 推荐训练配置

```python
# PyTorch 混合精度训练示例
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    optimizer.zero_grad()
    
    with autocast():  # 混合精度
        outputs = model(batch)
        loss = criterion(outputs, targets)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

# 梯度累积示例
accumulation_steps = 4  # 4 批次累积

for i, batch in enumerate(dataloader):
    outputs = model(batch)
    loss = criterion(outputs, targets) / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### 4.3 显存优化技巧

```bash
# 限制 PyTorch 显存分配
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# 监控显存使用
nvidia-smi dmon -s pucvmet
```

---

## 5. 模型评估方法

### 5.1 推荐评估指标

| 指标 | 公式 | 适用场景 | 目标值 |
|------|------|---------|--------|
| **IC (Information Coefficient)** | corr(pred, return) | 因子有效性 | > 0.03 |
| **ICIR** | IC / std(IC) | 因子稳定性 | > 0.5 |
| **Rank IC** | corr(rank_pred, rank_return) | 排序能力 | > 0.05 |
| **年化收益** | (1 + daily_return)^252 - 1 | 策略收益 | > 15% |
| **夏普比率** | (return - risk_free) / std(return) | 风险调整收益 | > 1.0 |
| **最大回撤** | max(peak - trough) / peak | 风险控制 | < 20% |
| **胜率** | win_days / total_days | 预测准确性 | > 55% |

### 5.2 回测验证方案

```python
# 推荐回测流程
1. 数据划分: train(70%) / validation(15%) / test(15%)
2. 时间序列交叉验证: 避免未来函数
3. 滚动窗口训练: 模拟真实交易场景
4. 交易成本考虑: 手续费 + 滑点 (0.1%-0.3%)
5. 基准对比: 对比沪深 300、中证 500 等指数

# 关键注意事项
- ⚠️ 避免未来函数 (使用 t 时刻数据预测 t+1)
- ⚠️ 考虑停牌、涨跌停限制
- ⚠️ 处理除权除息
- ⚠️ 样本外测试 (out-of-sample testing)
```

---

## 6. 潜在技术风险与缓解措施

| 风险 | 影响 | 缓解措施 | 优先级 |
|------|------|---------|--------|
| **过拟合** | 样本内表现好，实盘失效 | Dropout、早停、正则化、简化模型 | P0 |
| **数据泄露** | 评估结果虚高 | 严格时间序列划分、避免未来函数 | P0 |
| **市场风格切换** | 模型失效 | 在线学习、定期重训练、多模型融合 | P1 |
| **极端行情** | 预测失准 | 添加波动率特征、不确定性量化 | P1 |
| **训练不稳定** | 难以收敛 | 梯度裁剪、学习率调度、混合精度 | P1 |
| **推理延迟** | 实时预测慢 | 模型蒸馏、量化、ONNX 加速 | P2 |

---

## 7. 技术实施建议

### 7.1 推荐技术栈

```yaml
深度学习框架:
  - PyTorch 2.0+ (首选，生态丰富)
  - TensorFlow 2.x (备选)

量化平台:
  - QLib (Microsoft，强烈推荐)
  - 自研 (灵活性高)

数据处理:
  - Pandas + NumPy
  - Polars (性能更好，可选)

可视化:
  - Matplotlib + Seaborn
  - Plotly (交互式)

实验管理:
  - MLflow / Weights & Biases
  - TensorBoard

部署:
  - ONNX Runtime (推理加速)
  - FastAPI (API 服务)
  - Docker (容器化)
```

### 7.2 开发路线图

```
Phase 1 (2 周): Baseline 建立
├── 数据预处理 pipeline
├── LSTM baseline 模型
├── 基础评估指标
└── 简单回测框架

Phase 2 (3 周): 模型优化
├── Transformer 实现
├── 超参数调优
├── 特征工程优化
└── 混合精度训练

Phase 3 (2 周): 系统集成
├── 与 WebUI 集成
├── 实时预测 pipeline
├── 模型监控告警
└── 文档完善
```

---

## 8. 待互联网调研补充内容 ⚠️

由于 Brave Search API 未配置，以下内容建议后续补充:

### 8.1 待搜索论文 (2024-2026)
- [ ] "Deep Learning for Stock Prediction: A Survey 2024"
- [ ] "Transformer-based Financial Time Series Forecasting"
- [ ] "Temporal Fusion Transformer for Multi-horizon Forecasting"
- [ ] "Attention Mechanisms in Quantitative Trading"

### 8.2 待调研开源项目
- [ ] GitHub 高星量化预测项目 (stars > 1000)
- [ ] 最新开源的 Transformer 金融预测实现
- [ ] 国内量化平台开源项目 (JoinQuant、RiceQuant 等)

### 8.3 待验证最佳实践
- [ ] 2025 年量化预测 SOTA 模型性能
- [ ] 行业标准的特征工程方法
- [ ] 实盘部署的最佳实践案例

---

## 9. 结论与建议

### 9.1 技术选型结论

| 选型 | 验证结果 | 建议 |
|------|---------|------|
| LSTM | ✅ 合理 | 作为 baseline 和主力模型 |
| Transformer | ✅ 合理 | 作为对比和优化方向 |
| 25 个特征 | ✅ 充分 | 可保持， optionally 添加 2-3 个 |
| RTX 2070 8GB | ✅ 可用 | 添加混合精度训练优化 |
| 60 天序列长度 | ✅ 合理 | 可尝试 30/60/90 对比 |

### 9.2 优先实施建议

**P0 (立即实施):**
1. 实现 LSTM baseline 模型
2. 添加混合精度训练
3. 完善数据预处理 pipeline
4. 建立基础回测框架

**P1 (近期实施):**
1. 实现 Transformer 对比模型
2. 添加梯度累积和梯度裁剪
3. 实现学习率调度策略
4. 完善评估指标体系

**P2 (后续优化):**
1. 尝试 Temporal Fusion Transformer
2. 添加不确定性量化
3. 实现在线学习机制
4. 模型蒸馏和推理优化

### 9.3 配置建议

**强烈建议配置 Brave Search API:**
```bash
openclaw configure --section web
# 获取 API Key: https://brave.com/search/api/
```

配置后可补充:
- 最新论文调研 (2024-2026)
- 开源项目代码分析
- 行业最佳实践验证
- 竞品技术方案调研

---

## 📚 参考资料

### 经典论文
1. Hochreiter & Schmidhuber (1997) - Long Short-Term Memory
2. Vaswani et al. (2017) - Attention Is All You Need
3. Lim et al. (2021) - Temporal Fusion Transformers
4. Oreshkin et al. (2020) - N-BEATS

### 推荐资源
- Microsoft QLib: https://github.com/microsoft/qlib
- Hugging Face Transformers: https://huggingface.co/docs/transformers
- PyTorch Time Series: https://pytorch.org/

---

**报告生成时间:** 2026-03-06 03:00  
**下次更新:** 配置 Brave API 后补充互联网调研内容
