---
title: journald 日志
date: 2026-08-15  # date-auto-injected
---

# journald 日志

> systemd 配套的统一日志系统。

## 📂 存哪？

```
/run/log/journal/         # 运行时（内存）—— 不持久
/var/log/journal/         # 持久化（默认）
```

不是 syslog / rsyslog，journald 是独立系统。可选地把日志转发给 syslog。

## 📜 基础命令

```bash
journalctl                     # 全部日志
journalctl -f                  # 跟踪（tail -f 风格）
journalctl -n 100              # 最近 100 条
journalctl --since "1 hour ago"
journalctl --since "2024-01-15" --until "2024-01-16"
journalctl --since today
journalctl --since "10:00" --until "11:00"

# 按服务
journalctl -u nginx
journalctl -u nginx -u myapp   # 多服务
journalctl -u nginx -f         # 跟踪

# 按进程
journalctl _PID=1234
journalctl _UID=alice          # 用户
journalctl _COMM=nginx         # 进程名

# 按优先级
journalctl -p err              # err 及以上
journalctl -p warning..err     # 范围

# 按启动
journalctl -b                  # 本次启动
journalctl -b -1               # 上次启动
journalctl --list-boots        # 看启动列表
```

## 🔍 过滤

```bash
# 关键组合
journalctl -u nginx --since "1 hour ago" -p err

# grep 风格
journalctl -u nginx | grep "error"
journalctl -u nginx --grep "ERROR"          # 等价

# 字段过滤
journalctl _SYSTEMD_UNIT=nginx.service _PID=1234

# 看所有字段
journalctl -o verbose -n 1     # 单条详细
```

## 📊 输出格式

```bash
journalctl -o short             # 默认（短）
journalctl -o short-full        # 含日期
journalctl -o json             # JSON（一行/条）
journalctl -o json-pretty      # 美化 JSON
journalctl -o cat              # 不带元数据，纯文本
journalctl -o export            # 二进制（备份用）

# 单字段
journalctl -o json --output-fields=MESSAGE,_PID | head
```

## 🪜 配置

```bash
# /etc/systemd/journald.conf
[Journal]
Storage=persistent             # persistent / volatile / auto
Compress=yes                   # 大于 512B 自动压缩
SystemMaxUse=2G                # 最多占 2G
SystemKeepFree=100M            # 至少留 100M 给系统
MaxRetentionSec=30day          # 最多保留 30 天
ForwardToSyslog=no             # 不转发 syslog
RateLimitIntervalSec=10
RateLimitBurst=1000            # 防刷屏
```

```bash
sudo systemctl restart systemd-journald
```

## 🧹 清理

```bash
# 看大小
journalctl --disk-usage

# 清掉 7 天前
sudo journalctl --vacuum-time=7d

# 只保留 500M
sudo journalctl --vacuum-size=500M

# 验证配置
journalctl --verify
```

## 📜 服务端日志

journald 服务端可以转发 / 集中收集。

```bash
# 服务端：监听 19532 端口接收
systemd-journal-remote --listen

# 客户端：发给服务端
/etc/systemd/journal-upload.conf
URL=https://central-log.example.com
# 或
/etc/systemd/journald.conf
[ForwardToSyslog=yes]
```

详见 systemd-journal-upload / systemd-journal-gatewayd。

## 🛠 实战

### 服务起不来，1 分钟看到底

```bash
journalctl -u myapp -n 200 --no-pager --since "10 minutes ago"
```

### 找昨天 3 点的错误

```bash
journalctl --since "yesterday 03:00" --until "yesterday 03:30" -p err
```

### 服务挂了，自动记录重启原因

journald 默认记录 `_SYSTEMD_UNIT_START_TIME` 等字段。

### 大日志防爆

```bash
# 看日志增长最快的服务
journalctl --disk-usage
du -sh /var/log/journal/*

# 限大小（防 disk full）
sudo tee /etc/systemd/journald.conf <<EOF
[Journal]
SystemMaxUse=2G
SystemKeepFree=200M
MaxRetentionSec=14day
EOF
sudo systemctl restart systemd-journald
```

### 跨重启对比

```bash
# 本次 vs 上次
journalctl -b -u nginx          # 当前启动
journalctl -b -1 -u nginx       # 上次启动

# 找"上次启动后多久挂"的模式
```

## 🪤 与 syslog 关系

journald 出现后，`/var/log/syslog`、`/var/log/messages` 多数发行版仍在，但内容来自 systemd 转发。

可以并存：journald 写自己的 journal，**转发一份**到 rsyslog → /var/log/。

## 🪛 故障

```bash
# journalctl: failed to access journal
# 权限 / FUSE 问题
ls -la /var/log/journal/
sudo journalctl --verify

# 日志没增长
systemctl status systemd-journald
journalctl --flush            # 强制刷

# 时间戳不对（时区错）
timedatectl status             # 看时区
# journald 用本机时间

# 大量垃圾（循环日志）
journalctl -p debug -n 1 | head   # 看最低优先级
```

## 🔗 下一步

- [systemd](/04-process/systemd)
- [systemctl 命令](/12-systemd/systemctl)
- [Unit 文件](/12-systemd/unit)
- [systemd Timer](/12-systemd/timer)