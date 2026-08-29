---
title: FTP / SFTP
date: 2026-08-15  # date-auto-injected
---

# FTP / SFTP — 老牌文件传输协议

> <span class="kg-badge kg-badge--network">网络协议</span>
> FTP 明文 · SFTP 走 SSH · 备份上传场景

FTP（File Transfer Protocol）和 SFTP（SSH File Transfer Protocol）是两个常被混淆的协议：

| 协议 | 含义 | 安全 | 端口 |
|------|------|------|------|
| FTP | 老牌明文协议 | ❌ | 21（控制）+ 数据端口 |
| FTPS | FTP + TLS | ✅ | 990 + 数据端口 |
| SFTP | SSH 上的文件传输 | ✅ | **22**（SSH） |
| TFTP | 简单 UDP 文件传输 | ❌ | 69 |

**实战首选 SFTP**（SSH 自带、易配置、过防火墙）。

## 1. FTP 的关键问题

FTP 是双通道协议：

```
控制连接（port 21）：命令
数据连接（port 20 active / 随机端口 passive）：文件
```

**致命缺陷**：

- 用户名、密码、文件内容**全部明文**
- 需要多个端口 → 防火墙和 NAT 不友好
- 现代浏览器默认禁 FTP

**FTP 主动 vs 被动模式**：

| 模式 | 数据连接 | 适用 |
|------|----------|------|
| Active | server → client（容易过 NAT） | 服务器在公网 |
| Passive | client → server | 客户端在 NAT 后（**默认推荐**） |

## 2. SFTP 实战（OpenSSH 自带）

### 2.1 服务端

OpenSSH 默认开启 SFTP 子系统：

```bash
# /etc/ssh/sshd_config
Subsystem sftp internal-sftp -l INFO

Match Group sftpusers
    ChrootDirectory /home/%u
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
```

```bash
# 建用户（家目录）
useradd -m -s /sbin/nologin alice
passwd alice

# 限制用户到 sftpusers 组
usermod -aG sftpusers alice
chown root:root /home/alice
chmod 755 /home/alice
mkdir -p /home/alice/upload
chown alice:alice /home/alice/upload
```

```bash
systemctl restart sshd
```

### 2.2 客户端连接

```bash
# 命令行
sftp alice@server
sftp> put local.txt /upload/
sftp> get remote.txt
sftp> ls
sftp> bye

# 用密钥
sftp -i ~/.ssh/id_rsa alice@server

# rsync over ssh（最常用同步方式）
rsync -avz -e ssh /local/dir/ alice@server:/remote/dir/
```

### 2.3 客户端工具

| 工具 | 平台 |
|------|------|
| FileZilla | 跨平台 GUI |
| WinSCP | Windows |
| Cyberduck | macOS |
| lftp | Linux 命令行 |

## 3. FTPS（FTP + TLS）

```bash
# vsftpd 配置 FTPS
ssl_enable=YES
allow_anon_ssl=NO
force_local_data_ssl=YES
force_local_logins_ssl=YES
ssl_tlsv1=YES
ssl_sslv2=NO
ssl_sslv3=NO
ssl_ciphers=HIGH
rsa_cert_file=/etc/ssl/certs/vsftpd.pem
rsa_private_key_file=/etc/ssl/private/vsftpd.key
```

```bash
systemctl restart vsftpd
```

客户端需显式启用 TLS（如 FileZilla 选 "FTP over TLS (explicit)"）。

## 4. 实战：SFTP 限速

OpenSSH 自带 sftp 内置限速（OpenSSH 8.4+）：

```bash
# sshd_config
Subsystem sftp internal-sftp -l INFO -d /home/%u -u 0027
# -u umask
```

但没有原生带宽限制。要限速可用：

- `trickle` 包装
- iptables tc 规则
- 商业 sftp 网关（CrushFTP / JSCAPE MFT）

## 5. 实战：SFTP 服务器替代品

| 工具 | 特点 |
|------|------|
| OpenSSH SFTP | 内置、简洁 |
| ProFTPD mod_sftp | 可插拔模块 |
| CrushFTP | 商业、Web UI |
| SFTPGo | Go 语言、HTTP API、Web UI |

## 6. TFTP（极简文件传输）

```
UDP 69
无认证、无加密、无目录概念
只支持读 / 写整个文件
```

应用场景：网络设备配置文件、PXE 启动、网络摄像头固件。

```bash
# Linux 上
yum install -y tftp-server
systemctl start tftp
# 路径：/var/lib/tftpboot

# 客户端
tftp 192.168.1.10
> put file.bin
> get config.txt
> quit
```

## 7. 实战：SFTP 多用户隔离

```bash
# /etc/ssh/sshd_config
Subsystem sftp internal-sftp

# 用户分组
Match Group dev
    ChrootDirectory /srv/dev/%u
    ForceCommand internal-sftp

Match Group ops
    ChrootDirectory /srv/ops/%u
    ForceCommand internal-sftp

# 每个用户独立目录
for u in alice bob charlie; do
    useradd -m -s /sbin/nologin -g dev $u
    mkdir -p /srv/dev/$u/upload
    chown root:root /srv/dev/$u
    chmod 755 /srv/dev/$u
    chown $u:$u /srv/dev/$u/upload
done
```

每个用户登录后只看到自己的目录，安全性强。

## 8. SFTP 性能 vs scp vs rsync

| 工具 | 性能 | 特性 |
|------|------|------|
| scp | 中 | 简单 |
| sftp | 中 | 可中断、可恢复 |
| rsync | **优** | 增量、压缩、断点续传 |

**实战首选 rsync over ssh**：增量同步 + 断点续传 + 压缩。

## 9. 安全清单

```text
[ ] SSH 禁密码登录（用公私钥）
[ ] 禁 root 登录
[ ] 用 ChrootDirectory 隔离用户
[ ] 防火墙只开 22
[ ] 配置 fail2ban 防爆破
[ ] 用 SFTP 不要用 FTP
[ ] 日志定期审计
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| FTP 明文不可用 | "FTP=裸奔" |
| SFTP 走 SSH 22 | "SFTP=22 端口" |
| Chroot 隔离 | "Chroot=每人独立" |
| rsync over ssh | "rsync=ssh 增量" |
| TFTP 设备用 | "TFTP=网络设备" |

## 参考

- OpenSSH SFTP 文档
- RFC 959（FTP）/ RFC 4251-4254（SSH）
- SFTPGo：<https://github.com/drakkan/sftpgo>