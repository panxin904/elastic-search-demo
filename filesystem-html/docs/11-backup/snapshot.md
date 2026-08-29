---
title: 快照与备份
date: 2026-08-15  # date-auto-injected
---

# 快照与备份 — 数据保护的两大武器

> <span class="kg-badge kg-badge--backup">备份快照</span>
> 快照 = 瞬时副本 · 备份 = 异地持久 · 组合最佳

快照（Snapshot）与备份（Backup）是不同的概念，本质差别：

- **快照**：在同一存储上的"瞬时副本"，几乎零延迟恢复
- **备份**：把数据复制到独立位置，跨故障、跨地域

## 1. 快照 vs 备份

| 维度 | 快照 | 备份 |
|------|------|------|
| 存哪 | 同存储 | 异地 / 异介质 |
| 速度 | **秒级** | **小时级** |
| 空间开销 | 增量（低） | 全量（高） |
| 抗硬件故障 | ❌ | ✅ |
| 抗勒索软件 | ❌ | ✅ |
| 频率 | 高（分钟级） | 低（天级） |
| 跨集群恢复 | ❌ | ✅ |

## 2. 文件系统级快照

### 2.1 LVM Snapshot

```bash
# 创建快照（COW）
lvcreate -L 10G -s -n data-snap /dev/vg0/data

# 挂载
mkdir /mnt/snap
mount -o ro /dev/vg0/data-snap /mnt/snap

# 用完删除
umount /mnt/snap
lvremove /dev/vg0/data-snap
```

**限制**：快照本身也在 VG 里，**共享故障域**。

### 2.2 ZFS Snapshot

```bash
# 创建快照（瞬间）
zfs snapshot tank/data@backup-20260101

# 看
zfs list -t snapshot

# 克隆（可写）
zfs clone tank/data@backup-20260101 tank/data-clone

# 回滚
zfs rollback tank/data@backup-20260101

# 删
zfs destroy tank/data@backup-20260101
```

ZFS snapshot 是**真正原子**且**几乎零开销**。

### 2.3 Btrfs Snapshot

```bash
# 创建快照（COW）
btrfs subvolume snapshot /mnt/data /mnt/data/.snapshots/20260101

# 列表
btrfs subvolume list /mnt/data

# 删除
btrfs subvolume delete /mnt/data/.snapshots/20260101
```

### 2.4 ext4 / XFS 快照

ext4 和 XFS **没有原生快照**。要快照必须用：

- LVM（块设备级）
- ZFS / Btrfs 子卷
- 厂商方案（NetApp、EMC）

## 3. NAS / SAN 厂商快照

- NetApp Snapshot™：秒级快照，差量去重
- Dell EMC TimeFinder：SAN 复制
- Huawei OceanStor HyperClone

**优点**：企业级，快照效率高。
**缺点**：绑定厂商，复杂。

## 4. 数据库快照

### 4.1 MySQL

```sql
-- 1. 全量快照（mysqldump）
mysqldump --single-transaction --master-data=2 \
    --all-databases > /backup/full.sql

-- 2. 一致性快照（FLUSH TABLES WITH READ LOCK + LVM）
FLUSH TABLES WITH READ LOCK;
lvcreate -L 10G -s -n data-snap /dev/vg0/data
UNLOCK TABLES;

-- 3. Percona XtraBackup（热备份）
xtrabackup --backup --target-dir=/backup/inc1/
```

### 4.2 PostgreSQL

```bash
# 1. pg_basebackup（全量）
pg_basebackup -D /backup/pgbase -Fp -Xs -P

# 2. PITR（基于 WAL 的增量恢复）
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
restore_command = 'cp /backup/wal/%f %p'
```

## 5. 实战：完整快照策略

```text
[ ] 每小时 ZFS 快照（保留 24）
[ ] 每天增量快照（保留 7）
[ ] 每周全量快照（保留 4）
[ ] 每月异地备份（保留 12）
[ ] 定期演练恢复（每月 1 次）
```

## 6. 快照的限制

### 6.1 写入放大

COW 快照第一次写额外 IO → 大写场景性能降。

### 6.2 快照链深度

无限链 = 快照恢复慢 → 建议限制在 7 层内。

### 6.3 跨存储故障

**快照 ≠ 备份**。存储损坏 = 快照也丢。必须异地。

## 7. 实战：K8s 快照

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: db-snap-20260101
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: db-data
```

CSI Driver 创建快照（EBS Snapshot / Ceph RBD snap / ZFS snapshot 等）。

## 8. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 快照 = 同存储瞬时 | "快照=瞬时" |
| 备份 = 异地持久 | "备份=异地" |
| ZFS 快照是真原子 | "ZFS=真快照" |
| 快照链不超过 7 | "链≤7" |
| 两者都要有 | "近远结合" |

## 参考

- ZFS 文档：zfs(8) / zfs-snapshot(8)
- LVM 手册
- PostgreSQL 备份文档
- MySQL 备份最佳实践


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
