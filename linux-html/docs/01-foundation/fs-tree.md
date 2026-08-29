---
title: 文件系统树
date: 2026-08-15  # date-auto-injected
---

# Linux 文件系统树

> 一切从 `/` 开始。

## 🌳 FHS（Filesystem Hierarchy Standard）

```
/
├── bin/        # 基本命令（ls / cat / cp）— 现代发行版多为 /usr/bin 链接
├── sbin/       # 系统命令（fdisk / ip）— 多为 /usr/sbin 链接
├── etc/        # 配置文件
├── home/       # 普通用户的家目录
│   └── alice/  # /home/alice == ~
├── root/       # root 用户家目录（不在 /home 下）
├── var/        # 可变数据（日志、缓存、邮件）
│   ├── log/    # 系统日志（多数服务改用 journald 后这里空）
│   ├── cache/  # 应用缓存
│   └── lib/    # 状态信息（dpkg / rpm 数据库）
├── tmp/        # 临时文件（重启清空）
├── opt/        # 可选 / 第三方软件（如 Oracle、IntelliJ）
├── usr/        # 用户系统资源（Unix System Resources）
│   ├── bin/    # 用户命令
│   ├── lib/    # 库
│   ├── local/  # 本地编译安装的软件（避免污染系统）
│   └── share/  # 共享数据（man / doc）
├── boot/       # 启动文件（内核 vmlinuz / initramfs / grub）
├── dev/        # 设备文件
│   ├── sda     # 第一块 SCSI/SATA 硬盘
│   ├── sda1    # 第一分区
│   ├── null    # 空设备
│   ├── zero    # 零字节流
│   ├── random  # 真随机数
│   └── pts/0   # 伪终端
├── proc/       # 进程信息（虚拟文件系统）
│   ├── 1/      # PID 1 进程（systemd）
│   ├── cpuinfo # CPU 信息
│   ├── meminfo # 内存信息
│   └── sys/    # 内核参数（sysctl 写入这里）
├── sys/        # 设备树（虚拟文件系统）
├── run/        # 运行时数据（PID 文件 / 套接字）
├── mnt/        # 临时挂载点
├── media/      # 可移动设备自动挂载（光盘 / U 盘）
└── srv/        # 服务数据（FTP / WWW 等）
```

## 🔍 看一眼你的系统

```bash
tree -L 2 /                # 2 层树形（需要 tree 命令）
ls -la /                  # 顶层目录

# 查看具体目录
ls /etc | head            # 配置目录
ls /var/log               # 日志
ls /usr/bin | wc -l       # 统计可执行命令数
```

## 🧠 必知的关键目录

| 目录 | 用途 | 不要 |
|------|------|------|
| `/etc` | 配置文件 | 删文件 |
| `/var/log` | 旧式日志 | 改文件（让服务写） |
| `/tmp` | 临时文件 | 放重要数据 |
| `/proc` / `/sys` | 内核虚拟文件系统 | 当普通文件编辑 |
| `/boot` | 启动文件 | 随意删 |
| `/usr/local` | 自编译软件 | 系统包管理 |
| `/opt` | 第三方大软件 | 改系统目录 |

## 📂 真实路径 vs 软链

```bash
ls -l /bin /sbin /lib     # 通常是 /usr/bin /usr/sbin /usr/lib 的软链
file /bin                 # 看是不是 symlink
realpath /bin             # 真实路径
```

## 📌 几个特殊路径

| 符号 | 含义 |
|------|------|
| `/` | 根 |
| `~` | 当前用户家目录 |
| `~user` | user 的家目录 |
| `.` | 当前目录 |
| `..` | 上级目录 |
| `-` | 上一次的目录（`cd -`） |

## 🗺️ proc 与 sys

```bash
cat /proc/cpuinfo          # CPU 详情
cat /proc/meminfo          # 内存详情
cat /proc/loadavg          # 负载
ls /proc/$$/               # 当前进程（$$ 是 PID）

# sysctl 调整内核参数
sysctl net.ipv4.tcp_syncookies   # 读
sudo sysctl -w net.ipv4.tcp_syncookies=1   # 写
```

详见 [sysctl 调参](/14-kernel/sysctl)。

## ⚠️ 常见误区

```bash
# ❌ 在 /usr 下乱删文件
sudo rm /usr/bin/ls      # 系统崩了

# ❌ 把服务数据放 /etc
sudo cp app.db /etc/      # 不规范

# ✅ 个人数据放 /home 或 /var/lib/<service>
```

## 🔗 下一步

- [ls / cp / mv](/02-filesystem/ls)
- [权限 (rwx)](/02-filesystem/permissions)
- [mount / umount](/09-storage/mount)