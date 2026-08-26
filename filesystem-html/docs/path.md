---
title: 学习路径
---

# 学习路径

根据不同角色与目标，规划差异化学习路线。

## 🆕 新手入门（1-2 天）— 弄懂"打开文件背后发生了什么"

1. [inode 与 dentry](/01-basics/inode-dentry) — 理解文件的本质（不是文件名，是 inode）
2. [VFS 虚拟文件系统](/01-basics/vfs) — Linux 如何用统一接口抽象不同 FS
3. [文件描述符](/01-basics/file-descriptor) — open/read/write 背后的 fd 表
4. [Page Cache 页缓存](/01-basics/page-cache) — 为什么 read 后第二次会"变快"
5. [挂载 mount](/01-basics/mount) — 文件系统如何接入目录树
6. [ext4](/02-disk-fs/ext4) — Linux 默认 FS，看一遍就懂

## 🔧 后端 / 运维工程师（3-5 天）— 横向选型 + 日常运维

1. [本地盘 FS 横向对比](/02-disk-fs/compare) — ext4 vs XFS vs Btrfs vs ZFS 怎么选
2. [POSIX 权限与 ACL](/10-security/posix-perm) — chmod/chown/setfacl 的所有秘密
3. [du/df 与 lsof](/08-tools/du-df) — 排查"磁盘满了但 du 找不到"的经典问题
4. [Page Cache 调优](/09-perf/page-cache-tune) — `vm.dirty_ratio` 的玄学
5. [IO 调度器选型](/09-perf/io-scheduler) — SSD 用 none，HDD 用 mq-deadline
6. [快照技术](/11-backup/snapshot) — LVM / ZFS / Btrfs 快照原理
7. [rsync 增量同步](/11-backup/snapshot) — 备份与镜像的瑞士军刀

## 🌐 大数据工程师（5-7 天）— 分布式存储原理

1. [HDFS](/03-distributed/hdfs) — 大数据存储基石
2. [CephFS](/03-distributed/cephfs) — 统一存储（块/对象/文件三合一）
3. [JuiceFS](/03-distributed/juicefs) — 云原生元数据 + 对象存储组合
4. [S3 协议](/04-object/s3-protocol) — 对象存储的事实标准
5. [纠删码 EC](/04-object/erasure-coding) — vs 多副本的取舍
6. [Meta HDFS 演进](/12-cases/meta-hdfs) — 真实演进案例
7. [ByteDance JuiceFS](/12-cases/juicefs-bytedance) — PB 级实践

## ☸️ SRE / 平台工程师（5-7 天）— 云原生存储

1. [CSI 容器存储接口](/06-cloud-native/csi) — K8s 存储标准
2. [PV/PVC/StorageClass](/06-cloud-native/pv-pvc) — 声明式存储
3. [动态配置](/06-cloud-native/dynamic) — 自动创建 PV
4. [Rook Ceph Operator](/06-cloud-native/rook) — 工业级部署
5. [Longhorn](/06-cloud-native/longhorn) — 轻量分布式块
6. [Volume Snapshot / Clone](/06-cloud-native/snapshot) — 数据保护
7. [OverlayFS](/07-container/overlayfs) — 容器镜像原理
8. [Docker layers](/07-container/docker-layers) — 镜像分层缓存

## 🏗️ 架构师（1-2 周）— 系统设计与权衡

1. [对象存储 vs 文件存储 vs 块存储](/13-interview/comparison) — 三种存储的本质区别
2. [Netflix S3 架构](/12-cases/netflix-s3) — 每天万亿次操作的设计
3. [Snowflake 存储层](/12-cases/snowflake) — 计算存储分离典范
4. [文件系统设计模式](/13-interview/system-design) — 从单机到 PB 级
5. [S3 一致性模型](/04-object/consistency) — 强一致 vs 最终一致
6. [灾难恢复 RPO/RTO](/11-backup/dr) — SLA 设计
7. [3-2-1 备份原则](/11-backup/3-2-1) — 数据保护方法论
8. [加密静态 / 传输](/10-security/encryption) — 安全合规

## 🎯 求职者（3-5 天）— 面试高频题速通

1. [高频面试题](/13-interview/questions) — 50+ 题（含答案要点）
2. [系统设计题](/13-interview/system-design) — 6 大经典场景
3. [技术对比表](/13-interview/comparison) — ext4/XFS/Btrfs/ZFS 等 12 个对比维度
4. [横向对比与选型](/02-disk-fs/compare) — 面试必问
5. [Page Cache 与文件读流程](/01-basics/page-cache) — 高频原理题

## 📚 推荐配套学习

- **Linux 基础**：[本站 Linux 站](https://java-px.bot.cd/linux/) — 文本三剑客、systemd、SSH 等
- **网络协议**：[本站网络站](https://java-px.bot.cd/network/) — NFS / SMB 底层依赖网络
- **云原生**：[本站云原生站](https://java-px.bot.cd/cloud-native/) — CSI / Rook / Longhorn
- **大数据**：[本站大数据站](https://java-px.bot.cd/bigdata/) — HDFS / Hudi / Iceberg


<!-- auto-enrich:do-not-edit -->

## 实战示例

```bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
```

```yaml
# TODO: 配置示例
key: value
```

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |
<!-- auto-enrich:do-not-edit -->
