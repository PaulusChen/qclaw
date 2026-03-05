# Tester 任务列表

**负责人:** qclaw-tester  
**最后更新:** 2026-03-05 19:36  
**Cron:** 每 5 分钟自动检查

---

## 📍 工作流说明

**任务读取位置:** `docs/tasks/tester.md` (本文件)  
**交付物提交位置:** `tests/`, `docs/reports/`  
**提交流程:**
```bash
git add tests/ docs/reports/
git commit -m "[Test] 任务名称"
git push origin main
```

---

## 🔄 进行中

| 任务 ID | 任务名称 | 进度 | 备注 |
|---------|---------|------|------|
| TEST-001 | 前端单元测试 | 45% | 已创建基础测试用例，修复 format.ts 和测试用例 |
| TEST-002 | 后端单元测试 | 60% | 技术指标测试完成，utils 测试完成 |

---

## ⏳ 待开始

| 任务 ID | 任务名称 | 依赖 | 优先级 |
|---------|---------|------|--------|
| TEST-003 | 组件集成测试 | TEST-001 | 高 |
| TEST-004 | API 接口测试 | CODE-006 | 高 |
| TEST-005 | E2E 端到端测试 | CODE-006 | 中 |
| TEST-006 | 性能基准测试 | CODE-006 | 中 |

---

## ✅ 已完成

| 任务 ID | 任务名称 | 完成日期 | 交付物 |
|---------|---------|----------|--------|
| TEST-MVP-001 | MVP 功能测试 | 2026-03-05 | `docs/reports/` |
| TEST-MVP-002 | MVP 性能测试 | 2026-03-05 | `docs/reports/` |

---

## 📋 详细任务说明

### TEST-001: 前端单元测试 🔄

**描述:** 为 React 组件和 Redux slices 编写单元测试  
**技术栈:** Vitest + React Testing Library + Jest DOM  
**交付物:** `webui/src/**/*.test.tsx`

**测试范围:**
- [x] App 组件测试 ✅
- [x] Layout 组件测试 ✅
- [x] marketSlice 测试 ✅
- [x] adviceSlice 测试 ✅
- [x] format 工具函数测试 ✅
- [ ] IndicatorChart 组件测试
- [ ] NewsList 组件测试
- [ ] AIAdvice 组件测试
- [ ] Redux hooks 测试
- [ ] API services 测试

**命令:**
```bash
cd webui
npm test
npm run test:coverage
```

**最新结果:** 21 tests passed (100%)

**修复内容:**
- 修复 `formatPercent(0)` 返回 `'+0.00%'`
- 创建 `App.tsx`, `Layout/index.tsx`, `adviceSlice.ts`

### TEST-002: 后端单元测试 🔄

**描述:** 为 Python 模块编写单元测试  
**技术栈:** pytest + pytest-cov  
**交付物:** `tests/test_*.py`

**测试范围:**
- [ ] config.py 配置管理测试
- [x] utils.py 工具函数测试 (42 tests ✅)
- [x] indicators/ 技术指标测试 (115 tests ✅)
- [ ] integration/ OpenClaw 客户端测试
- [ ] data/ 数据获取测试

**命令:**
```bash
pytest tests/ --cov=src
```

**最新结果:** 157 tests passed (100%)

### TEST-003: 组件集成测试 ⏳

**描述:** 测试组件间交互和数据流  
**交付物:** `webui/src/**/*.integration.test.tsx`

**测试场景:**
- [ ] Dashboard 页面完整流程
- [ ] 数据加载 - 显示 - 刷新流程
- [ ] 错误处理和边界情况
- [ ] 用户交互响应

### TEST-004: API 接口测试 ⏳

**描述:** 测试后端 API 接口  
**依赖:** CODE-006 后端完成  
**交付物:** `tests/test_api_*.py`

**测试范围:**
- [ ] GET /api/market/indices
- [ ] GET /api/indicators/technical
- [ ] GET /api/advice/daily
- [ ] GET /api/news/list
- [ ] 错误响应测试
- [ ] 认证和权限测试

### TEST-005: E2E 端到端测试 ⏳

**描述:** 完整的用户流程测试  
**依赖:** CODE-006 后端完成  
**技术栈:** Playwright  
**交付物:** `tests/e2e/`

**测试场景:**
- [ ] 用户访问首页
- [ ] 查看大盘指标
- [ ] 查看 AI 建议
- [ ] 查看新闻资讯
- [ ] 数据自动刷新

### TEST-006: 性能基准测试 ⏳

**描述:** 性能基准和负载测试  
**依赖:** CODE-006 后端完成  
**交付物:** `docs/reports/performance-benchmark.md`

**测试指标:**
- [ ] 页面加载时间 < 3s
- [ ] API 响应时间 < 500ms
- [ ] 图表渲染时间 < 1s
- [ ] 并发用户支持 > 100

---

## 📊 测试覆盖率目标

| 模块 | 当前 | 目标 | 状态 |
|------|------|------|------|
| 前端组件 | 35% | 70% | 🟡 进行中 |
| Redux Slices | 90% | 90% | ✅ 达标 |
| 工具函数 | 100% | 100% | ✅ 达标 |
| 后端 API | 0% | 80% | ⏳ 待开始 |
| 集成测试 | 0% | 60% | ⏳ 待开始 |

---

## 📝 测试规范

### 命名规范
- 测试文件：`*.test.ts` / `test_*.py`
- 测试用例：`should + 预期行为`
- 描述块：`describe('模块名')`

### 测试结构
```typescript
describe('ComponentName', () => {
  it('should render correctly', () => {
    // 测试代码
  })

  it('should handle edge case', () => {
    // 边界情况测试
  })
})
```

### 断言优先级
1. 使用 `@testing-library/jest-dom` 断言
2. 优先测试用户可见行为
3. 避免测试实现细节

---

**说明:** 
- ✅ 优先保证核心功能测试覆盖
- ✅ 测试代码也要保持高质量
- ✅ 持续集成中自动运行测试
