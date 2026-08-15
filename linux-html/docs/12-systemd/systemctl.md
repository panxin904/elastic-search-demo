---
title: systemctl 命令
---

# systemctl 命令

> systemctl 是 systemd 的主控程序。

## 📜 基础

```bash
# 服务管理
systemctl start nginx           # 启动
systemctl stop nginx            # 停
systemctl restart nginx         # 重启（先 stop 再 start）
systemctl reload nginx          # 重载配置（不重启进程）

systemctl status nginx          # 状态 + 最近日志
systemctl is-active nginx       # active / inactive / failed
systemctl is-enabled nginx      # enabled / disabled / static

# 启用 / 禁用
systemctl enable nginx          # 开机启动
systemctl disable nginx         # 取消开机启动
systemctl enable --now nginx    # 启用 + 立即启动（一步）

# 看依赖
systemctl list-dependencies nginx
```

## 📋 列出

```bash
# 运行的
systemctl                       # 全部 Unit
systemctl list-units            # 默认显示 active
systemctl list-units --all      # 全部（含 inactive）
systemctl list-units --type=service           # 只 service
systemctl list-units --type=service --state=running    # 运行的

# 已安装的
systemctl list-unit-files      # 全部 Unit 文件
systemctl list-unit-files --type=service --state=enabled  # 启用的

# 失败的服务
systemctl --failed
```

## 🛠 Unit 操作

```bash
# 看 Unit 文件
systemctl cat nginx             # 看完整 Unit + drop-in

# 编辑（自动加 drop-in override.conf）
systemctl edit nginx             # 改 user 级
systemctl edit --full nginx     # 改完整 Unit
sudo systemctl edit nginx       # 改 system 级

# 重新加载所有 Unit 文件
systemctl daemon-reload

# 看状态详情
systemctl show nginx             # 所有属性
systemctl show -p MainPID nginx # 某个属性
systemctl show -p ActiveState -p SubState nginx

# 重新启动
systemctl restart nginx         # 重启
systemctl try-restart nginx     # 仅当 active 时才 restart
systemctl reload-or-restart nginx  # 优先 reload，失败才 restart
```

## 📜 日志（journald）

```bash
systemctl status nginx          # 自带最近 10 行
journalctl -u nginx -f          # 跟踪日志
journalctl -u nginx -n 100      # 最近 100 行
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx --since today

# 看启动日志
journalctl -b                   # 本次启动
journalctl -b -1                # 上次启动
```

详见 [journald](/12-systemd/journald)。

## 🎚 运行级别 / target

```bash
systemctl get-default           # 当前默认 target
systemctl set-default multi-user.target
systemctl list-units --type=target

# 切（慎用）
systemctl isolate multi-user.target   # 切到命令行
systemctl isolate graphical.target    # 切到桌面
systemctl rescue                       # 救援模式
```

| target | 旧 runlevel |
|--------|-------------|
| poweroff.target | 0 |
| rescue.target | 1 |
| multi-user.target | 3 |
| graphical.target | 5 |
| reboot.target | 6 |

## 🚀 服务生命周期

```bash
# 优雅重启（让 systemd 处理停止）
systemctl kill -s TERM nginx    # SIGTERM（默认）
systemctl kill -s USR1 nginx    # 自定义信号
systemctl kill -s KILL nginx    # SIGKILL（最后手段）

# 配置
# /etc/systemd/system.conf
DefaultTimeoutStopSec=90s      # 默认 90 秒强制停
# 或单个 Unit
[Service]
TimeoutStopSec=30
```

## 🪵 restart 策略

```ini
[Service]
Restart=always             # 任何退出都重启
Restart=on-failure         # 仅失败时重启（非 0 退出码）
Restart=on-success         # 仅成功退出后重启
Restart=no                 # 不重启
```

详见 [systemd](/04-process/systemd) 与 [Unit 文件](/12-systemd/unit)。

## 🛠 实战

```bash
# 服务起不来
systemctl status nginx
journalctl -u nginx -n 50 --no-pager

# 启用服务
sudo systemctl enable --now nginx

# 查 MainPID
systemctl show -p MainPID --value nginx

# 查何时启动
systemctl show -p ActiveEnterTimestamp --value nginx

# 重读配置
sudo systemctl daemon-reload

# 错误时降级
sudo systemctl edit nginx.service
# 加：
# [Service]
# Restart=on-failure
# RestartSec=5

# 批量启停
sudo systemctl start nginx myapp redis    # 一次性启 3 个

# 看谁监听了这个服务的端口
ss -tlnp | grep $(systemctl show -p MainPID --value nginx)
```

## 🪤 常用 Alias（写到 ~/.bashrc）

```bash
alias sc='systemctl'
alias scs='sudo systemctl status'
alias scr='sudo systemctl restart'
alias scl='sudo journalctl -u'
```

## 🔗 下一步

- [systemd](/04-process/systemd)
- [Unit 文件](/12-systemd/unit)
- [journald 日志](/12-systemd/journald)
- [systemd Timer](/12-systemd/timer)