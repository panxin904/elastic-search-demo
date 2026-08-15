---
title: 挂载与文件系统树
---

# 挂载与文件系统树

<span class="kg-badge kg-badge-basics">基础</span>

文件系统如何"接入"Linux 的目录树？挂载点的本质是什么？

## 什么是挂载

**mount** 是把一个文件系统（设备）关联到目录树某个节点的过程。Linux 所有 FS 共享一棵统一的目录树。

```bash
mount /dev/sdb1 /mnt/data
# /dev/sdb1 的根目录 → 接入到 /mnt/data
# 之后访问 /mnt/data 实际访问的是 /dev/sdb1 的根
```

## /etc/fstab 开机自动挂载

```bash
# <device>          <mountpoint>  <fstype>  <options>       <dump>  <pass>
UUID=abc-123       /              ext4      defaults        0       1
/dev/sdb1          /mnt/data      xfs       defaults,noatime 0      2
192.168.1.10:/share /mnt/nfs       nfs       defaults        0       0
tmpfs              /tmp           tmpfs     size=2G         0       0
```

- `defaults`：rw, suid, dev, exec, auto, nouser, async
- `noatime`：不更新访问时间（提升性能）
- `nodiratime`：不更新目录访问时间
- `nofail`：设备不存在时不报错（云盘场景）

## 挂载选项速查

```bash
mount -o <options> /dev/sdb1 /mnt/data
```

| 选项 | 作用 |
|------|------|
| `ro / rw` | 只读 / 读写 |
| `sync / async` | 同步 / 异步（默认 async） |
| `noatime` | 不更新 atime（性能优化） |
| `nodiratime` | 不更新目录 atime |
| `noexec` | 不允许执行二进制 |
| `nosuid` | 忽略 setuid bit |
| `nodev` | 不解析设备文件 |
| `relatime` | atime 仅在 mtime/ctime 更新后才更新（Linux 2.6.30+ 默认） |
| `discard` | 启用 TRIM（SSD） |
| `_netdev` | 等网络起来再挂（NFS 场景） |

## 现代挂载方式：systemd

```bash
# 看 mount 单元
systemctl list-units --type=mount

# fstab 自动转 mount 单元
systemctl daemon-reload

# 手动挂载
systemctl start mnt-data.mount
```

## mount 命令实战

```bash
# 查看所有挂载
mount
mount | column -t  # 美化输出

# 查看某个特定挂载
findmnt /mnt/data

# 只看某个类型的 FS
findmnt -t ext4,xfs

# 按来源看
findmnt -t nfs,cifs

# 重新挂载（修改选项不卸载）
mount -o remount,ro /mnt/data

# 挂载镜像
mount -o loop /tmp/disk.img /mnt/img

# 挂载 squashfs（只读压缩 FS）
mount -t squashfs /tmp/root.squashfs /mnt/squash

# 挂载 tmpfs（内存盘）
mount -t tmpfs -o size=512M tmpfs /tmp/ramdisk
```

## Bind Mount

```bash
# 把已挂载的目录再挂到别处（类似硬链接但对目录）
mount --bind /var/log /mnt/logs
mount -o bind,ro /etc /mnt/etc   # 只读 bind

# 也支持文件
mount --bind /etc/passwd /tmp/passwd
```

**用途**：
- 调试：把容器内 FS bind 到主机
- 权限：bind 只读后无法修改
- 容器：chroot + bind mount 模拟独立 FS

## /proc/mounts 解析

```bash
cat /proc/mounts
# rootfs / rootfs rw 0 0
# sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
# /dev/sda1 / ext4 rw,relatime 0 0
# tmpfs /run tmpfs rw,nosuid,nodev,size=... 0 0
# /dev/sdb1 /mnt/data xfs rw,relatime,attr2 0 0
```

格式：`device mountpoint fstype options dump pass`

## 案例：chroot + mount 模拟容器

```bash
# 创建一个简单的"chroot 监狱"
mkdir -p /opt/jail/{bin,lib,lib64}

# 拷贝必要的二进制
cp /bin/bash /opt/jail/bin/

# 拷贝依赖的动态库
ldd /bin/bash
# linux-vdso.so.1 (0x...)
# libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6
# ...
cp /lib/x86_64-linux-gnu/libc.so.6 /opt/jail/lib/

# bind mount /proc
mount --bind /proc /opt/jail/proc

# 进入
chroot /opt/jail /bin/bash
# 进了"监狱"，看不到外面的 FS
```

## mount namespace（容器核心）

```c
// 每个进程都有自己的 mount namespace
// unshare -m 创建一个新的 namespace
// 在新 namespace 里 mount 不影响其他进程
// 这就是 Docker 容器隔离的底层机制之一
```

## 常见问题

### 挂载失败：mount: unknown filesystem type 'xfs'

```bash
# 内核没编译 xfs 模块
modprobe xfs    # 加载
# 或重新编译内核
```

### 卸载失败：device is busy

```bash
# 有进程在用这个挂载点
lsof +D /mnt/data    # 找进程
fuser -mv /mnt/data  # 也行
# kill 后再 umount
umount /mnt/data

# 强制（不推荐）
umount -l /mnt/data   # lazy unmount
```

### 启动时挂载失败导致系统无法启动

```bash
# 编辑 /etc/fstab 时出错
# 启动时按 e 进入编辑，在 linux 行末尾加：
#    init=/bin/bash
# 然后 mount -o remount,rw /
# 修正 /etc/fstab
# exec /sbin/init 继续启动
```

## 关键 takeaway

| 概念 | 关键 |
|------|------|
| mount | 把 FS 接入目录树 |
| mount namespace | 容器隔离的基础 |
| fstab | 开机自动挂载配置 |
| bind mount | 把已挂载内容"再挂" |
| atime | 通常关闭（relatime 是好默认） |