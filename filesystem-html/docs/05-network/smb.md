---
title: SMB / CIFS
date: 2026-08-15  # date-auto-injected
---

# SMB / CIFS — Windows 世界的共享文件协议

> <span class="kg-badge kg-badge--network">网络协议</span>
> 微软主导 · 跨平台共享 · Active Directory 集成

SMB（Server Message Block）是微软提出的文件共享协议，又称 CIFS（Common Internet File System）。它是**Windows 文件共享的事实标准**，Linux/macOS 通过 Samba 兼容。

## 1. SMB 版本

| 版本 | Windows | 主要改进 |
|------|---------|---------|
| SMBv1 | Win95/98/XP | 老版本，**不安全**（WannaCry 漏洞） |
| SMBv2 | Vista / Win7 | 性能、签名、流水线 |
| SMBv2.1 | Win7 | 机会锁（Oplock）增强 |
| SMBv3 | Win8/Server 2012 | **AES 加密**、多通道、性能 |
| SMBv3.1.1 | Win10 | AES-256、加密完整性 |

**建议**：禁用 SMBv1，强制 SMBv2+。

## 2. 跨平台实现

| 实现 | 平台 | 备注 |
|------|------|------|
| Windows Server | Windows | 原生 |
| Samba | Linux/Unix | 主流 |
| macOS SMBX | macOS | Apple 自家实现 |
| NetApp / EMC 商用 | 各类 | 商业 NAS |

## 3. Samba 服务端部署（Linux）

### 3.1 安装

```bash
# CentOS
yum install -y samba samba-client

# Ubuntu
apt install -y samba
```

### 3.2 配置

`/etc/samba/smb.conf`：

```ini
[global]
   workgroup = WORKGROUP
   server string = Samba Server
   security = user
   passdb backend = tdbsam
   # 强制 SMBv2+
   min protocol = SMB2
   max protocol = SMB3
   # 启用加密（性能略降）
   server signing = mandatory
   smb encrypt = desired

[shared]
   comment = Public Share
   path = /data/shared
   browseable = yes
   writable = yes
   guest ok = no
   valid users = @smbgroup
   create mask = 0664
   directory mask = 0775
```

### 3.3 用户管理

```bash
# Samba 用户（依赖 Linux 系统用户）
useradd -s /sbin/nologin alice
smbpasswd -a alice

# 把用户加入组
groupadd smbgroup
gpasswd -a alice smbgroup

# 重启服务
systemctl restart smb
systemctl enable smb
```

### 3.4 防火墙

```bash
firewall-cmd --permanent --add-service=samba
firewall-cmd --reload
# 或开端口
firewall-cmd --permanent --add-port=445/tcp
firewall-cmd --permanent --add-port=139/tcp  # 老 netbios
```

## 4. 客户端挂载

### 4.1 Windows

```
\\192.168.1.10\shared
```

或映射网络驱动器 → Z:\\192.168.1.10\shared

### 4.2 Linux

```bash
# mount.cifs
mount -t cifs -o username=alice,password=secret,vers=3.1.1 \
    //192.168.1.10/shared /mnt/smb

# 凭证文件（推荐）
cat > /etc/samba/smb-cred <<EOF
username=alice
password=secret
EOF
chmod 600 /etc/samba/smb-cred

mount -t cifs -o credentials=/etc/samba/smb-cred,vers=3.1.1 \
    //192.168.1.10/shared /mnt/smb
```

### 4.3 macOS

`Finder → 前往 → 连接服务器` → `smb://192.168.1.10/shared`

## 5. 关键 SMB 特性

### 5.1 Opportunistic Locking（Oplock）

SMB 让客户端**缓存文件**和**锁文件**，提升性能：

| 类型 | 作用 |
|------|------|
| Level I Oplock | 独占缓存（无其它客户端） |
| Level II Oplock | 读缓存（多客户端读） |
| Batch Oplock | 独占 + 延迟关闭（本地写缓存） |
| Lease v2 (SMBv3) | 更细粒度的锁 |

**坑**：网络中断时，客户端可能持有"孤儿" oplock，需要重新协商。

### 5.2 多通道（SMBv3）

```ini
# 服务器端
server multi channel support = yes
```

多个 TCP 连接并发 → 总带宽叠加。配合多网卡时尤其明显。

### 5.3 持续可用性（SMBv3）

```ini
# 服务器端
# 启用 CA：客户端断连重连后文件句柄不丢
```

适合高可用场景（Hyper-V、SQL Server over SMB）。

### 5.4 DFS（分布式文件系统）

```ini
# 命名空间聚合多台服务器的共享
[dfs]
   path = /data/dfs
   msdfs root = yes
```

用户访问 `\\server\dfs\path` 时，自动路由到正确的存储。

## 6. 权限模型

SMB 通过 ACL（访问控制列表）做权限：

- Linux 上 Samba 把 POSIX 权限映射成 NTFS ACL
- 启用 `acl` 模块可以精确控制
- Windows 上的 NTFS ACL 是真正的"事实标准"

```bash
# 查看
getfacl /data/shared
# 设置
setfacl -m u:alice:rwx /data/shared/file.txt
```

## 7. 性能调优

### 7.1 块大小

SMB 内部默认 1MB I/O。NetApp/Windows 优化可达 1MB。

### 7.2 大文件传输

```bash
# 客户端增大 write size
mount -o rsize=130048,wsize=130048 ...
```

### 7.3 服务端调优

```ini
[global]
   # 接收缓冲
   socket options = TCP_NODELAY IPTOS_LOWDELAY
   # 死连接清理
   dead time = 15
   keepalive = 30
```

### 7.4 大并发

```ini
[global]
   max connections = 0       # 0=无限
   max smbd processes = 1000 # 最大进程数
```

## 8. 实战：与 AD 集成

```bash
# Samba + Winbind + AD
[global]
   security = ads
   realm = EXAMPLE.COM
   workgroup = EXAMPLE
   idmap config * : range = 16777216-33554431
   idmap config * : backend = rid
```

让 Linux 文件服务器加入 Active Directory 域，用户用域账号访问共享。

## 9. SMB vs NFS 选型

| 维度 | SMB | NFS |
|------|-----|-----|
| 主战场 | Windows / macOS | Linux / Unix |
| 权限 | NTFS ACL（精细） | POSIX（粗） |
| 安全 | 加密内置（v3+） | 需 Kerberos |
| 跨网 | 友好（端口 445） | v4 友好 |
| 性能 | 中 | **优**（Linux 平台） |
| 文件锁 | Oplock 强 | v4 lease 强 |

**经验**：

- 纯 Linux 集群 → **NFS**
- Windows 客户端多 → **SMB**
- 跨平台 → 两者都开

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 禁用 SMBv1 | "v1=万恶之源" |
| SMBv3 加密 | "v3=必开加密" |
| 多通道 = 性能 | "多通道叠加带宽" |
| Samba = Linux 端 | "Samba=Linux 实现" |
| Oplock 缓存原理 | "Oplock=客户端缓存" |

## 参考

- Samba 文档：<https://www.samba.org/samba/docs/
- MS-SMB 协议规范
- Microsoft SMB 最佳实践