---
title: FUSE
---

# FUSE — Filesystem in Userspace 用户态文件系统

> <span class="kg-badge kg-badge--tools">工具集</span>
> 用户态驱动 · 容器存储 · 灵活扩展

FUSE（Filesystem in Userspace）是 Linux 内核提供的一个**用户态文件系统框架**。它允许你**在用户进程**里实现一个完整文件系统，挂载到 VFS 上。**S3FS、GlusterFS、sshfs、JuiceFS、fuse-overlayfs** 等都用 FUSE。

## 1. FUSE 解决了什么问题

文件系统传统上在内核态实现：

- 写内核模块 = 难调试、崩溃影响全局、要 GPL
- 新文件系统开发门槛极高

FUSE 把"文件系统实现"挪到用户态：

```
┌──────────────────────────────────────┐
│        Application                   │
└──────────────┬───────────────────────┘
               │ syscall (open/read/write)
┌──────────────▼───────────────────────┐
│        Linux VFS                     │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│    FUSE kernel module                │
│    (libfuse 桥接)                    │
└──────────────┬───────────────────────┘
               │ 字符设备 / netlink
┌──────────────▼───────────────────────┐
│    User program (your FS logic)      │
│    - 实现 read / write / lookup      │
└──────────────────────────────────────┘
```

**好处**：

- 用户态开发，崩溃不影响内核
- 可用任何语言（C / Go / Python / Rust）
- 易部署（就是普通进程）

**代价**：性能略低于内核态（多一次上下文切换）。

## 2. libfuse 三版本

| 版本 | 编程语言 | 状态 |
|------|----------|------|
| libfuse 2 | C | 老 API |
| libfuse 3 | C | **当前推荐** |
| libfuse 4 | C | 实验 |

Go / Python / Rust 都有 bindings：

```go
import "github.com/hanwen/go-fuse/v2"

fs := gofs.NewFileSystem(...)   // 用户态 FS 实现
go fs.Serve(...)
```

```python
import fusepy

fusepy.main(MyFS(), mountpoint, foreground=True)
```

## 3. 实战：写一个最简 FUSE

```c
// hello-fs.c
#define FUSE_USE_VERSION 31
#include <fuse3/fuse.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

static const char *hello_path = "/hello";

static int hello_getattr(const char *path, struct stat *stbuf,
                         struct fuse_file_info *fi) {
    memset(stbuf, 0, sizeof(struct stat));
    if (strcmp(path, "/") == 0) {
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        return 0;
    }
    if (strcmp(path, hello_path) == 0) {
        stbuf->st_mode = S_IFREG | 0444;
        stbuf->st_nlink = 1;
        stbuf->st_size = strlen("Hello, FUSE!\n");
        return 0;
    }
    return -ENOENT;
}

static int hello_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
                         off_t offset, struct fuse_file_info *fi,
                         enum fuse_readdir_flags flags) {
    if (strcmp(path, "/") != 0) return -ENOENT;
    filler(buf, ".", NULL, 0, 0);
    filler(buf, "..", NULL, 0, 0);
    filler(buf, "hello", NULL, 0, 0);
    return 0;
}

static int hello_open(const char *path, struct fuse_file_info *fi) {
    if (strcmp(path, hello_path) != 0) return -ENOENT;
    return 0;
}

static int hello_read(const char *path, char *buf, size_t size, off_t offset,
                      struct fuse_file_info *fi) {
    if (strcmp(path, hello_path) != 0) return -ENOENT;
    const char *content = "Hello, FUSE!\n";
    size_t len = strlen(content);
    if (offset >= len) return 0;
    if (offset + size > len) size = len - offset;
    memcpy(buf, content + offset, size);
    return size;
}

static const struct fuse_operations hello_ops = {
    .getattr = hello_getattr,
    .readdir = hello_readdir,
    .open    = hello_open,
    .read    = hello_read,
};

int main(int argc, char **argv) {
    return fuse_main(argc, argv, &hello_ops, NULL);
}
```

编译并挂载：

```bash
gcc hello-fs.c -o hello-fs $(pkg-config --cflags --libs fuse3)
mkdir /tmp/hellomnt
./hello-fs /tmp/hellomnt -f

# 在另一个终端
ls /tmp/hellomnt
cat /tmp/hellomnt/hello
```

## 4. 主流 FUSE 项目

| 项目 | 用途 | 语言 |
|------|------|------|
| s3fs | S3 → 本地挂载 | C++ |
| goofys | S3（更轻量） | Go |
| sshfs | SSH → 本地 | C |
| rclone mount | 任意云盘 → 本地 | Go |
| JuiceFS | 元数据 + 对象存储 | Go |
| CephFS FUSE | CephFS → 本地 | C |
| GlusterFS FUSE | GlusterFS → 本地 | C |
| fuse-overlayfs | rootless 容器 | Go |
| mergerfs | 多盘合并 | C |
| bindfs | 权限重写挂载 | C |

## 5. 实战：s3fs 把 S3 bucket 当本地盘

```bash
# 1. 安装
apt install -y s3fs

# 2. 凭证（方式 1：passwd-s3fs 文件）
echo "AK:SK" > ~/.passwd-s3fs
chmod 600 ~/.passwd-s3fs

# 3. 挂载
mkdir /mnt/s3
s3fs mybucket /mnt/s3 \
    -o passwd_file=~/.passwd-s3fs \
    -o url=https://s3.amazonaws.com \
    -o use_path_request_style \
    -o allow_other

# 4. 像本地盘一样用
ls /mnt/s3
echo "test" > /mnt/s3/file.txt
```

## 6. 实战：JuiceFS / GlusterFS FUSE 客户端

```bash
# JuiceFS（前面章节有详）
juicefs mount -d redis://10.0.0.1:6379/1 /mnt/jfs

# GlusterFS
mount -t glusterfs server1:/gv0 /mnt/gv0
```

## 7. FUSE 性能优化

### 7.1 内核缓存

```bash
# 默认启用，FUSE 不主动穿透到内核缓存
# libfuse 3.0+ 启用 low-level 接口：write-back / write-through
```

### 7.2 big-writes / splice

```c
struct fuse_file_info fi;
fi->flags |= FUSE_DIRECT_IO;     // 直通（绕过 Page Cache）
// 或
fuse_set_signal_handlers(...);
```

### 7.3 io_uring 加速

```c
// libfuse 3.10+ 支持 io_uring
// fuse_session_mount() 加 FUSE_DEV_IOC_CLONE
```

## 8. FUSE 与容器

容器 rootless 模式：

```bash
# rootless 容器必须用 fuse-overlayfs（不能直接用 overlay2）
dockerd-rootless-setuptool.sh check
# 提示：
# - overlayfs 是 root-only
# - 用 fuse-overlayfs 替代
```

K8s CSI Driver 经常用 FUSE 客户端（JuiceFS、GlusterFS、CephFS）。

## 9. 调试 FUSE

```bash
# 1. 前台挂载看 log
./hello-fs /tmp/hellomnt -f -d

# 2. 用 strace 看 syscall
strace -f -e openat,read,write ls /tmp/hellomnt

# 3. 看 fuse 通信
strace -e trace=read,write -p $(pidof hello-fs)
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| FUSE = 用户态 FS | "FUSE=用户态驱动" |
| 性能略差 = 上下文切换 | "FUSE=慢一点" |
| libfuse 3 当前主流 | "libfuse3=现代" |
| 多语言 bindings | "C/Go/Py 都行" |
| 容器 rootless 用 fuse-overlayfs | "fuse=rootless" |

## 参考

- libfuse 文档：<https://github.com/libfuse/libfuse
- FUSE 内核文档：<https://www.kernel.org/doc/html/latest/filesystems/fuse.html
- 《Linux 文件系统内幕》- FUSE 章节


<!-- auto-enrich:do-not-edit -->

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
