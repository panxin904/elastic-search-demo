---
title: 学习路径
date: 2026-08-15  # date-auto-injected
---

# 📖 Linux 学习路径

> 根据你的角色选择对应路径，每条路径推荐了核心阅读顺序。

## 🛤️ 路径 1：纯新手（1 周）

适合**没接触过 Linux** 的同学，或只用 macOS / Windows。

1. [Linux 是什么](/01-foundation/intro) — 5 分钟了解 Linux 哲学
2. [发行版选择](/01-foundation/distros) — 选一个 Ubuntu 入门
3. [Shell 与终端](/01-foundation/shell) — zsh / bash 的区别
4. [文件系统树](/01-foundation/fs-tree) — 理解 `/` 是什么
5. [ls / cp / mv](/02-filesystem/ls) — 最常用 3 个命令
6. [权限 (rwx)](/02-filesystem/permissions) — 理解 644 / 755

**目标**：能 cd 到任意目录、看懂 ls 输出、修改文件权限。

## 🛤️ 路径 2：日常运维（2 周）

适合**想管服务器 / 部署应用**的开发者。

- 完成"新手"路径
- [find 查找](/02-filesystem/find) — 服务器上找文件
- [grep](/03-text/grep) — 查日志必会
- [ps / top / htop](/04-process/ps-top) — 查进程 / 内存
- [systemd](/04-process/systemd) — 服务管理
- [systemctl 命令](/12-systemd/systemctl) — 启停 / 重启 / 启用
- [journald 日志](/12-systemd/journald) — 查服务日志
- [OpenSSH 配置](/08-firewall-ssh/openssh) — 远程登录
- [ssh-keygen / ssh-copy-id](/08-firewall-ssh/ssh-keys) — 免密码登录
- [cron 定时任务](/04-process/cron) — 写定时脚本

**目标**：能管理自己的服务器，跑应用、查问题、写定时任务。

## 🛤️ 路径 3：后端 / SRE（3-4 周）

适合**做后端 / 运维工程师**。

- 完成"日常运维"路径
- [用户与用户组](/05-user/users-groups) — 多用户管理
- [chmod / chown / sudo](/05-user/chmod) — 权限精细控制
- [ACL 细粒度权限](/05-user/acl) — 跨用户共享
- [ip / ss / DNS](/07-network/ip) — 网络排查
- [iptables](/08-firewall-ssh/iptables) — 防火墙基础
- [ufw / firewalld](/08-firewall-ssh/ufw-firewalld) — 简化版
- [mount / fstab / LVM](/09-storage/mount) — 磁盘管理
- [SSH 隧道 / 代理](/08-firewall-ssh/ssh-tunnel) — 内网穿透
- [bash 基础语法](/11-shell/bash-syntax) — 自动化
- [变量与参数 / 数组 / 函数](/11-shell/variables) — 工程化脚本
- [信号 (kill)](/04-process/signals) — 优雅关停

**目标**：能独立运维一套生产环境的服务器。

## 🛤️ 路径 4：性能调优（4 周）

适合**遇到性能瓶颈**的开发者 / SRE。

- 完成"SRE"路径
- [top / htop 详解](/10-perf/top-htop) — 找到瓶颈进程
- [vmstat / mpstat](/10-perf/vmstat) — CPU 上下文切换
- [iostat / iotop](/10-perf/iostat) — 磁盘 IO 瓶颈
- [sar 持续监控](/10-perf/sar) — 历史数据回看
- [perf / strace](/10-perf/perf-strace) — 深入内核追踪
- [GRUB 引导参数](/14-kernel/grub) — 启动优化
- [sysctl 调参](/14-kernel/sysctl) — TCP / 内存 / 文件系统
- [swap 交换分区](/09-storage/swap) — 内存不够时
- [initramfs / 内核模块](/14-kernel/initramfs) — 定制启动

**目标**：能快速定位线上性能瓶颈，知道调哪些参数。

## 🛤️ 路径 5：安全合规（3 周）

适合**做安全 / 审计 / 等保合规**。

- 完成"SRE"路径
- [sshd_config 加固](/13-security/sshd-config) — 禁 root 登录 / 改端口
- [SELinux](/13-security/selinux) — CentOS / RHEL 强制访问控制
- [AppArmor](/13-security/apparmor) — Ubuntu 替代品
- [auditd 审计](/13-security/auditd) — 谁在何时做了什么
- [lynis 合规检查](/13-security/lynis) — 自动扫描
- [SSH 隧道 / 代理](/08-firewall-ssh/ssh-tunnel) — 内网安全访问
- [源码编译](/06-package/source) — 安全审计
- [容器化安装](/06-package/container) — 沙箱隔离

**目标**：让服务器满足等保 2.0 / 三级要求。

## 🛤️ 路径 6：面试冲刺（2 周）

适合**1-3 个月要面试**运维 / SRE 岗。

- 复习 [Shell 脚本](/11-shell/bash-syntax)
- [awk / sed](/03-text/awk) — 文本处理必问
- [grep / find / xargs 管道](/03-text/xargs) — 一行命令
- [systemd 服务管理](/12-systemd/systemctl)
- [iptables 四表五链](/08-firewall-ssh/iptables)
- [inode / 文件系统结构](/01-foundation/fs-tree)
- [LVM 原理](/09-storage/lvm)
- [swap 用途](/09-storage/swap)
- [load average 含义](/10-perf/top-htop)

## 🎯 速查卡片

| 我想 | 推荐先看 |
|------|---------|
| 入门 | [Linux 是什么](/01-foundation/intro) → [ls / cp / mv](/02-filesystem/ls) |
| 学命令 | [命令速查](/cheatsheet) → [文本三剑客](/03-text/grep) |
| 管服务器 | [systemd](/04-process/systemd) → [journald](/12-systemd/journald) → [cron](/04-process/cron) |
| 远程登录 | [SSH 配置](/08-firewall-ssh/openssh) → [ssh-keygen](/08-firewall-ssh/ssh-keys) |
| 调性能 | [top / htop](/10-perf/top-htop) → [iostat](/10-perf/iostat) |
| 写脚本 | [bash 语法](/11-shell/bash-syntax) → [函数](/11-shell/functions) |
| 找工作 | [速查](/cheatsheet) + [脚本调试](/11-shell/debug) |