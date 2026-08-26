---
title: du / df
---

# du / df — 磁盘空间分析

> <span class="kg-badge kg-badge--tools">工具集</span>
> 目录占用 · 文件系统空闲 · 实时排查

du 与 df 是排查"磁盘满了"的左膀右臂：

- **df**：文件系统级别的"剩余空间"
- **du**：目录级别的"占用分布"

## 1. df 基础

```bash
# 默认（KB 为单位）
df
df /

# 人类可读
df -h

# 看 inodes
df -i

# 看具体文件系统类型
df -Th
```

输出：

```text
Filesystem     Type   Size  Used  Avail  Use%  Mounted on
/dev/sda1      ext4   50G   45G   5G     90%   /
tmpfs          tmpfs  16G   0     16G    0%    /dev/shm
```

**关键字段**：

| 字段 | 含义 |
|------|------|
| Size | 文件系统总大小 |
| Used | 已用 |
| Avail | 可用（df 保留 ~5% 给 root） |
| Use% | 百分比 |
| Mounted on | 挂载点 |

## 2. df 与 reserved blocks

ext4 默认**保留 5% 给 root**：

```bash
# 看预留
tune2fs -l /dev/sda1 | grep "Reserved block count"

# 改预留 1%
tune2fs -m 1 /dev/sda1
```

`Use%` 显示 100% 但 du 不见大文件 → 可能就是 reserved 占的。

## 3. du 基础

```bash
# 目录总大小
du -sh /var/log

# 多级目录
du -h /var/log
# 输出每个子目录的大小

# 按大小排序
du -h /var/log | sort -h
```

## 4. du 与 df 不一致

| 场景 | 解释 |
|------|------|
| df 100% 但 du 不见大文件 | **deleted 但仍打开的文件**占空间 |
| df 显示 100% 但 du 还有空间 | 预留块（root reserve） |
| 容器场景 df 看到的是 overlay upper | du 看不到所有内容 |

排查 deleted 文件：

```bash
lsof | grep deleted
# 杀掉进程或重启
```

## 5. du 实战技巧

### 5.1 找最大目录

```bash
du -h --max-depth=1 /var | sort -hr | head -20
```

### 5.2 排除特定目录

```bash
du -h --exclude="node_modules" --exclude=".git" /project
```

### 5.3 多线程 du（ncdu）

```bash
apt install -y ncdu
ncdu /var
```

ncdu 是交互式 du，方向键浏览。

### 5.4 找大文件

```bash
find / -type f -size +100M -exec du -h {} +
```

## 6. 文件系统特殊场景

### 6.1 XFS

```bash
df -h /xfs
xfs_info /dev/sdb
xfs_growfs /mountpoint    # 在线扩
```

### 6.2 Btrfs

```bash
df -h /btrfs
btrfs filesystem df /btrfs    # 看 RAID 分布
btrfs filesystem du /btrfs    # 看占用
```

### 6.3 ZFS

```bash
df -h /zfs
zpool list
zpool iostat
```

### 6.4 NFS

```bash
df -h /nfs
nfsstat -c    # 看 NFS 客户端统计
```

## 7. 监控告警

```bash
# 看 inode 占用
df -i /var

# 看 inode 使用率
df -i /var | awk '{print $5}' | tail -n 1

# 告警脚本
#!/bin/bash
USE=$(df -h / | awk 'NR==2{print $5}' | tr -d '%')
if [ "$USE" -gt 80 ]; then
    echo "WARNING: disk usage ${USE}%"
fi
```

## 8. 容器场景

```bash
# 容器内看磁盘
docker exec my-container df -h

# 看 overlay 上层
du -sh /var/lib/docker/overlay2/<container-id>/diff

# 用 docker system df
docker system df
docker system df -v    # 详细
```

## 9. 实战：磁盘满了紧急排查

```bash
# 1. 看整体
df -h

# 2. 找大目录
du -h --max-depth=1 / | sort -hr | head -10

# 3. 看 deleted 文件
lsof | grep deleted | sort -k7 -h | tail -20

# 4. 看最大文件
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -h

# 5. 看 inode
df -i

# 6. 看 docker / k8s 容器
docker system df -v
kubectl get pvc -A
```

## 10. 实战：清理 Docker

```bash
# 全部清理
docker system prune -a

# 只清理 dangling
docker image prune
docker container prune
docker volume prune
docker network prune
```

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| df = 文件系统 | "df=系统级" |
| du = 目录 | "du=目录级" |
| df 100% 看预留 | "预留=5%" |
| du 找不到大文件看 lsof | "deleted 进程" |
| ncdu 是 du 升级版 | "ncdu=交互" |

## 参考

- df / du man 手册
- tune2fs 文档
- ncdu 文档：<https://dev.yorhel.nl/ncdu


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
