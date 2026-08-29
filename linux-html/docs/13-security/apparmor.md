---
title: AppArmor
date: 2026-08-15  # date-auto-injected
---

# AppArmor

> Ubuntu / Debian 默认的 MAC（强制访问控制）。

## 🤔 AppArmor vs SELinux

| | AppArmor | SELinux |
|--|----------|---------|
| 默认发行版 | Ubuntu / Debian | RHEL / CentOS / Fedora |
| 配置 | 文件路径（人类可读） | 标签（XML） |
| 学习曲线 | 低 | 陡 |
| 类型 | path-based（路径） | label-based（标签） |
| 模式 | enforce / complain / audit | enforcing / permissive / disabled |

## 📜 模式

```bash
# 全部 profile
sudo aa-status

# 单个 profile
sudo aa-status apache2
```

| 模式 | 含义 |
|------|------|
| `enforce` | 强制执行，违规即拒绝 |
| `complain` | 违规仅记日志，不阻止 |
| `unconfined` | 不限制 |

## 🔍 看现有 profile

```bash
ls /etc/apparmor.d/
# usr.sbin.mysqld
# usr.sbin.nginx
# ...
ls /etc/apparmor.d/ -la

sudo apparmor_status          # 当前生效 + 加载情况
```

## 🛠 设置 profile

```bash
# 安装工具
sudo apt install apparmor-utils

# 给某个二进制生成 profile
sudo aa-genprof /usr/bin/myapp
# 然后跑 myapp 做常见操作，工具会提示加规则
# 完成后 /etc/apparmor.d/ 会生成 profile

# 把 profile 转 complain（只警告，便于调试）
sudo aa-complain /usr/bin/myapp

# 启用 enforce
sudo aa-enforce /usr/bin/myapp
```

## 📜 profile 语法

```bash
# /etc/apparmor.d/usr.bin.myapp

#include <tunables/global>

/usr/bin/myapp {
  #include <abstractions/base>
  #include <abstractions/nameservice>

  # 二进制能读这些
  /usr/bin/myapp mr,

  # 配置
  /etc/myapp/** r,
  /opt/myapp/config.json r,

  # 日志（可写）
  /var/log/myapp.log w,

  # 拒绝 /var/www 等危险路径
  deny /etc/shadow r,
  deny /etc/passwd r,
  deny /home/** r,

  # 网络
  network inet stream,
  network inet6 stream,

  # capability
  capability dac_read_search,
  capability net_bind_service,
}
```

## 📊 关键 flags

| flag | 含义 |
|------|------|
| `r` | 读 |
| `w` | 写 |
| `x` | 执行（execve） |
| `m` | mmap |
| `k` | lock |
| `l` | link |
| `i` | inherit |
| `u` | unlink |
| `c` | write + unlink |
| `a` | append |
| `p` | PTRACE |

## 🪛 实战

### nginx 启用 profile

```bash
# 装 nginx 时自动创建
sudo apt install nginx
ls /etc/apparmor.d/ | grep nginx

# 启用
sudo aa-enforce /usr/sbin/nginx

# 拒绝 nginx 写 /tmp
sudo aa-complain /usr/sbin/nginx
# 看拒绝日志
sudo journalctl -k | grep DENIED
# 加规则：编辑 /etc/apparmor.d/usr.sbin.nginx，加 deny /tmp/** w,
```

### 自定义应用

```bash
# 1. 用 aa-genprof 走一遍"训练模式"
sudo aa-genprof /opt/myapp/server
# 操作应用，让工具观察到所有需要的 syscall / 文件

# 2. 启用
sudo aa-enforce /opt/myapp/server

# 3. 测试：故意试越权，看是否被阻止
```

### 让某 binary 完全不受限

```bash
sudo aa-disable /usr/bin/myapp
# 或
sudo ln -s /etc/apparmor.d/usr.bin.myapp /etc/apparmor.d/disable/usr.bin.myapp
```

## 🆚 vs SELinux

| 选择 | 推荐 |
|------|------|
| Ubuntu/Debian | AppArmor（默认开） |
| RHEL/Fedora/CentOS | SELinux（默认开） |
| 个人学习 | AppArmor（容易） |
| 企业级强制合规 | SELinux（严格） |
| 容器 / 镜像 | 都可（容器化后可关） |

容器化时代，很多发行版容器默认 **disable AppArmor/SELinux**。

## 🩺 故障

```bash
# 拒绝日志位置
sudo journalctl -k | grep DENIED   # 内核日志
sudo dmesg | grep DENIED

# 看具体被拒绝的 profile
sudo aa-log
# /var/log/syslog 或 /var/log/kern.log

# 把某 profile 转 complain（debug）
sudo aa-complain /usr/bin/myapp
```

## 🔗 下一步

- [SELinux](/13-security/selinux)
- [sshd_config 加固](/13-security/sshd-config)
- [auditd 审计](/13-security/auditd)