---
title: Docker 源码导读
---

# Docker 源码导读

**Docker 80% Go 写**——理解 Docker = 理解 Go 在系统编程中的应用。

## 一句话总结

> **Docker = containerd + runc + daemon + CLI**。**Go 优势：静态二进制 + goroutine 高并发 + 跨平台编译**。

---

## 一、Docker 架构全景

```
┌─────────────────┐
│  docker CLI     │  ← 用户输入
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│  dockerd daemon │  ← 后台进程
└────────┬────────┘
         │ gRPC
         ▼
┌─────────────────┐
│  containerd     │  ← 容器 runtime 抽象
└────────┬────────┘
         │ OCI spec
         ▼
┌─────────────────┐
│  runc           │  ← 实际 namespace/cgroup 操作
└─────────────────┘
```

**Docker 现在是上层**，底层是 containerd + runc，都是 Go 写。

## 二、源码结构

```bash
git clone https://github.com/moby/moby
cd moby
ls cmd/          # CLI / daemon 入口
ls daemon/       # 后台逻辑
ls api/          # REST API
ls container/    # 容器管理
ls image/        # 镜像
ls libcontainer/ # 早期 cgroup/namespace（已抽到 runc）
```

**关键 Go 包**：
- `daemon/graphdriver/`：镜像层存储（aufs/overlay2）
- `daemon/execdriver/`：执行驱动
- `daemon/network/`：网络（bridge/overlay）
- `pkg/archive/`：tar 压缩/解压

## 三、镜像分层

```go
// layer 注册
type layer struct {
    cacheID  string
    diffID   digest.Digest
    size     int64
    parent   *layer
    children map[*layer]struct{}
}

// roLayer 不可变，chainID = 所有 diffID 拼接的 sha256
type roLayer struct {
    *layer
    chainID digest.Digest
}

// graph driver：实际存储
type Driver interface {
    Create(id, parent string) error
    Get(id, mountLabel string) (containerfs.ContainerFS, error)
    Put(id string) error
    Remove(id string) error
    Diff(id string) (io.ReadCloser, error)
    ApplyDiff(id string, diff io.Reader) (int64, error)
}
```

**overlay2 驱动**：
- `/var/lib/docker/overlay2/<id>/diff`：可读可写层
- `/var/lib/docker/overlay2/<id>/merged`：联合挂载点
- `/var/lib/docker/overlay2/<id>/work`：OverlayFS 内部

## 四、Namespace + Cgroup 隔离

```go
import "github.com/opencontainers/runc/libcontainer"

// 创建 namespace
ns := []syscall.Cloneflag{
    syscall.CLONE_NEWNS,    // mount
    syscall.CLONE_NEWPID,   // PID
    syscall.CLONE_NEWNET,   // network
    syscall.CLONE_NEWUTS,   // hostname
    syscall.CLONE_NEWIPC,   // IPC
    syscall.CLONE_NEWUSER,  // UID/GID
}

// Cgroup 限制
cgroup := &configs.Cgroup{
    Name: "docker-abc",
    Resources: &configs.Resources{
        MemorySwappiness: nil,
        MemoryLimit:      func() int64 { return 512 * 1024 * 1024 },  // 512MB
        CpuShares:        func() uint64 { return 1024 },
        CpuQuota:         func() int64 { return 100000 },  // 100ms per 100ms
    },
}
```

**Cgroup v2 vs v1**：v2 是 unified hierarchy，K8s 1.25+ 全面支持。

## 五、Go 的协程在 Docker 中的应用

```go
// dockerd 用 goroutine 管理 container lifecycle
func (daemon *Daemon) containerStart(...) {
    go func() {
        if err := daemon.containerd.Start(context, ...); err != nil {
            errs <- err
        }
    }()
    select {
    case err := <-errs:
        return err
    case <-time.After(10 * time.Second):
        return errors.New("container start timeout")
    }
}

// 一个 dockerd 跑 10000+ 容器，10w+ goroutine
```

**Go 优势**：相比 C，goroutine 让 dockerd 能同时管海量容器。

## 六、containerd 源码导读

```bash
git clone https://github.com/containerd/containerd
ls cmd/ctr/       # containerd CLI
ls cmd/containerd/  # daemon 入口
ls services/      # 内部服务
ls core/          # 核心抽象
```

**关键概念**：
- **Content**：OCI blob 存储
- **Image**：不可变镜像
- **Snapshot**：文件系统快照（overlayfs/native/btrfs）
- **Task**：运行中的容器
- **Lease**：资源租约

## 七、OCI Spec

```json
{
  "ociVersion": "1.0.2",
  "process": {
    "user": { "uid": 0, "gid": 0 },
    "args": ["/bin/sh"],
    "env": ["PATH=/usr/local/bin"],
    "cwd": "/",
    "rlimits": [{ "type": "RLIMIT_NOFILE", "hard": 1024, "soft": 1024 }]
  },
  "root": { "path": "rootfs" },
  "hostname": "mycontainer",
  "mounts": [
    { "destination": "/proc", "type": "proc", "source": "proc" }
  ],
  "linux": {
    "namespaces": [
      { "type": "pid" }, { "type": "network" }, { "type": "ipc" }
    ],
    "resources": {
      "memory": { "limit": 536870912 },
      "cpu": { "shares": 1024 }
    }
  }
}
```

runc 接受 OCI spec JSON，启动容器。

## 八、Docker BuildKit

**新一代构建器**：

```go
// BuildKit 用 LLB (Low-Level Builder) 表示构建图
llb.Image("golang:1.22").
    Run(llb.Shlex("go build -o /out/myapp .")).
    Run(llb.Shlex("cp /out/myapp /output/"))

// 并行执行 + 缓存复用
```

**优势**：
- 并行执行步骤
- 精确缓存（按文件内容 hash）
- 不需要 dockerd（docker buildx 远程构建）
- 支持 rootless

## 九、Go 1.11+ Modules + Vendor

Docker 早期用 vendor，2020 年后转 Go modules：

```bash
go mod init github.com/moby/moby
go mod tidy
go mod vendor
```

## 关联章节

- **04-cloud-native/kubernetes-internals**：K8s 调度
- **04-cloud-native/cncf-ecosystem**：CNCF 全景
- **04-cloud-native/etcd-internals**：etcd Raft

## 一句话总结

> **Docker 源码 = containerd + runc + daemon**。**Go 的 namespace/cgroup 抽象让容器化变简单**。


<!-- auto-enrich:do-not-edit -->

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

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
