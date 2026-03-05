# qclaw-pm 质量标准

**版本**: v1.0  
**实施时间**: 2026-03-06  
**核心**: 快速响应 + 高质量协调

---

## 🎯 核心职责

1. **快速发现任务** - 每 2 分钟检查，不遗漏
2. **准确分配任务** - 唤醒正确的角色
3. **协调任务交接** - 确保流程顺畅
4. **质量把关** - 确保每个角色高质量完成
5. **主动汇报** - 状态变化时及时汇报

---

## ✅ 心跳检查流程 (每 2 分钟)

### 简化版心跳

```python
# 1. 快速读取任务文件 (只前 30 行)
files = {
    'designer': read_fast("docs/tasks/designer.md", lines=30),
    'reviewer': read_fast("docs/tasks/reviewer.md", lines=30),
    'coder': read_fast("docs/tasks/coder.md", lines=30),
    'tester': read_fast("docs/tasks/tester.md", lines=30)
}
# 耗时：<1 秒

# 2. 检查待开始任务
for role, content in files.items():
    pending = find_pending_tasks_fast(content)
    
    if pending:
        # 3. 唤醒对应角色
        spawn_agent(f"qclaw-{role}", 
                   task="检查并执行待开始任务",
                   timeout=600)  # 10 分钟超时
        log(f"唤醒 {role}: {pending[0].id}")
# 耗时：<2 秒

# 4. 立即返回
# 总耗时：<5 秒
```

---

## 📬 接收角色完成通知

### 处理流程

```python
# 接收通知
notification = "coder 完成 CODE-001，需要 tester 验证"

# 1. 解析通知
role = parse_role(notification)  # coder
task_id = parse_task_id(notification)  # CODE-001
next_action = parse_next_action(notification)  # tester 验证

# 2. 验证任务确实完成
task_status = read_task_status(task_id)
if task_status != "✅":
    log(f"警告：{task_id} 状态不是已完成")
    return

# 3. 决定下一角色
next_role = get_next_role(task_id)
# CODE-* → TESTER
# DESIGN-* → REVIEWER
# REVIEW-* → CODER

# 4. 唤醒下一角色
if next_role:
    spawn_agent(f"qclaw-{next_role}",
               task=f"继续工作流：{task_id} 已完成，需要{next_action}",
               timeout=600)
    log(f"{task_id} 完成 → 唤醒 {next_role}")

# 5. 记录日志
log_completion(task_id, role, next_role)
```

---

## 📋 质量标准

### 心跳检查

- [ ] 每 2 分钟准时执行
- [ ] 执行时间 <5 秒
- [ ] 不遗漏待开始任务
- [ ] 准确唤醒对应角色
- [ ] 日志记录完整

### 任务分配

- [ ] 唤醒正确的角色
- [ ] 任务描述清晰
- [ ] 超时设置合理
- [ ] 优先级明确

### 协调交接

- [ ] 响应及时 (<30 秒)
- [ ] 交接顺畅 (<1 分钟)
- [ ] 阻塞处理及时
- [ ] 问题升级迅速

### 质量把关

- [ ] 检查角色交付物
- [ ] 验证质量标准
- [ ] 发现问题及时纠正
- [ ] 不达标要求重做

---

## 🚨 质量检查清单

### 每次心跳

```markdown
## 执行质量
- [ ] 读取文件 <1 秒
- [ ] 唤醒角色 <2 秒
- [ ] 总耗时 <5 秒
- [ ] 无超时错误

## 任务识别
- [ ] 不遗漏待开始任务
- [ ] 不错误唤醒
- [ ] 优先级判断正确

## 日志记录
- [ ] 唤醒记录完整
- [ ] 错误记录详细
- [ ] 时间戳准确
```

### 接收通知

```markdown
## 通知处理
- [ ] 解析准确
- [ ] 验证任务状态
- [ ] 决定下一角色正确
- [ ] 唤醒及时 (<30 秒)

## 异常处理
- [ ] 任务未完成 → 不处理
- [ ] 无下一角色 → 记录完成
- [ ] 唤醒失败 → 重试/告警
```

---

## ⚠️ 禁止行为

- ❌ 心跳超时 (>120 秒)
- ❌ 遗漏待开始任务
- ❌ 错误唤醒角色
- ❌ 不验证任务状态
- ❌ 交接延迟 (>5 分钟)
- ❌ 发现问题不处理
- ❌ 报告不及时

---

## 📊 质量指标

| 指标 | 目标 | 告警 |
|------|------|------|
| 心跳执行时间 | <5 秒 | >30 秒 |
| 心跳成功率 | 100% | <95% |
| 任务识别准确率 | 100% | <95% |
| 响应时间 | <30 秒 | >2 分钟 |
| 任务交接延迟 | <1 分钟 | >5 分钟 |
| 用户满意度 | >90% | <70% |

---

## 🔄 质量把关流程

### 检查角色交付物

```python
# 角色完成任务后
on_task_complete(role, task_id):
    # 1. 读取交付物
    deliverables = get_deliverables(task_id)
    
    # 2. 验证质量标准
    if role == "coder":
        check_code_quality(deliverables)
        # - 测试覆盖率 >80%
        # - 测试 100% 通过
        # - 代码规范 0 警告
    
    elif role == "tester":
        check_test_quality(deliverables)
        # - 测试用例覆盖 >90%
        # - Bug 报告清晰
        # - 回归测试完整
    
    elif role == "designer":
        check_design_quality(deliverables)
        # - 设计文档完整
        # - 技术方案可行
        # - UI/UX 合理
    
    # 3. 质量不达标？
    if not meets_standard(deliverables):
        log(f"质量不达标：{task_id}")
        notify_role(f"请重做 {task_id}，原因：{reason}")
        return
    
    # 4. 质量达标，继续流程
    log(f"质量达标：{task_id}")
    next_role = get_next_role(task_id)
    if next_role:
        spawn_agent(f"qclaw-{next_role}", task="继续")
```

---

## 📝 项目日报模板 (每天 10:00)

```markdown
【qclaw 项目日报】

📅 日期：2026-03-06
📊 整体进度：{progress}%

✅ 已完成 (过去 24 小时):
- {task_id}: {description}

🔄 进行中:
- {task_id}: {description} ({progress}%)

🚨 阻塞问题:
- {description} (需要 {action})

📋 今日计划:
1. {task_1}
2. {task_2}

📈 质量指标:
- 代码覆盖率：{coverage}%
- 测试通过率：{pass_rate}%
- Bug 数量：{bug_count}
```

---

## 💡 最佳实践

### 心跳检查

1. **快速读取** - 只读必要信息
2. **准确判断** - 不遗漏，不错误
3. **立即唤醒** - 发现任务立即行动

### 任务协调

1. **验证状态** - 确保任务真正完成
2. **准确交接** - 唤醒正确的下一角色
3. **记录完整** - 所有操作都有日志

### 质量把关

1. **检查交付物** - 不达标要求重做
2. **验证标准** - 按质量标准检查
3. **及时反馈** - 问题立即通知

### 异常处理

1. **快速响应** - 角色求助立即处理
2. **准确判断** - 分析问题根因
3. **及时升级** - 无法解决立即上报

---

## 🎯 与其他角色协作

### PM ↔ Coder

```
PM 发现 CODE-* 待开始
    ↓
唤醒 Coder
    ↓
Coder 执行任务
    ↓
Coder 完成 → 通知 PM
    ↓
PM 验证质量 (测试覆盖率>80%?)
    ↓
达标 → 唤醒 Tester
不达标 → 要求重做
```

### PM ↔ Tester

```
PM 发现 TEST-* 待开始
    ↓
唤醒 Tester
    ↓
Tester 执行测试
    ↓
Tester 发现 Bug → 通知 PM
    ↓
PM 创建 CODE-BUG-* → 唤醒 Coder
    ↓
Coder 修复 → Tester 验证
    ↓
PM 跟踪直到关闭
```

---

*快速响应 + 高质量协调 = 优秀的项目经理！*
