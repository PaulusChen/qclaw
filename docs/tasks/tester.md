# Tester 任务列表

**负责人:** qclaw-tester  
**最后更新:** 2026-03-06 00:38
**Cron:** 每小时自动检查 (事件驱动模式)

---

## 📍 工作流说明

**任务读取位置:** `docs/tasks/tester.md` (本文件)  
**交付物提交位置:** `tests/integration/`, `tests/e2e/`, `docs/reports/`  
**提交流程:**
```bash
git add tests/integration/ tests/e2e/ docs/reports/
git commit -m "[Test] 任务名称"
git push origin main
```

---

## 🔄 进行中

| 任务 ID | 任务名称 | 进度 | 备注 |
|---------|---------|------|------|
| TEST-SYS-001 | Docker 系统测试 | 85% | 测试用例完备，Docker 可用。11 项跳过因需完整系统启动 |
| TEST-E2E-001 | 端到端流程测试 | 95% | 🔄 前端服务已启动，Coder 已修复 CODE-008，等待验证 |

---

## ⏳ 待开始

| 任务 ID | 任务名称 | 依赖 | 优先级 |
|---------|---------|------|--------|
| TEST-PERF-001 | 性能基准测试 | CODE-006 | 中 |
| TEST-LOAD-001 | 负载压力测试 | CODE-006 | 低 |

---

## ✅ 已完成

| 任务 ID | 任务名称 | 完成日期 | 交付物 |
|---------|---------|----------|--------|
| TEST-INT-001 | API 集成测试 | 2026-03-05 | `tests/integration/test_api_integration.py` ✅ |
| TEST-INT-002 | 数据库集成测试 | 2026-03-05 | `tests/integration/test_api_integration.py::TestDatabaseIntegration` ✅ |
| TEST-UNIT-FIX | 单元测试修复 | 2026-03-05 | `tests/conftest.py`, `tests/test_moving_average.py` ✅ |
| TEST-MVP | MVP 功能测试和性能测试 | 2026-03-05 | `docs/test/test_report_2026-03-05.md` ✅ (已归档) |
| TEST-ENV-001 | 启动前端服务构建测试环境 | 2026-03-06 | 前端服务运行在 localhost:3000 ✅ (已归档) |
| TEST-RUN-2026-03-05-2145 | 全量测试执行 | 2026-03-05 21:45 | `docs/reports/test-report-2026-03-05-2145.md` ✅ |
| TEST-RUN-2026-03-05-2228 | 全量测试执行 | 2026-03-05 22:28 | `docs/reports/test-report-2026-03-05-2228.md` ✅ |
| TEST-RUN-2026-03-05-2308 | 全量测试执行 | 2026-03-05 23:08 | `docs/reports/test-report-2026-03-05-2308.md` ✅ |
| TEST-RUN-2026-03-05-2315 | 全量测试执行 | 2026-03-05 23:15 | `docs/reports/test-report-2026-03-05-2315.md` ✅ |
| TEST-RUN-2026-03-05-2323 | 全量测试执行 | 2026-03-05 23:23 | `docs/reports/test-report-2026-03-05-2323.md` ✅ |
| TEST-RUN-2026-03-05-2328 | 全量测试执行 | 2026-03-05 23:28 | `docs/reports/test-report-2026-03-05-2328.md` ✅ |
| TEST-RUN-2026-03-05-2333 | 全量测试执行 | 2026-03-05 23:33 | `docs/reports/test-report-2026-03-05-2333.md` ✅ (191 通过，18 失败，11 跳过) |
| TEST-RUN-2026-03-05-2339 | 全量测试执行 | 2026-03-05 23:39 | `docs/reports/test-report-2026-03-05-2339.md` ✅ (184 单元 + 集成通过，18 E2E 失败，11 跳过) |
| TEST-RUN-2026-03-05-2348 | 全量测试执行 | 2026-03-05 23:48 | `docs/reports/test-report-2026-03-05-2348.md` ✅ (191 通过，18 E2E 失败，11 跳过) |
| TEST-RUN-2026-03-05-2353 | 全量测试执行 | 2026-03-05 23:53 | `docs/reports/test-report-2026-03-05-2353.md` ✅ (34 通过，18 E2E 失败，11 跳过) |
| TEST-RUN-2026-03-06-0024 | 全量测试执行 | 2026-03-06 00:24 | `docs/reports/test-report-2026-03-06_00-24.md` ✅ (191 通过，18 E2E 失败，11 跳过) |
| TEST-RUN-2026-03-06-0012 | 全量测试执行 | 2026-03-06 00:12 | `docs/reports/test-report-2026-03-06_00-12.md` ✅ (191 通过，18 E2E 失败，11 跳过) |
| TEST-RUN-2026-03-06-0005 | 全量测试执行 | 2026-03-06 00:05 | `docs/reports/test-report-2026-03-06_00-05.md` ✅ (191 通过，18 E2E 失败，11 跳过) |

---

## 📋 详细任务说明

### TEST-INT-001: API 集成测试 🔄

**描述:** 测试 API 模块间集成和数据流  
**依赖:** CODE-006 后端 API 完成  
**交付物:** `tests/integration/test_api_*.py`

**测试场景:**
- [ ] 大盘指标 API 集成测试
- [ ] 技术指标 API 集成测试
- [ ] AI 建议 API 集成测试
- [ ] 新闻资讯 API 集成测试
- [ ] 错误处理和异常流程
- [ ] 数据库事务测试
- [ ] Redis 缓存测试

**命令:**
```bash
docker-compose up -d
docker-compose exec -T api pytest tests/integration/ -v
```

### TEST-SYS-001: Docker 系统测试 🔄

**描述:** 在 Docker 环境中进行系统级自动化测试  
**交付物:** `tests/system/`, `scripts/test-docker.sh`

**测试内容:**
- [ ] Docker 容器启动测试
- [ ] 服务间通信测试
- [ ] 环境变量配置测试
- [ ] 数据持久化测试
- [ ] 健康检查测试
- [ ] 日志收集测试

**命令:**
```bash
# 启动完整系统
docker-compose up -d

# 运行系统测试
./scripts/test-system.sh

# 查看测试结果
docker-compose logs test
```

### TEST-INT-002: 数据库集成测试 ⏳

**描述:** 测试数据库操作和事务  
**依赖:** CODE-006 后端完成  
**交付物:** `tests/integration/test_database.py`

**测试范围:**
- [ ] 数据读写测试
- [ ] 事务回滚测试
- [ ] 并发访问测试
- [ ] 数据迁移测试

### TEST-E2E-001: 端到端流程测试 ⏳

**描述:** 完整用户流程的 E2E 测试  
**依赖:** CODE-008 前端 bug 修复  
**技术栈:** Playwright  
**交付物:** `tests/e2e/`

**测试场景:**
- [ ] 用户访问首页 → 查看大盘指标
- [ ] 用户查看 AI 投资建议
- [ ] 用户查看新闻资讯
- [ ] 数据自动刷新流程
- [ ] 错误页面显示

**命令:**
```bash
cd tests/e2e
npx playwright test
```

### TEST-ENV-001: 启动前端服务构建测试环境 ✅

**描述:** Tester 负责启动前端服务以构建 E2E 测试环境  
**优先级:** 高  
**依赖:** 无  
**交付物:** 前端服务在 localhost:3000 正常运行
**状态:** ✅ 已完成并归档

**完成内容:**
1. ✅ 执行 `npm run dev` 启动前端服务
2. ✅ 验证服务监听在 localhost:3000
3. ✅ E2E 测试可以正常访问

### TEST-PERF-001: 性能基准测试 🚀 已唤醒 - 依赖已完成，立即开始

**描述:** 系统性能基准测试  
**依赖:** CODE-006 完成  
**交付物:** `docs/reports/performance-benchmark.md`

**测试指标:**
- [ ] 页面加载时间 < 3s
- [ ] API 响应时间 < 500ms
- [ ] 图表渲染时间 < 1s
- [ ] 并发用户支持 > 100
- [ ] 内存使用 < 512MB
- [ ] CPU 使用率 < 80%

### TEST-LOAD-001: 负载压力测试 🚀 已唤醒 - 依赖已完成，立即开始

**描述:** 高负载下的系统稳定性测试  
**依赖:** CODE-006 完成  
**技术栈:** locust  
**交付物:** `docs/reports/load-test-report.md`

**测试场景:**
- [ ] 100 并发用户
- [ ] 500 并发用户
- [ ] 1000 并发用户
- [ ] 长时间运行测试 (24h)

---

## 🐳 Docker 测试环境

### 本地测试

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
docker-compose exec test pytest tests/integration/ -v

# 运行系统测试
docker-compose exec test pytest tests/system/ -v

# 查看测试报告
docker-compose logs test

# 停止测试环境
docker-compose -f docker-compose.test.yml down
```

### CI/CD 测试

```bash
# GitHub Actions 自动运行
# 参考 .github/workflows/ci.yml
```

---

## 📊 测试覆盖率目标

| 测试类型 | 负责角色 | 覆盖率目标 |
|---------|---------|-----------|
| 单元测试 | Coder | >80% |
| 集成测试 | Tester | >60% |
| E2E 测试 | Tester | 核心流程 100% |
| 系统测试 | Tester | 关键服务 100% |

---

## 📝 测试规范

### 集成测试命名
```python
def test_api_market_indices_success():
    """测试大盘指标 API 成功场景"""
    pass

def test_api_advice_daily_with_cache():
    """测试 AI 建议 API 缓存场景"""
    pass
```

### 系统测试脚本
```bash
#!/bin/bash
# tests/system/run.sh
docker-compose up -d
sleep 30
pytest tests/system/ -v
docker-compose down
```

---

## ⚠️ 当前阻塞

**TEST-E2E-001 阻塞中:**
- 原因：等待 Coder 修复 CODE-008 (16 个 UI bug)
- 影响：18 项 E2E 测试用例无法通过
- 解决：**Coder 立即修复 CODE-008**

**下一步行动:**
1. ✅ 前端服务已启动 (TEST-ENV-001 完成)
2. ✅ E2E 测试已执行，发现 16 个 bug
3. ⏳ 等待 Coder 修复 CODE-008
4. ⏳ 重新运行 E2E 测试验证修复

---

**说明:** 
- ✅ 专注于集成测试和系统测试
- ✅ 使用 Docker 环境进行自动化测试
- ✅ 单元测试由 Coder 负责
- ✅ **Tester 负责启动前端服务构建测试环境 (已完成)**

---

## 🔔 唤醒记录 (2026-03-06 00:50)

**来源:** QCLaw 项目组心跳检查  
**唤醒任务:** TEST-PERF-001 (性能基准测试), TEST-LOAD-001 (负载压力测试)  
**状态:** 🚀 已唤醒，等待处理


---

## 🔔 唤醒记录 (2026-03-06 00:52)

**来源:** QCLaw 项目组心跳检查  
**唤醒任务:** TEST-PERF-001 (性能基准测试), TEST-LOAD-001 (负载压力测试)  
**状态:** 🚀 已唤醒，等待处理

---

## 🔔 唤醒记录 (2026-03-06 00:54)

**来源:** QCLaw 项目组心跳检查  
**唤醒任务:** TEST-PERF-001 (性能基准测试), TEST-LOAD-001 (负载压力测试)  
**状态:** 🚀 已唤醒，等待处理

---

## 🔔 唤醒记录 (2026-03-06 00:58)

**来源:** QCLaw 项目组心跳检查  
**唤醒任务:** TEST-PERF-001 (性能基准测试), TEST-LOAD-001 (负载压力测试)  
**状态:** 🚀 已唤醒，等待处理

---

## 🔔 紧急唤醒 (2026-03-06 01:06)

**来源:** qclaw-pm (紧急阻塞处理)  
**唤醒任务:** TEST-E2E-001 验证 CODE-008 Bug 修复  
**状态:** 🚀 已唤醒，立即执行 E2E 测试验证  
**备注:** Coder 已提交修复，前端服务已启动 (HTTP 200)，重新运行 E2E 测试验证修复结果


---

## 🧠 深度学习预测功能测试 (新增 2026-03-06)

### TEST-DL-001: 单元测试 - LSTM 模型前向传播
**优先级:** P0  
**预计工时:** 0.5 天  
**依赖:** CODE-DL-002  
**交付物:** `tests/unit/test_lstm_model.py`

**需要完成:**
1. 测试 LSTM 模型初始化
2. 测试前向传播输出形状
3. 测试不同序列长度的输入
4. 测试批量数据处理

**测试用例:**
- test_lstm_init_success
- test_lstm_forward_output_shape
- test_lstm_variable_sequence_length
- test_lstm_batch_processing

---

### TEST-DL-002: 单元测试 - Transformer 模型前向传播
**优先级:** P1  
**预计工时:** 0.5 天  
**依赖:** CODE-DL-003  
**交付物:** `tests/unit/test_transformer_model.py`

**需要完成:**
1. 测试 Transformer 模型初始化
2. 测试位置编码正确性
3. 测试前向传播输出形状
4. 测试注意力掩码 (如果实现)

---

### TEST-DL-003: 集成测试 - 特征工程流水线
**优先级:** P0  
**预计工时:** 0.5 天  
**依赖:** CODE-DL-004  
**交付物:** `tests/integration/test_feature_pipeline.py`

**需要完成:**
1. 测试技术指标特征计算
2. 测试特征标准化
3. 测试序列构建
4. 测试数据集划分

**测试场景:**
- 完整数据流水线测试
- 缺失值处理测试
- 特征维度验证

---

### TEST-DL-004: 集成测试 - 模型训练流程
**优先级:** P0  
**预计工时:** 1 天  
**依赖:** CODE-DL-005  
**交付物:** `tests/integration/test_training_pipeline.py`

**需要完成:**
1. 测试完整训练循环
2. 测试验证循环
3. 测试早停机制
4. 测试模型保存和加载
5. 测试训练指标记录

**测试场景:**
- 小数据集快速训练测试
- 损失下降验证
- 检查点保存验证

---

### TEST-DL-005: 回测验证 - 历史数据回测
**优先级:** P1  
**预计工时:** 2 天  
**依赖:** CODE-DL-007  
**交付物:** `tests/backtest/test_historical_backtest.py`, `docs/reports/backtest_report.md`

**需要完成:**
1. 准备历史回测数据集
2. 实现回测引擎
3. 计算回测指标 (准确率、夏普比率、最大回撤)
4. 生成回测报告

**回测指标:**
- 预测准确率 (目标：>55%)
- 夏普比率 (目标：>1.0)
- 最大回撤 (目标：<20%)
- 年化收益 (目标：>15%)

---

### TEST-DL-006: 性能测试 - 预测延迟和吞吐量
**优先级:** P2  
**预计工时:** 1 天  
**依赖:** CODE-DL-007  
**交付物:** `tests/performance/test_prediction_latency.py`

**需要完成:**
1. 测试单次预测延迟 (目标：<100ms)
2. 测试批量预测吞吐量
3. 测试并发预测性能
4. 测试 GPU 加速效果 (如果可用)

**性能目标:**
- 单次预测延迟：<100ms
- 批量预测 (100 条)：<500ms
- 并发支持：>10 QPS

---

### TEST-DL-007: 数据质量测试 (NEW - 2026-03-06 设计复查)
**优先级:** P0  
**预计工时:** 0.5 天  
**依赖:** CODE-DL-014  
**交付物:** `tests/unit/test_data_validation.py`

**需要完成:**
1. 测试缺失值检测功能
2. 测试异常值检测功能
3. 测试数据分布分析
4. 验证数据质量报告生成

**测试用例:**
- test_missing_value_detection
- test_outlier_detection_3sigma
- test_outlier_detection_isolation_forest
- test_data_distribution_analysis
- test_validation_report_generation

---

### TEST-DL-008: 基线模型对比测试 (NEW - 2026-03-06 设计复查)
**优先级:** P1  
**预计工时:** 1 天  
**依赖:** CODE-DL-009  
**交付物:** `tests/integration/test_baseline_comparison.py`, `docs/reports/baseline_comparison_report.md`

**需要完成:**
1. 测试基线模型训练流程
2. 对比 LSTM vs LR/RF/XGBoost 准确率
3. 对比 Transformer vs LR/RF/XGBoost 准确率
4. 生成基线对比报告

**对比指标:**
- 预测准确率 (Accuracy)
- F1-Score
- AUC-ROC
- 训练时间
- 推理延迟

**预期结果:**
- LSTM/Transformer 准确率应优于基线模型
- 深度学习模型训练时间更长但推理延迟可接受

---

### TEST-DL-009: 模型稳定性测试 (NEW - 2026-03-06 设计复查)
**优先级:** P1  
**预计工时:** 0.5 天  
**依赖:** CODE-DL-005  
**交付物:** `tests/integration/test_model_stability.py`

**需要完成:**
1. 多次训练验证结果一致性 (固定随机种子)
2. 测试不同随机种子下的结果波动
3. 验证早停机制稳定性
4. 生成稳定性测试报告

**测试方法:**
- 固定种子训练 5 次，验证结果一致性
- 变化种子训练 5 次，统计准确率标准差
- 目标：准确率标准差 < 2%

---

### TEST-DL-010: 特征消融实验 (NEW - 2026-03-06 设计复查)
**优先级:** P2  
**预计工时:** 1 天  
**依赖:** CODE-DL-004  
**交付物:** `tests/integration/test_feature_ablation.py`, `docs/reports/feature_ablation_report.md`

**需要完成:**
1. 移除价格衍生特征，评估影响
2. 移除技术指标特征，评估影响
3. 移除波动率特征，评估影响
4. 移除成交量特征，评估影响
5. 生成特征消融实验报告

**实验设计:**
| 实验组 | 移除特征 | 预期准确率下降 |
|--------|---------|---------------|
| Full | 无 | - |
| No-Price-Derived | price_change, price_change_pct, etc. | < 2% |
| No-Technical | MACD, RSI, KDJ, etc. | 5-10% |
| No-Volatility | atr14, volatility_20 | 3-5% |
| No-Volume | volume_ratio, turnover_rate | 2-4% |

---

### TEST-DL-011: GPU 加速效果验证 (NEW - 2026-03-06 设计复查)
**优先级:** P1  
**预计工时:** 0.5 天  
**依赖:** CODE-DL-012  
**交付物:** `tests/performance/test_gpu_acceleration.py`, `docs/reports/gpu_acceleration_report.md`

**需要完成:**
1. 测试 CPU 训练时间 (单 epoch)
2. 测试 GPU 训练时间 (单 epoch)
3. 计算加速比
4. 验证混合精度训练效果
5. 生成 GPU 加速效果报告

**性能目标:**
- CPU 训练：~2 小时/epoch
- GPU 训练 (RTX 2070): ~5-10 分钟/epoch
- 加速比：12-24 倍
- 混合精度额外加速：1.5-2 倍

---
