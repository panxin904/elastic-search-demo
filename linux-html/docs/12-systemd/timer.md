---
title: systemd Timer
date: 2026-08-15  # date-auto-injected
---

# systemd Timer

> cron 的现代替代。

## ⏰ 两种 Timer

```ini
# 实时 Timer（基于 monotonic clock，从机器启动计时）
OnBootSec=                    # 启动后
OnStartupSec=                 # systemd 启动后
OnUnitActiveSec=              # 上次 Unit 启动后
OnUnitInactiveSec=            # 上次 Unit 停止后

# 实时钟（基于日历）
OnCalendar=                   # 类似 cron
```

## 📜 完整模板

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily backup
Requires=backup.service

[Timer]
# 每天 02:00
OnCalendar=*-*-* 02:00:00

# 启动后 5 分钟跑一次（首次启动补充）
OnBootSec=5min

# 距上次激活 1 天（兜底）
OnUnitActiveSec=1d

# 错过的补跑
Persistent=true

# 精度（避免大量同时唤醒）
AccuracySec=1min

# 单元
Unit=backup.service

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Backup job

[Service]
Type=oneshot
ExecStart=/opt/backup/run.sh
```

## 📅 OnCalendar 格式

```
格式：DayOfWeek Year-Month-Day Hour:Minute:Second
缩写：dow yyyy-mm-dd hh:mm:ss

示例：
*-*-* *:*:00              # 每分钟
*-*-* *:00:00             # 每小时
*-*-* 02:00:00            # 每天 02:00
Mon *-*-* 09:00:00        # 每周一 09:00
*-01-* 02:00:00           # 每月 1 号 02:00
*-*-01..07 02:00:00       # 每月 1-7 号
Fri 2024-12-25 00:00:00   # 2024-12-25 周五（一次性）

# 缩写
Mon..Fri                   # 周一到周五
Sat,Sun                    # 周末
*-*-* 0/2:00:00           # 每 2 小时
```

```bash
# 测试 OnCalendar（看下次触发）
systemd-analyze calendar "*-*-* 02:00:00"
# Original form: *-*-* 02:00:00
#        Range: ...
#        Normalized form: *-*-* 02:00:00
#    Next elapse: Tue 2024-01-16 02:00:00

# 看未来几次
systemd-analyze calendar --iterations=5 "Mon *-*-* 09:00:00"
```

## 📜 启用 Timer

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now backup.timer

# 看所有 Timer + 下次触发时间
systemctl list-timers
# NEXT                        LEFT     LAST                        PASSED  UNIT
# Tue 2024-01-16 02:00:00  CST  13h     Tue 2024-01-15 02:00:00  CST  13h ago backup.timer

# 立即触发（不等下次）
sudo systemctl start backup.timer

# 看状态
systemctl status backup.timer
journalctl -u backup.service -n 10
```

## 🆚 vs cron

| | cron | systemd Timer |
|--|------|----------------|
| 配置 | 一行表达式 | Unit 文件 |
| 精度 | 分钟 | 微秒 |
| 错过的补跑 | ❌ | `Persistent=true` |
| 依赖追踪 | ❌ | ✅（Requires / After） |
| 集中日志 | ❌ | journald |
| 多线程触发 | 不一定 | Randomusec 控制 |

## 🛠 实战

### 每 5 分钟检查 + 整点日志轮转

```ini
# /etc/systemd/system/healthcheck.timer
[Unit]
Description=Health check every 5 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
AccuracySec=10s
Unit=healthcheck.service

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/healthcheck.service
[Unit]
Description=Service health check

[Service]
Type=oneshot
ExecStart=/opt/healthcheck/check.sh
```

### 错过的补跑（电脑关机 / 服务 down）

```ini
[Timer]
OnCalendar=daily
Persistent=true         # 关键：开机补跑
```

下次启动时，systemd 会跑过去错过的。

### 多个触发

```ini
[Timer]
# 每周一 03:00
OnCalendar=Mon *-*-* 03:00:00

# 每月 1 号 04:00
OnCalendar=*-01-* 04:00:00
```

两个都会触发。

## ⚠️ 注意

- **OnCalendar 的时区**：用本机时区
- **执行多次**：同一分钟多个触发会全跑（避免重叠用 `ConditionPathExists` 或 `OnFailure=`）
- **测试**：用 `systemd-analyze calendar "..."` 确认理解

## 🪜 替换现有 cron

```bash
# 1. 把 cron 命令搬到 .service
# 2. 写 .timer
# 3. 启用
sudo systemctl enable --now myjob.timer
# 4. 保留 cron 几天，确认 timer 跑通
# 5. 删除 cron
crontab -e   # 删掉对应行
```

## 🔗 下一步

- [systemd](/04-process/systemd)
- [cron 定时任务](/04-process/cron)
- [systemctl 命令](/12-systemd/systemctl)
- [journald 日志](/12-systemd/journald)