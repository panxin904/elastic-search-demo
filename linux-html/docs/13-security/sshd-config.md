---
title: sshd_config 加固
---

# sshd_config 加固

> SSH 是云时代服务器对外最常见的服务。配错 = 全网可登录 root。

## 🛡 检查清单

| 项 | 推荐值 | 默认 | 备注 |
|----|--------|------|------|
| `PermitRootLogin` | `no` | `prohibit-password` | 禁 root 直登 |
| `PasswordAuthentication` | `no` | `yes` | 强制公钥 |
| `PubkeyAuthentication` | `yes` | `yes` | 公钥认证 |
| `PermitEmptyPasswords` | `no` | `no` | |
| `Port` | `非 22` | `22` | 防扫描 |
| `AllowUsers` / `AllowGroups` | 白名单 | 全开 | |
| `MaxAuthTries` | `3` | `6` | 防暴力 |
| `LoginGraceTime` | `30` | `120` | |
| `ClientAliveInterval` | `300` | `0` | 空闲超时 |
| `ClientAliveCountMax` | `2` | `3` | 600s 关闭 |
| `X11Forwarding` | `no` | `yes` | 不需要 X11 就关 |
| `AllowTcpForwarding` | `no`（或 limited） | `yes` | 限制端口转发 |
| `AllowAgentForwarding` | `no` | `yes` | 防止 agent 转发 |
| `PermitUserEnvironment` | `no` | `no` | 防 ~/.ssh/environment 绕过 |
| `Protocol` | `2` | `2` | 仅 SSH2 |
| `KexAlgorithms` | `curve25519` | 见下 | 现代算法 |
| `Ciphers` | `chacha20-poly1305@...` | 见下 | 现代加密 |
| `MACs` | `hmac-sha2-512-etm@...` | 见下 | 现代 MAC |

## 📜 完整配置

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
```

```ini
# /etc/ssh/sshd_config

# === 网络 ===
Port 2222
AddressFamily inet
ListenAddress 0.0.0.0

# === 协议 ===
Protocol 2

# === 认证 ===
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
KerberosAuthentication no
GSSAPIAuthentication no
UsePAM yes

# 白名单用户 / 组
AllowGroups ssh-users

# === 安全选项 ===
MaxAuthTries 3
MaxSessions 5
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2

X11Forwarding no
AllowTcpForwarding local     # 仅本地转发允许，禁 remote
AllowAgentForwarding no
PermitUserEnvironment no
PermitTunnel no               # 禁 IP / 设备隧道（除非需要）

# === 算法白名单 ===
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group18-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
HostKey /etc/ssh/ssh_host_ed25519_key,/etc/ssh/ssh_host_rsa_key
PubkeyAcceptedAlgorithms ssh-ed25519,ssh-ed25519-cert-v01@openssh.com,rsa-sha2-512,rsa-sha2-256

# === 日志 ===
LogLevel VERBOSE
SyslogFacility AUTH

# === 限速（用 iptables / fail2ban） ===
# sshd_config 没有内置限速，靠防火墙

# === 子系统（可选） ===
Subsystem sftp internal-sftp
```

```bash
# 测试配置
sudo sshd -t
# 无输出 = OK

# 应用
sudo systemctl reload sshd
# ⚠️ 不要 restart（可能断连接！）
```

## 🛡 禁用弱算法

```bash
# 列出当前支持的算法
ssh -Q kex
ssh -Q cipher
ssh -Q mac

# 哪些算法被接受？
nmap --script ssh2-enum-algos -p 22 server
```

**禁用清单**：
- `diffie-hellman-group1-sha1`（弱 DH）
- `ssh-dss`（DSA，弱）
- `hmac-md5*`（弱 MAC）
- `3des-cbc`（弱加密）
- `arcfour*`（RC4，已不安全）
- `*-etm@...` 前缀的旧版本

## 🛡 拒绝 root / 密码登录

```bash
# 禁 root 登录
PermitRootLogin no

# 禁密码认证（用公钥）
PasswordAuthentication no

# ⚠️ 改前确保已有可用的密钥 + sudo 普通用户
```

如果不放心，先并行开：

```ini
# 允许密码 + 公钥并存（过渡）
PubkeyAuthentication yes
PasswordAuthentication yes
# 测试 OK 后关
```

## 🛡 防暴力破解：fail2ban

```bash
sudo apt install fail2ban

# /etc/fail2ban/jail.local
[sshd]
enabled = true
port    = ssh
filter  = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime  = 3600
findtime = 600

# 重启
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd
```

## 🛡 MFA 二次验证

```bash
# Google Authenticator
sudo apt install libpam-google-authenticator
google-authenticator           # 跑出二维码，用 Authenticator App 扫

# /etc/pam.d/sshd
auth required pam_google_authenticator.so

# /etc/ssh/sshd_config
ChallengeResponseAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```

## 🛡 限制登录来源

### 用户白名单

```bash
# 仅允许 alice / deploy
AllowUsers alice deploy

# 或按组
AllowGroups ssh-users
```

### IP 白名单（用防火墙）

```bash
# iptables
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 2222 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 2222 -j DROP

# ufw
sudo ufw allow from 192.168.1.0/24 to any port 2222 proto tcp

# firewalld
sudo firewall-cmd --permanent --add-rich-rule='rule family=ipv4 source address=192.168.1.0/24 port port=2222 protocol=tcp accept'
sudo firewall-cmd --reload
```

## 🛡 审计登录

```bash
# 当前登录
who
w
last                    # 历史（从 /var/log/wtmp）

# 失败尝试
sudo lastb               # 失败登录
sudo journalctl _COMM=sshd --since today

# 成功的（找后门）
sudo journalctl -u sshd --since today | grep "Accepted"

# 看 ssh 攻击
sudo journalctl -u sshd | grep -i "invalid user"
sudo journalctl -u sshd | grep -i "failed password"
```

## 🛡 banner

```bash
# /etc/issue.net（连前显示）
echo "Authorized access only. All activity may be monitored and reported." | sudo tee /etc/issue.net

# sshd_config
Banner /etc/issue.net
```

⚠️ Banner **不要**说 "Welcome" 或暴露系统版本。

## 🛡 安全 checklist

```bash
# 1. 备份配置
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# 2. sshd -t 验证
sudo sshd -t

# 3. 改权限（密钥必须严格）
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/*.pub
chmod 644 ~/.ssh/known_hosts

# 4. 关 root + 密码
PermitRootLogin no
PasswordAuthentication no

# 5. reload
sudo systemctl reload sshd

# 6. 测：另开一个会话，确认能登录
ssh -p 2222 alice@server

# 7. 关掉当前会话前，确认新会话能 sudo
```

## 🔗 下一步

- [OpenSSH 配置](/08-firewall-ssh/openssh)
- [auditd 审计](/13-security/auditd)
- [lynis 合规](/13-security/lynis)