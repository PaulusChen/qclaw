# QCLaw 防阻塞机制

**版本**: v1.0  
**实施时间**: 2026-03-06  
**目标**: 零超时，零阻塞

---

## 🎯 阻塞场景分析

### 场景 1: PM 超时导致阻塞

```
PM 超时
    ↓
无法唤醒角色
    ↓
任务待开始>30 分钟
    ↓
项目阻塞
```

**预防方案**:
- ✅ 简化 PM 心跳 (<3 秒)
- ✅ 超时告警机制
- ✅ 角色自检备用方案

---

### 场景 2: 角色执行超时

```
角色执行任务
    ↓
遇到复杂问题
    ↓
执行超时 (10 分钟)
    ↓
PM 不知道进度
    ↓
无法协调下一角色
```

**预防方案**:
- ✅ 角色进度汇报 (每 2 分钟)
- ✅ 超时自动告警
- ✅ 任务拆分 (大任务→小任务)

---

### 场景 3: 任务依赖阻塞

```
TASK-A 完成
    ↓
需要唤醒 TASK-B
    ↓
但 TASK-B 依赖外部服务
    ↓
TASK-B 无法执行
    ↓
阻塞
```

**预防方案**:
- ✅ 依赖检查 (执行前验证)
- ✅ 降级方案 (服务不可用时的处理)
- ✅ 优先级调整 (先执行其他任务)

---

## ✅ 防阻塞机制

### 机制 1: PM 心跳优化 ⭐⭐⭐

**新的 PM 心跳** (每 10 分钟):
```python
# 只做一件事：发现待开始任务 → 立即唤醒

start_time = now()

for role in [designer, reviewer, coder, tester]:
    # 只读取前 20 行
    content = read_fast(f"docs/tasks/{role}.md", lines=20)
    
    # 只检查"待开始"部分
    if "待开始" in content:
        spawn_agent(f"qclaw-{role}", task="check_tasks")
        log(f"唤醒 {role}")

elapsed = now() - start_time
log(f"心跳完成，耗时 {elapsed}秒")

if elapsed > 30:
    alert("⚠️ PM 心跳耗时过长")
```

**目标**: <3 秒完成

---

### 机制 2: 角色进度汇报 ⭐⭐

**角色执行中** (每 2 分钟):
```python
# 长任务 (>5 分钟) 需要定期汇报进度
if task_duration > 5 minutes:
    send_progress_update(
        task_id=task.id,
        progress=calculate_progress(),
        eta=estimated_completion(),
        blockers=get_blockers()
    )
    
    # PM 接收进度更新
    on_progress_update(role, progress):
        log(f"{role} 进度：{progress}%")
        
        if progress < 50% and duration > 10 minutes:
            alert("⚠️ 任务执行过慢")
```

**效果**: PM 实时了解进度，及时发现阻塞

---

### 机制 3: 超时自动告警 ⭐⭐⭐

**告警规则**:

| 超时类型 | 阈值 | 告警 | 处理 |
|---------|------|------|------|
| PM 心跳 | >30 秒 | 警告 | 检查日志 |
| PM 心跳 | >60 秒 | 紧急 | 启用备用 |
| 角色执行 | >10 分钟 | 警告 | 询问进度 |
| 角色执行 | >30 分钟 | 紧急 | 手动介入 |
| 任务阻塞 | >30 分钟 | 警告 | PM 协调 |
| 任务阻塞 | >1 小时 | 紧急 | 用户介入 |

**告警通知**:
```python
# 监控脚本 (每 5 分钟)
check_pm_timeouts()
check_role_timeouts()
check_task_blockers()

if any_timeout():
    send_feishu_alert()
```

---

### 机制 4: 角色自检备用 ⭐⭐

**正常模式**:
```
角色 cron: 禁用
只由 PM 唤醒
```

**备用模式** (PM 连续超时≥3 次):
```
角色 cron: 启用 (每 30 分钟)
角色主动检查任务
防止阻塞
```

**切换逻辑**:
```python
# 监控 PM 超时
if pm_consecutive_timeouts >= 3:
    # 启用角色自检
    enable_role_self_check()
    
    # 发送告警
    send_feishu("🚨 PM 连续超时 3 次，已启用角色自检")
    
    # 角色每 30 分钟检查
    for role in [coder, tester]:
        set_cron(role, "*/30 * * * *", enabled=True)
```

---

### 机制 5: 任务优先级队列 ⭐⭐

**优先级定义**:

| 优先级 | 类型 | 响应时间 | 示例 |
|--------|------|---------|------|
| **P0** | 紧急 Bug | <5 分钟 | 生产环境 Bug |
| **P1** | 关键路径 | <10 分钟 | 阻塞其他任务 |
| **P2** | 常规任务 | <30 分钟 | 功能开发 |
| **P3** | 优化改进 | 下次心跳 | 代码优化 |

**处理逻辑**:
```python
# PM 心跳
tasks = get_all_pending_tasks()
sorted_tasks = sort_by_priority(tasks)

for task in sorted_tasks:
    if task.priority == P0:
        spawn_immediately()
    elif task.priority == P1:
        spawn_within_10min()
    else:
        spawn_within_30min()
```

---

## 📊 监控 Dashboard

### 实时指标

```
PM 状态:
- 心跳成功率：100% ✅
- 平均执行时间：2.3 秒 ✅
- 连续超时：0 ✅

角色状态:
- Designer: 空闲 ✅
- Coder: 执行中 (CODE-009, 45%) ✅
- Tester: 空闲 ✅
- Reviewer: 空闲 ✅

任务状态:
- 待开始：2
- 进行中：1
- 已完成：28
- 阻塞：0 ✅
```

### 告警历史

```markdown
## 最近告警

| 时间 | 级别 | 类型 | 处理 | 状态 |
|------|------|------|------|------|
| 00:58 | 🚨 | PM 超时 | 启用备用 | 已解决 |
| 00:55 | ⚠️ | PM 超时 | 检查日志 | 已解决 |
```

---

## 📝 运维手册

### 阻塞处理流程

```
1. 收到阻塞告警
    ↓
2. 确认阻塞类型
   - PM 超时？
   - 角色超时？
   - 任务依赖？
    ↓
3. 采取对应措施
   - PM 超时 → 启用角色自检
   - 角色超时 → 询问进度/手动介入
   - 任务依赖 → 协调资源/调整优先级
    ↓
4. 验证解决
   - 任务继续执行
   - 告警解除
    ↓
5. 记录根因
   - 更新文档
   - 防止复发
```

### 快速检查命令

```bash
# 检查 PM 状态
cat ~/.openclaw/cron/jobs.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
pm=[j for j in d['jobs'] if j['agentId']=='qclaw-pm'][0]
print(f\"PM 连续超时：{pm['state'].get('consecutiveErrors', 0)}\")
print(f\"上次状态：{pm['state'].get('lastRunStatus', 'N/A')}\")
"

# 检查待开始任务
grep -h "待开始" /home/openclaw/qclaw/docs/tasks/*.md

# 检查角色执行中
cat ~/.openclaw/logs/qclaw-*.log | grep "执行中" | tail -10

# 手动触发 PM
openclaw cron run qclaw-pm
```

---

## 🎯 持续改进

### 每周回顾

- [ ] 分析阻塞原因
- [ ] 优化告警阈值
- [ ] 更新防阻塞机制
- [ ] 演练备用方案

### 每月优化

- [ ] 审查 PM 心跳逻辑
- [ ] 优化角色自检机制
- [ ] 更新优先级定义
- [ ] 改进监控 Dashboard

---

*目标：零超时，零阻塞，项目全速前进！*
