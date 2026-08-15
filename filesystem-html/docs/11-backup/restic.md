---
title: restic
---

# restic — 跨云友好的备份工具

> <span class="kg-badge kg-badge--backup">备份快照</span>
> 多后端 · 增量 · Go 编写 · 易上手

restic 是一款 Go 写的备份工具。它的杀手锏是**支持 12+ 后端**——S3、SFTP、Backblaze B2、Azure Blob、Google Cloud Storage、本地、rclone mount 等等。

## 1. restic 核心特性

| 特性 | 含义 |
|------|------|
| **多后端** | S3 / SFTP / 本地 / 各种云 |
| **增量** | 永远增量（首次 = 全量） |
| **加密** | AES-256，密码学级别 |
| **去重** | 文件级（按内容寻址） |
| **校验** | 自动 + 手动 |
| **snapshot 模型** | 每次备份是一个 snapshot |
| **mount** | FUSE 浏览备份 |
| **跨平台** | Linux / macOS / Windows / FreeBSD |

## 2. 安装

```bash
# Linux
wget https://github.com/restic/restic/releases/download/v0.17.3/restic_0.17.3_linux_amd64.bz2
bunzip2 restic_0.17.3_linux_amd64.bz2
mv restic_0.17.3_linux_amd64 /usr/local/bin/restic
chmod +x /usr/local/bin/restic

# macOS
brew install restic

# Windows
scoop install restic
```

## 3. 初始化 Repo

### 3.1 本地

```bash
export RESTIC_PASSWORD='mypassword'
restic -r /backup/repo init
```

### 3.2 SFTP

```bash
export RESTIC_PASSWORD='mypassword'
restic -r sftp:user@backup-server:/backup/repo init
```

### 3.3 S3

```bash
export RESTIC_PASSWORD='mypassword'
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=yyy
restic -r s3:s3.amazonaws.com/my-bucket init
```

### 3.4 MinIO

```bash
export RESTIC_PASSWORD='mypassword'
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
restic -r s3:http://minio.example.com/my-bucket init
```

### 3.5 Backblaze B2 / Azure / GCS

类似 S3 模式，指定 endpoint。

## 4. 备份

```bash
# 默认压缩
restic -r /backup/repo backup /home/alice

# 自定义标签
restic -r /backup/repo backup \
    --tag daily --tag webserver \
    /var/www /etc/nginx

# 排除
restic -r /backup/repo backup \
    --exclude '*.log' \
    --exclude 'node_modules' \
    --exclude-file=/etc/restic/excludes \
    /project

# /etc/restic/excludes
*.tmp
*.bak
__pycache__
.git/objects
```

## 5. 实战：跨云异地备份

```bash
# 主备份到 S3
restic -r s3:s3.amazonaws.com/main-backup backup /home/alice

# 同步到另一家云（异地）
restic -r s3:s3.eu-west-1.amazonaws.com/dest-backup copy \
    --from-repo s3:s3.amazonaws.com/main-backup \
    --from-password xxx \
    snapshot latest
```

## 6. 实战：列出 / 恢复

```bash
# 列快照
restic -r /backup/repo snapshots

# 看快照内容
restic -r /backup/repo ls latest

# 恢复特定文件
restic -r /backup/repo restore latest \
    --target /tmp/restore \
    --include 'home/alice/report.pdf'

# 恢复整个快照
restic -r /backup/repo restore latest --target /tmp/restore

# 快照对比
restic -r /backup/repo diff  latest~1 latest
```

## 7. 实战：自动备份 + 保留策略

```bash
#!/bin/bash
export RESTIC_PASSWORD='secret'
export RESTIC_REPOSITORY='s3:s3.amazonaws.com/my-backup'

restic backup \
    --tag daily \
    --exclude-caches \
    --exclude-file=/etc/restic/excludes \
    /var/data /home

# 保留策略
restic forget \
    --keep-hourly 24 \
    --keep-daily 7 \
    --keep-weekly 4 \
    --keep-monthly 12 \
    --keep-yearly 5 \
    --prune

# 校验
restic check
restic check --read-data-subset=10%  # 校验 10% 数据
```

```cron
0 2 * * * /usr/local/bin/restic-backup.sh
```

## 8. 实战：FUSE 浏览

```bash
mkdir /mnt/restic
restic -r /backup/repo mount /mnt/restic
# 在 /mnt/restic 下能看到 snapshots/ 目录
ls /mnt/restic/snapshots/
fusermount -u /mnt/restic
```

## 9. 实战：与 restic-server 协同

自己搭一个 SFTP-like restic 服务：

```bash
# 服务端（任意能 SSH 的机器）
restic-server --path /backup

# 客户端
restic -r rest:http://server:8000/ init
```

适合不想用公共云的场景。

## 10. 实战：rclone 后端

```bash
# rclone 把任何云盘暴露成 S3 / 本地
rclone serve s3 /path/to/data --addr :8000

# restic 用这个 S3
restic -r s3:http://localhost:8000/mybucket init
```

支持：Google Drive / OneDrive / Dropbox / WebDAV / SFTP 等等。

## 11. 性能与限制

| 维度 | 表现 |
|------|------|
| 大文件 | 中（不如 Borg） |
| 小文件 | 优（文件级 dedup） |
| 网络 | 中（增量传输） |
| 加密 | AES-256 |
| 内存 | 100-500 MB |
| 速度 | 中等 |

## 12. 与 Borg 对比

| 维度 | restic | Borg |
|------|--------|------|
| 去重 | 文件级 | **块级** |
| 后端 | **12+** | SSH / 本地 |
| 跨云 | **优** | 中 |
| 速度 | 中 | **优** |
| 学习曲线 | **低** | 中 |
| 适合场景 | **多云 / 通用** | 长保留 / 大数据 |

## 13. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| restic = 多后端 | "restic=多端" |
| 文件级去重 | "去重=文件级" |
| 永远增量 | "增量=永久" |
| FUSE 挂载浏览 | "FUSE=浏览" |
| forget + prune 清理 | "forget=保留" |

## 参考

- restic 官方文档：<https://restic.readthedocs.io/
- GitHub：<https://github.com/restic/restic
- restic-server：<https://github.com/restic/rest-server