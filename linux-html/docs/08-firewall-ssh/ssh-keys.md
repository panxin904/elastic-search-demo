---
title: ssh-keygen / ssh-copy-id
date: 2026-08-15  # date-auto-injected
---

# ssh-keygen / ssh-copy-id

> 公私钥配对，免密码登录更安全。

## 🔐 ssh-keygen 生成密钥

```bash
ssh-keygen -t ed25519                 # 推荐
ssh-keygen -t ed25519 -C 'alice@work' # 加注释（便于识别）
ssh-keygen -t rsa -b 4096             # 兼容性更好（老系统）

# 自定义文件 / 密码
ssh-keygen -t ed25519 -f ~/.ssh/id_work -C 'work key'

# 评估强度
ssh-keygen -lf ~/.ssh/id_ed25519      # 显示指纹
ssh-keygen -l -v -f ~/.ssh/id_ed25519 # 显示 ASCII art 指纹
```

## 🆚 算法选择

| | ed25519 | RSA-4096 | ECDSA-P256 |
|--|---------|----------|-------------|
| 长度 | 256-bit | 4096-bit | 256-bit |
| 安全 | ✅ 强 | ✅ 强 | ⚠ 某些实现被怀疑 NSA 留后门 |
| 速度 | 极快 | 慢 | 快 |
| 兼容 | OpenSSH 6.5+ (2014) | 全 | OpenSSH 5.7+ (2011) |

**推荐 ed25519**。仅兼容老系统（OpenSSH < 6.5）才用 RSA-4096。

## 🚀 ssh-copy-id 上传公钥

```bash
ssh-copy-id user@host                       # 默认 ~/.ssh/id_rsa.pub
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host
ssh-copy-id -i ~/.ssh/id_work.pub user@host -p 2222

# 第一次会问密码（用于把公钥传到服务器）
```

自动过程：
1. ssh 登录服务器（密码）
2. 创建 `~/.ssh/` 目录（如不存在）
3. 写入 `~/.ssh/authorized_keys`
4. 设置权限 `700` / `600`

## 🛠 手工上传

```bash
# 方法 1：ssh + cat
cat ~/.ssh/id_ed25519.pub | ssh user@host \
  'mkdir -p ~/.ssh && chmod 700 ~/.ssh && \
   cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'

# 方法 2：scp + ssh
scp ~/.ssh/id_ed25519.pub user@host:/tmp/
ssh user@host 'cat /tmp/id_ed25519.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

## 🔒 强制使用密钥登录

```bash
# 服务器端 sshd_config
PasswordAuthentication no
PubkeyAuthentication yes

# 改完
sudo sshd -t && sudo systemctl reload sshd
```

**⚠️ 重要**：先确保当前会话已能用密钥登录，再关闭密码认证！

## 🧬 多密钥管理

### 一台机器多个身份

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_work -C 'work'
ssh-keygen -t ed25519 -f ~/.ssh/id_personal -C 'personal'

# 客户端 ~/.ssh/config
Host work-git
    HostName github.com
    User alice
    IdentityFile ~/.ssh/id_work

Host personal-git
    HostName github.com
    User alice
    IdentityFile ~/.ssh/id_personal
```

### SSH Agent

避免每次输私钥密码：

```bash
eval $(ssh-agent -s)                    # 启动 agent
ssh-add ~/.ssh/id_ed25519               # 加私钥（输入密码一次）
ssh-add -l                              # 列出已加

# macOS / Windows 用 keychain 自动解锁
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
ssh-add --apple-load-keychain           # 重启后恢复

# 转发 agent 到远端（慎用！）
ssh -A user@host                        # 开启 agent 转发
# 远端可访问本地的私钥
```

## 🛡 服务器端密钥指纹验证

第一次连接会问 "Are you sure you want to continue connecting?"

```
The authenticity of host 'server' can't be established.
ED25519 key fingerprint is SHA256:abc...
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no)?
```

可以提前确认服务器的指纹：

```bash
ssh-keyscan server                      # 拉取服务器公钥
ssh-keyscan -t ed25519 server          # 指定算法
```

## 🧹 清理旧密钥

```bash
# 看所有 known_hosts
ssh-keygen -l -f ~/.ssh/known_hosts

# 删某条
ssh-keygen -R server                    # 删整个 server
ssh-keygen -R '[10.0.0.5]:2222'         # 指定端口

# 服务器端：清理过期 authorized_keys
ssh-keygen -lf ~/.ssh/authorized_keys   # 列出所有公钥
```

## 🛡 安全实践

```bash
# 1. 私钥密码
ssh-keygen -t ed25519 -o -a 100
# -o OpenSSH 格式 / -a 100 = 100 轮 KDF（破解更难）

# 2. 私钥 600
chmod 600 ~/.ssh/id_*

# 3. 转发到 agent 时避免长期保持
unset SSH_AUTH_SOCK                     # 清理

# 4. 多设备审计
for f in ~/.ssh/id_*.pub; do
  echo "=== $f ==="
  ssh-keygen -lf "$f"
done

# 5. 强算法（sshd_config）
PubkeyAcceptedAlgorithms ssh-ed25519,ssh-rsa
```

## 🪝 故障排查

```bash
# "Permission denied (publickey)"
ssh -v user@host                        # -v 看详细
# 看 "Offering public key" / "Authentications that can continue"

# 常见原因：
# 1. 服务器端 ~/.ssh 权限不对
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 2. authorized_keys 末尾换行
# 加一个空行 + 重新登录

# 3. 私钥权限太开（被拒）
chmod 600 ~/.ssh/id_ed25519

# 4. SELinux 改了 authorized_keys 上下文（RHEL）
restorecon -R -v ~/.ssh

# 5. 服务器 PermitRootLogin no
# 用普通用户 + sudo
```

## 🔗 下一步

- [OpenSSH 配置](/08-firewall-ssh/openssh)
- [SSH 隧道 / 代理](/08-firewall-ssh/ssh-tunnel)
- [sshd_config 加固](/13-security/sshd-config)