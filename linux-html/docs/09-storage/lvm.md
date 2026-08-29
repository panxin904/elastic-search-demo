---
title: LVM 逻辑卷
---

# LVM 逻辑卷管理

> Logical Volume Manager：让磁盘管理**灵活**起来。

## 🤔 为什么用 LVM

传统分区：
- 分完就定死，改大小要搬家 / 重新分区
- 多块硬盘拼一个空间？只能 RAID

LVM：
- 动态扩缩容（在线）
- 多块硬盘 / 多分区合成一个大空间
- 快照（snapshot）
- 在线迁移数据

## 🧱 三大概念

```
物理卷 PV (Physical Volume)         - 物理硬盘 / 分区
  ↓ vgcreate
卷组 VG (Volume Group)               - 多个 PV 合成一个池
  ↓ lvcreate
逻辑卷 LV (Logical Volume)           - 在 VG 池里"分"出的一块虚拟磁盘
  ↓ mkfs
文件系统                              - ext4 / xfs / btrfs
```

例如：

```
   /dev/sda1   /dev/sdb1   /dev/sdc1     物理卷 PV
       ↓           ↓            ↓
       └───────────┼────────────┘
                   ↓ vgcreate
            ┌─────────────┐
            │   vg_data   │  卷组 VG
            └─────────────┘
                ↓ lvcreate
       ┌─────────┼─────────┐
       ↓         ↓         ↓
   lv_root   lv_home   lv_swap      逻辑卷 LV
       ↓         ↓         ↓
      ext4      xfs       swap       文件系统
```

## 🛠 LVM 实战（从头）

```bash
# 1. 准备物理卷
sudo pvcreate /dev/sdb1 /dev/sdc1

# 2. 创建卷组
sudo vgcreate vg_data /dev/sdb1 /dev/sdc1
sudo vgextend vg_data /dev/sdd1       # 后期加盘

# 3. 创建逻辑卷
sudo lvcreate -L 100G -n lv_root vg_data        # 100G
sudo lvcreate -l 100%FREE -n lv_data vg_data   # 剩余全部

# 4. 格式化 + 挂载
sudo mkfs.xfs /dev/vg_data/lv_root
sudo mkdir /data
sudo mount /dev/vg_data/lv_data /data

# 5. fstab 自动挂载
echo '/dev/vg_data/lv_data /data xfs defaults,nofail 0 2' | sudo tee -a /etc/fstab
```

## 📊 状态查询

```bash
sudo pvs                       # 物理卷
sudo vgs                       # 卷组
sudo lvs                       # 逻辑卷
sudo pvs /dev/sdb1             # 单个 PV
sudo lvs -o +devices           # 看 LV 用哪些 PV

# 看映射
sudo lvs -o "lv_name,lv_size,pool_lv,data_percent"
sudo lvs --segments           # 看 LV segment
```

## 📏 在线扩容

### LV 扩容（增大）

```bash
# 1. 扩 LV
sudo lvextend -L +50G /dev/vg_data/lv_data
sudo lvextend -l +100%FREE /dev/vg_data/lv_data  # 用尽 VG

# 2. 扩文件系统（ext4 / xfs 都支持在线）
sudo xfs_growfs /data
sudo resize2fs /dev/vg_data/lv_data

# ext4 一步搞定（test 选项不真改）
sudo resize2fs /dev/vg_data/lv_data 100G
```

### VG 扩容（加硬盘）

```bash
# 加新盘
sudo pvcreate /dev/sdd1
sudo vgextend vg_data /dev/sdd1
# 现在 vg 有新空间了
```

### LV 缩小（⚠️ 必须先缩 FS）

```bash
# 1. 卸载
sudo umount /data

# 2. 缩 FS
sudo resize2fs /dev/vg_data/lv_data 50G   # xfs 不支持缩

# 3. 缩 LV
sudo lvreduce -L 50G /dev/vg_data/lv_data

# 4. 挂回
sudo mount /dev/vg_data/lv_data /data
```

⚠️ **ext4 才支持缩**；**xfs 只能扩不能缩**。

## 📸 LVM 快照

```bash
# 创建快照（写时复制）
sudo lvcreate -L 10G -s -n lv_data_snap /dev/vg_data/lv_data

# 用快照（只读快照）
sudo mkdir /snap
sudo mount -o ro /dev/vg_data/lv_data_snap /snap

# 看大小
sudo lvs -o "lv_name,lv_size,data_percent"
# lv_data_snap 满 100% 时自动失效

# 删除快照
sudo umount /snap
sudo lvremove /dev/vg_data/lv_data_snap
```

## 🔄 迁移数据（pvmove）

把数据从一块物理盘移到另一块：

```bash
# 加新盘
sudo pvcreate /dev/sdd1
sudo vgextend vg_data /dev/sdd1

# 在线迁移
sudo pvmove /dev/sdb1
# 现在 sdb1 数据全在 sdd1

# 移除旧盘
sudo vgreduce vg_data /dev/sdb1
sudo pvremove /dev/sdb1
```

## 🪞 镜像（mirror）

```bash
sudo lvcreate -m 1 --mirrorlog core \
  -L 50G -n lv_mirror vg_data
# -m 1 镜像 1 副本
```

LVM 镜像 = 软 RAID 1。

## 📋 实战

```bash
# 看空间够不够扩
sudo vgs
# VG       #PV #LV  Size   VFree
# vg_data    2   3  200g 50g

# 扩 /data 50G
sudo lvextend -L +50G /dev/vg_data/lv_data
sudo xfs_growfs /data
df -h /data

# 数据库热备：用快照做一致性备份
# 1. flush + lock
sudo mysql -e 'FLUSH TABLES WITH READ LOCK;'
# 2. 快照
sudo lvcreate -L 5G -s -n db_snap /dev/vg_data/lv_mysql
# 3. unlock
sudo mysql -e 'UNLOCK TABLES;'
# 4. 备份快照
sudo mount -o ro,nouuid /dev/vg_data/db_snap /mnt/snap
sudo tar czf /backup/db-$(date +%F).tar.gz -C /mnt/snap /var/lib/mysql
sudo umount /mnt/snap
sudo lvremove /dev/vg_data/db_snap
```

## 🆚 LVM vs ZFS / Btrfs

| | LVM | ZFS / Btrfs |
|--|-----|-------------|
| 扩缩容 | ✅ | ✅ |
| 快照 | ✅ | ✅ |
| 数据校验 | ❌ | ✅（自带） |
| 软件 RAID | 需要 mdadm | 内置 |
| 学习曲线 | 中 | 中 |
| 内核支持 | 内核 | Btrfs 内核 / ZFS 用户态 |

**生产数据库 / 关键数据**：ZFS / Btrfs 更合适（自带校验）。

## 🔗 下一步

- [mount / umount](/09-storage/mount)
- [fstab 自动挂载](/09-storage/fstab)
- [ext4 / xfs / btrfs](/09-storage/fs-types)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
