---
title: containerd
---

# containerd — 容器运行时的工业标准

> <span class="kg-badge kg-badge--container">容器 FS</span>
> K8s 默认 CRI · CNCF 毕业项目 · 高性能

containerd 是 Docker 公司开源的容器运行时（2015 年），现由 CNCF 管理，是 **Kubernetes 1.0+ 的默认 CRI 运行时**。它从 Docker daemon 中剥离，专注容器生命周期管理。

## 1. containerd 是什么

| 角色 | 含义 |
|------|------|
| 容器运行时 | 创建 / 启动 / 停止容器 |
| 镜像管理 | pull / push / tag |
| 存储管理 | overlay / snapshotter |
| 网络管理 | CNI 插件 |

**和 Docker 关系**：

```
Docker = containerd + dockerd(CLI/UI/buildx) + libcontainer
K8s CRI = containerd + CRI 插件（无 dockerd）
```

## 2. containerd 架构

```
┌──────────────────────────────────────┐
│        Client (ctr / nerdctl)         │
└────────────────┬─────────────────────┘
                 │ gRPC
┌────────────────▼─────────────────────┐
│  containerd daemon (containerd)      │
│  - Supervisor                        │
│  - Scheduler                         │
└──┬───────────┬──────────┬───────────┘
   │           │          │
   ▼           ▼          ▼
┌──────┐  ┌────────┐  ┌─────────────┐
│Image │  │Runtime │  │ Snapshotter │
│Service│ │service │  │ (overlayfs) │
└──────┘  └────┬───┘  └─────────────┘
              │
              ▼
        ┌────────────┐
        │ runc       │
        │ (OCI)      │
        └────────────┘
```

## 3. 与 Docker 关键差异

| 维度 | Docker | containerd |
|------|--------|-----------|
| CLI | docker | ctr / nerdctl |
| 镜像构建 | docker build / buildx | img / buildkit |
| 存储 | /var/lib/docker | /var/lib/containerd |
| 性能 | 略差（多封装一层） | **优** |
| K8s 集成 | dockershim（已弃用） | CRI 原生 |
| 大规模生产 | 中等 | **优** |

**生产推荐**：K8s 节点用 containerd（或 CRI-O）；开发环境可以用 Docker Desktop。

## 4. 安装

### 4.1 简易安装

```bash
# Ubuntu
apt-get update
apt-get install -y containerd

# CentOS
yum install -y containerd.io
```

### 4.2 K8s 节点（推荐 kubeadm）

```bash
# 用 containerd 作为 CRI
containerd config default | tee /etc/containerd/config.toml

# 修改配置
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sed -i 's|sandbox_image = "k8s.gcr.io/pause:3.8"|sandbox_image = "registry.k8s.io/pause:3.9"|' \
    /etc/containerd/config.toml

systemctl restart containerd
```

```bash
# kubeadm 初始化时指定
kubeadm init --cri-socket unix:///run/containerd/containerd.sock
```

## 5. 配置文件 config.toml

```toml
version = 2

[plugins]
  [plugins."io.containerd.snapshotter.v1.overlayfs"]
    no_unix_acl = true

[plugins."io.containerd.grpc.v1.cri"]
  sandbox_image = "registry.k8s.io/pause:3.9"
  disable_apparmor = false
  disable_cgroup = false

  [plugins."io.containerd.grpc.v1.cri".containerd]
    snapshotter = "overlayfs"
    default_runtime_name = "runc"

    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
        runtime_type = "io.containerd.runc.v2"
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
          SystemdCgroup = true

    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
      runtime_type = "io.containerd.runsc.v1"

  [plugins."io.containerd.grpc.v1.cri".cni]
    bin_dir = "/opt/cni/bin"
    conf_dir = "/etc/cni/net.d"
    max_pool_size = 5
```

## 6. 实用命令（ctr）

```bash
# 镜像列表
ctr images ls

# 拉镜像
ctr images pull docker.io/library/nginx:alpine

# 标签
ctr images tag docker.io/library/nginx:alpine nginx:latest

# 推镜像
ctr images push nginx:latest

# 容器列表
ctr containers ls

# 任务（运行实例）列表
ctr tasks ls

# 运行一个临时容器
ctr run -d docker.io/library/alpine:latest myalpine /bin/sh

# 进 shell
ctr task exec --exec-id sh myalpine /bin/sh

# nsenter 进容器
nsenter -t <PID> -m -u -i -n -p -- /bin/sh

# 看存储占用
ctr snapshots ls
```

## 7. 实用命令（nerdctl，Docker 兼容）

nerdctl 是 containerd 的 docker 兼容 CLI：

```bash
# 安装
wget https://github.com/containerd/nerdctl/releases/download/v2.0.4/nerdctl-2.0.4-linux-amd64.tar.gz
tar -xzf nerdctl-2.0.4-linux-amd64.tar.gz -C /usr/local/bin

# 用法几乎和 docker 一样
nerdctl run -d -p 80:80 nginx:alpine
nerdctl ps
nerdctl images
nerdctl build -t myapp .
nerdctl compose up    # 兼容 docker-compose
```

## 8. 镜像构建（img 或 BuildKit）

```bash
# 用 img（纯 Go 实现）
img build -t myapp:latest .

# 用 BuildKit standalone
buildctl build \
    --frontend dockerfile.v0 \
    --local context=. \
    --local dockerfile=. \
    --output type=image,name=myapp:latest
```

## 9. 与 Docker Hub 的互通

containerd 默认能识别 `docker.io` 的镜像，但配置私有 Registry 需要：

```toml
[plugins."io.containerd.grpc.v1.cri".registry.mirrors]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
    endpoint = ["https://registry-1.docker.io"]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."myreg.example.com"]
    endpoint = ["https://myreg.example.com"]
```

私密凭证：

```bash
mkdir -p /etc/containerd/certs.d/myreg.example.com
cat > /etc/containerd/certs.d/myreg.example.com/hosts.toml <<EOF
server = "https://myreg.example.com"
[host."https://myreg.example.com"]
  capabilities = ["pull", "resolve"]
  skip_verify = false
EOF
```

## 10. 性能调优

### 10.1 启用 overlayfs metacopy

```toml
[plugins."io.containerd.snapshotter.v1.overlayfs"]
  no_unix_acl = true
```

需要内核 5.11+。

### 10.2 SSD 选择

容器 metadata 在 `/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/`，放 SSD。

### 10.3 大并发场景

```toml
[grpc]
  max_concurrent_streams = 100
```

### 10.4 cgroup 驱动

```toml
SystemdCgroup = true   # K8s 推荐
# 而不是 cgroupfs
```

## 11. 故障排查

```bash
# 看 containerd 日志
journalctl -u containerd -f

# 看具体错误
ctr containers info <container-id>
ctr tasks ls -q | xargs -I {} ctr tasks info {}

# 清理无用镜像
ctr images rm $(ctr images ls -q)
ctr containers rm $(ctr containers ls -q)
ctr tasks rm $(ctr tasks ls -q)
```

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| containerd = K8s 默认 CRI | "containerd=K8s 默认" |
| 比 docker 性能优 | "containerd=快" |
| 工具：ctr / nerdctl / buildctl | "三件套" |
| 配置核心：SystemdCgroup | "Cgroup 配 Systemd" |
| 镜像走 overlayfs snapshotter | "存储=overlay" |

## 参考

- containerd 文档：<https://containerd.io/docs/
- CRI 规范：<https://github.com/containerd/containerd/tree/main/pkg/cri
- nerdctl：<https://github.com/containerd/nerdctl>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
