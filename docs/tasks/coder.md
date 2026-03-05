# Coder 任务列表

**负责人:** qclaw-coder  
**最后更新:** 2026-03-05 19:13  
**Cron:** 每 5 分钟自动检查

---

## 📍 工作流说明

**任务读取位置:** `docs/tasks/coder.md` (本文件)  
**交付物提交位置:** 
- 前端代码：`webui/`
- 后端代码：`src/`
- **单元测试:** `tests/`, `webui/src/**/*.test.tsx`

**提交流程:**
```bash
git add src/ webui/ tests/
git commit -m "[Code] 任务名称"
git push origin main
```

---

## 🔄 进行中

| 任务 ID | 任务名称 | 进度 | 备注 |
|---------|---------|------|------|
| CODE-003 | 量化指标模块 | 0% | 开始开发 |
| CODE-TEST-001 | 后端单元测试 | 0% | 新增任务 |

---

## ⏳ 待开始

| 任务 ID | 任务名称 | 依赖 | 备注 |
|---------|---------|------|------|
| CODE-004 | AI 建议模块 | - | 需要 OpenClaw API |
| CODE-005 | 新闻资讯模块 | - | - |
| CODE-006 | 后端 API 开发 | - | FastAPI |
| CODE-TEST-002 | 前端单元测试 | CODE-003~005 | 组件测试 |

---

## ✅ 已完成

| 任务 ID | 任务名称 | 完成日期 | 交付物 |
|---------|---------|----------|--------|
| CODE-001 | 项目初始化 | 2026-03-05 | `webui/` |
| CODE-002 | 大盘指标模块 | 2026-03-05 | `webui/src/components/MarketCard/` |

---

## 📋 任务说明

### CODE-003: 量化指标模块 🔄

**描述:** 实现 MACD、KDJ、RSI 等技术指标图表  
**交付物:**
- `webui/src/components/IndicatorChart/`
- `src/indicators/` 技术指标实现

**技术要点:**
- ECharts 多图表布局
- 指标数据计算
- 交互式图表

### CODE-TEST-001: 后端单元测试 🔄

**描述:** 为 Python 模块编写单元测试（Coder 职责）  
**交付物:** `tests/test_*.py`

**测试范围:**
- [ ] `test_config.py` - 配置管理测试
- [ ] `test_utils.py` - 工具函数测试
- [ ] `test_indicators.py` - 技术指标测试
- [ ] `test_openclaw_client.py` - OpenClaw 客户端测试
- [ ] `test_api.py` - API 接口测试

**命令:**
```bash
pytest tests/ --cov=src --cov-report=html
```

**覆盖率目标:** >80%

### CODE-TEST-002: 前端单元测试 ⏳

**描述:** 为 React 组件编写单元测试（Coder 职责）  
**依赖:** CODE-003~005 完成  
**交付物:** `webui/src/**/*.test.tsx`

**测试范围:**
- [x] `App.test.tsx` - App 组件测试
- [x] `Layout.test.tsx` - 布局组件测试
- [x] `marketSlice.test.ts` - Redux 状态测试
- [x] `adviceSlice.test.ts` - Redux 状态测试
- [ ] `IndicatorChart.test.tsx` - 指标图表测试
- [ ] `NewsList.test.tsx` - 新闻列表测试
- [ ] `AIAdvice.test.tsx` - AI 建议测试

**命令:**
```bash
cd webui
npm test
npm run test:coverage
```

**覆盖率目标:** >70%

---

## 🧪 测试职责说明

**Coder 负责:**
- ✅ 单元测试（Unit Tests）
- ✅ 测试自己的代码
- ✅ 保证测试覆盖率
- ✅ 修复测试失败

**Tester 负责:**
- ✅ 集成测试（Integration Tests）
- ✅ 系统测试（System Tests）
- ✅ E2E 测试（End-to-End）
- ✅ 性能测试（Performance Tests）
- ✅ Docker 环境自动化测试

---

**说明:** 
- ✅ 只读取本文件获取任务
- ✅ 代码和单元测试提交到对应目录
- ❌ 不要读取其他角色的任务文件
