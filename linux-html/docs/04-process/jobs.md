---
title: 前台后台 (jobs / nohup / disown)
---

# jobs / nohup / disown

> 让进程脱离终端稳定运行。

## 🪟 前台 / 后台

```bash
./app                       # 前台跑（占住当前 shell）
./app &                     # 后台启动（立即返回）

# Ctrl+Z 暂停当前前台任务
fg                          # 切回前台继续
bg                          # 切到后台继续

jobs                        # 看当前 shell 的后台任务
```

## 🔇 nohup - 免疫 SIGHUP

`nohup` 让进程**忽略 SIGHUP**（终端关闭信号）。

```bash
nohup ./long-running.sh > output.log 2>&1 &
nohup python3 server.py &

# 等价
./app & disown        # 后台 + 从 jobs 列表移除
```

## 🔗 disown - 从 jobs 移除

```bash
./app &                 # 后台
jobs                   # 看得到
disown %1              # 从 jobs 移除（但进程仍在跑）
disown -a              # 移除所有
disown -h %1           # 不发 SIGHUP（保留在 jobs）
```

进程不会因为父 shell 退出而被收尸。

## 📊 用 screen / tmux 守护

`nohup` 已经够用，但对**长时间会话**（开发、调试）用 screen / tmux 更好。

```bash
# tmux（推荐）
tmux new -s dev          # 创建会话
./app                    # 跑应用
Ctrl+B, 然后 D           # 脱离
tmux ls                  # 列出会话
tmux attach -t dev      # 重新进入
tmux kill-session -t dev

# screen
screen -S dev            # 创建
Ctrl+A, D                # 脱离
screen -r dev            # 重新进入
```

## 🖥 setsid - 完全脱离父进程

```bash
setsid ./app </dev/null >/tmp/app.log 2>&1 &
# 父进程退出后，app 被 init 收养（PPID=1）
```

`nohup` 已经能解决 95% 的场景。

## 🔥 实战

```bash
# 后台运行 + 不被 SIGHUP 杀 + 输出到文件 + 立即返回
nohup ./server.js > /var/log/app.log 2>&1 < /dev/null &

# 查 PID
echo $!                  # 上一条命令的 PID
pgrep -f server.js

# 优雅关停
kill -TERM $(cat /var/run/app.pid)

# 系统级：用 systemd（推荐）
sudo tee /etc/systemd/system/myapp.service <<EOF
[Unit]
Description=My App
After=network.target

[Service]
ExecStart=/usr/bin/node /opt/app/server.js
Restart=on-failure
User=appuser

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable --now myapp
```

## 🧱 守护进程 vs 后台

| | 后台 `&` | 守护进程 |
|--|----------|----------|
| 父进程 | 当前 shell | init / systemd |
| 终端关闭 | 默认挂（除非 nohup） | 继续运行 |
| 自动重启 | ❌ | ✅（systemd） |
| 集中日志 | ❌ | ✅（journald） |
| 适用场景 | 临时 / 调试 | 生产环境 |

**生产环境永远用 systemd 部署**，不要靠 nohup。

## 🔗 下一步

- [systemd](/04-process/systemd)
- [systemctl 命令](/12-systemd/systemctl)
- [信号 (kill)](/04-process/signals)