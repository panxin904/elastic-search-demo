---
title: 面试题与高频考点
---

# 文件系统面试高频题

> <span class="kg-badge kg-badge--interview">面试对比</span>
> 经典题 · 标准答案 · 高频考点

本章整理文件系统 / 存储领域的**经典面试题**，按概念 → 实战 → 设计三层次组织。

## 1. 基础概念题

### Q1. 什么是文件系统？作用是什么？

**答案**：文件系统是操作系统在块设备之上组织的**数据 + 元数据结构**，对外暴露命名空间与操作接口（open / read / write / close）。

作用：
- **数据组织**：把块设备的字节流组织成"文件"
- **元数据管理**：文件名、权限、时间戳、位置
- **持久化**：保证数据不丢（fsync / 日志）
- **共享**：多进程 / 用户访问同一文件
- **安全**：权限、ACL

### Q2. inode 与 dentry 是什么？

- **inode**：索引节点，存储文件的**元数据 + 数据块指针**（文件名不存）
- **dentry**：目录项，**文件名 → inode**的映射（不含文件内容）

```
文件名 ──→ dentry ──→ inode ──→ 数据块
```

**实战**：删除文件 = unlink dentry，inode 与数据块仍在 → 可恢复（undel）。

### Q3. Page Cache 是什么？为何重要？

**答案**：内核缓存**磁盘数据 + 用户写入**的内存区。

- **读**：命中 = 0 IO，miss 才读盘
- **写**：先写 Page Cache，异步刷盘（由脏页参数控制）

重要：
- 命中率 > 95% 时，应用 IO 性能提升 10-100 倍
- 数据库场景可绕过（O_DIRECT）

### Q4. fsync 做了什么？

**答案**：把文件的所有脏数据**强制刷到磁盘**，调用返回时数据已在物理介质上。

```c
fsync(fd);
```

- 代价：毫秒级（机械硬盘 10ms，NVMe 1ms）
- 应用：数据库持久化（WAL）、关键数据
- 折中：fdatasync（不刷元数据）

## 2. 分布式题

### Q5. HDFS 与 CephFS 的核心区别？

| 维度 | HDFS | CephFS |
|------|------|--------|
| 主控 | NameNode | MDS（可分布） |
| 数据 | DataNode | OSD |
| 一致性 | 强 | 强 |
| 写吞吐 | **极高** | 高 |
| 小文件 | 差 | 中 |
| K8s | 无原生 | Rook |

### Q6. 为什么 CephFS 用 CRUSH 算法？

**答案**：CRUSH 是去中心化的**数据分布算法**，不依赖元数据查找。

- 解决传统 hash 算法的"故障域"问题
- 每个 OSD 自己算副本位置 → 无中心瓶颈
- 支持权重、机架感知

### Q7. 对象存储 vs 文件系统？

| 维度 | 对象存储 | 文件系统 |
|------|----------|----------|
| 接口 | HTTP REST | POSIX |
| 操作 | PUT/GET/DELETE | open/read/write |
| 性能 | 高（流式） | 中（多 syscall） |
| 跨网 | **优** | 差 |
| 强一致 | ✅ | ✅ |

## 3. 性能与故障题

### Q8. 磁盘 IO 延迟升高，怎么排查？

```
1. iostat -x 1 看 %util, await
2. iotop 找 IO 重的进程
3. dmesg 看硬件错误
4. strace / perf trace 看 syscall
5. 看 Page Cache 命中率（sar -B）
```

| 现象 | 诊断 |
|------|------|
| %util > 80% | 磁盘饱和 |
| await 升高 | IO 排队 |
| Page Cache hit 突降 | 重启 / 清缓存 |

### Q9. df 显示 100%，但 du 不见大文件？

**答案**：**deleted 但仍被进程持有**的文件。

```bash
lsof | grep deleted
# 杀掉持有 fd 的进程
```

### Q10. 什么是 EC？为何比副本省空间？

**答案**：纠删码（Erasure Coding）通过数学算法（Reed-Solomon）把 k 个数据片算出 m 个校验片，任意 ≤ m 个片丢失可恢复。

```
副本：k 数据 × N 副本 = 100%+ 开销
EC：k + m  = 50% 左右开销（k=m 时）
```

代价：恢复时网络 IO 略高、编解码有 CPU 开销。

## 4. K8s / 云原生题

### Q11. PV / PVC / StorageClass 关系？

- **PV**：实际存储
- **PVC**：申请单（用户视角）
- **StorageClass**：动态创建模板

```
PVC（user 申请）→ K8s → SC（模板）→ CSI Driver → 创建 PV → 绑定 PVC
```

### Q12. 静态 PV vs 动态 PV？

| 维度 | 静态 | 动态 |
|------|------|------|
| 创建 | 管理员手工 | K8s + CSI 自动 |
| 适合 | 测试 | **生产** |
| StorageClass | 不用 | **必需** |
| 拓扑 | 立即绑定 | WaitForFirstConsumer |

### Q13. RWO vs RWX？

- **RWO (ReadWriteOnce)**：单节点读写
- **RWX (ReadWriteMany)**：多节点读写

支持 RWX 的存储：NFS、CephFS、GlusterFS、JuiceFS、Longhorn、MinIO（限块）。

## 5. 协议题

### Q14. NFSv4 与 NFSv3 关键区别？

| 维度 | NFSv3 | NFSv4 |
|------|--------|--------|
| 连接 | 多连接 | 单连接 |
| 状态 | 无 | **有** |
| 锁 | 外部 | 内置 |
| 端口 | 多 | 2049 单端口 |
| 安全 | 无 | Kerberos |

### Q15. SMB vs NFS？

- **SMB**：Windows 共享、ACL 精细、SMBv3 加密
- **NFS**：Unix/Linux 共享、POSIX 权限、Kerberos

## 6. 设计题

### Q16. 设计一个对象存储系统的关键模块？

```
1. 元数据服务：对象 → 位置
2. 数据节点：实际存数据
3. 复制：副本 / EC
4. 认证：IAM / 签名
5. SDK：HTTP REST API
6. 监控：指标 / 日志
```

### Q17. 设计一个分布式 FS 需要考虑什么？

```
- 元数据 / 数据分离
- 一致性模型（强 / 最终）
- 副本策略（副本 vs EC）
- 故障恢复
- 容量扩展
- 多租户
- 权限
- 协议兼容（POSIX / NFS / S3）
```

## 7. 大厂面试高频题

| 公司 | 高频题 |
|------|--------|
| 字节 | K8s 存储 / Ceph 原理 / JuiceFS |
| 阿里 | OSS / NAS / 纠删码 / PolarFS |
| 腾讯 | COS / CFS / 多云容灾 |
| AWS | S3 强一致 / Glacier / FSx |
| Meta | HDFS Federation / EC / Presto |
| Google | GFS / Spanner / Colossus |
| 微软 | Azure Blob / ADLS / ANF |
| 苹果 | APFS / iCloud / HDFS |

## 8. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| inode = 元数据 | "inode=元" |
| Page Cache = 加速 | "Cache=加速" |
| EC = 空间省 | "EC=省" |
| K8s = PVC / SC | "K8s=声明式" |
| RWX 才是共享 | "RWX=共享" |

## 参考

- 各大公司面试经验
- 《数据密集型应用系统设计》（DDIA）
- Linux / K8s 官方文档