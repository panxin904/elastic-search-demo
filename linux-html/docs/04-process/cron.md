---
title: cron 定时任务
---

# cron - 定时任务

> Linux 上历史悠久的定时任务系统。

## ⏰ cron 表达式

```
┌────────── 分钟 (0 - 59)
│ ┌──────── 小时 (0 - 23)
│ │ ┌────── 日 (1 - 31)
│ │ │ ┌──── 月 (1 - 12)
│ │ │ │ ┌── 周 (0 - 6，0 = 周日)
│ │ │ │ │
* * * * *
```

| 字段 | 允许值 |
|------|--------|
| 分钟 | 0-59 |
| 小时 | 0-23 |
| 日 | 1-31 |
| 月 | 1-12 (或 jan-dec) |
| 周 | 0-6 (或 sun-sat) |

### 特殊字符

| 符号 | 含义 |
|------|------|
| `*` | 每（任意） |
| `*/5` | 每 5 |
| `1,3,5` | 1 或 3 或 5 |
| `1-5` | 1 到 5 |
| `0 9 * * 1-5` | 工作日 9:00 |

## 📜 crontab 命令

```bash
crontab -l                        # 列出当前用户的 cron
crontab -e                        # 编辑（默认用 EDITOR 变量）
crontab -r                        # 删除所有 cron（**慎用**）
crontab -u alice -l               # 看 alice 的 cron（需 root）
crontab /tmp/mycron               # 从文件载入
```

## 📝 实战例子

```bash
# 每分钟跑一次
* * * * * /opt/script.sh

# 每 5 分钟
*/5 * * * * /opt/check.sh

# 每天凌晨 2:30
30 2 * * * /opt/backup.sh

# 每周一 09:00
0 9 * * 1 /opt/work.sh

# 工作日（周一到周五）18:00
0 18 * * 1-5 /opt/eod.sh

# 每月 1 号 04:00
0 4 1 * * /opt/monthly.sh

# 每 30 分钟（写法一）
*/30 * * * * /opt/check.sh
# 等价（写法二）
0,30 * * * * /opt/check.sh

# 春节除夕 23:00（农历不行，只能按阳历）— 不支持
```

## 🛠 crontab 写法

```bash
# 编辑 crontab
crontab -e

# 标准头部
# ┌────────── 分钟
# │ ┌──────── 小时
# │ │ ┌────── 日
# │ │ │ ┌──── 月
# │ │ │ │ ┌── 周
# │ │ │ │ │
# * * * * *  /path/to/script.sh
```

```bash
# 完整写法
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=alice@example.com
HOME=/home/alice

# 0 2 * * * /opt/backup.sh 2>&1 | logger -t backup
```

环境变量要在 crontab 里显式设（cron 启动时只设最简环境）。

## ⚠️ 常见陷阱

```bash
# 1. 路径问题
* * * * * backup.sh              # ❌ 找不到
* * * * * /opt/backup.sh         # ✅ 用绝对路径

# 2. 环境变量
* * * * * cd /opt && ./run.sh   # ✅ cd + &&
* * * * * /opt/run.sh            # 脚本里 cd

# 3. 输出没处理
* * * * * /opt/backup.sh > /dev/null 2>&1  # 不发邮件

# 4. 多个任务锁
* * * * * flock -n /tmp/mylock /opt/run.sh   # 防并发

# 5. 时区
date                              # 当前时区
ls -la /etc/localtime              # 时区文件
```

## 🪛 系统级 cron

```bash
/etc/cron.d/        # 包级定时任务
/etc/cron.daily/    # 每天执行
/etc/cron.hourly/   # 每小时执行
/etc/cron.weekly/   # 每周执行
/etc/cron.monthly/  # 每月执行

# 放到 /etc/cron.d/myapp
cat > /etc/cron.d/myapp <<EOF
# 每 5 分钟同步数据
*/5 * * * * appuser /opt/myapp/sync.sh
EOF
```

## 🩺 排查

```bash
# cron 是否在跑
systemctl status cron
pgrep -af cron

# 看系统日志（cron 会记到 syslog）
grep CRON /var/log/syslog
journalctl -u cron -f

# 邮件通知（cron 默认会 mail 输出）
MAILTO=alice@example.com
```

如果没收到邮件，看 `mail` 命令。

## 🆚 cron vs systemd Timer

| | cron | systemd Timer |
|--|------|---------------|
| 配置 | crontab | .timer Unit |
| 精度 | 分钟 | 微秒 |
| 依赖追踪 | ❌ | ✅ |
| 错过补跑 | ❌ | Persistent=true |
| 集中日志 | ❌ | journald |

详见 [systemd Timer](/12-systemd/timer)。

## 🔗 下一步

- [systemd](/04-process/systemd)
- [systemd Timer](/12-systemd/timer)
- [bash 基础语法](/11-shell/bash-syntax)