---
title: 全维度对比
---

# 文件系统全维度对比表

> <span class="kg-badge kg-badge--interview">面试对比</span>
> 17 个 FS / 存储 一张表看全

本章把本站涉及的所有文件系统 / 存储做一个**终极对比**，作为面试 / 选型的最后参考。

## 1. 总体对比矩阵

| FS / 存储 | 类型 | 主战场 | POSIX | 一致性 | 主从 | 推荐度 |
|-----------|------|--------|-------|--------|------|--------|
| **ext4** | 本地盘 | 通用 Linux | ✅ | 强 | 单点 | ⭐⭐⭐⭐ |
| **XFS** | 本地盘 | RHEL / 大文件 | ✅ | 强 | 单点 | ⭐⭐⭐⭐ |
| **Btrfs** | 本地盘 | SUSE / 快照 | ✅ | 强 | 单点 | ⭐⭐⭐ |
| **ZFS** | 本地盘 | NAS / 备份 | ✅ | 强 | 单点 | ⭐⭐⭐⭐ |
| **NTFS** | 本地盘 | Windows | ❌ | 强 | 单点 | ⭐⭐⭐⭐ |
| **APFS** | 本地盘 | Apple | ✅ | 强 | 单点 | ⭐⭐⭐ |
| **HDFS** | 分布式 | Hadoop | 半 | 强 | NameNode | ⭐⭐⭐⭐ |
| **CephFS** | 分布式 | 全场景 | ✅ | 强 | MDS | ⭐⭐⭐⭐ |
| **GlusterFS** | 分布式 | 中小企业 | ✅ | 最终 | 无 | ⭐⭐⭐ |
| **JuiceFS** | 分布式 | K8s / AI | ✅ | 强 | 外部 KV | ⭐⭐⭐⭐⭐ |
| **MooseFS** | 分布式 | 入门 | ✅ | 强 | Master | ⭐⭐⭐ |
| **Lustre** | 分布式 | HPC | ✅ | 强 | MDS | ⭐⭐⭐⭐ |
| **S3 / OSS** | 对象 | 通用 / 云 | ❌ | 强 | 多副本 | ⭐⭐⭐⭐⭐ |
| **MinIO** | 对象 | 自建 | ❌ | 强 | 集群 | ⭐⭐⭐⭐ |
| **NFS** | 协议 | Unix 共享 | ✅ | 强 | 单服务 | ⭐⭐⭐⭐ |
| **SMB** | 协议 | Windows 共享 | ✅ | 强 | 单服务 | ⭐⭐⭐⭐ |
| **WebDAV** | 协议 | 远程 / 网盘 | ✅ | 强 | 单服务 | ⭐⭐⭐ |

## 2. 按业务场景选型

### 2.1 我是 Linux 运维，单机

| 需求 | 推荐 |
|------|------|
| 通用 | ext4 / XFS |
| 大文件 | XFS |
| 快照 / 备份 | Btrfs / ZFS |
| RHEL 系 | XFS |
| Debian 系 | ext4 |

### 2.2 我是大数据工程师

| 需求 | 推荐 |
|------|------|
| Hadoop / Hive / Spark | **HDFS** |
| 数据湖（Iceberg / Delta） | **S3 / OSS + Iceberg** |
| 实时（Flink） | Kafka + S3 / OSS |

### 2.3 我是 K8s 工程师

| 需求 | 推荐 |
|------|------|
| 块存储（数据库） | **Rook-Ceph RBD / Longhorn** |
| 共享（RWX） | **JuiceFS / CephFS / NFS CSI** |
| 对象存储 | **MinIO + CSI** |
| 测试 | host-path |

### 2.4 我是企业存储管理员

| 需求 | 推荐 |
|------|------|
| 全场景 | **Ceph** |
| NAS / 文件共享 | **GlusterFS / NFS** |
| 自建对象存储 | **MinIO** |
| 备份归档 | **Borg + S3 / Glacier** |

### 2.5 我是 Windows 用户

| 需求 | 推荐 |
|------|------|
| 系统盘 | NTFS |
| 文件共享 | SMB |
| Apple | APFS |

### 2.6 我是 HPC 研究员

| 需求 | 推荐 |
|------|------|
| 大文件流式 IO | **Lustre** |
| 中小集群 | BeeGFS / NFS |

### 2.7 我是 AI / ML 工程师

| 需求 | 推荐 |
|------|------|
| 数据集共享 | **JuiceFS / Alluxio + S3** |
| 大模型 checkpoint | **S3 / OSS** |
| 多 worker 并行 | **Lustre / JuiceFS** |

## 3. 关键特性对比

### 3.1 数据一致性

| FS | 一致性 |
|----|--------|
| ext4 / XFS / ZFS / Btrfs | 强（本地） |
| HDFS | 强（写完成即可读） |
| CephFS | 强 |
| GlusterFS | 最终一致（默认） |
| JuiceFS | 强 |
| S3 | 强（2020+） |

### 3.2 副本与 EC

| FS | 默认策略 | EC |
|----|----------|----|
| ext4 / XFS | 不支持 | 不支持 |
| HDFS | 3 副本 | RS 6+3 |
| Ceph | 3 副本 | EC k+m |
| GlusterFS | 副本 | Dispersed |
| JuiceFS | 对象存储自带 | ✅ |
| Lustre | RAID | 软件 RAID |
| MinIO | EC 4+2 | ✅ |

### 3.3 性能特点

| FS | 顺序写 | 顺序读 | 随机读 | 小文件 |
|----|--------|--------|--------|--------|
| ext4 | 优 | 优 | 中 | 中 |
| XFS | **优** | **优** | 中 | 中 |
| ZFS | 优 | 优 | 中 | 中 |
| Btrfs | 优 | 优 | 中 | 中 |
| HDFS | **极优** | **极优** | 差 | **差** |
| CephFS | 优 | 优 | 中 | 中 |
| GlusterFS | 中 | 中 | 中 | **优** |
| JuiceFS | 中 | 中 | 中 | **优** |
| S3 | 中 | 中 | 中 | 中 |
| MinIO | 中 | 中 | 中 | 中 |
| Lustre | **极优** | **极优** | 中 | 中 |

## 4. K8s 集成对比

| FS | RWX | 动态供给 | CSI | Rook |
|----|-----|---------|-----|------|
| NFS | ✅ | ✅ | ✅ | ❌ |
| SMB | ✅ | ✅ | ✅ | ❌ |
| Rook-Ceph RBD | ❌ | ✅ | ✅ | ✅ |
| Rook-CephFS | ✅ | ✅ | ✅ | ✅ |
| GlusterFS | ✅ | ✅ | ✅ | ❌ |
| Longhorn | ✅ | ✅ | ✅ | ❌ |
| OpenEBS Mayastor | ❌ | ✅ | ✅ | ❌ |
| JuiceFS | ✅ | ✅ | ✅ | ❌ |
| MinIO | ✅ | ✅ | ✅ | ❌ |
| hostPath | ❌ | ❌ | ❌ | ❌ |

## 5. 容灾对比

| FS | 跨机房 | 多 AZ | 异地灾备 |
|----|--------|--------|----------|
| HDFS | Federation / Rack | ✅ | CRR |
| CephFS | 副本 | ✅ | 异地复制 |
| GlusterFS | Geo-Repl | ✅ | ✅ |
| JuiceFS | 跨桶 | ✅ | ✅ |
| Lustre | 多 OSS | 中 | 软件方案 |
| S3 | ✅ | ✅ | CRR |

## 6. 学习曲线

| FS | 难度 |
|----|------|
| ext4 / XFS | 极低 |
| NTFS | 低 |
| NFS / SMB | 低 |
| HDFS | 中 |
| GlusterFS | 中 |
| CephFS | **高** |
| Lustre | **高** |
| JuiceFS | 低 |
| MinIO | 低 |
| ZFS | 中 |

## 7. 成本对比

| FS | 硬件成本 | 软件成本 | 运维 |
|----|---------|---------|------|
| ext4 / XFS | 低 | 0 | 极低 |
| HDFS | 中 | 0 | 中 |
| Ceph | 高 | 0 | **高** |
| GlusterFS | 中 | 0 | 中 |
| JuiceFS | 低（对象存储） | 0 | 低 |
| MinIO | 中 | 0 | 低 |
| Lustre | 高 | 0（社区）/ 商业 | **高** |
| S3 / OSS | 高（云） | 按量 | 0 |

## 8. 终极选型表

| 你是 | 用 |
|------|-----|
| Linux 初学者 | ext4 |
| Linux 中级 | XFS |
| SUSE 用户 | Btrfs |
| 备份 / NAS 家用 | ZFS |
| 大数据 | HDFS + 对象存储 |
| K8s 共享 | JuiceFS / CephFS |
| K8s 数据库 | Rook-Ceph / Longhorn |
| 自建对象存储 | MinIO |
| 科研 HPC | Lustre |
| Windows 客户端多 | SMB |
| Linux 客户端多 | NFS |
| 云原生 | JuiceFS / 对象存储 + Iceberg |
| 个人网盘 | Nextcloud（WebDAV） |

## 9. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 没有银弹 | "无万能" |
| 业务驱动选型 | "业务=选型" |
| JuiceFS + HDFS + 对象 = 现代三大件 | "三大件" |
| 运维成本不能忽视 | "运维=成本" |
| 永远画决策树 | "决策树=工具" |

## 参考

- 本站点全部章节
- DDIA
- 各大厂商白皮书


<!-- auto-enrich:do-not-edit -->

## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
