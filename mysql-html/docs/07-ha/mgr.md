---
title: MGR 组复制
---

# 🌐 MySQL MGR 组复制

> MGR（MySQL Group Replication）是 MySQL 5.7.17+ 官方推出的高可用与高扩展方案，基于 Paxos 协议实现强一致性。

## 🎯 MGR 是什么？

MGR 是 MySQL 官方提供的 **多主同步复制** 方案，支持：

- **单主模式**：1 主多从，自动选主
- **多主模式**：多主多从，任何节点都可写

```
单主模式：
┌──────────┐
│  Primary │ ← 写
└──────────┘
     │
     ▼ 复制（Paxos 协议）
  ┌──────────┐
  │ Secondary│ ← 读
  └──────────┘

多主模式：
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Node 1  │  │  Node 2  │  │  Node 3  │
│  (R/W)   │  │  (R/W)   │  │  (R/W)   │
└──────────┘  └──────────┘  └──────────┘
     ↑ 互相同步（任何节点都能写）
```

## 🏛️ MGR 的核心特性

### 1. 基于 Paxos 协议

```
Paxos 协议保证：
- 大多数节点确认 → 事务提交
- 单节点故障不影响集群
- 强一致性（不是最终一致性）
```

### 2. 自动成员管理

```
新节点加入：
1. 新节点发起加入请求
2. 现有节点投票
3. 多数同意后，新节点加入

故障检测：
1. 节点间互相 ping
2. 5 秒无响应 → 怀疑故障
3. 多数确认 → 踢出集群
```

### 3. 冲突检测

```
多主模式下：
- 同时在两个节点更新同一行 → 冲突
- 后提交的事务被回滚
- 客户端收到错误
```

## ⚙️ MGR 部署

### 1. 配置文件（所有节点）

```ini
[mysqld]
# 开启 GTID（必需）
gtid_mode = ON
enforce_gtid_consistency = ON

# binlog 配置
log_bin = /var/log/mysql/mysql-bin
binlog_format = ROW

# MGR 配置
plugin-load = "group_replication.so"
transaction_write_set_extraction = XXHASH64
group_replication_group_name = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
group_replication_start_on_boot = OFF
group_replication_local_address = "192.168.1.10:33061"
group_replication_bootstrap_group = OFF
group_replication_single_primary_mode = ON   # 单主模式
group_replication_enforce_update_everywhere_checks = ON
```

### 2. 启动 MGR 集群

```sql
-- 1. 在第一个节点引导集群
SET GLOBAL group_replication_bootstrap_group = ON;
START GROUP_REPLICATION;
SET GLOBAL group_replication_bootstrap_group = OFF;

-- 2. 在其他节点加入集群
START GROUP_REPLICATION;

-- 3. 查看集群状态
SELECT * FROM performance_schema.replication_group_members;
```

### 3. 单主 vs 多主

```sql
-- 单主模式（默认）
SET GLOBAL group_replication_single_primary_mode = ON;

-- 多主模式
SET GLOBAL group_replication_single_primary_mode = OFF;
SET GLOBAL group_replication_enforce_update_everywhere_checks = ON;
STOP GROUP_REPLICATION;
START GROUP_REPLICATION;
```

## 📊 MGR 的限制

### 1. 性能开销

```
单主模式：
- 写入延迟增加 20-30%
- 因为需要等待多数节点确认

多主模式：
- 写入延迟增加更多
- 冲突检测消耗 CPU
```

### 2. 网络要求

```
- 节点间延迟 < 10ms（同机房）
- 跨地域不推荐（延迟过高）
- 推荐万兆网络
```

### 3. 集群大小

```
推荐：3-9 个节点
- 最少 3 节点（容错 1 节点）
- 5 节点（容错 2 节点）
- 超过 9 节点性能下降
```

## 🛠️ MGR 运维

### 查看集群状态

```sql
-- 查看成员
SELECT
  MEMBER_ID,
  MEMBER_HOST,
  MEMBER_PORT,
  MEMBER_STATE,    -- ONLINE / RECOVERING / ERROR
  MEMBER_ROLE     -- PRIMARY / SECONDARY
FROM performance_schema.replication_group_members;

-- 查看组复制统计
SELECT * FROM performance_schema.replication_group_member_stats;
```

### 切换主节点

```sql
-- 单主模式下，手动切换主节点
SELECT group_replication_set_as_primary('server-uuid');

-- 或用 MySQL Shell
dba.switchPrimary()
```

### 故障检测

```sql
-- 查看可疑/失效节点
SELECT * FROM performance_schema.replication_group_member_stats
WHERE MEMBER_STATE != 'ONLINE';
```

## 🔥 MGR vs MHA

| 特性 | MHA | MGR |
|---|---|---|
| 切换时间 | 10-30 秒 | < 1 秒（自动） |
| 数据一致性 | 半同步下零丢失 | 强一致（Paxos） |
| 集群模式 | 主从 | 单主 / 多主 |
| 性能开销 | 较小 | 中等（20-30%） |
| 复杂度 | 中等 | 高 |
| 成熟度 | 成熟 | 较新 |
| 节点数 | 1 主多从 | 3-9 节点 |

**选择建议：**
- 中小规模、追求简单：选 MHA
- 大规模、强一致：选 MGR

## 🎯 实战：MGR 读写分离

```java
// MySQL Router 配置
[DEFAULT]
routing_strategy = round-robin

[master]
address = 192.168.1.10:3306
priority = 100

[slave1]
address = 192.168.1.11:3306
priority = 50

[slave2]
address = 192.168.1.12:3306
priority = 50
```

```sql
-- 应用配置（Java）
-- jdbc:mysql:mysqlrouter://router:6446/mydb
```

## 🎯 总结

**MGR 核心：**
- ✅ 基于 Paxos 协议的强一致复制
- ✅ 单主 / 多主两种模式
- ✅ 自动故障检测和切换
- ✅ MySQL 官方方案

**适用场景：**
- 中大规模集群（3-9 节点）
- 强一致性需求
- 官方技术支持需求

**注意事项：**
- 网络延迟必须低
- 性能开销约 20-30%
- 需要 MySQL 5.7.17+ / 8.0+

**下一步：** [🚦 ProxySQL 中间件](../07-ha/proxysql) — 高性能 MySQL 代理