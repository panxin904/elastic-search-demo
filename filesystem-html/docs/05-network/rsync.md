---
title: rsync
---

# rsync — 增量同步神器

> <span class="kg-badge kg-badge--network">网络协议</span>
> 增量传输 · SSH 隧道 · 经典同步工具

rsync 是文件**增量同步**的事实标准。它通过"滚动校验和"算法，只传输差异部分。在备份、镜像、跨机同步场景里几乎"必装"。

## 1. rsync 算法核心

把文件切成小块：

1. 发送方给每个块算两个滚动校验（弱 32-bit + 强 MD5）
2. 接收方对比
3. 匹配的块不传输 → 只传不匹配的

```
发送方                接收方
file A ──── 块 ───→  file B（已存在）
              ├ 校验和 ─→ 对比
              ←─ 不匹配块 ─┤
              ── 匹配块保留 ─→
```

效果：**带宽 = 差异大小**，而不是整个文件。

## 2. 命令格式

```bash
rsync [options] SRC DEST
rsync [options] SRC [USER@]HOST:DEST
rsync [options] [USER@]HOST:SRC DEST
```

| 角色 | 含义 |
|------|------|
| SRC | 源 |
| DEST | 目的 |
| 末尾 `/` | 同步目录内容 |
| 不带 `/` | 同步目录本身 |

```bash
# 本地同步（类似 cp）
rsync -av /src/ /dst/

# 远程推送
rsync -av /local/data/ user@server:/remote/data/

# 远程拉取
rsync -av user@server:/remote/data/ /local/data/

# SSH 端口
rsync -av -e "ssh -p 2222" /local/ user@server:/remote/
```

## 3. 关键选项

| 选项 | 含义 |
|------|------|
| `-a` | 归档模式（-rlptgoD） |
| `-v` | verbose |
| `-z` | 压缩传输 |
| `-P` | `--partial --progress`（断点续传+进度） |
| `-e` | 指定 SSH 命令 |
| `--delete` | 删目标多余文件（**慎用**） |
| `--exclude` | 排除模式 |
| `--bwlimit=KB/s` | 限速 |
| `--dry-run` | 试运行 |
| `--checksum` | 校验和而非 mtime（更可靠，慢） |

## 4. 实战场景

### 4.1 Web 服务器同步

```bash
rsync -avz --delete \
    --exclude '.git' \
    /var/www/html/ \
    user@web2:/var/www/html/
```

### 4.2 数据库备份 + 同步

```bash
# 备份 + 同步
mysqldump db | gzip > /backup/db.sql.gz
rsync -avz /backup/ user@backup-server:/backup/db/
```

### 4.3 大目录增量

```bash
rsync -avzP --bwlimit=10000 /data/ user@server:/data/
```

P = partial + progress，断网可续传。

### 4.4 双向同步（unison）

```bash
# unison 是双向同步，rsync 是单向
unison /local/dir/ ssh://user@server//remote/dir/
```

### 4.5 守护进程模式

```bash
# /etc/rsyncd.conf
[backup]
    path = /data/backup
    read only = false
    auth users = alice
    secrets file = /etc/rsyncd.secrets
```

```bash
rsync -av rsync://alice@server/backup/ /local/
```

## 5. 守护进程模式（无 SSH）

适合内网同步，无加密需求：

```ini
# /etc/rsyncd.conf
uid = nobody
gid = nobody
use chroot = yes
max connections = 10
pid file = /var/run/rsyncd.pid
log file = /var/log/rsyncd.log
transfer logging = yes

[shared]
    path = /data/shared
    comment = Public
    read only = no
    hosts allow = 192.168.1.0/24
```

```bash
rsync -av rsync://server/shared/ /local/
```

## 6. SSH 加密 + 密钥

```bash
# 用 keyfile
rsync -av -e "ssh -i /root/.ssh/backup.key" /data/ backup@server:/backup/

# 把私钥密码存 ssh-agent
ssh-add /root/.ssh/backup.key
rsync -av /data/ backup@server:/backup/   # 自动用 agent
```

## 7. --delete 的风险

`--delete` 会删目标端多余文件，**慎用**！

```bash
# 错误用法（破坏性）
rsync -av --delete /wrong/place/ user@server:/target/

# 安全用法：先试运行
rsync -avn --delete /src/ user@server:/dst/
# 再执行
rsync -av --delete /src/ user@server:/dst/
```

**生产经验**：用 `--max-delete=N` 限制最大删除数。

```bash
rsync -av --delete --max-delete=5 /src/ /dst/
```

## 8. 备份保留策略

```bash
#!/bin/bash
# 保留 7 天每天 + 4 周每周 + 12 月每月
BACKUP=/backup/data
TODAY=$(date +%Y%m%d)
DAY=$(date +%u)
MONTH=$(date +%Y%m)

mkdir -p $BACKUP/daily $BACKUP/weekly $BACKUP/monthly

# 每日
rsync -a /data/ $BACKUP/daily/$TODAY/

# 每周日保留
if [ "$DAY" = "7" ]; then
    rsync -a /data/ $BACKUP/weekly/$TODAY/
fi

# 每月 1 号保留
if [ "$(date +%d)" = "01" ]; then
    rsync -a /data/ $BACKUP/monthly/$MONTH/
fi

# 清理 7 天前的 daily
find $BACKUP/daily -maxdepth 1 -mtime +7 -type d -exec rm -rf {} \;
```

## 9. 性能

```bash
# 大文件：单 rsync 流可能打不满带宽
# 用并发
for d in dir1 dir2 dir3 dir4; do
    rsync -av /data/$d/ user@server:/data/$d/ &
done
wait

# 压缩对文本强，对二进制弱
# 强加密用 -e ssh -c aes256-ctr
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 增量 = 滚动校验 | "差分=只传变化" |
| -a -v -z -P 是核心 | "-avzP 黄金组合" |
| --delete 是高危 | "delete=高危" |
| 断点续传靠 -P | "-P=续传" |
| 双向同步要用 unison | "unison=双向" |

## 参考

- rsync 官方文档：<https://rsync.samba.org/>
- 论文：Tridgell 1999 算法论文
- Unison：<https://www.cis.upenn.edu/~bcpierce/unison/>