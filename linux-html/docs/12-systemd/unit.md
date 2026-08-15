---
title: Unit 文件
---

# systemd Unit 文件

> Unit 是 systemd 管理的对象。配置即声明（不写过程）。

## 📂 Unit 文件位置（按优先级）

```
/etc/systemd/system/       # 系统管理员配置（最高）
/run/systemd/system/       # 运行时（systemd 生成）
/usr/lib/systemd/system/    # 包安装默认（最低）
```

同名 Unit 优先级：`/etc > /run > /usr/lib`。

## 🧱 Unit 类型

| 类型 | 后缀 | 用途 |
|------|------|------|
| Service | `.service` | 后台服务 |
| Socket | `.socket` | socket 激活 |
| Target | `.target` | 一组 Unit |
| Timer | `.timer` | cron 替代 |
| Mount | `.mount` | 挂载点 |
| Automount | `.automount` | 自动挂载 |
| Path | `.path` | 文件监视 |
| Slice | `.slice` | cgroup 切片 |
| Scope | `.scope` | 外部进程（Docker / systemd-run） |
| Swap | `.swap` | swap 分区 |
| Device | `.device` | 内核识别设备 |

## 📜 Service Unit 完整模板

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Web App
Documentation=https://example.com/docs

# 启动顺序（依赖）
After=network.target postgresql.service
Wants=redis.service              # 软依赖（启动 redis，但不阻塞失败）
Requires=postgresql.service      # 硬依赖（启动失败则 myapp 失败）
BindsTo=postgresql.service       # 同生共死（pg 停，myapp 停）

# 条件
ConditionPathExists=/etc/myapp/.env
ConditionFileNotEmpty=/etc/myapp/.env

[Service]
Type=simple                       # 启动类型
User=appuser
Group=appgroup
WorkingDirectory=/opt/myapp

# 启动命令
ExecStartPre=/opt/myapp/bin/check
ExecStart=/opt/myapp/bin/server.js
ExecStartPost=/opt/myapp/bin/notify-ready
ExecStop=/opt/myapp/bin/graceful-stop
ExecReload=/bin/kill -HUP $MAINPID

# 进程
ExecMainStart=/opt/myapp/bin/server.js
PIDFile=/var/run/myapp.pid
Environment=NODE_ENV=production
EnvironmentFile=/etc/myapp.env

# 资源限制
MemoryMax=2G
TasksMax=512
CPUQuota=200%                      # 2 核
LimitNOFILE=65536
CPUWeight=100

# 重启
Restart=always
RestartSec=5
StartLimitBurst=10
StartLimitIntervalSec=60s

# 安全
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
NoNewPrivileges=yes
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
ReadOnlyPaths=/etc /usr

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

# 超时
TimeoutStartSec=30
TimeoutStopSec=30
TimeoutAbortSec=10

[Install]
WantedBy=multi-user.target         # multi-user.target 启用时启动
Also=myapp.service                  # 备选 Unit
```

## 🧬 Type - 启动类型

| Type | 含义 |
|------|------|
| `simple` | 默认。ExecStart 进程即服务（不能 fork） |
| `exec` | 类似 simple，但 systemd 会等进程启动 |
| `forking` | ExecStart 会 fork（传统 daemon） |
| `oneshot` | 一次性任务（与 RemainAfterExit 配合） |
| `notify` | 类似 simple，但等进程发 sd_notify 才算 ready |
| `dbus` | 启动后会在 D-Bus 上注册名字 |
| `idle` | 等其他 active 任务完了再启动 |

```ini
Type=simple                # Node.js / Go 服务
Type=exec                  # 类似 simple
Type=forking               # 经典 daemon（如 nginx 默认）
Type=oneshot               # 一次性任务
```

## 🔗 依赖类型

| 指令 | 含义 |
|------|------|
| `Requires=` | 硬依赖。失败则本 Unit 失败。 |
| `Wants=` | 软依赖。失败不阻塞。 |
| `BindsTo=` | 同生共死（强 + 双向） |
| `RequiredBy=` / `WantedBy=` | 反向依赖 |
| `After=` / `Before=` | 顺序（不是依赖） |
| `PartOf=` | 父 Unit 停止 / 重启，自己也跟 |
| `Conflicts=` | 不能并存 |

## 🔁 重启策略

```ini
[Service]
Restart=no              # 不重启
Restart=always          # 任何退出都重启
Restart=on-success      # 0 退出码
Restart=on-failure      # 非 0 退出码 / 信号 / 超时
Restart=on-abnormal     # 非 0 退出码 / 信号 / 超时（除 normal）
Restart=on-watchdog      # watchdog 超时
```

## 🔒 安全加固（systemd 推荐）

```ini
[Service]
NoNewPrivileges=yes             # 拒绝 setuid
ProtectSystem=strict             # /usr /boot 只读
ProtectHome=yes                  # /home 不可访问
PrivateTmp=yes                   # 隔离 /tmp
PrivateDevices=yes               # 隔离 /dev
ProtectKernelTunables=yes        # 不能改 sysctl
ProtectControlGroups=yes         # 不能改 cgroup
RestrictNamespaces=yes           # 不能创建命名空间
RestrictRealtime=yes             # 不能实时调度
MemoryDenyWriteExecute=yes       # 禁 W^X 内存
CapabilityBoundingSet=           # 限制 capability
LockPersonality=yes
SystemCallArchitectures=native
SystemCallFilter=@system-service # 白名单 syscall
UMask=0077                       # 文件默认 077
```

模板（systemd 自带）：

```bash
# 看 systemd 给"系统服务"的默认沙箱
systemd-analyze security nginx

# 用 systemd-analyze 建议的最小化
systemd-analyze security --offline=true myapp.service
```

## 🪜 Override - 不改 Unit 文件

```bash
sudo systemctl edit nginx.service
# 打开编辑器，只写你想覆盖的段落
# /etc/systemd/system/nginx.service.d/override.conf 会被创建

# /etc/systemd/system/nginx.service.d/override.conf
[Service]
Restart=always
RestartSec=3

sudo systemctl daemon-reload
sudo systemctl restart nginx
```

drop-in 优先级最高，与 Unit 文件合并。

## 🛠 实战

### Web 应用 service

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Node App
After=network.target postgresql.service

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
Environment=NODE_ENV=production
ExecStart=/usr/bin/node /opt/myapp/dist/server.js
Restart=on-failure
RestartSec=5

# 安全
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### 部署流程

```bash
# 1. 放 Unit 文件
sudo cp myapp.service /etc/systemd/system/
sudo systemctl daemon-reload

# 2. 测试
sudo systemctl start myapp
sudo systemctl status myapp
journalctl -u myapp -f

# 3. 启用
sudo systemctl enable myapp

# 4. 改环境变量（不改 Unit）
sudo systemctl edit myapp
# [Service]
# Environment=NODE_ENV=staging
sudo systemctl restart myapp
```

## 🔗 下一步

- [systemd](/04-process/systemd)
- [systemctl 命令](/12-systemd/systemctl)
- [journald 日志](/12-systemd/journald)
- [systemd Timer](/12-systemd/timer)