---
title: sysctl 调参
---

# sysctl - 内核运行时调参

> 修改 `/proc/sys/` 下的内核参数，**运行时生效**，无需重启。

## 📜 基础命令

```bash
# 读
sysctl net.ipv4.tcp_syncookies           # 单个
sysctl -a | head                         # 全部（很多）

# 写（运行时）
sudo sysctl -w net.ipv4.ip_forward=1

# 永久
echo "net.ipv4.ip_forward = 1" | sudo tee /etc/sysctl.d/99-custom.conf
sudo sysctl -p /etc/sysctl.d/99-custom.conf
sudo sysctl --system                    # 加载全部 /etc/sysctl.d/*
```

## 🗂️ 参数分类

```
/proc/sys/
├── kernel/        - 内核核心
├── vm/            - 虚拟内存
├── fs/            - 文件系统
├── net/           - 网络
├── net/ipv4/      - IPv4
├── net/ipv6/      - IPv6
├── net/core/      - 协议无关
├── net/netfilter/ - 防火墙
├── abi/           - 二进制兼容
├── debug/         - 调试
└── fs/
```

## 📚 关键参数

### 网络 / TCP 优化

```bash
# 防 SYN 洪水攻击
net.ipv4.tcp_syncookies = 1

# 启用 IP 转发（路由器 / 网关 / NAT 必须）
net.ipv4.ip_forward = 1

# 不接受 ICMP 重定向（防中间人）
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# 不发 ICMP 重定向（除路由器）
net.ipv4.conf.all.send_redirects = 0

# 防 IP 转发（防 IP 伪造）
net.ipv4.conf.all.rp_filter = 1

# 防 source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# 启用 BBR（Linux 4.9+，推荐）
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# TCP 连接跟踪表（高并发）
net.netfilter.nf_conntrack_max = 262144
net.netfilter.nf_conntrack_buckets = 65536
```

### TCP 性能调优

```bash
# 文件描述符
fs.file-max = 1000000

# 端口范围
net.ipv4.ip_local_port_range = 1024 65535

# TCP 队列
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 4096

# TIME_WAIT 优化
net.ipv4.tcp_max_tw_buckets = 131072
net.ipv4.tcp_tw_reuse = 1

# TCP 缓冲区（高带宽大延迟优化）
# net.ipv4.tcp_rmem = 4096 87380 6291456
# net.ipv4.tcp_wmem = 4096 65536 6291456

# BBR（内核 ≥ 4.9）
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
```

### 内存

```bash
# dirty ratio（写 IO 抖动调）
vm.dirty_ratio = 5
vm.dirty_background_ratio = 2

# overcommit
vm.overcommit_memory = 0       # 启发式（默认）
vm.overcommit_memory = 1       # 永不全校验（DB 用）

# swap 倾向
vm.swappiness = 10              # 数据库：低
vm.swappiness = 60              # 默认

# 大页（数据库）
vm.nr_hugepages = 1024

# OOM killer 行为
vm.overcommit_memory = 2
vm.overcommit_ratio = 80
```

### 文件系统

```bash
# 文件描述符
fs.file-max = 1000000
fs.nr_open = 1048576

# inotify（Node.js / 文件监控）
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 8192

# dirty page（写性能）
vm.dirty_ratio = 5
vm.dirty_background_ratio = 2
```

### 安全加固

```bash
# ASLR（地址随机化，已默认开）
kernel.randomize_va_space = 2

# 内核指针限制（防泄漏）
kernel.kptr_restrict = 2

# dmesg 限制
kernel.dmesg_restrict = 1

# BPF JIT 限制
net.core.bpf_jit_harden = 2

# perf 子系统限制（防越权）
kernel.perf_event_paranoid = 3

# kexec（禁重启进新内核）
kernel.kexec_load_disabled = 1
```

## 📝 /etc/sysctl.d/ 推荐配置

```bash
# /etc/sysctl.d/99-custom.conf

# === 网络安全 ===
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_source_route = 0

# === 网络性能 ===
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.ip_local_port_range = 1024 65535
fs.file-max = 1000000
net.ipv4.tcp_fastopen = 3

# === 文件系统 ===
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 8192

# === 内核安全 ===
kernel.randomize_va_space = 2
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
kernel.perf_event_paranoid = 3
kernel.kexec_load_disabled = 1

# === 内存（数据库） ===
# vm.swappiness = 1
# vm.dirty_ratio = 5
# vm.dirty_background_ratio = 2
```

```bash
sudo sysctl --system
```

## 📋 实战

### Web 服务器

```bash
# /etc/sysctl.d/99-web.conf
net.core.somaxconn = 8192
net.ipv4.tcp_max_syn_backlog = 8192
fs.file-max = 200000
fs.nr_open = 200000
net.ipv4.tcp_tw_reuse = 1
```

### 数据库（MySQL / PG）

```bash
# /etc/sysctl.d/99-db.conf
vm.swappiness = 1                  # 几乎不用 swap（DB 自己管）
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 4096
```

### K8s / 容器节点

```bash
# /etc/sysctl.d/99-k8s.conf
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
```

### 高并发 / Redis / Nginx

```bash
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
fs.file-max = 200000
```

## 🔍 查看参数含义

```bash
# 列出某类别
sysctl net.ipv4.tcp

# 查参数含义（搜索）
# https://www.kernel.org/doc/Documentation/sysctl/

# sysctl 自带说明（多数没有）
man sysctl
```

## 🩺 故障

```bash
# 设置失败（readonly）
# 多半是内核不支持 / 模块没加载
sysctl -w kernel.some_param=1
# sysctl: setting key "kernel.some_param": Read-only file system

# 看是不是只读
ls -la /proc/sys/<path>
# 不可写 = 内核不支持或参数被 lock

# 完全重启后失效
# /etc/sysctl.d/ 没加 → 写一个
```

## 🔗 下一步

- [GRUB 引导](/14-kernel/grub)
- [initramfs](/14-kernel/initramfs)
- [内核模块](/14-kernel/modules)


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
