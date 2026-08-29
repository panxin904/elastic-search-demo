---
title: 发行版选择
date: 2026-08-15  # date-auto-injected
---

# 发行版选择

> 同一个内核 + 不同软件 = 不同发行版（Distribution）。选哪个不是信仰问题，是工程问题。

## 🏛️ 三大族谱

```
                    ┌─ Debian ─── Ubuntu ─── Linux Mint ─── Kali
                    │              │
                    │              └─ (Server LTS)
   Linux 内核 ──────┼─ RHEL 系 ── Fedora ─── RHEL ─── Rocky / AlmaLinux
                    │              │
                    │              └─ CentOS Stream（已变更）
                    │
                    └─ 独立 ───── Arch ─── Manjaro
                                  Gentoo ─── Calculate
                                  Alpine（容器）
                                  NixOS
```

## 📊 主流选择

| 发行版 | 包管理 | 适合 | 备注 |
|--------|--------|------|------|
| **Ubuntu Server LTS** | apt / deb | 服务器 / 云 / 新手 | 文档最多，社区最大 |
| **Debian** | apt / deb | 稳定服务器 | 比 Ubuntu 更保守 |
| **RHEL** | dnf / rpm | 企业付费 / 商业支持 | 7 年支持 |
| **Rocky / AlmaLinux** | dnf / rpm | RHEL 替代 | 免费、社区维护 |
| **Fedora** | dnf / rpm | 桌面 / 新特性 | RHEL 的上游 |
| **CentOS Stream** | dnf / rpm | RHEL 上游滚动版 | 不再是"稳定克隆" |
| **Arch** | pacman | 极客 / 极简 | rolling release |
| **Alpine** | apk | Docker 镜像 | 体积小（5MB） |
| **openSUSE Leap / Tumbleweed** | zypper | 桌面 / 企业 | YaST 配置 |

## 🎯 选型维度

```
1. 用途  - 桌面？服务器？容器？
2. 包管理 - 你熟悉 apt 还是 dnf？
3. 稳定性 - LTS / stable / rolling
4. 生态  - 文档、社区、商业支持
5. 兼容性 - 硬件 / 软件 / Docker
```

## 🛠️ 服务器选型建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| 中小企业 / 云主机 | **Ubuntu Server 24.04 LTS** | 文档最多，5 年支持 |
| 金融 / 政企 | **RHEL / Rocky 9** | 长期 7-10 年支持，认证合规 |
| 个人学习 / 折腾 | **Debian 12 stable** | 干净、稳定 |
| Docker 镜像 | **Alpine** | 5MB 镜像，musl libc |
| 开发机 | **Fedora 40+** | 新版本 / 新工具 |
| K8s / 容器 | Ubuntu / Rocky | 与云厂商对齐 |

## 🆚 apt vs dnf

| | apt (Debian/Ubuntu) | dnf (RHEL/Fedora) |
|--|---------------------|-------------------|
| 包格式 | `.deb` | `.rpm` |
| 包索引 | `/etc/apt/sources.list` | `/etc/yum.repos.d/*.repo` |
| 安装 | `apt install nginx` | `dnf install nginx` |
| 搜索 | `apt search nginx` | `dnf search nginx` |
| 升级 | `apt upgrade` | `dnf upgrade` |
| 仓库 | universe / multiverse | epel / rpmfusion |
| 大小写 | 不敏感 | 不敏感 |

两者 80% 命令相同。挑一个用顺，再学另一个不难。

## 🔥 版本生命周期（重要）

| 发行版 | 长期支持 |
|--------|---------|
| Ubuntu 24.04 LTS | 至 2029-04 |
| Ubuntu 22.04 LTS | 至 2027-04 |
| Debian 12 | ~5 年 |
| RHEL 9 | 至 2032 |
| Rocky 9 | 同 RHEL 9 |

服务器永远选 **LTS**（长期支持），桌面可以跟新版。

## 🔗 下一步

- [Shell 与终端](/01-foundation/shell)
- [apt (Debian/Ubuntu)](/06-package/apt)
- [yum / dnf (RHEL)](/06-package/yum-dnf)