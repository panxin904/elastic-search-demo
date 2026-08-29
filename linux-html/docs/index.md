---
date: 2026-08-15  # date-auto-injected
layout: home

hero:
  name: Linux 服务器 知识图谱
  text: 系统化学习
  tagline: 用知识图谱串联 Linux 服务器与高频命令
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧠 思维导图
      link: /mindmap
    - theme: alt
      text: 📋 命令速查
      link: /cheatsheet
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "常用命令（ls / find / grep / awk）记不牢？",
      "Shell 脚本（bash / zsh）写不出来？",
      "systemd / 服务管理一团乱？",
      "iptables / nftables 防火墙不会配？",
      "内核参数调优（sysctl / cgroup）无从下手？"
    ]
const goals = [
      "入门基础（发行版 / Shell / 文件系统树）",
      "文件与目录（ls / cp / mv / find / 权限）",
      "文本三剑客（grep / sed / awk）",
      "Shell 脚本（bash 语法 / 流程控制 / 函数）",
      "服务管理（systemd / supervisor）",
      "网络配置（iptables / ip / ss / netstat）"
    ]
const relatedSites = [
      { site: "filesystem", path: "/01-storage/ext4", label: "ext4 文件系统" },
      { site: "network", path: "/01-fundamentals/tcp-ip", label: "TCP/IP 协议" },
      { site: "devops", path: "/01-pipeline/overview", label: "CI/CD 流水线" },
      { site: "security", path: "/01-basics/permissions", label: "Linux 权限" },
      { site: "observability", path: "/02-logs/filebeat", label: "日志采集" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>

features:
  - icon: 🌐
    title: 入门基础
    details: Linux 是什么、发行版选择、Shell 类型、文件系统树
    link: /01-foundation/intro
    linkText: 开始学习 →
  - icon: 📁
    title: 文件与目录
    details: ls / cp / mv / find / ln / 权限 / 压缩归档
    link: /02-filesystem/ls
    linkText: 看文件操作 →
  - icon: 📦
    title: 文本三剑客
    details: grep / awk / sed / sort / uniq / xargs
    link: /03-text/grep
    linkText: 看文本处理 →
  - icon: ⚙️
    title: 进程与任务
    details: ps / top / 信号 / systemd / cron / jobs
    link: /04-process/ps-top
    linkText: 看进程管理 →
  - icon: 🛠️
    title: 用户与权限
    details: user / group / chmod / chown / sudo / ACL
    link: /05-user/chmod
    linkText: 看权限 →
  - icon: 📦
    title: 软件包管理
    details: apt / yum-dnf / 源码编译 / 容器化
    link: /06-package/apt
    linkText: 看包管理 →
  - icon: 🌐
    title: 网络
    details: ip / ping / curl / DNS / ss
    link: /07-network/ip
    linkText: 看网络命令 →
  - icon: 🔥
    title: 防火墙 / SSH
    details: iptables / ufw / OpenSSH / ssh-keygen / 隧道
    link: /08-firewall-ssh/iptables
    linkText: 看防火墙 →
  - icon: 🗄️
    title: 存储
    details: mount / fstab / LVM / ext4-xfs / swap
    link: /09-storage/lvm
    linkText: 看存储 →
  - icon: ⚡
    title: 性能监控
    details: top / htop / vmstat / iostat / sar / perf / strace
    link: /10-perf/top-htop
    linkText: 看性能 →
  - icon: 📜
    title: Shell 脚本
    details: bash 语法 / 变量 / 数组 / 函数 / 调试
    link: /11-shell/bash-syntax
    linkText: 看脚本 →
  - icon: 🛠️
    title: systemd 服务
    details: systemctl / Unit / journald / Timer
    link: /12-systemd/systemctl
    linkText: 看 systemd →
  - icon: 🔒
    title: 安全加固
    details: SELinux / AppArmor / sshd_config / auditd / lynis
    link: /13-security/selinux
    linkText: 看安全 →
  - icon: 🏗️
    title: 内核与启动
    details: GRUB / initramfs / 内核模块 / sysctl
    link: /14-kernel/grub
    linkText: 看内核 →

---

## 🎯 为什么写这个知识图谱？

```
日常 Linux 服务器管理很常见，但绝大多数人：
  ❌ 会敲命令却不知道做了什么
  ❌ 背熟了 ls / cd / cat，遇到排查就抓瞎
  ❌ 看了 iptables 教程也搞不清规则顺序
  ❌ 写 shell 脚本只会复制粘贴

本图谱的目标：
  ✅ 系统化讲解常用命令（文件 / 进程 / 网络 / 用户 / 存储）
  ✅ 文本处理三剑客 grep / awk / sed 实战
  ✅ systemd 取代 init 的全套用法
  ✅ 防火墙 / SSH 加固 + SELinux / AppArmor
  ✅ 性能排查工具栈（top / iostat / strace / perf）
  ✅ Shell 脚本从入门到能写出工程化脚本
```

## 🎯 学习路径

```
🆕 入门     →  🌐 入门基础 →  📁 文件与目录 →  📦 文本三剑客
⚙️ 系统     →  ⚙️ 进程与任务 →  🛠️ 用户与权限 →  🛠️ systemd 服务
🌐 网络     →  🌐 网络 →  🔥 防火墙 / SSH
🗄️ 进阶    →  🗄️ 存储 →  📜 Shell 脚本
⚡ 性能     →  ⚡ 性能监控
🔒 加固     →  🔒 安全加固 →  🏗️ 内核与启动
```

完整路径请看 [📖 学习路径](/path)。


## 💡 知识图谱 + 思维导图

- [🌐 知识图谱](/graph) — 全局节点关系图，鼠标拖拽，点击节点跳转
- [🧭 思维导图](/mindmap) — 树形结构概览，可展开/收起
- [📋 命令速查](/cheatsheet) — 30+ 高频命令快速查阅

## 🎁 学习建议

```
1. 初学者  →  从"入门基础 / 文件与目录 / 文本三剑客"开始
2. 日常运维  →  把"进程 / 用户权限 / 网络 / SSH"补齐
3. 服务部署  →  加入"systemd 服务"
4. 性能调优  →  "性能监控 / 内核 / sysctl"
5. 安全合规  →  "防火墙 / SELinux / auditd"
```

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [devops](https://java-px.bot.cd/devops/)：DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/)：云原生
- [network](https://java-px.bot.cd/network/)：Linux 网络
- [security](https://java-px.bot.cd/security/)：Linux 安全
- [rust](https://java-px.bot.cd/rust/)：Linux 系统编程
- [filesystem](https://java-px.bot.cd/filesystem/)：文件系统
