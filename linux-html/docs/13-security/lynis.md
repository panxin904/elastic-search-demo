---
title: lynis 合规检查
---

# lynis - 合规基线检查

> 开源安全审计工具。给出"哪些项不符合 CIS / 等保 / GDPR 等基线"。

## 📦 安装

```bash
# Debian / Ubuntu
sudo apt install lynis

# RHEL / CentOS
sudo yum install epel-release
sudo yum install lynis
```

或最新版（GitHub）：

```bash
git clone https://github.com/CISOfy/lynis.git
cd lynis
sudo ./lynis audit system
```

## 🚀 基础

```bash
sudo lynis audit system             # 完整扫描
sudo lynis audit system --quick     # 快速（不深入）
sudo lynis audit system --pentest   # 渗透测试模式

# 不实际跑，给出命令预览
sudo lynis audit system --no-colors --quiet
```

输出在 `/var/log/lynis.log` 和 `/var/log/lynis-report.dat`。

## 📋 输出结构

```
[+] Initializing program
------------------------------------
  - Detecting OS...                [ DONE ]
  - Clearing log...                [ DONE ]
  
[+] System tools
------------------------------------
  - Scanning available tools...
  - Checking system binaries...

[+] Boot and services
------------------------------------
  - Checking boot services...
  - Checking startup files...

[+] Kernel
------------------------------------
  - Checking kernel version...
  - Checking loaded kernel modules...
  - Checking kernel configuration...

[+] Memory and processes
------------------------------------
  - Checking dead / zombie processes...
  - Checking IO scheduler...

[+] Users, Groups and Authentication
------------------------------------
  - Checking consistency of /etc/passwd...
  - Checking password aging...
  - Checking password hashing rounds...

[+] Filesystems
------------------------------------
  - Checking mount points...
  - Checking /tmp mount options...
  - Checking /var mount options...

[+] Storage
------------------------------------
  - Checking free space...

...

[+] Tests: 234 - performed in 87 seconds
------------------------------------
  - Tests performed : 234
  - Warnings : 3
  - Suggestions : 12
  - Hardening index : 65/100
```

最后是 **Hardening index**（硬化指数）。

## ⚠️ Warnings vs Suggestions

| | Warnings | Suggestions |
|--|----------|-------------|
| 严重性 | 必须修 | 建议修 |
| 例子 | SSH PermitRootLogin yes | Banner 未配置 |

```bash
# 看 Warning
grep -i warning /var/log/lynis.log
grep -i warning /var/log/lynis-report.dat

# 看 Suggestion
grep -i suggestion /var/log/lynis.log
```

每条 Warning 会有：
- `Why`：为什么要看
- `How to resolve`：怎么修
- `Resources`：参考链接

## 🛠 实战：跑一遍

```bash
sudo lynis audit system
# 看 Hardening score（越接近 100 越安全）

# 列 Warning + Solution
sudo lynis show warnings
sudo lynis show details <TEST-ID>

# 列 Suggestions
sudo lynis show suggestions
```

例：

```
[+] Hardening Suggestions
[+]      ---------------------------------------------------------------
 * Consider hardening SSH configuration (PermitRootLogin)
 * Details:  SSH allows root login. Disable PermitRootLogin=no
 * Solution:  Edit /etc/ssh/sshd_config: PermitRootLogin no

 * Configure minimum password length
 * Details:  Password minimum length is 5. CIS recommends 14+
 * Solution:  Edit /etc/login.defs: PASS_MIN_LEN 14

 * Install AIDE for file integrity
 * Solution:  sudo apt install aide
```

## 📋 常用检查项

| 类别 | 检查 |
|------|------|
| 认证 | 密码策略 / root 登录 / sudo 配置 / 失败锁定 |
| 防火墙 | iptables / firewalld / 默认策略 |
| SSH | 算法 / 端口 / 协议 / 空密码 / 弱 MAC |
| 文件权限 | world-writable / unowned / SUID / 特殊位 |
| 内核 | sysctl / 模块 / 大页 / ASLR / kptr_restrict |
| 日志 | auditd / syslog / logrotate |
| 加密 | TLS 配置 / 弱算法 |
| 软件 | 已知 CVE / 版本陈旧 |

## 🔧 CI / 自动化

```bash
# 非交互（CI 用）
sudo lynis audit system --no-colors --quiet --wait

# 导出 report
sudo lynis audit system --report-file /var/log/lynis-$(date +%F).log

# 只看 hardening score
sudo lynis audit system --quiet | grep "Hardening index"

# 用 cron 定期跑
0 3 * * 0 /usr/bin/lynis audit system --quiet --report-file /var/log/lynis-weekly.log 2>&1
```

## 🔥 配合 CIS-CAT / OpenSCAP

| 工具 | 风格 |
|------|------|
| **lynis** | 通用建议，含详细文档 |
| **OpenSCAP** | SCAP 标准（合规审计） |
| **CIS-CAT** | CIS Benchmark 严格对照 |
| **vuls** | 已知 CVE 漏洞扫描 |
| **Nikto** | Web 服务扫描 |

```bash
# OpenSCAP（RedHat 系）
sudo apt install openscap-scanner
sudo oscap info /usr/share/openscap/scap-ubuntu-22.04-ds.xml
sudo oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis /usr/share/openscap/scap-ubuntu-22.04-ds.xml
```

## 🩺 实战：让 hardening score 提高

```bash
sudo lynis audit system
# Hardening: 65/100

# 找出扣分点
sudo lynis show warnings
sudo lynis show suggestions

# 例子：常见 12 个 Suggestions
# 1. SSH PermitRootLogin no
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl reload sshd

# 2. 密码最小长度
sudo sed -i 's/^PASS_MIN_LEN.*/PASS_MIN_LEN 14/' /etc/login.defs

# 3. 防火墙开启
sudo ufw enable

# 4. auditd 启用
sudo systemctl enable --now auditd

# 5. AIDE 文件完整性
sudo apt install aide
sudo aideinit
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# 再跑
sudo lynis audit system
# Hardening: 87/100
```

## 🪤 与 Fail2ban / rkhunter 配合

```bash
# rkhunter：rootkit 扫描
sudo apt install rkhunter
sudo rkhunter --check --update

# chkrootkit
sudo apt install chkrootkit
sudo chkrootkit

# fail2ban：动态封禁
sudo apt install fail2ban
# /etc/fail2ban/jail.local
[sshd]
enabled = true
maxretry = 5
bantime  = 3600
```

## 🔗 下一步

- [sshd_config 加固](/13-security/sshd-config)
- [auditd 审计](/13-security/auditd)
- [OpenSSH 配置](/08-firewall-ssh/openssh)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
