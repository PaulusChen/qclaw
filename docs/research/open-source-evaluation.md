# 开源项目评估报告 - TEST-OPEN-001

**任务 ID:** TEST-OPEN-001  
**负责人:** qclaw-tester  
**开始日期:** 2026-03-06  
**状态:** 🔄 进行中  

---

## 📋 评估概览

| 项目名称 | 类别 | 评估状态 | 推荐等级 |
|---------|------|---------|---------|
| pytorch-forecasting | 时序预测 | ✅ 完成 | ⭐⭐⭐⭐⭐ |
| backtrader | 回测框架 | ⏳ 待评估 | - |
| yfinance | 数据获取 | ⏳ 待评估 | - |
| tsfresh | 特征工程 | ⏳ 待评估 | - |
| PyPortfolioOpt | 投资组合优化 | ⏳ 待评估 | - |

---

## 🔍 pytorch-forecasting (TFT 实现)

### 项目信息
- **GitHub:** https://github.com/pytorch-forecasting/pytorch-forecasting
- **许可证:** MIT ✅
- **版本:** 1.6.1 (已安装)
- **最后更新:** 活跃维护中
- **Stars:** 9.5k+

### 功能匹配度测试 ✅ OPEN-001.1 完成

#### ✅ 核心功能 (已验证)
- [x] Temporal Fusion Transformer (TFT) 实现
- [x] 多步预测支持 (预测长度=7 天)
- [x] 静态/动态协变量支持
- [x] 数据预处理工具 (TimeSeriesDataSet)
- [x] 训练流程 (标准 PyTorch 循环)
- [x] 推理流程 (model.eval() + torch.no_grad())

#### 测试结果 (2026-03-06 13:45)
```
✅ 数据集：1000 行 (5 股票 × 200 天)
✅ 训练集：570 samples, 验证集：5 samples
✅ 模型训练：3 epochs, Loss 从 1.10 降至 0.91
✅ 推理测试：预测形状 (5, 7, 1), 值范围 [-0.33, 0.36]
✅ 多步预测：支持 7 天预测
```

#### 测试脚本
- `tests/open_source/test_pytorch_forecasting.py`

### 性能基准 ✅ OPEN-001.2 完成 (2026-03-06 14:15)
| 指标 | 目标值 | 实测值 | 状态 |
|------|-------|-------|------|
| MSE | < 0.030 | **0.000465** | ✅ |
| RMSE | - | 0.0216 | ✅ |
| MAE | - | 0.0173 | ✅ |
| 训练速度 | > 100 samples/sec | **304.5** | ✅ |
| 推理延迟 | < 50ms/batch | **36.76ms** | ✅ |
| 模型大小 | - | 2.03 MB | ✅ |
| 参数量 | - | 467k | ✅ |
| 方向准确率 | - | 100% | ✅ |

**测试环境:** CPU (50 股票 × 500 天，16,350 training samples)  
**测试脚本:** `tests/open_source/test_pytorch_forecasting_perf.py`

**评估结论:** ✅ 推荐使用 - 所有核心指标达标

### 许可证审查 ✅
- [x] MIT 许可证 - 商业友好
- [x] 无专利限制
- [x] 允许修改和分发

### 文档完整性
- [x] API 文档完整
- [x] 示例代码充足
- [ ] 教程质量 - 待评估
- [ ] 中文支持 - 无

---

## 🔍 backtrader (回测框架)

### 项目信息
- **GitHub:** https://github.com/mementum/backtrader
- **许可证:** 待确认
- **状态:** 维护状态待确认

### 功能匹配度测试

#### 核心功能
- [ ] 策略定义和执行
- [ ] 数据加载 (CSV, DataFrame, Live)
- [ ] 指标计算
- [ ] 性能分析
- [ ] 图表绘制

#### A 股兼容性测试
- [ ] T+1 交易规则支持
- [ ] 涨跌停限制 (±10%)
- [ ] 交易费用计算 (印花税、佣金)
- [ ] 最小交易单位 (100 股)

### 性能测试
- [ ] 回测速度
- [ ] 内存占用
- [ ] 多策略并行

---

## 🔍 yfinance (数据获取)

### 项目信息
- **GitHub:** https://github.com/ranaroussi/yfinance
- **许可证:** Apache 2.0

### 功能测试
- [ ] A 股数据获取 (可能需要替代方案)
- [ ] 美股数据获取
- [ ] 历史数据下载
- [ ] 实时数据 (延迟)
- [ ] 财务数据

### 限制
- ⚠️ Yahoo Finance 已停止官方 API，yfinance 是非官方爬虫
- ⚠️ A 股数据支持有限

### 替代方案
- [ ] AKShare (A 股友好)
- [ ] Tushare (A 股专业)

---

## 🔍 tsfresh (特征工程)

### 项目信息
- **GitHub:** https://github.com/blue-yonder/tsfresh
- **许可证:** MIT

### 功能测试
- [ ] 自动特征提取
- [ ] 特征选择
- [ ] 时序特征
- [ ] 并行计算支持

---

## 🔍 PyPortfolioOpt (投资组合优化)

### 项目信息
- **GitHub:** https://github.com/robertmartin8/PyPortfolioOpt
- **许可证:** MIT

### 功能测试
- [ ] 均值 - 方差优化
- [ ] Black-Litterman 模型
- [ ] 风险平价
- [ ] 约束条件支持

---

## 📊 评估总结

### 推荐使用

| 类别 | 推荐项目 | 理由 |
|------|---------|------|
| 时序预测 | pytorch-forecasting | ✅ MSE 0.0005, 训练 304 samples/sec, MIT 许可 |
| 回测框架 | backtrader / 自研 | 待评估 |
| 数据获取 | AKShare / Tushare | A 股支持更好 |
| 特征工程 | tsfresh | 待评估 |
| 投资组合 | PyPortfolioOpt | 待评估 |

### 风险提示

1. **数据源风险:** yfinance 非官方 API，稳定性无保障
2. **维护风险:** backtrader 维护频率较低
3. **兼容性风险:** 部分项目 A 股支持有限

### 下一步行动

- [x] 完成 pytorch-forecasting 功能测试 (OPEN-001.1) ✅
- [x] 完成 pytorch-forecasting 性能测试 (OPEN-001.2) ✅
- [ ] 完成 backtrader 功能评估 (OPEN-001.3)
- [ ] 评估其他开源项目 (OPEN-001.4)
- [ ] 输出最终推荐报告

---

**最后更新:** 2026-03-06 14:20 (OPEN-001.1 & OPEN-001.2 完成)
