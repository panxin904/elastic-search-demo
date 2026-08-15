---
title: 容器存储驱动
---

# 容器存储驱动 — OverlayFS、device-mapper、Btrfs 对比

> <span class="kg-badge kg-badge--container">容器 FS</span>
> Snapshotter · 选驱动 · 性能与兼容

容器运行时的**存储驱动（Storage Driver）**决定镜像如何存、容器如何写入。Docker、containerd、Kubernetes 都使用相同的逻辑：基于一个**快照器（Snapshotter）**在文件系统层之上做 COW。

## 1. 主流存储驱动

| Driver | 后端 | 平台 | 推荐度 |
|--------|------|------|--------|
| **overlay2** | OverlayFS | Linux | **首选** |
| **fuse-overlayfs** | FUSE OverlayFS | 不支持 overlay 的 Linux | rootless 用 |
| **devicemapper** | LVM thin pool | CentOS/RHEL 7 | 历史 |
| **btrfs** | Btrfs subvolume | OpenShift / SUSE | 中等 |
| **zfs** | ZFS | Ubuntu 22+ | 备选 |

**当前事实标准**：overlay2（Linux 内核 ≥ 5.11 时）。

## 2. overlay2 的优势

- **内核原生**：性能最佳
- **简单**：无需额外 daemon / 配置
- **空间效率**：分层去重（hash 内容寻址）
- **社区认可**：Docker / containerd / Podman 都用

```bash
# Docker 选 overlay2
# /etc/docker/daemon.json
{
  "storage-driver": "overlay2"
}

# containerd 选 overlayfs
# /etc/containerd/config.toml
[plugins."io.containerd.snapshotter.v1.overlayfs"]
  no_unix_acl = true
```

## 3. Snapshotter 架构（containerd 为例）

```
Application (K8s Pod)
        │
        ▼
containerd (CRI Plugin)
        │
        ▼
Snapshotter (overlayfs)
        │
        ▼
    OverlayFS mount
        │
   ┌────┴─────┐
   ▼          ▼
Image Layer  Image Layer
(ro)         (ro)
   │          │
   └────┬─────┘
        ▼
Container Upper Layer (rw)
```

每个容器 = 1 个 mount 命名空间，根目录是 overlay mount：

- **lower**：镜像层（只读）
- **upper**：容器写入层
- **work**：COW 临时区

## 4. 选择驱动的判断

### 4.1 检查 Linux 内核

```bash
uname -r
# 5.11+ 推荐 overlay2
# 4.x 推荐 overlay2（用 metacopy=0）
# 3.x 老内核用 fuse-overlayfs
```

### 4.2 写密集场景

overlay2 第一次写要 copy-up → 对**大量小文件首次写入**不友好。

对策：

- 用 tmpfs 做 upper（仅 RAM）
- 用 buildkit 缓存层
- 把 volume 挂出来（不走 image layer）

### 4.3 嵌套容器

CI runner / DIND（Docker in Docker）→ overlayfs 套 overlayfs 会出"不兼容"问题。

解决：

- 用 **vfs** 存储驱动（性能差但最通用）
- 或用 fuse-overlayfs
- 或用 kernel ≥ 5.13 支持嵌套

## 5. 实战：Docker 配置 overlay2

```bash
# 1. 准备文件系统（推荐 xfs）
mkfs.xfs -L docker /dev/sdb
mkdir -p /var/lib/docker
mount /dev/sdb /var/lib/docker

# 2. 配置 daemon
cat > /etc/docker/daemon.json <<EOF
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
EOF

# 3. 重启
systemctl restart docker

# 4. 验证
docker info | grep -i storage
docker system df
```

## 6. 实战：containerd 配置 overlayfs

```toml
# /etc/containerd/config.toml
version = 2

[plugins]
  [plugins."io.containerd.snapshotter.v1.overlayfs"]
    no_unix_acl = true
    remap_uids = ""       # rootless 用
    remap_gids = ""
    slow_chown = false

[plugins."io.containerd.grpc.v1.cri".containerd]
  snapshotter = "overlayfs"
```

```bash
systemctl restart containerd
```

## 7. Rootless 模式

无 root 权限跑容器（安全）：

```bash
# 安装 rootless 工具
apt install -y dockerd-rootless-setuptool

# 启动
dockerd-rootless-setuptool.sh install

# 用 fuse-overlayfs 而非 overlay2
cat > ~/.config/docker/daemon.json <<EOF
{
  "storage-driver": "fuse-overlayfs"
}
EOF
```

Rootless 模式只能用 fuse-overlayfs / vfs（因 overlay2 需要 root 挂载）。

## 8. 实战：快照迁移

把 Docker 容器导出 → 导入到其他机器：

```bash
# 1. 导出
docker save myimage:tag -o myimage.tar

# 2. 导入（自动识别）
docker load -i myimage.tar

# 3. 用 buildkit 输出 OCI layout（推荐）
buildctl build --output type=oci,dest=./oci .
oras push myreg.example.com/myapp:v1 ./oci:application/vnd.oci.image.index.v1+json
```

## 9. 性能与监控

```bash
# 看层大小
docker history myimage:tag

# 看磁盘占用
docker system df

# 看存储驱动
docker info | grep -A2 Storage

# 监控 IO
iostat -x 1   # 看底层磁盘
```

Prometheus 指标：

```yaml
# cadvisor 自动收集容器 IO
- job_name: cadvisor
  static_configs:
    - targets: ['cadvisor:8080']
```

## 10. 常见错误

### 10.1 "backing filesystem is unsupported"

```text
ERRO[0000] 'overlay' is not supported over this filesystem.
```

原因：

- 文件系统不是 ext4 / xfs / btrfs
- 用了 overlayfs 套 overlayfs
- 内核 < 3.18

解决：换 xfs / ext4 文件系统 + 升内核。

### 10.2 "no space left on device"

```bash
docker system prune -a     # 清无用镜像和容器
docker volume prune         # 清无用卷
```

### 10.3 "layer does not exist"

镜像层被破坏 → 重新 pull：

```bash
docker pull myimage:tag --all-tags=true
```

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| overlay2 是事实标准 | "overlay2=默认" |
| 内核 5.11+ 才完全发挥 | "5.11=佳" |
| 写密集用 tmpfs upper | "tmpfs=高写" |
| Rootless 用 fuse-overlayfs | "rootless=fuse" |
| 嵌套容器用 vfs | "嵌套=vfs" |

## 参考

- Docker 存储驱动文档
- containerd Snapshotter 文档
- rootlesscontainer 文档