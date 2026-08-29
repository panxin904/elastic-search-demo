---
title: SSH 隧道 / 代理
date: 2026-08-15  # date-auto-injected
---

# SSH 隧道 / 代理

> SSH 不只是"登录"——还能穿透防火墙、做端口转发、代理上网。

## 🚇 本地端口转发（-L）

把远端服务"拉"到本地访问。

```bash
# 场景：远端 mysql 3306 不外露，本地连
ssh -L 13306:localhost:3306 user@dbserver
# 现在本地可以连 mysql -h 127.0.0.1 -P 13306

# 场景：访问公司内网 web（公司跳板机 + 内网 web）
ssh -L 8080:internal-web:80 user@bastion
# 浏览器访问 http://localhost:8080 → 跳板 → 内网 web

# 多端口
ssh -L 13306:db:3306 -L 8080:web:80 user@bastion

# 绑定 0.0.0.0（让其他机器也能访问）
ssh -L 0.0.0.0:8080:internal-web:80 user@bastion
# 慎用：他人可访问（除非防火墙限）
```

### 实战：远程 MySQL

```bash
# 在 1.1.1.1 上跑 mysql，3306 端口未暴露
ssh -L 13306:localhost:3306 user@1.1.1.1

# 本地连
mysql -h 127.0.0.1 -P 13306 -u root -p
```

## 🌐 远端端口转发（-R）

把本地服务"推"到远端。

```bash
# 场景：本机 8080 跑 web demo，给客户临时演示
ssh -R 0.0.0.0:9000:localhost:8080 user@server
# 客户访问 http://server:9000 → SSH → 你的 8080

# GatewayPorts 需打开
# /etc/ssh/sshd_config
GatewayPorts yes
# 或 GatewayPorts clientspecified 让 ssh 命令指定
```

### 实战：远程办公访问内网

```bash
# 在公司机器：
ssh -R 0.0.0.0:9001:localhost:3389 user@home-server
# 现在家里 RDP 到 home-server:9001 = 公司电脑 RDP
```

## 🌍 SOCKS 代理（-D）

把 SSH 当作 SOCKS 5 代理，整个流量走 SSH 隧道。

```bash
# 起本地 SOCKS5 代理：1080 端口
ssh -D 1080 user@server

# 浏览器配置 SOCKS5 代理：127.0.0.1:1080
# 所有浏览器流量 → SSH 隧道 → server → 互联网

# 远程 DNS（防止 DNS 泄露）
# 浏览器 + 启用 "Remote DNS"

# 仅代理某个子网（Firefox：about:config → network.proxy.no_proxies_on）
```

### 实战：访问公司内网 + 不暴露公网

```bash
# 起代理
ssh -D 1080 -C user@bastion
# -C 压缩（慢速线路有用）

# 浏览器 / curl 走 SOCKS
curl --proxy socks5h://127.0.0.1:1080 http://internal-app/
```

## 🌐 动态 SSH（ProxyCommand）

让 SSH 通过另一个代理连接。

```bash
# 通过跳板机连接内网
ssh -o ProxyCommand='ssh -W %h:%p user@bastion' user@internal
# 等价于
ssh -J user@bastion user@internal
# 需要 OpenSSH 7.3+

# ~/.ssh/config
Host internal-*
    ProxyJump user@bastion
```

## 🔧 持久化转发

服务器上保持 SSH 连接：

```bash
# ~/.ssh/config
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3

# systemd 单元（推荐）
# /etc/systemd/system/tunnel.service
[Unit]
Description=SSH Tunnel
After=network.target

[Service]
User=alice
ExecStart=/usr/bin/ssh -N -L 13306:db:3306 user@server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

sudo systemctl enable --now tunnel
```

`-N` 不开远程 shell（仅做转发）。

## 🛡 安全

```bash
# 端口绑定到 localhost（不让外网访问）
ssh -L 127.0.0.1:8080:internal:80 user@bastion

# 多跳 + 禁用密码
ssh -J -o PubkeyAuthentication=yes user1@bastion user2@internal

# 限制 ServerAlive（避免长时挂）
ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=2 -L ...

# 用 ControlMaster / ControlPersist 复用连接
# ~/.ssh/config
Host bastion
    ControlMaster auto
    ControlPersist 10m
    ControlPath ~/.ssh/cm-%r@%h:%p

# 再连 internal 时复用 SSH 连接（快很多）
ssh internal
```

## 🔧 跳板链

```bash
# 多跳代理
ssh -L 8080:internal-web:80 user@bastion
# local 8080 → bastion → internal-web:80

# 用 ProxyJump（更简单）
ssh -J user@bastion,user@internal-bastion user@final-target
```

## 🪤 实战

### 远程调试 Web 服务（开发机无法直连）

```bash
# 把远程 3000 端口转回本地
ssh -L 3000:localhost:3000 deploy@prod
# 浏览器访问 localhost:3000 = 远程 prod 3000
```

### 临时暴露本地 demo

```bash
ssh -R 0.0.0.0:9000:localhost:3000 user@demo.example.com
# 发 https://demo.example.com:9000/ 给客户
```

### 用 SSH 当跳板访问 K8s API

```bash
ssh -L 6443:master:6443 user@k8s-bastion
# kubectl --server=https://localhost:6443
```

## ❓ 常见问题

```bash
# "channel_setup_fails_connection_refused"
# 远端 sshd 端口未开 / 防火墙拒绝

# "bind: Address already in use"
# 本地端口被占，换一个：-L 13307:...

# "Warning: remote port forwarding failed for listen port"
# 远端 GatewayPorts no，且你写 0.0.0.0
```

## 🔗 下一步

- [OpenSSH 配置](/08-firewall-ssh/openssh)
- [ssh-keygen](/08-firewall-ssh/ssh-keys)
- [防火墙 / iptables](/08-firewall-ssh/iptables)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
