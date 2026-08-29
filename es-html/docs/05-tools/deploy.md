---
title: ES 部署与配置
date: 2026-08-15  # date-auto-injected
---

<span class="kg-badge kg-badge-ops">部署</span>

# ES 部署与生产配置参考

> 26 个生产环境必备的 ES 7 部署与配置模板，按 **6 大主题** 整理。
> 每个模板含场景说明、完整 yaml/命令、关键说明，可直接复制到生产环境使用。

## 🎯 6 大主题

| 主题 | 数量 | 内容 |
|---|---|---|
| 🛠️ **安装方式** | 4 | Tar 包 / Docker 单机 / Docker Compose 集群 / RPM |
| 🏗️ **集群配置** | 3 | 基础集群 / 分片分配 / 恢复与慢日志 |
| 🧩 **节点角色** | 4 | Master / Data / Coordinating / Hot-Warm-Cold |
| 💾 **内存与 GC** | 4 | Heap 计算 / G1GC / memory_lock / 熔断器 |
| 🔐 **安全与 TLS** | 3 | 启用 xpack.security / 用户角色 / 网络安全 |
| 📊 **监控配置** | 3 | xpack.monitoring / Cerebro / 告警阈值 |

<EsDeploymentConfig />

## 📚 学习路径

### 🌱 新人（按顺序阅读）
1. 🛠️ Tar 包部署 → 跑通第一个集群
2. 🏗️ 集群配置 → 理解 elasticsearch.yml
3. 💾 Heap 大小 → 调优第一刀
4. 📊 Cerebro → 可视化监控

### 🚀 进阶（生产就绪）
1. 🧩 节点角色 → 拆分 master/data/coordinating
2. 🔐 xpack.security → 启用认证 + TLS
3. 💾 G1GC + memory_lock → 关键性能配置
4. 📊 监控告警阈值 → 接入 Prometheus / CloudWatch

### 🏆 高阶（大规模集群）
1. 🧩 Hot-Warm-Cold 架构 → 降低存储成本
2. 🏗️ 分片分配 + Awareness → 抗 AZ 故障
3. 🔐 字段级权限 → 多租户隔离
4. 📊 独立监控集群 → 大规模可观测性

## ⚠️ 部署前检查清单

部署 ES 集群到生产前，请确认：

- [ ] **OS**：Linux x86_64，内核 ≥ 3.10
- [ ] **内存**：每节点 ≥ 16G（生产 ≥ 32G）
- [ ] **磁盘**：SSD 推荐，RAID 或多盘 JBOD，单独挂载点
- [ ] **网络**：千兆网卡，节点间低延迟（< 10ms）
- [ ] **JDK 17**（ES 7.x 推荐 11，7.17+ 支持 17）
- [ ] **vm.max_map_count ≥ 262144**
- [ ] **关闭 swap**
- [ ] **关闭 THP (transparent_hugepage)**
- [ ] **ulimit nofile ≥ 65536**
- [ ] **3 / 5 / 7 节点奇数**（master 需要 majority）
- [ ] **DNS 解析**：节点间用主机名而非 IP
- [ ] **时间同步**：NTP 服务，所有节点时间一致
- [ ] **安全**：9200 / 9300 端口只允许内网访问

## 🔗 关联文档

- [安装部署](/04-ops/installation)
- [JVM 调优](/04-ops/jvm-tuning)
- [分片分配](/04-ops/shard-allocation)
- [集群健康](/04-ops/cluster-health)
- [集群重启](/04-ops/restart)
- [监控 Cerebro](/04-ops/monitoring)
- [Java Client 官方文档](https://www.elastic.co/guide/en/elasticsearch/client/java-api-client/current/installation.html)
