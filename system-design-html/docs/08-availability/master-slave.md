---
title: 主备与主从
---

# 主备与主从

> 1 主 1 备 / 1 主多从，最简单的高可用方案。**写主读从，备机待命**。

## 1. 什么是主备 / 主从？

```
主备（Master-Backup / Active-Passive）：
  - 1 主 + 1 备
  - 备机平时不服务
  - 主机挂了，备机接管

主从（Master-Slave / Active-Standby）：
  - 1 主 + 多从
  - 从机可以读
  - 主机挂了，从机选举一个接管

📌 主备是主从的特殊形式（1 从）
   工业场景更多用主从（读写分离）
```

## 2. 主备模式（Active-Passive）

### 2.1 工作模式

```
正常：
  Master ← write
  Backup ← 同步 Master

故障：
  Master 挂了
  Backup 升级为 Master
  应用切换 IP/DNS 到新 Master

恢复：
  旧 Master 恢复
  变成新 Master 的 Backup
```

### 2.2 数据同步

```
同步方式：
  1. 同步复制：Master 写完所有 Backup 才返回
     - 强一致
     - 性能差（要等所有 Backup ACK）
  2. 异步复制：Master 写本地即返回
     - 性能好
     - 可能丢数据（Master 挂了 Backup 还没同步）
  3. 半同步：至少 1 个 Backup ACK 才返回
     - 折中
     - MySQL 5.7+ 默认

📌 银行用同步，电商用半同步
```

### 2.3 切换方式

```
VIP 漂移（Virtual IP）：
  - Master 持有一个 VIP（如 10.0.0.100）
  - 应用连 VIP
  - 切换时 Backup 接管 VIP
  - 应用无感知

Keepalived：
  - 基于 VRRP 协议
  - Master/Backup 互发心跳
  - 3 次没收到心跳 → Backup 接管
  - 切换时间 < 1s

MHA（MySQL High Availability）：
  - MySQL 专用
  - 自动检测 + 切换
  - 30s 内完成
```

### 2.4 优缺点

```
优点：
  - 简单
  - 强一致（同步模式）
  - 切换快（VIP）

缺点：
  - 备机浪费（平时不服务）
  - 单 Master 性能瓶颈
  - 脑裂风险（双 Master）
```

## 3. 主从模式（Master-Slave）

### 3.1 工作模式

```
        Master
          │
    ┌─────┼─────┐
    ↓     ↓     ↓
  Slave1 Slave2 Slave3
  读     读     读

读写分离：
  - 写请求：Master
  - 读请求：Slave（轮询 / 加权）
  - 性能提升 3-5x
```

### 3.2 复制方式

```
MySQL 主从复制：
  1. Master 写 binlog
  2. Slave IO 线程拉 binlog
  3. Slave SQL 线程重放
  4. 数据最终一致（异步）

半同步复制（MySQL 5.7+）：
  - Master 写 binlog + 至少 1 Slave ACK
  - 强一致增强
```

### 3.3 主从切换

```
场景：Master 挂了

步骤：
  1. Slave 提升为新 Master
  2. 其他 Slave 改连新 Master
  3. 应用切换
  4. 旧 Master 恢复后 → 变成 Slave

实现：
  - MHA
  - MGR（MySQL Group Replication）
  - Orchestrator
```

### 3.4 读写分离的坑

```
问题 1：主从延迟
  - Master 写完，Slave 还没同步
  - 读 Slave 看不到新数据
  - 解决：强制读 Master（关键业务）

问题 2：主从不一致
  - 异步复制必然延迟
  - 突然宕机可能丢数据
  - 解决：半同步 + 定期对账

问题 3：脑裂
  - Master 假死
  - Slave 选举新 Master
  - 旧 Master 恢复 → 双写
  - 解决：fencing / STONITH
```

## 4. 主备 vs 主从

| 维度 | 主备 | 主从 |
|---|---|---|
| 机器数 | 2 | 2+ |
| 备机/从机 | 不服务 | 可读 |
| 资源利用率 | 低 | 高 |
| 切换 | 简单 | 复杂 |
| 性能 | 单机 | 多机 |
| 适用 | 强一致 | 读多写少 |

## 5. 工程实现

### 5.1 MySQL 主从配置

```bash
# Master 配置
[mysqld]
server-id = 1
log-bin = /var/lib/mysql/mysql-bin.log
binlog-format = ROW

# Slave 配置
[mysqld]
server-id = 2
relay-log = /var/lib/mysql/relay-bin.log
read-only = ON
log-slave-updates = ON

# Master 创建复制用户
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%' IDENTIFIED BY 'password';

# Slave 配置主从
CHANGE MASTER TO
  MASTER_HOST='10.0.0.1',
  MASTER_USER='repl',
  MASTER_PASSWORD='password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=0;

START SLAVE;
```

### 5.2 读写分离（ShardingSphere）

```yaml
# application.yml
spring:
  shardingsphere:
    rules:
      replica-query:
        data-sources:
          prds:
            primary-data-source-name: ds-master
            replica-data-source-names: ds-slave1,ds-slave2
            load-balancers:
              name: round-robin
```

```java
// 强制读主
@Hint("prds")
public List<Order> getRecentOrders(Long userId) {
    return orderDao.findByUserId(userId);
}
```

### 5.3 Keepalived VIP 漂移

```bash
# Master keepalived.conf
vrrp_script check_mysql {
    script "/usr/bin/check_mysql.sh"
    interval 2
    weight -20
    fall 3
    rise 2
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    virtual_ipaddress {
        10.0.0.100
    }
    track_script {
        check_mysql
    }
}
```

## 6. 监控告警

```
核心指标：
  - Master-Slave 延迟（Seconds_Behind_Master）
  - Slave IO / SQL 线程状态
  - 复制错误
  - 主从数据一致性（pt-table-checksum）

告警：
  - 延迟 > 60s → 告警
  - 复制中断 → 立即告警
  - 主从数据不一致 → 立即告警
```

## 7. 何时用主备 / 主从？

```
主备：
  - 强一致（金融）
  - 业务量不大
  - 简单可靠

主从：
  - 读多写少（电商、内容）
  - 性能要求高
  - 可容忍最终一致（异步）

📌 99% 互联网业务用主从
   金融核心用主备（同步）
```

## 8. 一句话总结

```
📌 主备：1 主 1 备，备机不服务（强一致、资源浪费）
📌 主从：1 主多从，从机可读（读写分离、性能高）
📌 复制：同步（强） / 半同步（折中） / 异步（快）
📌 切换：VIP 漂移（Keepalived）/ MHA / MGR
📌 读写分离：主写从读，延迟问题是核心
📌 防脑裂：fencing（强制 kill 旧 Master）
📌 主从 vs 主备：性能 vs 一致性的取舍
```

## 9. 参考资料

- MySQL High Availability (Charles Bell, 2010)
- MHA 官方文档
- Keepalived 官方文档
- "MySQL High Availability: Tools for Building Robust Data Centers"
- ShardingSphere 读写分离
- PXC / Galera 集群方案


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
