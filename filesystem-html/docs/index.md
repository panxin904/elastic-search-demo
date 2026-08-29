---
layout: home
title: 文件系统 / 文件服务 / 存储全栈
date: 2026-08-27  # date-auto-injected
hero:
  name: 文件全栈
  text: Filesystem & Storage Atlas
  tagline: 系统掌握本地盘 FS / 分布式 FS / 对象存储 / 网络协议 / 云原生存储 / 容器 FS / 性能调优，构建完整存储工程师能力栈
  actions:
    - theme: brand
      text: 开始学习
      link: /path
    - theme: alt
      text: 知识图谱
      link: /graph
    - theme: alt
      text: 思维导图
      link: /mindmap
    - theme: alt
      text: 速记卡
      link: /cheatsheet
features:
  - icon: 📁
    title: 文件系统基础
    details: inode · VFS · Page Cache · 文件描述符 · 挂载 · 日志 · 路径解析
    link: /01-basics/inode-dentry
    linkText: 基础篇
  - icon: 💾
    title: 本地盘文件系统
    details: ext4 · XFS · Btrfs · ZFS · NTFS · APFS 横向对比与选型调优
    link: /02-disk-fs/ext4
    linkText: 本地盘
  - icon: 🌐
    title: 分布式文件系统
    details: HDFS · CephFS · GlusterFS · JuiceFS · MooseFS · Lustre 架构对比
    link: /03-distributed/hdfs
    linkText: 分布式
  - icon: 📦
    title: 对象存储
    details: S3 协议 · MinIO · 阿里云 OSS · 腾讯云 COS · 纠删码 · 生命周期
    link: /04-object/s3-protocol
    linkText: 对象存储
  - icon: 🔗
    title: 网络文件协议
    details: NFS · SMB/CIFS · WebDAV · FTP/SFTP · rsync 跨机文件访问
    link: /05-network/nfs
    linkText: 网络协议
  - icon: ☸️
    title: 云原生存储
    details: CSI · PV/PVC · StorageClass · Rook · Longhorn · OpenEBS
    link: /06-cloud-native/csi
    linkText: 云原生
  - icon: 🐳
    title: 容器文件系统
    details: OverlayFS · Docker layers · containerd · BuildKit · 存储驱动
    link: /07-container/overlayfs
    linkText: 容器
  - icon: 🛠️
    title: 文件工具集
    details: FUSE · debugfs · rsync · find/fd · inotify · du/df · lsof
    link: /08-tools/fuse
    linkText: 工具
  - icon: ⚡
    title: 性能调优
    details: IO 调度器 · Page Cache · fsync · readahead · Direct I/O
    link: /09-perf/io-scheduler
    linkText: 性能
  - icon: 🔒
    title: 安全与权限
    details: POSIX 权限 · ACL · xattr · 加密 · auditd 审计
    link: /10-security/posix-perm
    linkText: 安全
  - icon: 💼
    title: 备份与快照
    details: LVM/ZFS snapshot · Borg · restic · 3-2-1 原则 · RPO/RTO
    link: /11-backup/snapshot
    linkText: 备份
  - icon: 🏢
    title: 企业案例
    details: Netflix S3 · ByteDance JuiceFS · CERN EOS · Snowflake · Meta HDFS
    link: /12-cases/netflix-s3
    linkText: 案例
  - icon: 🎯
    title: 面试 / 实战
    details: 高频面试题 · 系统设计题 · 技术对比表
    link: /13-interview/questions
    linkText: 面试
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "从单块磁盘的 inode 到跨数据中心的对象存储，怎么系统学？",
      "POSIX 权限 / ACL / Capabilities 到底有什么区别？",
      "本地 FS（ext4 / xfs / btrfs / zfs）怎么选？",
      "网络 FS（NFS / SMB / CIFS）vs 分布式 FS（Ceph / MinIO / HDFS）",
      "K8s CSI 抽象、PV / PVC / StorageClass 怎么设计？"
    ]
const goals = [
      "存储全栈（单机 FS / 网络 FS / 分布式 FS / 对象存储）",
      "POSIX 权限模型 + ACL + 高级特性",
      "本地 FS 实战（ext4 / xfs / btrfs / zfs）",
      "网络 FS（NFS / SMB / CIFS / pNFS）",
      "分布式存储（Ceph / MinIO / HDFS / JuiceFS）",
      "云原生存储（CSI / Rook / Longhorn）"
    ]
const relatedSites = [
      { site: "linux", path: "/11-shell/debug", label: "Linux 实战" },
      { site: "bigdata", path: "/02-hdfs/architecture", label: "HDFS 架构" },
      { site: "cloud-native", path: "/06-storage/overview", label: "CSI 抽象" },
      { site: "devops", path: "/01-pipeline/overview", label: "CI/CD 流水线" },
      { site: "architecture", path: "/01-distributed/cap", label: "分布式理论" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>


## 关于本知识库

无论你是：

- 🆕 **初学者** 想弄清楚"打开一个文件背后发生了什么"
- 🔧 **运维工程师** 面对 ext4/ZFS/HDFS 选型困惑
- ☸️ **SRE / 平台工程师** 需要掌握 CSI / Rook / Longhorn 等 K8s 存储方案
- 🏗️ **架构师** 设计 PB 级数据湖或对象存储系统
- 🎯 **求职者** 备战存储相关面试

都能在这里找到对应的知识路径。

## 站点统计

<div class="kg-stats">
  <div class="kg-stat"><div class="kg-stat-num">13</div><div class="kg-stat-label">知识大类</div></div>
  <div class="kg-stat"><div class="kg-stat-num">76</div><div class="kg-stat-label">核心节点</div></div>
  <div class="kg-stat"><div class="kg-stat-num">70+</div><div class="kg-stat-label">内容页</div></div>
  <div class="kg-stat"><div class="kg-stat-num">3</div><div class="kg-stat-label">交互组件</div></div>
</div>

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [linux](https://java-px.bot.cd/linux/)：Linux 文件系统
- [observability](https://java-px.bot.cd/observability/)：存储监控
- [postgresql](https://java-px.bot.cd/postgresql/)：PG 存储引擎
- [mysql](https://java-px.bot.cd/mysql/)：MySQL InnoDB


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

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
