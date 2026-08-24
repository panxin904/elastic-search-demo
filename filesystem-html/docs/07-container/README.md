# 07 · 容器文件系统

<span class="kg-badge kg-badge-container">容器</span>

Docker 镜像背后——OverlayFS 与分层原理。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [OverlayFS 联合挂载](/07-container/overlayfs) | 镜像层的底层技术 |
| [Docker 镜像分层](/07-container/docker-layers) | 为什么 `docker pull` 这么慢/快 |
| [containerd 快照](/07-container/containerd) | K8s 默认 runtime 的快照机制 |
| [BuildKit 缓存](/07-container/buildkit) | 新一代构建工具 |
| [存储驱动对比](/07-container/storage-drivers) | overlay2 / devicemapper / btrfs |

## 核心思想

```
镜像层（只读）
    ↓
容器层（读写）
    ↓
Union Mount 合并视图
```

Docker 镜像被设计成只读 + 多层共享——多个容器共享同一个镜像基础层，每个容器只有自己的薄写入层。空间占用小，启动快，传输高效。
## 🎯 本章学习路径

1. **了解场景**：每个协议都有它的设计目标（NFS = Unix 共享、SMB = Windows、FTP = 老系统）
2. **掌握配置**：端口 / 加密方式 / 性能调优
3. **安全加固**：防火墙规则 / TLS 配置 / 用户认证
4. **监控告警**：连接数 / 延迟 / 错误率

详细各协议配置见子节点文章。
