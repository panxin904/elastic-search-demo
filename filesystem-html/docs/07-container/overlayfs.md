---
title: OverlayFS
---

# OverlayFS — 联合文件系统的标准实现

> <span class="kg-badge kg-badge--container">容器 FS</span>
> COW · 写时复制 · 容器镜像基础

OverlayFS（Overlay File System）是 Linux 内核的**联合挂载（Union Mount）**实现。它把两个目录（lowerdir + upperdir）合并为一个视图，对上层透明。Docker / containerd / Kubernetes 的容器镜像存储几乎全部基于它。

## 1. OverlayFS 概念

```
┌─────────────────────────────────────────────┐
│           Merged View (用户视角)            │
└────────────────┬────────────────────────────┘
                 │ 联合挂载
┌─────────────┐ ┌──────────┐ ┌──────────────┐
│  Upperdir   │ │ Lowerdir │ │ Workdir      │
│  (可写层)   │ │ (只读层) │ │ (内部工作)   │
│  /upper    │ │ /lower   │ │ /work        │
└─────────────┘ └──────────┘ └──────────────┘
```

- **lowerdir**：只读层（多个，堆叠），即镜像层
- **upperdir**：可写层（一个），容器运行时写入这里
- **workdir**：overlay 内部用来处理 copy-up 的临时区
- **merged**：合并后的视图（挂载点）

## 2. 文件系统四类操作

| 操作 | 含义 |
|------|------|
| **Copy-up** | lower 中文件被读 → 复制到 upper，再修改 |
| **Whiteout** | 在 upper 创建 `.wh.<filename>` 隐藏 lower 的同名文件 |
| **Opaque dir** | 在 upper 创建 `.wh..wh..opq` 隐藏 lower 的整个子目录 |
| **Rename** | rename 操作 atomic 在 upper 完成 |

## 3. 内核挂载示例

```bash
mkdir -p /tmp/overlay/{lower,upper,work,merged}

# 准备 lower 层
echo "Hello from lower" > /tmp/overlay/lower/file.txt
echo "old" > /tmp/overlay/lower/old.txt

# upper 初始为空
mount -t overlay overlay \
    -o lowerdir=/tmp/overlay/lower,upperdir=/tmp/overlay/upper,workdir=/tmp/overlay/work \
    /tmp/overlay/merged

# 看效果
ls /tmp/overlay/merged
cat /tmp/overlay/merged/file.txt
```

```bash
# 修改 merged 中的文件
echo "modified" > /tmp/overlay/merged/file.txt

# 查看 upper 出现的内容（这就是 copy-up）
ls /tmp/overlay/upper

# 删除 lower 中的文件
rm /tmp/overlay/merged/old.txt
# upper 里出现 .wh.old.txt（whiteout）
```

## 4. OverlayFS 与容器镜像

```
镜像层（lowerdir，ro）
├─ sha256:abc (基础镜像层)
├─ sha256:def (apt-get install python)
└─ sha256:xyz (COPY ./app)

容器层（upperdir，rw）  ← 每个容器独立
```

Docker pull 一个 4 层镜像 → lowerdir 有 4 个目录；每个容器启动 → upperdir 一个独立目录。

## 5. OverlayFS 性能特性

### 5.1 优点

- **零拷贝启动**：N 个容器共享同一镜像层，磁盘占零
- **分层缓存**：Docker 镜像复用极好
- **快速启动**：不用复制整个 FS

### 5.2 缺点

- **Copy-up 第一次写**：lower 文件第一次写要先复制到 upper，延迟增加
- **文件 inode 变化**：copy-up 后 inode 改变，对 inotify 不友好
- **大量小文件时性能下降**：N 个小文件 copy-up = N 次额外 IO
- **overlay 层数有限**：内核参数 `default max lower dirs` 默认是 500

```bash
# 看内核支持的层数
cat /sys/module/overlay/parameters/metacopy
# 建议内核 5.11+
```

## 6. 与其他 FS 对比

| FS | 联合挂载 | 生产用 | 备注 |
|----|----------|--------|------|
| **OverlayFS** | ✅ | **首选** | Linux 内核原生 |
| AUFS | ✅ | 历史 | Docker 早期用过，Ubuntu-only |
| devicemapper | ❌ | 历史 | Red Hat 用过 |
| btrfs | ✅ | 部分 | OpenShift 默认 |
| zfs | ✅ | 部分 | illumos/FreeBSD |

**OverlayFS 是当前事实标准**——其他基本退役。

## 7. 内核版本差异

| 内核 | 关键特性 |
|------|---------|
| 3.18 | 初始支持 |
| 4.7 | 多 lowerdir |
| 5.11 | **metacopy**（copy-up 不复制文件内容，只复制 inode 元数据） |
| 5.15+ | volatile mounts（容器场景用） |

**生产推荐**：Linux 内核 ≥ 5.11。

## 8. 关键参数与排查

```bash
# 看 overlay 挂载
mount | grep overlay
cat /proc/mounts | grep overlay

# 内核参数
/sys/module/overlay/parameters/
  metacopy        # ON：copy-up 只复制元数据（快）
  redirect_dir    # ON：rename 跨层优化
  index           # ON：使用 index dir（更快查找）
```

```bash
# 看容器占用
du -sh /var/lib/docker/overlay2/

# 看层关系
docker image inspect nginx:alpine
# 输出 RootFS.Layers 数组
```

## 9. 与 SELinux / AppArmor

容器场景的 OverlayFS 经常需要打 SELinux context：

```bash
# Docker 启动容器时自动做 chcon
docker run --security-opt label=disable nginx
# 或
mount -t overlay overlay -o lowerdir=...,upperdir=...,workdir=...,context="system_u:object_r:container_file_t:s0"
```

AppArmor profile 也要确保允许 overlay 路径读写。

## 10. 实战：性能调优

### 10.1 用 tmpfs 做 upper

```bash
mount -t tmpfs tmpfs /var/lib/docker/overlay2 -o size=10G
# 容器写操作走内存（适合只读容器 + 输出走 volume）
```

**风险**：tmpfs 容量耗尽 = 容器写失败。

### 10.2 用独立 SSD 当 upper

大文件写场景，把 upper 放 SSD，lower 放 HDD：

```bash
mount -t overlay overlay \
    -o lowerdir=/hdd/lower,upperdir=/ssd/upper,workdir=/ssd/work \
    /merged
```

### 10.3 内核参数优化

```bash
# /etc/sysctl.conf
fs.overlay-max-layers=512    # 默认 128 / 内核 5.x 后更高

# /etc/modprobe.d/overlay.conf
options overlay metacopy=1 redirect_dir=1 index=1
```

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| OverlayFS = 联合挂载 | "Overlay=union mount" |
| 镜像 = lowerdir | "镜像=只读层" |
| 容器 = upperdir | "容器=可写层" |
| Copy-up 是性能瓶颈 | "首次写要复制" |
| 内核 5.11+ 有 metacopy | "5.11=元数据优化" |

## 参考

- Linux 内核 OverlayFS 文档
- Docker overlay2 驱动文档
- AUFS 历史与 OverlayFS 起源