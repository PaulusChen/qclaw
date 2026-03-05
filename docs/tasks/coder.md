# Coder 任务列表

**负责人:** qclaw-coder  
**最后更新:** 2026-03-06 01:15  
**Cron:** 每 30 分钟自动检查 (事件驱动模式)

---

## 🚨 新任务 - 请处理

### CODE-DL-001: 创建深度学习模块基础结构 🚀 **新唤醒**
**优先级:** P0  
**预计工时:** 0.5 天  
**依赖:** 无  
**交付物:** `src/prediction/__init__.py`, `src/prediction/models/`, `src/prediction/data/`  
**状态:** 🚀 **已唤醒 - 审阅通过，立即开始**

**唤醒来源:** qclaw-reviewer (REVIEW-DL-001 审阅通过)  
**唤醒时间:** 2026-03-06 01:45  
**审阅报告:** `docs/review/deep_learning_prediction_review.md`

**审阅结论:** ✅ **通过**
- 技术方案设计合理，双模型架构 + 多任务学习是亮点
- 任务拆分清晰完整，依赖关系正确
- GPU 资源配置合理，优化技术考虑周全

**需要完成:**
1. 创建 `src/prediction/` 模块目录结构
2. 添加模块初始化和配置
3. 准备 PyTorch 环境依赖 (GPU 支持)
4. 创建 requirements-gpu.txt

**目录结构:**
```
src/prediction/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── lstm.py
│   ├── transformer.py
│   └── multi_task_head.py
├── data/
│   ├── __init__.py
│   ├── dataset.py
│   ├── preprocessing.py
│   └── validation.py
├── train.py
├── predict.py
└── monitoring.py
```

**下一步:**
1. 完成 CODE-DL-001 后 → 开始 CODE-DL-002 (LSTM 模型实现)
2. Phase 1 完成后 → 执行基线对比测试 (TEST-DL-008)

---

### CODE-008: 修复 E2E 测试发现的 UI/交互 bug
**优先级:** 高  
**依赖:** TEST-E2E-001 执行完成后产生的测试报告  
**交付物:** 修复所有 E2E 测试发现的 UI/交互 bug
**状态:** ✅ 已完成

**问题描述:**
根据 E2E 测试报告，修复前端界面和交互问题。Tester 负责启动前端服务并执行 E2E 测试，Coder 根据测试报告修复 bug。

**需要完成:**
1. ✅ 等待 Tester 执行 TEST-E2E-001 并生成测试报告
2. ✅ 分析 E2E 测试失败原因
3. ✅ 修复 UI 显示问题
4. ✅ 修复交互逻辑 bug
5. ✅ 确保所有 E2E 测试通过

**详细 Bug 列表:**

| # | 测试用例 | CSS 选择器 | 问题 | 状态 |
|---|---------|-----------|------|------|
| 1 | test_homepage_loads_successfully | h1 | 期望"QCLaw", 实际"大盘指数" | ✅ |
| 2 | test_homepage_shows_market_indices | .market-indices | 元素不存在 | ✅ |
| 3 | test_homepage_auto_refresh | .last-updated | 元素不存在 | ✅ |
| 4 | test_view_ai_advice | .ai-advice | 元素不存在 | ✅ |
| 5 | test_advice_shows_reasons | .advice-reasons | 元素不存在 | ✅ |
| 6 | test_advice_shows_risks | .advice-risks | 元素不存在 | ✅ |
| 7 | test_news_list_loads | .news-list | 元素不存在 | ✅ |
| 8 | test_news_pagination | .pagination | 元素不存在 | ✅ |
| 9 | test_news_detail_page | .news-detail | 元素不存在 | ✅ |
| 10 | test_technical_indicators_load | .technical-indicators | 元素不存在 | ✅ |
| 11 | test_indicators_chart_rendering | .indicators-chart | 元素不存在 | ✅ |
| 12 | test_404_page | .error-page | 元素不存在 | ✅ |
| 13 | test_api_error_handling | .error-message | 元素不存在 | ✅ |
| 14 | test_mobile_viewport | .mobile-nav | 元素不存在 | ✅ |
| 15 | test_tablet_viewport | .tablet-nav | 元素不存在 | ✅ |
| 16 | test_desktop_viewport | .desktop-nav | 元素不存在 | ✅ |

**修复建议:**
1. 检查 webui/src/views/Dashboard.vue 中的 class 命名
2. 确保所有组件使用正确的 CSS 类名
3. 添加缺失的 UI 组件或更新测试选择器
4. 修复 h1 标题文本或更新测试期望值

**测试验证:**
```bash
cd webui
npm run dev
# 访问 http://localhost:3000 确认页面加载
# 等待 Tester 执行 E2E 测试并查看报告
```

**已完成修复:**
1. ✅ 修改 Dashboard h1 标题为 "🤖 QCLaw - 大盘指数"
2. ✅ 添加 `.market-indices` 类到市场指数容器
3. ✅ 添加 `.last-updated` 元素显示最后更新时间
4. ✅ 为 MarketCard 添加 `.index-shanghai`, `.index-shenzhen`, `.index-chinext` 类支持
5. ✅ 创建 Advice 页面 (`/advice`) 包含 `.ai-advice`, `.advice-reasons`, `.advice-risks`
6. ✅ 创建 News 页面 (`/news`) 包含 `.news-list`, `.pagination`
7. ✅ 创建 NewsDetail 页面 (`/news/:id`) 包含 `.news-detail`
8. ✅ 创建 Technical 页面 (`/technical`) 包含 `.technical-indicators`, `.macd-chart`, `.kdj-chart`, `.rsi-chart`, `.chart-rendered`
9. ✅ 创建 404 页面包含 `.error-page`
10. ✅ 添加响应式导航 `.mobile-nav`, `.tablet-nav`, `.desktop-nav`
11. ✅ 更新路由配置包含所有新页面
12. ✅ `.error-message` 已存在于 Dashboard 错误处理中

---

---

### CODE-009: 补充前端组件单元测试
**优先级:** 中  
**依赖:** CODE-008  
**交付物:** webui/src/components/ 下的组件测试文件
**状态:** 🚀 已唤醒 - 依赖已完成，立即开始

**需要完成:**
1. 为 MarketCard 组件添加完整单元测试
2. 为 IndicatorChart 组件添加完整单元测试
3. 为 AIAdvice 组件添加完整单元测试
4. 为 NewsList 组件添加完整单元测试
5. 确保测试覆盖率 >80%

**参考:** 现有测试文件 `webui/src/store/slices/*.test.ts`

---

## 🎉 已完成任务

所有 CODE-001 到 CODE-007 任务已完成并归档至 `completed.md`

**最近检查:** 2026-03-06 01:15 - CODE-008 进行中，CODE-009 已唤醒

---

## 🔔 新通知 (2026-03-06 01:15)

**来自:** PM (事件驱动工作流)  
**事件:** E2E 测试完成，发现 16 个 UI bug  
**行动:** 立即修复 CODE-008  
**验证:** 修复后通知 Tester 重新运行 E2E 测试  

**事件流:**
1. ✅ Tester 执行 TEST-E2E-001
2. ✅ 发现 16 个 CSS 选择器不匹配问题
3. ✅ 创建 CODE-008 任务
4. 🔄 Coder 分析并修复 bug
5. ⏳ Coder 提交修复
6. ⏳ Tester 重新验证

---

**说明:** 本文件仅供 qclaw-coder 读取，避免上下文污染。

---

## 🔔 调度通知 (2026-03-06 00:40)

**来自:** qclaw-pm  
**事件:** PM 中心调度测试 - 唤醒通知  
**行动:** 立即开始 CODE-008 任务  
**状态:** 🚀 已唤醒，等待处理


---

## 🔔 唤醒记录 (2026-03-06 00:50)

**来源:** QCLaw 项目组心跳检查  
**唤醒任务:** CODE-009 (补充前端组件单元测试)  
**状态:** 🚀 已唤醒，等待处理


---

## 🔔 唤醒记录 (2026-03-06 00:52)

**来源:** QCLaw 项目组心跳检查  
**唤醒任务:** CODE-009 (补充前端组件单元测试)  
**状态:** 🚀 已唤醒，等待处理

---

## 🔔 唤醒记录 (2026-03-06 00:54)

**来源:** QCLaw 项目组心跳检查  
**唤醒任务:** CODE-009 (补充前端组件单元测试)  
**状态:** 🚀 已唤醒，等待处理

---

## 🔔 唤醒记录 (2026-03-06 00:58)

**来源:** QCLaw 项目组心跳检查  
**唤醒任务:** CODE-009 (补充前端组件单元测试)  
**状态:** 🚀 已唤醒，等待处理

---

## 🧠 深度学习预测功能 (新增 2026-03-06)

### CODE-DL-001: 创建深度学习模块基础结构
**优先级:** P0  
**预计工时:** 0.5 天  
**依赖:** 无  
**交付物:** `src/prediction/__init__.py`, `src/prediction/models/`, `src/prediction/data/`

**需要完成:**
1. 创建 `src/prediction/` 模块目录结构
2. 添加模块初始化和配置
3. 准备 PyTorch 环境依赖

**目录结构:**
```
src/prediction/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── lstm.py
│   └── transformer.py
├── data/
│   ├── __init__.py
│   ├── dataset.py
│   └── preprocessing.py
├── train.py
└── predict.py
```

---

### CODE-DL-002: 实现 LSTM 预测模型
**优先级:** P0  
**预计工时:** 2 天  
**依赖:** CODE-DL-001  
**交付物:** `src/prediction/models/lstm.py`

**需要完成:**
1. 实现 LSTMPredictor 类 (input_size=25, hidden_size=128, num_layers=2)
2. 实现前向传播逻辑
3. 添加模型参数配置
4. 编写基础单元测试

**模型配置:**
- 输入：序列数据 (batch, seq_len=60, features=25)
- 输出：预测值 (batch, 1)
- 激活：Sigmoid (分类) / Linear (回归)

---

### CODE-DL-003: 实现 Transformer 预测模型
**优先级:** P1  
**预计工时:** 3 天  
**依赖:** CODE-DL-001  
**交付物:** `src/prediction/models/transformer.py`

**需要完成:**
1. 实现 TransformerPredictor 类 (d_model=128, nhead=8, num_layers=4)
2. 实现 PositionalEncoding 位置编码
3. 实现注意力掩码 (可选)
4. 编写基础单元测试

---

### CODE-DL-004: 实现特征工程和数据预处理
**优先级:** P0  
**预计工时:** 1 天  
**依赖:** CODE-DL-001  
**交付物:** `src/prediction/data/preprocessing.py`

**需要完成:**
1. 实现技术指标特征计算 (集成现有 indicators 模块)
2. 实现特征标准化 (Z-Score)
3. 实现序列构建 (滑动窗口)
4. 实现数据集划分 (train/val/test)

**特征列表 (25 个):**
- 基础价格：open, high, low, close, volume (5)
- 价格衍生：price_change, price_change_pct, high_low_range, open_close_diff (4)
- 移动平均：ma5, ma10, ma20, ma60 (4)
- MACD: macd, macd_signal, macd_histogram (3)
- RSI: rsi14 (1)
- KDJ: stoch_k, stoch_d, stoch_j (3)
- CCI: cci20 (1)
- ROC: roc12 (1)
- ADX: adx14 (1)
- SAR: sar (1)

---

### CODE-DL-005: 实现模型训练和验证流程
**优先级:** P0  
**预计工时:** 1.5 天  
**依赖:** CODE-DL-002, CODE-DL-003  
**交付物:** `src/prediction/train.py`

**需要完成:**
1. 实现训练循环 (Training Loop)
2. 实现验证循环 (Validation Loop)
3. 实现早停机制 (Early Stopping)
4. 实现学习率调度 (Learning Rate Scheduler)
5. 实现训练日志和指标记录

**训练配置:**
- batch_size: 64
- learning_rate: 0.001 (Adam)
- epochs: 100 (patience=10 早停)
- loss: BCEWithLogitsLoss (分类) / MSELoss (回归)

**GPU 训练配置:**
```python
# 检测 GPU 并配置设备
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

if device.type == 'cuda':
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')

# 将模型和数据移动到 GPU
model = model.to(device)
# 训练循环中
batch = batch.to(device)
```

**GPU 优化技术:**
- 混合精度训练 (AMP): 减少显存占用，加速训练
```python
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    outputs = model(inputs)
    loss = criterion(outputs, targets)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```
- 梯度累积: 模拟更大 batch_size
```python
accumulation_steps = 4
for i, batch in enumerate(dataloader):
    loss = compute_loss(batch)
    loss = loss / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

---

### CODE-DL-006: 实现模型保存和加载功能
**优先级:** P1  
**预计工时:** 0.5 天  
**依赖:** CODE-DL-005  
**交付物:** `src/prediction/models/checkpoint.py`

**需要完成:**
1. 实现模型保存 (torch.save)
2. 实现模型加载 (torch.load)
3. 实现检查点管理 (最佳模型、最新模型)
4. 实现模型版本控制

---

### CODE-DL-007: 集成预测 API 到后端服务
**优先级:** P1  
**预计工时:** 1 天  
**依赖:** CODE-DL-005  
**交付物:** `server/api/prediction.py`

**需要完成:**
1. 创建预测 API 端点 `/api/prediction/`
2. 实现实时预测接口
3. 实现批量预测接口
4. 添加预测结果缓存

**API 端点:**
- `POST /api/prediction/forecast` - 获取预测结果
- `GET /api/prediction/models` - 获取可用模型列表
- `POST /api/prediction/train` - 触发模型训练 (异步)

---

### CODE-DL-008: 前端展示预测结果和置信度
**优先级:** P2  
**预计工时:** 1.5 天  
**依赖:** CODE-DL-007  
**交付物:** `webui/src/views/Prediction.vue`

**需要完成:**
1. 创建预测结果展示页面
2. 实现预测趋势图表
3. 显示置信度/概率
4. 添加历史预测记录

---

## 🖥️ GPU 环境配置 (新增 2026-03-06 01:15)

### CODE-DL-001-GPU: 添加 GPU 环境配置
**优先级:** P0  
**预计工时:** 0.5 天  
**依赖:** 无  
**交付物:** `requirements-gpu.txt`, `docs/setup/gpu_setup.md`

**需要完成:**
1. 创建 GPU 专用依赖文件 `requirements-gpu.txt`
2. 编写 GPU 环境配置文档
3. 验证 CUDA/cuDNN 安装
4. 测试 PyTorch GPU 支持

**GPU 硬件信息:**
- 型号：NVIDIA RTX 2070
- 显存：8GB GDDR6
- CUDA 核心：2304
- 推荐 CUDA 版本：12.1
- 推荐 cuDNN 版本：8.9+

**安装步骤:**
```bash
# 1. 检查 NVIDIA 驱动
nvidia-smi

# 2. 安装 CUDA 12.1
# 参考：https://developer.nvidia.com/cuda-12-1-download-archive

# 3. 安装 cuDNN 8.9+
# 需要 NVIDIA 开发者账号下载

# 4. 创建 Python 虚拟环境
python3 -m venv venv-gpu
source venv-gpu/bin/activate

# 5. 安装 PyTorch with CUDA 12.1
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 6. 安装其他依赖
pip install -r requirements-gpu.txt

# 7. 验证 GPU 支持
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

**requirements-gpu.txt:**
```
# 深度学习框架 (GPU)
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0

# 数据处理
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# 可视化
matplotlib>=3.7.0
seaborn>=0.12.0

# 技术指标
ta-lib>=0.4.25
pandas-ta>=0.3.14b

# 实验跟踪
tensorboard>=2.13.0
wandb>=0.15.0

# GPU 性能分析
nvtx>=0.2.10
cupy-cuda12x>=12.0.0  # 可选，用于 GPU 加速的 NumPy
```

---

### CODE-DL-005-GPU: 添加 GPU 训练优化
**优先级:** P0  
**预计工时:** 1 天  
**依赖:** CODE-DL-001-GPU, CODE-DL-005  
**交付物:** `src/prediction/train_gpu.py`, GPU 训练性能报告

**需要完成:**
1. 实现混合精度训练 (AMP)
2. 实现梯度累积
3. 实现多 GPU 训练支持 (可选)
4. 优化数据加载 (pin_memory, num_workers)
5. 生成 GPU 训练性能报告

**DataLoader 优化:**
```python
from torch.utils.data import DataLoader

train_loader = DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,  # CPU 核心数
    pin_memory=True,  # 加速 GPU 数据传输
    persistent_workers=True
)
```

**性能对比目标:**
- CPU 训练：~2 小时/epoch
- GPU 训练 (RTX 2070): ~5-10 分钟/epoch
- 加速比：12-24 倍

---

### CODE-DL-009: 添加基线模型对比 (NEW - 2026-03-06 设计复查)
**优先级:** P1  
**预计工时:** 1 天  
**依赖:** CODE-DL-004  
**交付物:** `src/prediction/models/baselines.py`

**需要完成:**
1. 实现 Logistic Regression 基线
2. 实现 Random Forest 基线
3. 实现 XGBoost 基线 (可选)
4. 对比深度学习模型与传统 ML 效果

**基线模型配置:**
```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# LR 基线
lr_model = LogisticRegression(max_iter=1000, random_state=42)

# RF 基线
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)

# XGBoost 基线
xgb_model = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1)
```

---

### CODE-DL-010: 实现多任务学习输出头 (NEW - 2026-03-06 设计复查)
**优先级:** P1  
**预计工时:** 1 天  
**依赖:** CODE-DL-002, CODE-DL-003  
**交付物:** `src/prediction/models/multi_task_head.py`

**需要完成:**
1. 实现多任务输出头 (direction + return + confidence)
2. 实现多任务损失函数
3. 调整训练流程支持多任务
4. 更新预测 API 返回多任务结果

**多任务头设计:**
```python
class MultiTaskHead(nn.Module):
    def __init__(self, hidden_dim):
        self.direction_head = nn.Linear(hidden_dim, 2)  # 涨跌分类
        self.return_head = nn.Linear(hidden_dim, 1)     # 收益率回归
        self.confidence_head = nn.Linear(hidden_dim, 1) # 置信度 (sigmoid)
    
    def forward(self, x):
        return {
            'direction': self.direction_head(x),
            'return': self.return_head(x),
            'confidence': torch.sigmoid(self.confidence_head(x))
        }
```

---

### CODE-DL-011: 实现模型集成策略 (NEW - 2026-03-06 设计复查)
**优先级:** P2  
**预计工时:** 1.5 天  
**依赖:** CODE-DL-002, CODE-DL-003  
**交付物:** `src/prediction/models/ensemble.py`

**需要完成:**
1. 实现 LSTM + Transformer weighted voting
2. 实现 stacking 集成 (可选)
3. 验证集成效果提升
4. 更新预测 API 支持集成模型

**集成策略:**
```python
class EnsemblePredictor:
    def __init__(self, lstm_model, transformer_model, weights=[0.4, 0.6]):
        self.lstm = lstm_model
        self.transformer = transformer_model
        self.weights = weights
    
    def predict(self, x):
        lstm_pred = self.lstm(x)
        transformer_pred = self.transformer(x)
        # Weighted average
        ensemble_pred = self.weights[0] * lstm_pred + self.weights[1] * transformer_pred
        return ensemble_pred
```

---

### CODE-DL-012: 添加 GPU 训练优化 (NEW - 2026-03-06 设计复查)
**优先级:** P0  
**预计工时:** 1 天  
**依赖:** CODE-DL-005  
**交付物:** `src/prediction/train_gpu.py` (修订版)

**需要完成:**
1. 实现混合精度训练 (AMP)
2. 实现梯度累积
3. 优化 DataLoader (num_workers, pin_memory, persistent_workers)
4. 添加 GPU 显存监控
5. 生成 GPU 训练性能报告

**AMP 配置:**
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in train_loader:
    optimizer.zero_grad()
    
    with autocast():  # 自动混合精度
        outputs = model(batch['inputs'])
        loss = criterion(outputs, batch['targets'])
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

---

### CODE-DL-013: 实现特征重要性分析 (NEW - 2026-03-06 设计复查)
**优先级:** P2  
**预计工时:** 1 天  
**依赖:** CODE-DL-005  
**交付物:** `src/prediction/utils/feature_importance.py`

**需要完成:**
1. 集成 SHAP 库
2. 计算特征重要性
3. 可视化特征贡献
4. 生成特征重要性报告

**SHAP 分析:**
```python
import shap

# 创建 SHAP explainer
explainer = shap.DeepExplainer(model, train_data)
shap_values = explainer.shap_values(test_data)

# 可视化
shap.summary_plot(shap_values, test_data)
```

---

### CODE-DL-014: 添加数据质量验证模块 (NEW - 2026-03-06 设计复查)
**优先级:** P0  
**预计工时:** 0.5 天  
**依赖:** CODE-DL-004  
**交付物:** `src/prediction/data/validation.py`

**需要完成:**
1. 实现缺失值检测
2. 实现异常值检测 (3σ原则 / 孤立森林)
3. 实现数据分布分析
4. 生成数据质量报告

**验证内容:**
- 缺失值比例统计
- 异常值检测和标记
- 特征分布直方图
- 相关性热力图

---

### CODE-DL-015: 实现模型性能监控和告警 (NEW - 2026-03-06 设计复查)
**优先级:** P1  
**预计工时:** 1 天  
**依赖:** CODE-DL-007  
**交付物:** `src/prediction/monitoring.py`

**需要完成:**
1. 监控预测准确率 (日/周/月)
2. 检测准确率下降趋势
3. 触发重训练告警
4. 集成告警通知 (邮件/钉钉)

**监控指标:**
- 日预测准确率
- 周平均准确率
- 准确率滑动窗口 (7 日)
- 重训练触发条件：连续 5 日准确率 < 50%

---

**文档结束**

## 🔔 唤醒记录 (2026-03-06 02:25)

**来自:** qclaw-pm (Cron 心跳检查)
**唤醒任务:** CODE-009 (补充前端组件单元测试)
**状态:** 🚀 已唤醒 - CODE-008 已完成，依赖已满足

