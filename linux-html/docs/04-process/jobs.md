---
title: 前台后台 (jobs / nohup / disown)
date: 2026-08-15  # date-auto-injected
---

# jobs / nohup / disown

> 让进程脱离终端稳定运行。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Linux 任务控制 / 守护进程</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">前台/后台 · SIGHUP · nohup · setsid · tmux</text>

  <!-- 前台后台转换 -->
  <g>
    <text x="50" y="90" font-size="13" font-weight="700" fill="#1e293b">① 前台 / 后台 / 守护转换</text>

    <rect class="at-hover-card" x="40" y="105" width="120" height="60" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="100" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">前台进程</text>
    <text x="100" y="145" text-anchor="middle" font-size="9" fill="#475569">绑定 tty</text>

    <path d="M160,135 L195,135" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="177" y="128" text-anchor="middle" font-size="9" fill="#64748b">Ctrl+Z</text>

    <rect class="at-hover-card" x="195" y="105" width="120" height="60" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="255" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">后台暂停</text>
    <text x="255" y="145" text-anchor="middle" font-size="9" fill="#475569">jobs 列查看</text>

    <path d="M315,135 L350,135" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="332" y="128" text-anchor="middle" font-size="9" fill="#64748b">bg %1</text>

    <rect class="at-hover-card" x="350" y="105" width="130" height="60" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="415" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">后台运行</text>
    <text x="415" y="145" text-anchor="middle" font-size="9" fill="#475569">可继续 fg</text>

    <path d="M480,135 L515,135" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="497" y="128" text-anchor="middle" font-size="9" fill="#64748b">disown</text>

    <rect class="at-hover-card" x="515" y="105" width="45" height="60" rx="6" fill="#1e293b"/>
    <text x="537" y="132" text-anchor="middle" font-size="11" font-weight="700" fill="#10b981">脱离</text>
    <text x="537" y="150" text-anchor="middle" font-size="9" fill="#10b981">jobs</text>
  </g>

  <!-- SIGHUP 问题 -->
  <g>
    <text x="50" y="200" font-size="13" font-weight="700" fill="#1e293b">② SIGHUP 问题（终端关闭 → 进程被杀）</text>

    <rect class="at-hover-card" x="40" y="210" width="520" height="65" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="55" y="232" font-size="11" font-weight="700" fill="#991b1b">⚠️ 场景：</text>
    <text x="120" y="232" font-size="10" fill="#475569">ssh 登录后跑 nohup ./long-job &amp; → 关闭 ssh → 终端发送 SIGHUP → 进程被杀</text>
    <text x="55" y="252" font-size="11" font-weight="700" fill="#10b981">✅ 解法：</text>
    <text x="120" y="252" font-size="10" fill="#475569">nohup CMD &amp; → 进程忽略 SIGHUP / disown -h %1 / setsid CMD 完全脱离会话</text>
    <text x="55" y="267" font-size="9" fill="#475569">现代替代：tmux / screen / systemd-run --user</text>
  </g>

  <!-- 4 种方案对比 -->
  <g>
    <text x="50" y="295" font-size="13" font-weight="700" fill="#1e293b">③ 4 种守护方案对比</text>

    <rect class="at-hover-card" x="40" y="305" width="125" height="65" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="102" y="327" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">nohup CMD &amp;</text>
    <text x="102" y="345" text-anchor="middle" font-size="9" fill="#475569">⭐ 简单快速</text>
    <text x="102" y="362" text-anchor="middle" font-size="9" fill="#10b981">忽略 SIGHUP</text>

    <rect class="at-hover-card" x="175" y="305" width="125" height="65" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="237" y="327" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">setsid CMD</text>
    <text x="237" y="345" text-anchor="middle" font-size="9" fill="#475569">⭐⭐ 新会话</text>
    <text x="237" y="362" text-anchor="middle" font-size="9" fill="#3b82f6">彻底脱离</text>

    <rect class="at-hover-card" x="310" y="305" width="125" height="65" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="372" y="327" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">tmux/screen</text>
    <text x="372" y="345" text-anchor="middle" font-size="9" fill="#475569">⭐⭐⭐ 可重连</text>
    <text x="372" y="362" text-anchor="middle" font-size="9" fill="#f59e0b">推荐生产</text>

    <rect class="at-hover-card" x="445" y="305" width="115" height="65" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
    <text x="502" y="327" text-anchor="middle" font-size="11" font-weight="700" fill="#5b21b6">systemd-run</text>
    <text x="502" y="345" text-anchor="middle" font-size="9" fill="#475569">现代标准</text>
    <text x="502" y="362" text-anchor="middle" font-size="9" fill="#8b5cf6">日志集成</text>
  </g>

  <!-- 实战场景 -->
  <g>
    <text x="50" y="390" font-size="13" font-weight="700" fill="#1e293b">④ 实战场景对照</text>

    <rect class="at-hover-card" x="40" y="400" width="510" height="60" rx="6" fill="#1e293b" stroke="#1e293b" stroke-width="1"/>
    <text x="55" y="423" font-size="10" font-weight="700" fill="#10b981"># 跑一个长任务到后台</text>
    <text x="55" y="438" font-size="10" fill="#e2e8f0" font-family="monospace">$ nohup python train.py &gt; train.log 2&gt;&amp;1 &amp;     # 最常用</text>
    <text x="55" y="453" font-size="10" fill="#e2e8f0" font-family="monospace">$ tmux new -s job 'python train.py'   # 推荐 · 可重连</text>
  </g>
</svg>

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

<ClientOnly>
  <GiscusComment />
</ClientOnly>

<!-- giscus-injected:do-not-edit -->
