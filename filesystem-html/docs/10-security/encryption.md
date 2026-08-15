---
title: 文件系统加密
---

# 文件系统加密 — 静态数据保护

> <span class="kg-badge kg-badge--security">安全权限</span>
> LUKS / eCryptfs / fscrypt · 加密即安全

文件系统加密保护**静态数据**——磁盘被偷 / 磁盘镜像泄漏时，无法读出真实内容。

## 1. 加密层级

```
┌──────────────────────────────────┐
│  应用层加密（应用自己）           │  ← GPG / OpenSSL
├──────────────────────────────────┤
│  文件系统加密                     │  ← ext4 / xfs / btrfs
├──────────────────────────────────┤
│  块设备加密                       │  ← LUKS / dm-crypt
├──────────────────────────────────┤
│  物理加密（自加密盘）             │  ← SED（Self-Encrypting Drive）
└──────────────────────────────────┘
```

每层独立，常**叠加**：

- 块设备 + FS 加密（双重保险）
- 应用加密 + FS 加密（合规场景）

## 2. LUKS（Linux Unified Key Setup）

LUKS 是 Linux 的**块设备加密标准**。基于 dm-crypt，提供密码学强度的保护。

### 2.1 创建 LUKS

```bash
# 1. 准备设备
dd if=/dev/zero of=/dev/sdb bs=1M count=100
# 或用真盘

# 2. 创建 LUKS 头
cryptsetup luksFormat /dev/sdb
# WARNING: 确认！输入 YES
# 输入密码（或 keyfile）

# 3. 打开
cryptsetup open /dev/sdb mysecret
# 输入密码
# → /dev/mapper/mysecret

# 4. 格式化（任意 FS）
mkfs.ext4 /dev/mapper/mysecret

# 5. 挂载
mkdir /mnt/secret
mount /dev/mapper/mysecret /mnt/secret

# 6. 用完
umount /mnt/secret
cryptsetup close mysecret
```

### 2.2 自动挂载

```bash
# /etc/crypttab
mysecret /dev/sdb /etc/keys/luks.key luks
```

```bash
# 生成 keyfile
dd if=/dev/urandom of=/etc/keys/luks.key bs=512 count=1
chmod 600 /etc/keys/luks.key
cryptsetup luksAddKey /dev/sdb /etc/keys/luks.key
```

```bash
# /etc/fstab
/dev/mapper/mysecret /mnt/secret ext4 defaults,_netdev 0 2
```

重启自动解密。

### 2.3 LUKS 版本

| 版本 | 加密算法 | 推荐 |
|------|----------|------|
| LUKS1 | AES / 其它 | 老系统 |
| LUKS2 | Argon2 PBKDF, 支持 token | **推荐** |

```bash
# 看 LUKS 版本
cryptsetup luksDump /dev/sdb | grep "Version"
```

## 3. 实战：远程解密（cloud-init）

云端主机需要密码解锁 LUKS，用 network-bound disk encryption (NBDE)：

```bash
# Tang + Clevis 方案
yum install -y tang clevis
systemctl start tangd

# 绑定
clevis bind luks -d /dev/sdb \
    '{"t": {"url": "http://tang.example.com"}}'

# 自动解锁（启动时连 tang 服务器）
```

## 4. 实战：替换现有磁盘加密

```bash
# 在线加密（非破坏性）
cryptsetup reencrypt --encrypt \
    --reduce-device-size 32M /dev/sdb
```

需要新内核 + 文件系统未挂载。

## 5. 文件系统级加密（fscrypt）

fscrypt 是 Linux 内核原生文件系统加密（ext4 / xfs / btrfs）。

```bash
# 1. 设置策略密钥
mkdir -p /etc/fscrypt
fscrypt setup

# 2. 在目录上启用加密
mkdir /encrypted
chmod 700 /encrypted
fscrypt encrypt /encrypted --user=alice

# 输入密码 → 拿到 protector
```

```bash
# 3. 之后在该目录下创建的文件自动加密
echo "secret" > /encrypted/file.txt
# 数据在磁盘上加密存储

# 4. 解锁（系统重启后）
fscrypt unlock /encrypted
# 输入密码
```

**优点**：

- 不用整个块设备加密
- 多用户独立密钥
- 与 SUID / capabilities 不冲突

## 6. eCryptfs（历史）

eCryptfs 是堆叠式加密 FS，曾经用于 Ubuntu Home dir encryption。

**现状**：已被 fscrypt 取代。Ubuntu 22+ 默认不再用。

```bash
# 老 Ubuntu 用法（已弃用）
ecryptfs-setup-private
```

## 7. 实战：全盘加密（full disk encryption, FDE）

```bash
# 安装时启用 LUKS（大多数发行版默认）
# Ubuntu / CentOS 7+ 安装器都支持

# /boot 不加密（必须能启动）
/dev/sda1   /boot      ext2   defaults  0 2
/dev/sda2   /          ext4   defaults  0 1
# /dev/sda2 实际是 LUKS 解密后的 /dev/mapper/root
```

## 8. 性能影响

| 加密方式 | 性能损失 | 说明 |
|----------|----------|------|
| 无加密 | 0% | 基准 |
| LUKS AES-NI | **< 5%** | 现代 CPU 支持硬件加速 |
| LUKS 无硬件 | 20-50% | 软加密 |
| fscrypt | 5-15% | 取决于文件系统 |
| 自加密盘（SED） | ~0% | 加密在盘内 |

**结论**：现代 CPU 几乎无感知。

## 9. 实战：加密备份到异地

```bash
# 加密备份文件
gpg --symmetric --cipher-algo AES256 backup.tar.gz
# 输出 backup.tar.gz.gpg

# 解密
gpg --decrypt backup.tar.gz.gpg > backup.tar.gz
```

## 10. 关键差异：LUKS vs fscrypt

| 特性 | LUKS | fscrypt |
|------|------|---------|
| 加密层级 | 块设备 | 文件系统 |
| 加密范围 | 整块设备 | 部分目录 |
| 性能 | 高 | 高 |
| 多用户 | 单密钥 | 多密钥 |
| 容器友好 | ❌（容器见不到） | ✅ |
| 内核版本 | 任意 | ≥ 4.6 |

**生产推荐**：

- 全盘数据保护 → **LUKS**
- 单用户 / 多用户数据 → **fscrypt**
- 自加密盘 + LUKS → **双保险**

## 11. 实战：KMS 自动管理密钥

```bash
# cloud KMS / HSM 集成
# 例如：AWS KMS + LUKS + 启动脚本
# /etc/init.d/decrypt-luks 启动时调 KMS 解密
```

或用 `clevis` + `Tang` 实现：

- 主机重启时 → 自动连 tang 服务器验证 → 解密 LUKS
- tang 服务器不可达 → 不解密
- 无需人工输入密码

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| LUKS = 块设备加密 | "LUKS=块" |
| fscrypt = 目录加密 | "fscrypt=目录" |
| AES-NI 几乎无损耗 | "AES-NI=无感" |
| keyfile 加密 key | "keyfile=密钥" |
| Tang + Clevis 远程解锁 | "NBDE=远程" |

## 参考

- cryptsetup 手册
- fscrypt 文档：<https://github.com/google/fscrypt
- dm-crypt 内核文档
- 实用：LUKS2 规范