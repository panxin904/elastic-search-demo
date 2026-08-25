---
title: MHA 故障切换
---

# 🏗️ MySQL MHA 故障切换

> MHA（Master High Availability）是业界成熟的 MySQL 主库故障自动切换方案，30 秒内完成切换，数据零丢失。

## 🎯 MHA 是什么？

MHA 由日本 DeNA 公司开发的一套 **MySQL 高可用解决方案**，专注于 **主库故障自动切换**。

```
┌────────────────────────────────────────────┐
│              MHA 架构                        │
│                                            │
│  ┌──────────┐    ┌──────────────────────┐  │
│  │  Master  │    │  MHA Manager (Node)   │  │
│  │  主库    │    │  - 监控主库           │  │
│  └──────────┘    │  - 故障检测           │  │
│       │          │  - 自动提升从库为新主 │  │
│       │ 复制     │  - 切换应用 VIP       │  │
│       ▼          └──────────────────────┘  │
│  ┌──────────┐                               │
│  │  Slave1  │ ◄── 候选主库                  │
│  │  Slave2  │                               │
│  └──────────┘                               │
└────────────────────────────────────────────┘
```

## 🔄 MHA 的工作流程

```
正常状态：

Master ── 复制 ──> Slave1
   │              │
   └── 复制 ──> Slave2

MHA Manager 持续监控主库（每 3 秒 ping 一次）


主库宕机！

1. 检测故障（10-30 秒）
   - 多次 SSH 失败
   - 多次 ping 失败
   - 触发 failover

2. 选择新主库
   - 比较各个从库的 relay log 位置
   - 选择数据最新的从库
   - 提升为新主库

3. 补齐差异数据
   - 从其他从库拉取差异 binlog
   - 应用到新主库（保证数据一致）

4. 切换其他从库
   - 重新指向新主库
   - 开始复制

5. 应用切换
   - VIP 漂移到新主库
   - 应用自动连接新主库
```

**切换时间：10-30 秒**
**数据丢失：0 字节**（基于半同步复制）

## 📦 MHA 的组成

### 1. MHA Manager（管理节点）

```
- 运行在独立的机器（不能是主库或从库）
- 监控主库健康
- 触发故障切换
- 配置文件：app1.cnf
```

### 2. MHA Node（数据节点）

```
- 运行在每台 MySQL 服务器（主 + 从）
- 负责复制差异 binlog
- 应用差异数据到新主库
```

## ⚙️ MHA 安装配置

### 1. 环境准备

```
服务器：
- master: 192.168.1.10
- slave1: 192.168.1.11（候选主）
- slave2: 192.168.1.12
- manager: 192.168.1.13（MHA Manager）
```

### 2. 配置主从 + 半同步复制

```sql
-- 主库
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
SET GLOBAL rpl_semi_sync_master_enabled = ON;

-- 从库
INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';
SET GLOBAL rpl_semi_sync_slave_enabled = ON;
STOP SLAVE IO_THREAD; START SLAVE IO_THREAD;

-- 验证
SHOW STATUS LIKE 'Rpl_semi_sync%';
```

### 3. SSH 免密登录

```bash
# 在所有服务器上生成 SSH key
ssh-keygen -t rsa

# 在 Manager 服务器上免密登录所有 MySQL 服务器
ssh-copy-id root@192.168.1.10
ssh-copy-id root@192.168.1.11
ssh-copy-id root@192.168.1.12
```

### 4. MHA 配置文件（/etc/mha/app1.cnf）

```ini
[server default]
manager_workdir=/var/log/mha/app1
manager_log=/var/log/mha/app1/manager.log
user=root
ssh_user=root
repl_user=repl_user
repl_password=StrongP@ss!

[server1]
hostname=192.168.1.10
port=3306
candidate_master=1   # 优先提升为新主库

[server2]
hostname=192.168.1.11
port=3306
candidate_master=1

[server3]
hostname=192.168.1.12
port=3306
candidate_master=0   # 不优先提升为主库
```

### 5. 启动 MHA Manager

```bash
# 前台启动（调试用）
masterha_manager --conf=/etc/mha/app1.cnf

# 后台启动
nohup masterha_manager --conf=/etc/mha/app1.cnf \
  > /var/log/mha/manager.log 2>&1 &

# 检查状态
masterha_check_status --conf=/etc/mha/app1.cnf
```

## 🔧 手动故障切换

```bash
# 主动切换（用于主库维护）
masterha_master_switch --master_state=alive \
  --conf=/etc/mha/app1.cnf \
  --new_master_host=192.168.1.11

# 在线切换流程：
# 1. MHA 触发切换
# 2. 阻塞写入几秒
# 3. 提升新主库
# 4. 其他从库指向新主库
# 5. 解除阻塞，应用继续
```

## 🚨 自动故障切换

### 故障检测

```bash
# MHA Manager 每 3 秒检测一次
# 检测方式：
# 1. SSH 到主库执行命令
# 2. ping 主库
# 3. 检查主库响应
# 如果连续失败 → 触发 failover
```

### 切换流程

```
1. [T=0]    检测到主库故障
2. [T+3s]   确认主库不可达
3. [T+5s]   选 Slave1 为新主（数据最新）
4. [T+10s]  从其他从库拉取差异 binlog
5. [T+15s]  应用差异到新主库
6. [T+20s]  其他从库指向新主库
7. [T+25s]  VIP 漂移到新主库
8. [T+30s]  应用自动连接新主库 ✅
```

## 🛠️ MHA 配套脚本

### master_ip_failover（VIP 漂移）

```bash
#!/bin/bash
# /usr/local/bin/master_ip_failover
# VIP 漂移到新主库
new_master=$1
vip="192.168.1.100/24"
interface="eth0"

ssh ${new_master} "ip addr add ${vip} dev ${interface}"
# 在旧主库上移除 VIP
ssh ${old_master} "ip addr del ${vip} dev ${interface}"

# 或使用 keepalived（更专业）
```

### master_ip_online_change（在线切换）

```bash
#!/bin/bash
# 在线切换时阻塞写入几秒
mysql -h $old_master -e "FLUSH TABLES WITH READ LOCK"
# ... 切换 ...
mysql -h $old_master -e "UNLOCK TABLES"
```

## 📊 MHA 优缺点

### ✅ 优点

- 切换时间短（10-30 秒）
- 数据零丢失（需半同步复制）
- 自动检测 + 自动切换
- 配置相对简单
- 业界成熟方案

### ❌ 缺点

- 只管理主库故障切换（从库故障需其他方案）
- 需要独立 Manager 节点
- 切换时短暂阻塞写入
- 不支持多主集群

## 🎯 MHA 最佳实践

### 1. 半同步复制必须开启

```ini
[mysqld]
# 主库
plugin-load = "rpl_semi_sync_master=semisync_master.so"
rpl_semi_sync_master_enabled = ON
rpl_semi_sync_master_timeout = 30000  # 30 秒超时

# 从库
plugin-load = "rpl_semi_sync_slave=semisync_slave.so"
rpl_semi_sync_slave_enabled = ON
```

### 2. 定期测试切换

```bash
# 每月演练一次故障切换
masterha_master_switch --master_state=dead \
  --conf=/etc/mha/app1.cnf \
  --new_master_host=192.168.1.11
```

### 3. 监控告警

```bash
# 监控 MHA Manager 进程
ps aux | grep masterha_manager

# 监控 MHA 日志
tail -f /var/log/mha/app1/manager.log
```

### 4. 配置 VIP + Keepalived

```
VIP = 192.168.1.100（应用连接这个地址）
MHA 切换时，VIP 漂移到新主库
应用自动连接到新主库（无需修改配置）
```

## 🎯 总结

**MHA 核心：**
- ✅ 自动检测主库故障（10-30 秒）
- ✅ 自动提升数据最新的从库
- ✅ 补齐差异数据（保证数据一致）
- ✅ 切换 VIP（应用无感知）

**前置条件：**
- 半同步复制
- SSH 免密登录
- 独立的 Manager 节点

**下一步：** [🌐 MGR 组复制](../07-ha/mgr) — MySQL 官方高可用方案

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
