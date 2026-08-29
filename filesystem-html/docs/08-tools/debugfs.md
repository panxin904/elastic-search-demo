---
title: debugfs
date: 2026-08-15  # date-auto-injected
---

# debugfs — ext 系列文件系统调试工具

> <span class="kg-badge kg-badge--tools">工具集</span>
> 抢救数据 · 手动编辑元数据 · 文件系统诊断

debugfs 是 e2fsprogs 包提供的 ext2/ext3/ext4 **交互式调试器**。它是文件系统管理员和数据救援的"瑞士军刀"——可以打开一个块设备直接读写 inode、目录、数据块。

## 1. 危险！先看免责声明

debugfs 直接读写元数据：

- **不通过内核 VFS**（绕过锁）
- 操作没有"撤销"按钮
- 一条命令可能毁掉整个 FS

**使用原则**：

1. 先 unmount 或 ro 打开
2. 先备份镜像（`dd`）再做实验
3. 不熟悉的命令先 `help`

## 2. 启动 debugfs

```bash
# 打开设备（默认 rw）
debugfs /dev/sdb1

# 只读模式（强烈推荐先试）
debugfs -R "open -r /dev/sdb1"

# 操作镜像文件
debugfs /tmp/disk.img
```

## 3. 常用命令

### 3.1 ls 与 stat

```bash
debugfs:  ls /                      # 列出根目录
debugfs:  ls /home
debugfs:  stat /etc/passwd         # 看文件 inode 信息
debugfs:  stat /etc
```

```text
Inode: 1234567   Type: regular    Mode: 0644
Size: 2048
Blocks: (8): 1000243-1000250
```

### 3.2 看文件内容

```bash
debugfs:  cat /etc/passwd
debugfs:  dump /etc/passwd /tmp/passwd.backup
```

```text
# dump 把文件复制到本地
```

### 3.3 看 inode

```bash
debugfs:  stat <inode_num>
debugfs:  icheck <block_num>      # 反查哪个 inode 占这块
```

### 3.4 修改 inode（危险）

```bash
debugfs:  set_inode_field <i> mode 0644   # 改权限
debugfs:  set_inode_field <i> uid 1000    # 改 UID
```

### 3.5 删 / 恢复 文件

```bash
debugfs:  rm /home/lostfile
debugfs:  undel <inode> /home/restored.txt  # 恢复 deleted 文件
```

**undel 限制**：只能恢复未被覆盖的块，时间紧迫！

### 3.6 修复 / 清理孤儿

```bash
debugfs:  lsdel           # 列已删除但 inode 还在的
debugfs:  kill_file <inode>     # 标记 inode 空闲
debugfs:  free_blocks <n>      # 手动释放块
```

### 3.7 看 superblock

```bash
debugfs:  stats
debugfs:  show_super_stats -h
```

显示：

- 块大小
- 总块数
- 空闲块数
- inode 总数
- 最后一个 mount 路径

## 4. 实战：误删文件恢复

```bash
# 1. 立刻卸载该分区（防覆盖）
umount /dev/sdb1

# 2. 只读打开 debugfs
debugfs -R "open -r /dev/sdb1"

# 3. 找最近删除的文件
debugfs:  lsdel
# 输出：
# Inode Owner  Mode  Size    Blocks   Time deleted
# 123456 alice  0644  4096    1 2 3 4  Mon Jan  1 10:00 2026

# 4. 恢复
debugfs:  undel <123456> /restored.txt

# 5. 退出后挂载复制
```

## 5. 实战：删大文件后空间没释放

有时候删了大文件但 `df` 不变（被打开未关闭）：

```bash
lsof /mountpoint | grep deleted
# COMMAND  PID  USER   FD   TYPE DEVICE   SIZE  NODE  NAME
# bash    1234 root   12r  REG  8,16  100G 12345 /var/log/big.log (deleted)

# 强杀进程
kill -9 1234
```

## 6. 实战：改 magic number 误识别恢复

误把 ext4 当成 ext3 / ntfs 格式化前：

```bash
# 看 superblock 备份
debugfs:  show_super_stats -h

# 找最后一个 superblock 备份位置
dumpe2fs /dev/sdb1 | grep -i "backup superblock"

# 用 e2fsck 修复
e2fsck -b <block_num> /dev/sdb1
```

## 7. 实战：手动删除坏目录

```bash
# 目录 entry 损坏 → 无法 ls / rm
debugfs:  rm_dir /path/to/baddir
```

## 8. 实战：检查文件系统健康

```bash
# debugfs 检查扩展属性
debugfs:  ea_list /file
debugfs:  ea_get /file user.mime

# 查挂载次数
debugfs:  stats | grep Mount
```

## 9. 与 e2fsprogs 工具集

```bash
# 调试包常用工具
e2fsck      # 检查/修复
tune2fs     # 改 FS 参数
dumpe2fs    # 看详细信息
mke2fs      # 创建 ext FS
resize2fs   # 扩/缩 FS
```

```bash
# 实际修复案例
umount /dev/sdb1
e2fsck -f -y -C 0 /dev/sdb1
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| debugfs 是大锤 | "debugfs=大锤" |
| 只读模式先试 | "先 ro 后 rw" |
| undel 抢时间 | "undel=抢时间" |
| dumpe2fs 看 superblock 备份 | "dump=superblock" |
| e2fsck 修 FS | "e2fsck=修复" |

## 参考

- e2fsprogs 文档：<https://e2fsprogs.sourceforge.net/
- debugfs 用户手册
- 数据恢复实战案例（ext 系列）


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
