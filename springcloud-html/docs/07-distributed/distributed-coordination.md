---
title: 分布式协调
date: 2026-08-15  # date-auto-injected
---

# 🔄 分布式协调服务

> 在分布式系统中实现**协调、选举、配置管理、元数据存储**。

## 🎯 为什么需要分布式协调？

分布式系统中常见需求：
- **Leader 选举**：多节点选一个主节点
- **配置管理**：配置变更后所有节点实时感知
- **服务发现**：服务上下线自动感知
- **分布式锁**：见前文
- **集群管理**：节点加入 / 退出感知

**单机方案失效**，需要专门的**协调服务**。

## 🛠️ 三大协调服务对比

| 特性 | **ZooKeeper** | **etcd** | **Consul** |
|---|---|---|---|
| **算法** | ZAB（Paxos 变种）| Raft | Raft |
| **数据模型** | ZNode 树 | KV 键值对 | KV + 服务 |
| **一致性** | CP（强一致）| CP | CP / AP 可配 |
| **客户端** | 多种语言 | Go / HTTP | Go / HTTP / DNS |
| **Leader 选举** | ✅ | ✅ | ✅ |
| **配置中心** | ✅（NodeWatch）| ✅（Watch）| ✅ |
| **服务发现** | 需自己实现 | 需自己实现 | ✅（原生）|
| **健康检查** | 需自己实现 | TTL | ✅ |
| **多数据中心** | ❌ | ❌ | ✅ |
| **生态** | Hadoop / Kafka / Dubbo | K8s | 微服务 |

## 🐘 ZooKeeper 详解

### 数据模型

```
/
  /app
    /order-service
      node-0001     (临时节点：服务实例1)
      node-0002     (临时节点：服务实例2)
      node-0003     (临时节点：服务实例3)
    /inventory-service
      node-0001
      ...
```

| 节点类型 | 特性 | 用途 |
|---|---|---|
| **持久节点** | 一直存在 | 配置信息 |
| **临时节点** | 会话断开自动删除 | 服务注册、心跳 |
| **顺序节点** | 自动加序号 | 分布式锁、选举 |
| **TTL 节点** | 到期自动删除 | 定时任务 |

### 核心特性：ZAB 协议

**ZAB（ZooKeeper Atomic Broadcast）**

```
            Leader
            /    \
           ↓      ↓
       Follower  Follower
           ↑      ↑
           └──────┘

阶段 1：Leader 收到写请求 → 生成 Proposal
阶段 2：Leader 向所有 Follower 广播 Proposal
阶段 3：Follower 收到超过半数 ACK → Leader 提交
阶段 4：通知所有 Follower 提交
```

**保证：**
- **原子广播**：写操作要么全部成功要么全部失败
- **顺序一致性**：同一 Leader 的操作按发送顺序执行
- **崩溃恢复**：Leader 崩溃后能从 Follower 中选举新 Leader

### Watch 机制

```java
// 监听节点变化（一次性）
zk.exists("/app/order-service", watchedEvent -> {
    switch (watchedEvent.getType()) {
        case NodeCreated: System.out.println("节点创建"); break;
        case NodeDeleted: System.out.println("节点删除"); break;
        case NodeDataChanged: System.out.println("数据变更"); break;
    }
});
```

**注意：** Watch 是**一次性**的，触发后需要重新注册。

### Leader 选举

**典型场景：** 多节点部署一个主节点（Master）

```java
// Curator 的 LeaderLatch
LeaderLatch leaderLatch = new LeaderLatch(client, "/master-election");
leaderLatch.start();

if (leaderLatch.hasLeadership()) {
    // 我是 Leader
    doMasterJob();
}
```

**选举过程：**
```
1. 所有节点创建 /election 临时节点
2. 第一个创建的成为 Leader（zxid 最大者优先）
3. 其他节点 Watch Leader 节点
4. Leader 宕机 → 临时节点删除 → Watcher 触发 → 重新选举
```

## 🔵 etcd 详解

### 数据模型

```
/registry/services/order-service/192.168.1.10  →  {"port": 8080, "weight": 1}
```

KV 键值对，比 ZK 的 ZNode 树更扁平。

### 核心 API

```bash
# 写入（带租约）
etcdctl put /key value --lease=1234

# 读取
etcdctl get /key

# 监听（前缀）
etcdctl watch /prefix --prefix

# 租约（TTL）
etcdctl lease grant 30
etcdctl lease keepalive 1234
```

### Raft 共识算法

```
                Leader
               /  |  \
              ↓   ↓   ↓
           Follower Follower Follower
           
       Term 5      Term 6       Term 7
       ──────────  ──────────   ──────────
       Leader A    Leader B     Leader C
```

**Raft 简化了 Paxos：**

| 角色 | 职责 |
|---|---|
| **Leader** | 处理所有写请求、复制日志 |
| **Candidate** | 选举中的候选 |
| **Follower** | 被动响应、转发请求 |

**选举过程：**
```
1. Follower 超时未收到 Leader 心跳 → 成为 Candidate
2. Candidate 增加 Term，发起投票 RequestVote RPC
3. 多数派同意 → 成为新 Leader
4. 其他节点降级为 Follower
```

### 应用：K8s

**K8s 的所有数据都存在 etcd：**
- Pod 信息
- Service 端点
- ConfigMap / Secret
- 集群状态

## 🟢 Consul 详解

### 核心功能（一体化）

| 功能 | Consul 提供 |
|---|---|
| **服务发现** | ✅ 原生支持 |
| **健康检查** | ✅ HTTP / TCP / gRPC |
| **KV 存储** | ✅ |
| **多数据中心** | ✅ |
| **DNS 接口** | ✅ |

### 服务注册示例

```hcl
# 服务定义
service {
  name = "order-service"
  port = 8080
  
  check {
    http = "http://localhost:8080/health"
    interval = "10s"
  }
}
```

**服务发现：**
```bash
# DNS 方式
dig @127.0.0.1 -p 8600 order-service.service.consul

# HTTP 方式
curl http://localhost:8500/v1/catalog/service/order-service
```

## 🎯 选型建议

```
                       K8s 云原生？
                            │
              ┌─────────────┴─────────────┐
              是                          否
              │                           │
           etcd                    已有 ZooKeeper？
                                        │
                                  ┌─────┴─────┐
                                 是           否
                                  │           │
                              继续用 ZK    复杂业务？
                                              │
                                        ┌─────┴─────┐
                                       是           否
                                        │           │
                                    Consul       简单用 etcd
```

## 🛠️ Spring Cloud 集成

### Spring Cloud Zookeeper

```yaml
spring:
  cloud:
    zookeeper:
      connect-string: 127.0.0.1:2181
```

```java
// 服务注册
@RestController
public class OrderController {
    // 自动注册到 ZK
}

// 服务发现
@Service
public class OrderClient {
    @Autowired
    private DiscoveryClient discoveryClient;

    public List<ServiceInstance> getInstances() {
        return discoveryClient.getInstances("inventory-service");
    }
}
```

### Spring Cloud Consul

```yaml
spring:
  cloud:
    consul:
      host: 127.0.0.1
      port: 8500
      discovery:
        service-name: order-service
```

### Spring Cloud Kubernetes（基于 etcd）

```yaml
spring:
  cloud:
    kubernetes:
      discovery:
        enabled: true
```

## 📊 协调服务的应用场景

| 场景 | 实现 |
|---|---|
| **分布式锁** | ZK 临时顺序节点 / etcd Lease |
| **Leader 选举** | Curator LeaderLatch / etcd election |
| **配置中心** | ZK NodeWatch / etcd watch / Apollo |
| **服务发现** | ZK / Consul / Nacos |
| **集群成员管理** | ZK 临时节点 / etcd Lease |
| **元数据存储** | ZK / etcd / Consul |

## ⚠️ 协调服务的坑

### 1. 脑裂（Split-Brain）

**场景：** 网络分区导致两个节点都认为自己是 Leader

**解决：** 多数派投票（Raft / ZAB 都解决）

### 2. Watch 丢失

ZK 的 Watch 是**一次性**的，触发后未及时重注册

**解决：** 用 Curator 的 `NodeCache` / `PathChildrenCache`

### 3. 会话过期

客户端与 ZK 断开 → 会话超时 → 临时节点删除

**解决：** 重连 + 重建临时节点 / 业务幂等

### 4. 数据量限制

ZK / etcd 设计用于**元数据**，不适合存大量业务数据

**建议：** 数据控制在 **MB 级**

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| ZooKeeper 选举机制？| ZAB 协议（2 阶段：发现 + 同步）|
| Raft vs Paxos？| Raft 是 Paxos 的简化版（角色 + 任期）|
| ZooKeeper vs etcd？| ZK ZNode 树 vs etcd KV，更强一致性 |
| Watch 机制？| 一次性 + 客户端重注册 |
| Leader 选举过程？| 超时 → Candidate → RequestVote → 多数派 |

---

- 上一章：[📊 分布式存储](/07-distributed/distributed-storage)
- 下一章：[🔍 分布式追踪](/07-distributed/distributed-tracing)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地
