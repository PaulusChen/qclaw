# PM 超时告警机制

**版本**: v1.0  
**实施时间**: 2026-03-06  
**目标**: PM 超时立即告警，防止任务阻塞

---

## 🎯 告警规则

### 告警级别

| 级别 | 触发条件 | 通知方式 | 处理方式 |
|------|---------|---------|---------|
| **⚠️ 警告** | PM 连续超时 2 次 | 飞书消息 | 检查 PM 日志 |
| **🚨 紧急** | PM 连续超时 3 次 | 飞书@用户 | 启用备用方案 |
| **🔥 严重** | PM 连续超时 5 次 | 飞书@用户 + 邮件 | 手动介入 |

---

## 📬 告警通知模板

### 警告通知 (2 次超时)

```
⚠️ PM 超时警告

PM 连续超时 2 次，可能原因:
- 任务过于复杂
- 唤醒角色过多
- 系统资源不足

建议检查:
1. 查看 PM 日志：tail -f ~/.openclaw/logs/qclaw-pm.log
2. 检查任务文件是否过大
3. 确认唤醒的角色是否正常

当前状态:
- 待开始任务：{count}
- 最近超时：{timestamp}
```

### 紧急通知 (3 次超时)

```
🚨 PM 超时紧急告警

PM 连续超时 3 次，已自动启用备用方案！

备用方案:
1. 启用角色自检机制 (每 30 分钟)
2. Coder/Tester 可以主动检查任务
3. 防止任务阻塞

需要立即处理:
1. 检查 PM 为什么超时
2. 优化 PM 心跳逻辑
3. 确认角色自检正常

当前阻塞任务:
- {task_list}
```

---

## 🔧 告警实现

### PM 心跳监控脚本

```python
#!/usr/bin/env python3
# ~/.openclaw/scripts/pm_timeout_monitor.py

import json
import sys
from datetime import datetime

def check_pm_timeouts():
    # 读取 PM 执行历史
    with open("~/.openclaw/cron/jobs.json") as f:
        jobs = json.load(f)
    
    pm_job = [j for j in jobs if j['agentId']=='qclaw-pm'][0]
    state = pm_job['state']
    
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_run_status = state.get('lastRunStatus', 'ok')
    
    # 判断告警级别
    if consecutive_errors >= 5:
        send_alert("CRITICAL", consecutive_errors)
    elif consecutive_errors >= 3:
        send_alert("URGENT", consecutive_errors)
    elif consecutive_errors >= 2:
        send_alert("WARNING", consecutive_errors)
    
    return consecutive_errors

def send_alert(level, count):
    # 飞书通知
    message = {
        "CRITICAL": "🔥 PM 连续超时{count}次！需要立即手动介入！",
        "URGENT": "🚨 PM 连续超时{count}次，已启用备用方案！",
        "WARNING": "⚠️ PM 连续超时{count}次，请检查原因"
    }[level]
    
    # 发送飞书消息
    send_feishu(message.format(count=count))
    
    # 记录日志
    log(f"PM timeout alert: {level} ({count} times)")

if __name__ == "__main__":
    check_pm_timeouts()
```

### Cron 配置 (每 5 分钟检查)

```json
{
  "id": "pm-timeout-monitor",
  "schedule": "*/5 * * * *",
  "command": "~/.openclaw/scripts/pm_timeout_monitor.py"
}
```

---

## 🔄 备用方案

### 角色自检机制

**触发条件**: PM 连续超时≥3 次

**配置**:
```json
{
  "qclaw-coder": {
    "cron": "*/30 * * * *",
    "enabled": true  // PM 正常时为 false
  },
  "qclaw-tester": {
    "cron": "*/30 * * * *",
    "enabled": true
  }
}
```

**自检逻辑**:
```python
# 角色自检 (每 30 分钟)
tasks = read_own_task_file()
pending = find_pending_tasks(tasks)

if pending:
    # 有待开始任务 → 执行
    execute_task(pending[0])
    log("PM 超时，角色自检执行任务")
else:
    # 无任务 → 立即返回
    log("无待开始任务，休眠")
```

---

## 📊 监控指标

### PM 健康度

| 指标 | 健康 | 警告 | 危险 |
|------|------|------|------|
| 连续超时次数 | 0 | 2-3 | ≥5 |
| 平均执行时间 | <5 秒 | 5-30 秒 | >30 秒 |
| 心跳成功率 | 100% | 95-99% | <95% |
| 任务阻塞时间 | 0 分钟 | 5-30 分钟 | >30 分钟 |

### 告警历史

```markdown
## 告警记录

| 时间 | 级别 | 原因 | 处理 | 状态 |
|------|------|------|------|------|
| 2026-03-06 00:55 | WARNING | PM 超时 2 次 | 检查日志 | 已解决 |
| 2026-03-06 00:58 | URGENT | PM 超时 3 次 | 启用备用 | 处理中 |
```

---

## 📝 运维手册

### PM 超时处理流程

```
1. 收到告警通知
    ↓
2. 查看 PM 日志
   tail -f ~/.openclaw/logs/qclaw-pm.log
    ↓
3. 分析超时原因
   - 任务太复杂？
   - 唤醒角色太多？
   - 系统资源不足？
    ↓
4. 采取措施
   - 简化 PM 任务
   - 减少唤醒数量
   - 增加 timeout 时间
    ↓
5. 验证修复
   - 手动触发 PM
   - 观察执行时间
   - 确认不再超时
    ↓
6. 关闭告警
   - 重置超时计数
   - 记录根因和解决方案
```

### 手动触发 PM

```bash
# 手动运行 PM 心跳
openclaw cron run qclaw-pm

# 查看执行日志
tail -f ~/.openclaw/logs/qclaw-pm.log

# 检查超时计数
cat ~/.openclaw/cron/jobs.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
pm=[j for j in d['jobs'] if j['agentId']=='qclaw-pm'][0]
print(f\"连续超时：{pm['state'].get('consecutiveErrors', 0)}\")
"
```

---

## 🎯 预防措施

### 日常检查

- [ ] PM 心跳成功率 100%
- [ ] PM 执行时间 <5 秒
- [ ] 无待开始任务阻塞>5 分钟
- [ ] 角色自检机制正常 (备用)

### 每周回顾

- [ ] 分析 PM 超时原因
- [ ] 优化 PM 心跳逻辑
- [ ] 更新告警阈值
- [ ] 演练备用方案

---

*目标：PM 零超时，零阻塞！*
