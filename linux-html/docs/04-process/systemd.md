---
title: systemd
---

# systemd

> 现代 Linux 的 init 系统和服务管理器。从 CentOS 7 / Ubuntu 16.04 开始默认采用。

## 🏗️ systemd 的角色

```
   BIOS / UEFI
        │
        ▼
   GRUB 引导加载
        │
        ▼
   内核 + initramfs
        │
        ▼
   systemd (PID 1)
        │
   ┌────┴────┬────────┬─────────┐
   ▼         ▼        ▼         ▼
  .service  .timer  .socket   .target
  (服务)    (定时)  (套接字)   (运行级别)
```

PID 1 的 `systemd` 是所有进程的"祖先"，是 Linux 启动后第一个进程。

## 🎯 基本概念

| 术语 | 含义 |
|------|------|
| **Unit** | systemd 管理对象（service / timer / socket ...） |
| **Service** | 一个后台服务 |
| **Target** | 一组 Unit 的集合（类似"运行级别"） |
| **Wants / Requires** | 软 / 硬依赖 |
| **Timer** | 替代 cron 的定时器 |

## 🛠 systemctl - 命令

```bash
# 服务管理
systemctl start nginx.service       # 启动
systemctl stop nginx                # 停
systemctl restart nginx             # 重启
systemctl reload nginx              # 重读配置（不重启进程）
systemctl status nginx              # 状态 + 最近日志

# 开机启动
systemctl enable nginx              # 启用
systemctl disable nginx             # 禁用
systemctl is-enabled nginx          # 看是否启用

# 列出
systemctl list-units                # 当前加载的 Unit
systemctl list-unit-files           # 所有已安装的 Unit
systemctl --type=service            # 只看 service 类型

# 日志
journalctl -u nginx -f              # 跟踪日志
journalctl -u nginx -n 100          # 最近 100 条
journalctl --since "1 hour ago"     # 时间过滤
```

详见 [journald](/12-systemd/journald)。

## 📄 Unit 文件

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Web App
After=network.target postgresql.service
Wants=redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/node /opt/myapp/server.js
Restart=on-failure
RestartSec=5
Environment=NODE_ENV=production
EnvironmentFile=/etc/myapp.env

[Install]
WantedBy=multi-user.target
```

放 `/etc/systemd/system/`（最高优先级）或 `/usr/lib/systemd/system/`（包默认）。

```bash
systemctl daemon-reload           # 重读所有 Unit
systemctl enable myapp.service    # 启用
systemctl start myapp
systemctl status myapp
```

详见 [Unit 文件](/12-systemd/unit)。

## 🎚 target - 运行级别

```bash
systemctl list-units --type=target
systemctl get-default             # 看默认 target
systemctl set-default multi-user.target
systemctl isolate rescue.target    # 切到救援模式（慎用）

# 常用 target
# multi-user.target   = 运行级别 3（多用户 + 网络 + 命令行）
# graphical.target     = 运行级别 5（带 GUI）
# rescue.target        = 单用户救援
# poweroff.target      = 关机
```

## ⏱ Timer - 替代 cron

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily backup

[Timer]
OnCalendar=daily
OnCalendar=Mon *-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl list-timers             # 列出所有定时器
systemctl start backup.timer      # 立即触发
systemctl enable backup.timer      # 启用
```

详见 [systemd Timer](/12-systemd/timer)。

## 📋 实战

```bash
# 看为什么服务起不来
systemctl status nginx
journalctl -u nginx -n 50 --no-pager

# 重写 service 的环境变量
systemctl edit nginx.service       # 创建 override.conf
systemctl daemon-reload
systemctl restart nginx

# 看进程启动时长
systemctl show nginx -p ActiveEnterTimestamp

# 看服务依赖
systemctl list-dependencies nginx

# 自定义 service（应用启动模板）
sudo tee /etc/systemd/system/myapp.service <<EOF
[Unit]
Description=My App
After=network.target

[Service]
ExecStart=/opt/myapp/run.sh
Restart=always
User=appuser

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now myapp
```

## 🆚 systemd vs init.d

| | systemd | init.d (SysVinit) |
|--|---------|---------------------|
| 并行启动 | ✅ | ❌ |
| 按需启动 socket | ✅ | ❌ |
| 依赖图 | ✅ | ❌ |
| 统一日志 | journald | 各服务自己的 log |
| 进程追踪 | cgroups | 不精确 |
| 配置 | Unit 文件（声明式） | shell 脚本 |

## 🔗 下一步

- [systemctl 命令](/12-systemd/systemctl)
- [Unit 文件](/12-systemd/unit)
- [journald 日志](/12-systemd/journald)
- [systemd Timer](/12-systemd/timer)