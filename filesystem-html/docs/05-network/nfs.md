---
title: NFS
---

# NFS 网络文件系统 — UNIX 世界的经典共享协议

> <span class="kg-badge kg-badge--network">网络协议</span>
> RPC · v4 · 共享文件夹标准

NFS（Network File System）是 Sun 公司在 1984 年提出的网络文件系统协议，是 Unix/Linux 之间共享文件的标准方式。今天主流是 **NFSv4**（2003 标准化），它在性能、安全、状态上比 NFSv3 强很多。

## 1. NFS 协议版本

| 版本 | 特点 |
|------|------|
| NFSv2 | UDP，无状态，老 |
| NFSv3 | UDP/TCP，64 位偏移，无状态 |
| NFSv4 | 单连接、有状态、内置 ACL、防火墙友好 |
| NFSv4.1 | pNFS 并行 I/O |
| NFSv4.2 | 服务器端复制、稀疏文件、空间预留 |

## 2. 架构

```
┌─────────────────┐
│  NFS Client     │
│  - 内核 NFS 模块 │
└────────┬────────┘
         │ TCP/UDP (port 2049)
┌────────▼────────┐
│  NFS Server     │
│  - nfsd         │
│  - mountd       │
│  - rpcbind      │
└─────────────────┘
```

- **nfsd**：内核态服务，处理 NFS 请求
- **mountd**：处理挂载请求（v4 不需要）
- **rpcbind / portmap**：RPC 端口映射（v4 不需要）
- **lockd / statd**：NFS 文件锁（v4 内置）

## 3. 服务端部署

### 3.1 安装

```bash
# CentOS / RHEL
yum install -y nfs-utils

# Ubuntu / Debian
apt install -y nfs-kernel-server
```

### 3.2 配置导出

`/etc/exports`：

```
/data/shared   192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)
/home/users    *(rw,sync,no_subtree_check,root_squash)
/backup        10.0.0.0/8(ro,sync,no_subtree_check)
```

| 选项 | 含义 |
|------|------|
| rw / ro | 读写 / 只读 |
| sync / async | 同步写盘 / 异步写盘（async 性能高但宕机丢数据） |
| no_subtree_check | 不检查父目录（**推荐**，避免权限问题） |
| root_squash | 把 root 用户映射成 nobody（**安全默认**） |
| no_root_squash | root 保留权限（**危险**，仅限可信客户端） |
| all_squash | 所有用户映射成 nobody |
| anonuid/anongid | 自定义映射 UID/GID |
| fsid | 显式指定 FS ID（NFSv4 推荐） |

### 3.3 启动

```bash
# 启动服务
systemctl start nfs-server
systemctl enable nfs-server

# 重新加载配置（不中断）
exportfs -r

# 验证
exportfs -v
showmount -e localhost
```

## 4. 客户端挂载

### 4.1 手动挂载

```bash
mount -t nfs -o vers=4.2,rsize=1048576,wsize=1048576,hard,intr \
    192.168.1.10:/data/shared /mnt/nfs
```

| 选项 | 推荐值 | 含义 |
|------|--------|------|
| vers | 4.2 | NFS 版本 |
| rsize / wsize | 1048576 | 单次读/写最大字节数（v4 默认 1MB） |
| hard | hard | 失败后无限重试（**推荐**） |
| soft | soft | 失败后报错（不推荐，破坏一致性） |
| intr | - | 允许中断 hard 重试（**v4 已不需要**） |
| sec | sys/krb5i/krb5p | 安全模式（推荐 krb5p 加密） |
| noatime | - | 不更新访问时间（性能优化） |

### 4.2 自动挂载（/etc/fstab）

```
192.168.1.10:/data/shared /mnt/nfs nfs4 defaults,_netdev,noatime,hard 0 0
```

### 4.3 自动发现（autofs）

```bash
# /etc/auto.master
/mnt/nfs  /etc/auto.nfs  --timeout=60

# /etc/auto.nfs
shared  -fstype=nfs4,rw,hard,noatime  192.168.1.10:/data/shared
```

按需挂载，减少空挂载的客户端开销。

## 5. 性能调优

### 5.1 服务端

```bash
# /etc/sysconfig/nfs
# 调整 nfsd 线程数
RPCNFSDCOUNT=64
RPCNFSDPRIORITY=0
NEED_SVCGSSD=""

# TCP 槽位数
MOUNTD_PORT=20048
STATD_PORT=20049
LOCKD_TCPPORT=20050
LOCKD_UDPPORT=20051
```

### 5.2 块大小

```bash
mount -t nfs -o rsize=1048576,wsize=1048576 ...
```

rsize/wsize 在 Linux 上 max = 1 MiB（NFSv4）。

### 5.3 网络

- 用 10GbE / 25GbE 网络
- **TCP 单流** → 多连接能跑满带宽
- 启用 jumbo frame（MTU 9000）

### 5.4 安全模式

```bash
# Kerberos 加密（性能 ~60%，但安全）
mount -o sec=krb5p server:/path /mnt/nfs

# 完整性（不解密，但 HMAC）
mount -o sec=krb5i server:/path /mnt/nfs
```

## 6. NFSv4.1 pNFS（并行 I/O）

pNFS 把数据平面拆出去，client 直接访问各存储后端：

```
       ┌─── DS1（数据服务器）───┐
Client ├─── DS2 ────────────────┤
       └─── DS3 ────────────────┘
            ↑
       MDS（元数据）
```

吞吐可比单 server 高 5-10×。需要服务端支持（Linux NFS Ganesha + 后端 / NetApp / 国产厂商）。

## 7. 实战监控

```bash
# 服务端指标
nfsstat -s            # 客户端看服务端性能
nfsstat -c            # 客户端自身

# /proc/net/rpc/nfsd 暴露详细计数器
cat /proc/net/rpc/nfsd

# 推荐用 Prometheus node_exporter + grafana dashboard
```

## 8. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| NFSv4 主流 | "v4=单连接状态化" |
| 默认 root_squash | "root=anonymous" |
| 推荐 hard + sync | "hard 永不放弃" |
| rsize/wsize = 1M | "1M=块大小" |
| pNFS 是性能关键 | "pNFS=并行" |

## 参考

- Linux NFS wiki：<https://wiki.linux-nfs.org/>
- RFC 5661（NFSv4.1）
- RHEL Storage Administration Guide