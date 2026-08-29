---
title: auditd 文件审计
---

# auditd — Linux 文件系统审计

> <span class="kg-badge kg-badge--security">安全权限</span>
> 文件访问审计 · 合规 · 入侵检测

auditd 是 Linux 内核审计系统（audit subsystem）的用户态守护进程。它记录**谁**、**何时**、**对什么**文件做了什么操作——是合规、入侵检测的关键工具。

## 1. 启动

```bash
# 安装
yum install -y audit

# 启动
systemctl start auditd
systemctl enable auditd

# 看状态
auditctl -s
```

## 2. 核心规则

```bash
# 监控某文件
auditctl -w /etc/passwd -p wa -k password-file

# 监控目录
auditctl -w /etc/ -p wa -k etc-config

# 监控 syscall
auditctl -a always,exit -F arch=b64 -S open -F path=/etc/shadow -k shadow-read

# 监控用户
auditctl -a always,exit -F uid=1000 -F arch=b64 -S execve -k user-exec
```

**关键选项**：

| 选项 | 含义 |
|------|------|
| `-w` | watch 文件 / 目录 |
| `-p` | 权限（r=read, w=write, x=exec, a=attribute） |
| `-k` | 关键字（查询时用） |
| `-a list,action` | 高级规则 |

## 3. 持久化规则

`/etc/audit/rules.d/audit.rules`：

```bash
# 删 /etc/audit/rules.d/* 防止规则乱
echo "-w /etc/passwd -p wa -k password-file" > /etc/audit/rules.d/pwd.rules

# 重载
augenrules --load
systemctl restart auditd
```

## 4. 查询审计日志

```bash
# 原始日志
/var/log/audit/audit.log

# 用 ausearch 查
ausearch -k password-file           # 按关键字
ausearch -ts today                  # 今天
ausearch -ui 1000                   # 按用户
ausearch -x /usr/bin/cat            # 按命令

# 用 aureport 看汇总
aureport --summary
aureport --file                     # 文件汇总
aureport --user                     # 用户汇总
```

## 5. 实战：监控敏感文件

```bash
# /etc/shadow 的所有读写
-w /etc/shadow -p wa -k shadow

# /etc/passwd 写操作
-w /etc/passwd -p wa -k passwd

# SSH 密钥
-w /etc/ssh/sshd_config -p wa -k ssh-config
-w /home/*/.ssh/ -p wa -k ssh-keys

# sudo
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers
```

## 6. 实战：监控可疑 syscall

```bash
# 监控 setuid 调用（提权行为）
auditctl -a always,exit -F arch=b64 -S setuid -S setgid -S setreuid -k privilege-change

# 监控 mount
auditctl -a always,exit -F arch=b64 -S mount -k mount-change

# 监控 chmod / chown
auditctl -a always,exit -F arch=b64 -S chmod -S chown -S fchmod -S fchown -k permission-change
```

## 7. 实战：监控特定用户

```bash
# 监控 uid 0 的所有操作（root 越权）
auditctl -a always,exit -F uid=0 -k root-actions

# 监控可疑用户（如离职）
auditctl -a always,exit -F uid=1234 -k suspicious-user
```

## 8. 实战：监控网络相关 syscall

```bash
# bind / connect
auditctl -a always,exit -F arch=b64 -S bind -S connect -k network
```

## 9. 性能影响

| 规则数 | 性能影响 |
|--------|---------|
| < 100 | 几乎无感 |
| 100-1000 | 1-5% CPU |
| > 1000 | 明显开销 |

**建议**：用关键字与 syscall 规则**精确化**。

```bash
# 反例：监控整个 / 目录
auditctl -w / -p wa     # 灾难

# 正例：监控特定敏感文件
auditctl -w /etc/passwd -p wa
```

## 10. 实战：合规配置

```bash
# STIG / CIS 通用模板
# /etc/audit/rules.d/stig.rules

# 1. 时间变更
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -k time-change
-a always,exit -F arch=b64 -S clock_settime -k time-change
-w /etc/localtime -p wa -k time-change

# 2. 网络变更
-a always,exit -F arch=b64 -S sethostname -S setdomainname -k system-locale
-w /etc/issue -p wa -k system-locale
-w /etc/issue.net -p wa -k system-locale
-w /etc/hosts -p wa -k system-locale
-w /etc/sysconfig/network -p wa -k system-locale

# 3. 用户/组变更
-w /etc/group -p wa -k identity
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k identity
-w /etc/sudoers.d/ -p wa -k identity

# 4. 文件系统挂载
-a always,exit -F arch=b64 -S mount -k mounts
```

## 11. 实战：日志分析

```bash
# 看最频繁的失败事件
ausearch --message USER_LOGIN --success no --interpret | head

# 失败登录
aureport --login --summary | grep Failed

# 异常时间登录（如深夜 3 点）
ausearch --ts today --raw | grep "03:"

# 暴力 SSH
aureport --login --summary --failed
```

## 12. 实战：对接 SIEM

```bash
# 1. 实时监控文件
ausearch -k password-file -ts today --format csv > /tmp/audit.csv
# 推到 Splunk / ELK

# 2. auditbeat（Elastic 官方）
yum install -y auditbeat
auditbeat setup -e
systemctl start auditbeat

# 3. 配合 aureport 自动告警脚本
#!/bin/bash
COUNT=$(ausearch -k shadow -ts today | wc -l)
if [ "$COUNT" -gt 5 ]; then
    echo "WARNING: Shadow file accessed $COUNT times today"
    curl -X POST https://alert-system/api/alert -d "..."
fi
```

## 13. 容器场景

```bash
# K8s 节点：监控敏感路径
auditctl -w /etc/kubernetes/ -p wa -k k8s-config
auditctl -w /var/lib/docker/ -p wa -k docker-data

# 容器内看不到 auditd（容器没有 CAP_AUDIT_*）
# 改用主机侧 auditd 监控关键目录
```

## 14. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| auditd = 内核审计 | "auditd=审计" |
| -w 监控文件 | "-w=文件" |
| -p wa 是常用权限 | "wa=写+属性" |
| -k 加标签查 | "-k=标签" |
| 性能 = 规则数 | "规则多=慢" |

## 参考

- auditctl(8) / ausearch(8) / aureport(8) 手册
- Linux Audit 文档
- STIG 安全基线
- CIS Benchmark


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
