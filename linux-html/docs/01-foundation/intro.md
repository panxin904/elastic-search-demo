---
title: Linux 是什么
date: 2026-08-15  # date-auto-injected
---

# Linux 是什么

> Linux = 内核 + 工具 + 生态。不是一个"操作系统"，而是一个家族。

## 🧬 一句话定义

**Linux 是开源的类 Unix 内核**，由 Linus Torvalds 在 1991 年发布。配合 GNU 工具集合与各类桌面/服务器组件，构成完整的 GNU/Linux 操作系统。

```
Linux  ≠  GNU/Linux  ≠  Ubuntu  ≠  CentOS
   │
   ├─ 内核 (kernel)：进程、内存、文件系统、设备、网络
   ├─ GNU 工具集 (coreutils / bash / grep ...)
   ├─ 软件包 (apt / yum / pacman ...)
   ├─ 系统服务 (systemd / SysVinit ...)
   ├─ 桌面环境 (GNOME / KDE / XFCE ...)
   └─ 应用 (Nginx / MySQL / Docker ...)
```

## 🎯 Linux 的核心特性

| 特性 | 含义 |
|------|------|
| 开源 | GPL 协议，源码可见、可改、可分发 |
| 多用户 | 每个用户独立身份与权限 |
| 多任务 | 同时运行多个进程，CPU 时间片调度 |
| 模块化内核 | 按需加载驱动（LKM） |
| 文件一切 | 设备 / 进程 / 套接字都是文件 |
| 一切皆文本 | 配置文件 / 日志 / 状态都是文本 |

## 🆚 Linux vs 其他系统

| | Windows | macOS | Linux |
|--|---------|-------|-------|
| 内核 | NT（闭源） | XNU（Darwin，开源部分） | Linux（开源） |
| 包管理 | exe / msi | dmg / pkg / brew | apt / yum / pacman |
| 用户权限 | UAC | sudo / ACL | rwx + sudo + SELinux |
| 系统更新 | 自动 | 强制升级 | 包管理器，灵活 |
| 占用 | 大 | 大 | 极小（几十 MB） |
| 定制性 | 低 | 中 | 极高 |

## 🏗️ Linux 系统长什么样

```
┌────────────────────────────────────────────────┐
│                   用户应用                       │
│       (Nginx / MySQL / Docker / Python)         │
├────────────────────────────────────────────────┤
│              系统调用 (syscall)                 │
│  open / read / fork / exec / socket / ioctl ...  │
├────────────────────────────────────────────────┤
│                  Linux 内核                      │
│  进程调度 · 内存管理 · 虚拟文件系统 · 网络栈    │
│              · 设备驱动 · 安全模块              │
├────────────────────────────────────────────────┤
│                  硬件                            │
│   CPU · 内存 · 磁盘 · 网卡 · GPU · 总线         │
└────────────────────────────────────────────────┘
```

## 🚀 为什么要学

| 角色 | 为什么 |
|------|--------|
| 后端 / SRE | 服务器 99% 是 Linux |
| 数据 / AI | GPU 训练机 / 大数据集群几乎都是 Linux |
| 嵌入式 / IoT | Android / 路由器 / 智能设备 |
| 安全 / 渗透 | Linux 是默认环境 |
| 前端开发 | 部署 / Docker / CI 都基于 Linux |

## 🔧 我应该装哪个发行版？

| 场景 | 推荐 |
|------|------|
| 新手入门 | Ubuntu Desktop / Linux Mint |
| 服务器 / 桌面 | Ubuntu LTS / Debian |
| 企业稳定 | RHEL / Rocky / AlmaLinux |
| 包管理新潮 | Fedora / openSUSE |
| 极简定制 | Arch / Gentoo |
| 容器 / 云 | Alpine |

详见 [发行版选择](/01-foundation/distros)。

## 🔗 下一步

- [发行版选择](/01-foundation/distros)
- [Shell 与终端](/01-foundation/shell)
- [文件系统树](/01-foundation/fs-tree)