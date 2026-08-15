---
title: OpenSSH 配置
---

# OpenSSH 配置

> sshd 是 Linux 服务器对外最重要的服务。配置不当 = 全网可登录 root。

## 📜 默认端口

```
22/tcp    SSH 默认
```

建议改成非 22（减少自动化扫描），但用非标端口 ≠ 安全，只是"躲"。

## 📂 sshd 关键文件

```
/etc/ssh/sshd_config         # 服务端配置
/etc/ssh/ssh_config          # 客户端配置（每用户）
~/.ssh/config                # 用户客户端配置
~/.ssh/authorized_keys       # 公钥白名单
~/.ssh/known_hosts           # 已确认的服务器指纹
~/.ssh/id_ed25519            # 用户私钥
~/.ssh/id_ed25519.pub        # 用户公钥
```

权限必须严格：

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 644 ~/.ssh/authorized_keys
chmod 644 ~/.ssh/known_hosts
```

## 🛡 关键 sshd_config

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak  # 备份
sudo systemctl reload sshd                                # 改完 reload
```

### 基础加固

```bash
# 禁 root 登录
PermitRootLogin no

# 仅允许公钥（禁密码）
PasswordAuthentication no
PubkeyAuthentication yes

# 限制允许的用户 / 组
AllowGroups ssh-users

# 改端口
Port 2222

# 禁空密码
PermitEmptyPasswords no

# 禁 X11（一般不需要）
X11Forwarding no

# 禁 TCP 转发（除非需要）
AllowTcpForwarding no

# 禁 Agent 转发
AllowAgentForwarding no
```

### 性能 / 安全

```bash
# 限制尝试次数
MaxAuthTries 3
MaxSessions 5

# 闲置超时
ClientAliveInterval 300
ClientAliveCountMax 2     # 600 秒（10 分钟）无活动则断

# 登录提示
Banner /etc/issue.net

# 仅允许现代算法
KexAlgorithms curve25519-sha256@libssh.org
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
```

### 完整示例

```bash
# /etc/ssh/sshd_config

Port 2222
AddressFamily inet
ListenAddress 0.0.0.0

Protocol 2

# 认证
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
KerberosAuthentication no
GSSAPIAuthentication no
UsePAM yes

# 限制
MaxAuthTries 3
MaxSessions 5
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2

AllowGroups ssh-users

# 安全选项
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no
PermitUserEnvironment no

# 算法白名单
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group18-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# 日志
LogLevel VERBOSE
SyslogFacility AUTH

Subsystem sftp internal-sftp
```

```bash
# 应用
sudo sshd -t                    # 验证配置语法
sudo systemctl reload sshd
```

## 🔑 公钥认证

### 生成密钥对

```bash
ssh-keygen -t ed25519                  # 推荐（256 位，安全快速）
ssh-keygen -t ed25519 -C 'alice@work'   # 加注释
ssh-keygen -t rsa -b 4096              # 兼容性更好但更长
```

会生成：
- `~/.ssh/id_ed25519` (私钥，**永不外传**)
- `~/.ssh/id_ed25519.pub` (公钥，可分享)

### 上传公钥

```bash
# 推荐（自动）
ssh-copy-id user@host
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host

# 手工
cat ~/.ssh/id_ed25519.pub | ssh user@host 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

### 强制使用密钥（关掉密码登录）

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no

sudo systemctl reload sshd
```

⚠️ **先测**：`PasswordAuthentication no` 之前，确保已有可用密钥。

### 多设备密钥

不同设备用不同密钥，authorized_keys 加注释：

```
ssh-ed25519 AAAA... alice@laptop
ssh-ed25519 AAAA... alice@desktop
ssh-ed25519 AAAA... alice@ci-runner
```

要回收某设备，删对应行。

## 🔒 限制登录

### 仅限特定用户

```bash
AllowUsers alice deploy
AllowGroups ssh-users developers
```

### 仅限特定来源 IP

```bash
# 改 sshd_config 不支持 IP 限制，用防火墙
sudo ufw allow from 192.168.1.0/24 to any port 2222
sudo ufw deny 2222
```

### 二步验证（2FA）

```bash
sudo apt install libpam-google-authenticator

# 用户配置
google-authenticator
# 输出二维码，扫到 Authenticator App

# /etc/pam.d/sshd
auth required pam_google_authenticator.so

# sshd_config
ChallengeResponseAuthentication yes
```

## 🪝 客户端配置

`~/.ssh/config`：

```
Host myserver
    HostName 192.168.1.10
    User alice
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

Host *.example.com
    User alice
    IdentityFile ~/.ssh/work_ed25519

Host *
    ServerAliveInterval 60
    Compression yes
```

然后 `ssh myserver` 一键登录。

## 🔗 下一步

- [ssh-keygen / ssh-copy-id](/08-firewall-ssh/ssh-keys)
- [SSH 隧道 / 代理](/08-firewall-ssh/ssh-tunnel)
- [sshd_config 加固](/13-security/sshd-config)