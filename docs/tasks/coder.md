# Coder 任务列表

**负责人:** qclaw-coder  
**最后更新:** 2026-03-06 00:17  
**Cron:** 每 5 分钟自动检查

---

## 🚨 新任务 - 请处理

### CODE-008: 前端服务启动修复
**优先级:** 高  
**依赖:** 无  
**交付物:** 前端服务可在 localhost:3000 正常启动

**问题描述:**
E2E 测试全部失败 (18 项)，原因是前端服务未启动，localhost:3000 连接被拒绝。

**需要完成:**
1. 检查前端构建配置 (webui/vite.config.ts)
2. 确保 `npm run dev` 或 `npm run build && npm run preview` 可以正常启动服务
3. 验证服务监听在 localhost:3000
4. 更新启动脚本或 Docker 配置

**测试验证:**
```bash
cd webui
npm run dev
# 访问 http://localhost:3000 确认页面加载
```

---

### CODE-009: 补充前端组件单元测试
**优先级:** 中  
**依赖:** CODE-008  
**交付物:** webui/src/components/ 下的组件测试文件

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

**最近检查:** 2026-03-06 00:17 - 有待处理任务 CODE-008, CODE-009

---

**说明:** 本文件仅供 qclaw-coder 读取，避免上下文污染。
