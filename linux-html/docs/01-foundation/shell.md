---
title: Shell 与终端
date: 2026-08-15  # date-auto-injected
---

# Shell 与终端

> 区分 **Shell**（命令解释器）与 **Terminal**（终端模拟器）。

## 🔍 Shell vs Terminal

| 概念 | 是什么 |
|------|--------|
| **Shell** | 命令行解释器。解析输入 → 执行。常见 `bash` / `zsh` / `fish` |
| **Terminal** | 终端模拟器。提供窗口 + 渲染字符。常见 `Terminal.app` / `iTerm2` / `GNOME Terminal` / `Windows Terminal` |
| **TTY** | Linux 真实终端设备（/dev/tty1 等） |
| **PTY** | 伪终端（Terminal 应用打开的就是 PTY） |
| **Console** | 系统控制台（/dev/console） |

## 🐚 主流 Shell

| Shell | 特点 |
|-------|------|
| **sh** | POSIX 标准，几乎所有系统都有 |
| **bash** (Bourne Again) | Linux 默认，GNU 项目 |
| **zsh** | macOS 默认（Catalina+），强大补全 |
| **fish** | 友好 UI / 智能补全，但脚本语法不兼容 |
| **dash** | Debian 默认 /bin/sh，更快，更精简 |
| **nushell** | 新派，结构化数据 |
| **xonsh** | Python + Shell 混合 |

## 🔎 查看当前 Shell

```bash
echo $SHELL          # 当前登录 shell
echo $0              # 当前运行的 shell（bash / zsh）
ps -p $$ -o comm=    # 当前进程名

cat /etc/shells      # 系统所有可用 shell
chsh -l              # 列出可切换的 shell
```

## 🪄 bash 速查

### 环境与配置

```bash
bash --version                    # 版本
echo $PATH                        # 路径
which ls                          # 命令路径
type ls                           # 命令类型（alias/builtin/外部）

# 配置文件加载顺序
/etc/profile       # 全局登录
~/.bash_profile    # 用户登录
~/.bashrc          # 用户交互式
```

### 快捷键

| 键 | 行为 |
|----|------|
| `Tab` | 补全 |
| `↑` / `↓` | 历史 |
| `Ctrl+R` | 反向搜索历史 |
| `Ctrl+L` | 清屏 |
| `Ctrl+A` / `Ctrl+E` | 行首 / 行尾 |
| `Ctrl+U` / `Ctrl+K` | 删到行首 / 行尾 |
| `Ctrl+W` | 删一个词 |
| `Ctrl+C` | 中断当前命令 |
| `Ctrl+D` | EOF / 退出 |

### history

```bash
history                   # 列出
!42                       # 跑第 42 条
!!                        # 上一条
!vim                      # 最近以 vim 开头
Ctrl+R 然后输入关键字      # 交互式搜索
```

## 🐚 zsh 速查（macOS 默认）

```bash
# 切换到 zsh（macOS 默认）
chsh -s /bin/zsh

# zsh 配置文件加载顺序
~/.zshenv      # 环境变量
~/.zshrc       # 主配置（含 prompt / alias / 插件）

# 推荐配置：Oh My Zsh + 插件
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# 极简配置（推荐用 starship）
brew install starship
echo 'eval "$(starship init zsh)"' >> ~/.zshrc
```

## 🐟 fish 速查

```bash
# 安装（macOS）
brew install fish

# 自动补全 + 语法高亮默认开启
# 配置
fish_config       # 打开 web 配置
~/.config/fish/config.fish
```

## 🔄 切换默认 Shell

```bash
chsh -s $(which fish)             # 当前用户切换
echo /usr/bin/zsh | sudo tee -a /etc/shells
sudo chsh -s /usr/bin/zsh root    # 改 root 的 shell
```

## ⚠️ 注意

- 写脚本始终用 `#!/usr/bin/env bash` 或 `#!/usr/bin/env zsh`，不要用 `#!/bin/sh` 写 bash 特性
- 关键脚本加 `set -euo pipefail` 严格模式
- 配置文件 ~/.bashrc vs ~/.bash_profile：前者交互式，后者登录 shell

## 🔗 下一步

- [bash 基础语法](/11-shell/bash-syntax)
- [文件系统树](/01-foundation/fs-tree)
- [用户与用户组](/05-user/users-groups)