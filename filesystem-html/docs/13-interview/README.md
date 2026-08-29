# 13 · 面试 / 实战

<span class="kg-badge kg-badge-interview">面试</span>

求职导向的高频题、系统设计、对比表。

## 概念图

<!-- mermaid-injected:do-not-edit -->

```mermaid
graph LR
  basic[基础题]
  design[设计题]
  case[场景题]
  opt[优化题]
  basic --> design
  design --> case
  case --> opt
```

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [高频面试题](/13-interview/questions) | 50+ 道（含要点答案） |
| [系统设计题](/13-interview/system-design) | 6 大经典场景（文件上传/同步/对象存储等） |
| [技术对比表](/13-interview/comparison) | 12 个核心维度的横向对比 |

## 面试题分类

```
底层原理（30%）
├── inode / Page Cache / VFS
├── 读写流程 / 同步语义
└── 分布式一致性 / CAP

工具使用（20%）
├── du/df/lsof/find 排查
├── rsync / 备份恢复
└── 性能分析 iostat / strace

架构设计（30%）
├── 对象存储系统设计
├── 分布式 FS 选型
└── 数据湖 / 数据备份方案

横向对比（20%）
├── ext4 vs XFS vs Btrfs
├── NFS vs SMB
└── S3 vs HDFS vs Ceph
```
## 🎯 本章学习路径

1. **了解场景**：每个协议都有它的设计目标（NFS = Unix 共享、SMB = Windows、FTP = 老系统）
2. **掌握配置**：端口 / 加密方式 / 性能调优
3. **安全加固**：防火墙规则 / TLS 配置 / 用户认证
4. **监控告警**：连接数 / 延迟 / 错误率

详细各协议配置见子节点文章。


<!-- auto-enrich:do-not-edit -->

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
