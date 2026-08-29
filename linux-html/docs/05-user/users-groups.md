---
title: 用户与用户组
date: 2026-08-15  # date-auto-injected
---

# 用户与用户组

> Linux 是多用户系统。每个文件 / 进程都属于某个用户 + 组。

## 🧬 三层身份

```
UID (User ID)        - 用户唯一标识
GID (Group ID)       - 主组
附属组                - 用户可同时属于多个组
```

```bash
id                      # 看自己
id alice                # 看 alice
whoami                  # 当前用户
who                    # 当前登录用户
groups alice            # alice 的所有组

cat /etc/passwd        # 所有用户
cat /etc/group         # 所有组
```

## 👤 /etc/passwd 字段

```
alice:x:1000:1000:Alice:/home/alice:/bin/bash
│     │ │    │    │       │         │
│     │ │    │    │       │         └─ 登录 shell
│     │ │    │    │       └─ 家目录
│     │ │    │    └─ GECOS（注释，可空）
│     │ │    └─ GID（主组）
│     │ └─ UID
│     └─ 密码占位（x = 真密码在 /etc/shadow）
└─ 用户名
```

## 🔐 /etc/shadow

```
alice:$6$abc...xyz:19000:0:99999:7:::
│     │             │    │ │     │ │││
│     │             │    │ │     │ │└─ 未使用
│     │             │    │ │     │ └─ 账户失效日
│     │             │    │ │     └─ 密码失效日
│     │             │    │ └─ 密码最大有效天数
│     │             │    └─ 警告天数
│     │             └─ 最后修改日（距 1970-01-01）
│     └─ 哈希密码（$6 = SHA-512）
└─ 用户名
```

只有 root 能读 `/etc/shadow`。

## 🛠 用户管理

```bash
# 创建用户
useradd -m -s /bin/bash alice        # -m 创建 home，-s 指定 shell
useradd -m -G dev,docker bob         # 加入附加组

# 设置密码
passwd alice                        # 交互
echo 'alice:p@ssw0rd' | chpasswd     # 脚本（不安全）

# 修改
usermod -aG docker alice             # -a 追加；不带 -a 会覆盖
usermod -s /bin/zsh alice           # 改 shell
usermod -d /home/new alice          # 改家目录
usermod -L alice                    # 锁定
usermod -U alice                    # 解锁

# 删除
userdel -r alice                    # -r 同时删除 home
```

## 🛡 用户组管理

```bash
groupadd dev                         # 创建组
groupadd -g 1500 dev                 # 指定 GID
groupmod -n devops dev               # 改名
groupmod -g 1501 dev                 # 改 GID
groupdel dev                         # 删组

# 看用户所属组（附加）
getent group dev                     # 看组里成员
groups alice
id alice
```

## 🏠 家目录与骨架

```bash
ls -la /etc/skel/                    # 用户骨架（useradd 时拷贝）
# 新建用户的 .bashrc / .profile 等从这里拷贝

# 给已建用户补骨架
cp /etc/skel/.bashrc /home/alice/
chown alice:alice /home/alice/.bashrc
```

## 🌍 UID 范围

| UID | 用途 |
|-----|------|
| 0 | root |
| 1-999 | 系统用户（服务、伪用户） |
| 1000+ | 普通用户 |
| 1000-60000 | 可分配 |
| 65534 | `nobody`（无人能登录的服务用） |

## 🛡 sudo - 临时提权

```bash
sudo cmd                          # 以 root 跑
sudo -u alice cmd                  # 以 alice 跑
sudo -i                            # 切 root（保持环境）
sudo -s                            # 用 root shell
sudo !!                            # 上一条命令加 sudo

# 编辑受保护文件
sudo -e /etc/nginx/nginx.conf     # 安全编辑
```

### /etc/sudoers

```bash
visudo                            # 安全编辑
# 用户 alice 拥有所有权限
alice    ALL=(ALL:ALL) ALL

# dev 组可重启 nginx / 重启服务
%dev    ALL=(ALL) /bin/systemctl restart nginx

# 免密码（仅限内网测试机）
alice   ALL=(ALL) NOPASSWD: ALL
```

## 🔐 /etc/login.defs

用户创建默认值：UID 范围、家目录模式、密码策略：

```bash
UID_MIN          1000
UID_MAX         60000
GID_MIN          1000
HOME_MODE        0700
PASS_MAX_DAYS    99999
```

## 🛠 实战

```bash
# 创建 devops 用户，加入常用组
useradd -m -G wheel,docker,sudo devops
passwd devops

# 允许某用户 sudo
echo 'devops ALL=(ALL) ALL' >> /etc/sudoers.d/devops

# 给老用户补附加组
usermod -aG docker alice

# 列出所有能 sudo 的人
getent group wheel sudo
```

## 🔗 下一步

- [chmod 权限](/05-user/chmod)
- [chown / chgrp](/05-user/chown)
- [sudo 提权](/05-user/sudo)
- [ACL 细粒度权限](/05-user/acl)