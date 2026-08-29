---
title: CERN EOS 存储
date: 2026-08-15  # date-auto-injected
---

# CERN — EOS 粒子物理数据的存储底座

> <span class="kg-badge kg-badge--cases">企业案例</span>
> EOS · CERN · 粒子物理 · PB/天

CERN（欧洲核子研究组织）是大型强子对撞机（LHC）的所在地。每秒产生上百万次粒子碰撞，**每年产生数十 PB 数据**。他们用 **EOS**（CERN 开发的存储系统）管理这些数据。

## 1. 数据规模

| 指标 | 数值 |
|------|------|
| 总容量 | **EB 级** |
| 年新增 | ~100 PB |
| 单文件数 | 十亿级 |
| 文件大小 | 1 KB ~ 100 GB |
| 用户数 | 全球 13000+ 物理学家 |

## 2. EOS 简介

EOS 是 CERN 开发的**对象 + POSIX** 存储系统：

- 基于开源 CernVM-FS / QuarkDB
- 支持 POSIX + S3-like
- 跨数据中心复制
- 设计用于**海量小文件 + 大文件**

## 3. 架构

```
┌──────────────────────────────────────┐
│     Workers / Physics Analysis       │
│         (C++ / Python / ROOT)        │
└────────────┬─────────────────────────┘
             │  FUSE / XRootD / POSIX
┌────────────▼─────────────────────────┐
│       EOS MGM (Master)               │
│    - 元数据管理                       │
│    - 调度 / 复制                     │
└─┬────────────────────┬────────────┬───┘
  │                    │            │
┌─▼──────────┐  ┌──────▼───────┐ ┌──▼──────────┐
│ EOS FST    │  │ EOS FST      │ │ EOS FST     │
│ (1PB)      │  │ (1PB)        │ │ (1PB)       │
│ - 单盘 /  │  │ - 单盘 /     │ │ - 单盘 /    │
│   RAID     │  │   RAID       │ │   RAID      │
└────────────┘  └──────────────┘ └─────────────┘
```

## 4. 设计取舍

### 4.1 元数据策略

- **元数据走 MGM**（QuarkDB：基于 RocksDB + Redis 协议的 KV）
- **数据走 FST**（File Storage Target，FUSE 后端）

### 4.2 协议兼容

| 协议 | 用途 |
|------|------|
| POSIX (FUSE) | 用户态挂载 |
| XRootD | 高性能 ROOT IO（粒子物理专用） |
| HTTP / WebDAV | Web 访问 |
| S3 | 对象存储 |
| GridFTP | 网格计算 |

### 4.3 副本策略

- 默认 2 副本
- 可配 EC（节省空间）
- 自动修复
- 跨数据中心复制

## 5. 实战：粒子物理工作流

```text
1. LHC 探测（每秒 600 M 事件）
     ↓ 触发 + 压缩
2. 在线筛选（每个事件 100 KB）
     ↓ 写盘
3. EOS 暂存区（PB 级）
     ↓ 拷贝
4. EOS 长期存储（100 PB+）
     ↓ 用户访问
5. ROOT 分析（物理学家下载）
```

## 6. 实战：客户端

### 6.1 FUSE 挂载

```bash
# 用户主机
mount -t fuse eos@MGM_IP fuse /eos -o allow_other
ls /eos/experiment/atlas/data/Run3/
```

### 6.2 XRootD

```bash
# ROOT 用 XRootD 直接访问
TFile *f = TFile::Open("root://eos.example.org//path/file.root");
```

### 6.3 HTTP

```bash
curl https://eos.example.org/path/to/file
```

## 7. 性能优化

### 7.1 写优化

- 多 FST 并行写
- 写预分配（避免空间碎片）
- 大文件分片

### 7.2 读优化

- 客户端缓存（EOS 内置）
- CDN 边缘加速
- P2P 模式（XRootD）

### 7.3 EC 配置

```bash
eos fs add <fs> <path> <size> layout=raid6 # 6+2 EC
```

## 8. 监控与运维

### 8.1 关键指标

- 总容量 / 已用
- 写入速率
- 单 FST 健康
- 副本一致性

### 8.2 常见问题

| 故障 | 处置 |
|------|------|
| 单 FST 挂 | MGM 自动重路由 |
| MGM 挂 | 切换 HA |
| 文件锁 | EOS 内置锁 |
| 配额超限 | 触发告警 |

## 9. CERN 的开源贡献

CERN 把 EOS、MGM、XRootD、QuarkDB 都开源：

- **EOS**：GitHub 公开仓库
- **CernVM-FS**：高能物理软件分发
- **Indico**：会议管理
- **Zenodo**：科研数据存档

## 10. 经验教训

| 经验 | 说明 |
|------|------|
| **元数据 / 数据分离** | MGM + FST 分离，可扩展 |
| **多协议** | POSIX + XRootD + HTTP 满足不同场景 |
| **PB 级易用** | CERN 设计哲学是"对物理学家友好" |
| **跨数据中心** | LHC 多站点数据共享 |
| **EC 节省** | 100 PB × 50% = 50 PB 节省 |

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| EOS = CERN 制造 | "EOS=CERN" |
| 元数据 MGM | "MGM=元数据" |
| 数据 FST | "FST=数据" |
| 多协议 = 友好 | "多协议=易用" |
| EC 节省空间 | "EC=省 PB" |

## 参考

- EOS 文档：<https://eos-docs.web.cern.ch/
- EOS GitHub
- CERN Storage Whitepaper