---
title: BorgBackup
---

# BorgBackup — 增量 + 去重 + 加密的备份神器

> <span class="kg-badge kg-badge--backup">备份快照</span>
> 增量 · 去重 · 加密 · 服务器备份首选

BorgBackup（borg）是一款用 Python 写的去重、压缩、加密备份工具。它是**服务器备份**的事实标准之一，主打"增量去重，备份越大越省空间"。

## 1. Borg 核心特性

| 特性 | 含义 |
|------|------|
| **去重** | 块级内容寻址，相同数据只存一份 |
| **增量** | 一次完整，多次增量 |
| **加密** | AES-256-CTR（认证 + 加密） |
| **压缩** | lz4 / zstd / zlib |
| **远程** | SSH 协议，支持 push 模式 |
| **校验** | 备份结束自动校验 |
| **挂载** | 可 mount 备份为只读文件系统 |

## 2. 架构

```
Borg client (server)           Repository (backup server)
   │                                │
   ├──── SSH ────► /path/to/repo ◄───┤
   │                                │
   │  chunks (deduped)             │
   │  segments                     │
   │  manifests                    │
```

## 3. 安装与初始化

```bash
# 安装
pip install borgbackup  # 任意平台
apt install borgbackup  # Debian/Ubuntu
yum install borgbackup  # CentOS

# 初始化（创建 repo）
export BORG_PASSPHRASE='mypassword'
borg init --encryption=repokey /backup/repo

# 或者用 SSH 远端
borg init --encryption=repokey ssh://user@backup.example.com/./repo
```

加密模式：

| 模式 | 含义 |
|------|------|
| `none` | 无加密 |
| `repokey` | AES-256-CTR，key 在 repo 内（要 passphrase） |
| `keyfile` | key 独立文件 |
| `repokey-blake2` | repokey + Blake2b hash（推荐） |
| `authenticated` | 仅认证不加密 |
| `authenticated-blake2` | 推荐之一 |

## 4. 实战：备份整个系统

```bash
# 首次完整备份
borg create --stats \
    --compression lz4 \
    --exclude '/proc/*' \
    --exclude '/tmp/*' \
    --exclude '/sys/*' \
    /backup/repo::'sys-2026-01-01' \
    /

# 之后增量（同一台机器）
borg create --stats \
    --compression lz4 \
    /backup/repo::'sys-2026-01-02' \
    /
# 增量只传新数据
```

## 5. 实战：备份目录

```bash
# 备份 /home /var/www
borg create --stats \
    --compression zstd \
    /backup/repo::'docs-20260101' \
    /home/alice \
    /var/www

# 加 --exclude
borg create --stats \
    --exclude '*.log' \
    --exclude 'node_modules' \
    /backup/repo::'projects-20260101' \
    /home/alice/projects/
```

## 6. 实战：cron 自动备份

```bash
# /etc/cron.daily/borg-backup
#!/bin/bash
export BORG_PASSPHRASE='secret'
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin

REPO=/backup/repo
HOSTNAME=$(hostname)
DATE=$(date +%Y-%m-%d)

borg create --stats --compression lz4 \
    --exclude '/proc/*' --exclude '/sys/*' --exclude '/tmp/*' \
    "$REPO::${HOSTNAME}-${DATE}" /

# 清理 7 天前的
borg prune --keep-daily=7 --keep-weekly=4 --keep-monthly=12 "$REPO"

# 校验
borg check "$REPO"
```

## 7. 实战：远程备份

```bash
# 远端 SSH repo
borg init --encryption=repokey-blake2 \
    ssh://backup@backup-server.example.com/./repo

# 备份
borg create --stats --compression lz4 \
    ssh://backup@backup-server.example.com/./repo::'data-20260101' \
    /var/data

# 配置 SSH key
ssh-copy-id backup@backup-server.example.com

# 配置无 passphrase 的 key + BORG_PASSPHRASE
export BORG_PASSPHRASE='...'
```

## 8. 实战：列出备份 / 恢复

```bash
# 列归档
borg list /backup/repo

# 看某归档内容
borg list /backup/repo::docs-20260101

# 恢复文件
borg extract /backup/repo::docs-20260101 home/alice/report.pdf

# 恢复整个归档
borg extract /backup/repo::docs-20260101

# 恢复到指定目录
borg extract /backup/repo::docs-20260101 --stdout home/alice/file.txt > /tmp/file.txt

# 挂载（FUSE）
borg mount /backup/repo::docs-20260101 /mnt/borg
ls /mnt/borg
umount /mnt/borg
```

## 9. 实战：prune 策略

```bash
# 保留规则
borg prune -v --list \
    --keep-within=1d \           # 1 天内的全保留
    --keep-daily=7 \             # 7 个 daily
    --keep-weekly=4 \            # 4 个 weekly
    --keep-monthly=12 \          # 12 个 monthly
    --prefix='{hostname}-' \
    /backup/repo
```

## 10. 性能调优

```bash
# 调块大小（小文件用 8KB，大文件用 2MB）
borg create --chunker-params=buzhash,14,18,16,4095 \
    /backup/repo::full /data
# chunker-params = algo,min_exp,max_exp,hash_key,mask

# 用专用用户运行
borg create --remote-path=/usr/local/bin/borg1.2 ssh://...
```

## 11. 实战：从其他备份工具迁移

```bash
# 从 tar
borg create /backup/repo::imported-20260101 -

# 从 restic
# 用 borg-import 工具
```

## 12. 与 restic 对比

| 维度 | Borg | restic |
|------|------|--------|
| 后端 | SSH / 本地 | S3 / SFTP / 本地 / 12+ |
| 去重 | **块级** | 文件级 |
| 性能 | **优** | 中 |
| 加密 | ✅ | ✅ |
| 校验 | ✅ | ✅ |
| mount | FUSE | FUSE |
| 学习曲线 | **陡** | **平缓** |
| 适用 | 长时间持有大数据 | 跨云 / 多后端 |

**实战选择**：

- 数据量大 + 长期保留 → **Borg**
- 多后端 / 跨云 → **restic**
- 简单备份 → **restic**
- 极简单 → **tar + cron**

## 13. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| Borg = 块级去重 | "Borg=块去重" |
| repokey 加密 | "repokey=AES-256" |
| prune 策略保留 | "prune=保留" |
| FUSE 挂载可读 | "FUSE=浏览" |
| SSH 协议传输 | "SSH=传输" |

## 参考

- Borg 官方文档：<https://borgbackup.readthedocs.io/
- GitHub：<https://github.com/borgbackup/borg
- 实战：Borg 增量备份案例


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
