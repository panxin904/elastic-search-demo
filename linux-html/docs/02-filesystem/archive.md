---
title: 压缩与归档
date: 2026-08-15  # date-auto-injected
---

# 压缩与归档

> 三大件：tar / gzip / zip。服务器上 tar 是绝对主力。

## 📦 tar - 归档（不是压缩）

```bash
# 打包（不压缩）
tar -cf dir.tar dir/

# 打包 + gzip 压缩（最常用）
tar -czf dir.tar.gz dir/

# 打包 + bzip2（更小但慢）
tar -cjf dir.tar.bz2 dir/

# 打包 + xz（最小，CPU 重）
tar -cJf dir.tar.xz dir/

# 解压到当前目录
tar -xf file.tar.gz

# 解压到指定目录
tar -xf file.tar.gz -C /dest

# 仅查看内容
tar -tf file.tar.gz

# 排除
tar -czf --exclude='*.log' dir.tar.gz dir/
tar -czf --exclude='node_modules' --exclude='.git' src.tar.gz src/

# 解压单个文件
tar -xf dir.tar.gz dir/specific-file
```

### 常用选项

| 短 | 长 | 作用 |
|----|----|------|
| `-c` | `--create` | 创建 |
| `-x` | `--extract` | 解压 |
| `-t` | `--list` | 查看 |
| `-v` | `--verbose` | 详细 |
| `-f` | `--file` | 指定文件（必带） |
| `-z` | `--gzip` | gzip |
| `-j` | `--bzip2` | bzip2 |
| `-J` | `--xz` | xz |
| `-C` | `--directory` | 切换目录 |
| `-p` | `--preserve-permissions` | 保留权限 |
| `--exclude` | - | 排除模式 |

## 🗜 gzip / gunzip / zcat

```bash
gzip file                  # file → file.gz（删除原文件）
gzip -k file               # 保留原文件
gzip -9 file               # 最高压缩比
gunzip file.gz             # 解压
zcat file.gz               # 看内容（不解压）
```

## 🧊 xz / unxz（更高压缩）

```bash
xz file                    # file → file.xz
unxz file.xz               # 解压
xzcat file.xz              # 看内容
xz -T 4 file               # 4 线程并行（更快）
```

## 📦 zip / unzip

```bash
zip file.zip file          # 压单文件
zip -r dir.zip dir/        # 递归压缩
zip -e file.zip file       # 加密码
zip -9 file.zip file       # 最高压缩

unzip file.zip             # 解压
unzip -d /dest file.zip    # 解压到指定目录
unzip -l file.zip          # 看内容
unzip -o file.zip          # 覆盖不提示
```

## 🪟 7z（高压缩 + 多格式）

```bash
sudo apt install p7zip-full

7z a dir.7z dir/                # 压缩
7z x dir.7z -o /dest            # 解压（独立 -o）
7z l dir.7z                     # 看内容
```

## 📊 选哪个

| 格式 | 压缩比 | 速度 | 兼容 |
|------|--------|------|------|
| `.gz` | 中 | 快 | 极广 |
| `.bz2` | 高 | 中 | 较广 |
| `.xz` | 很高 | 慢 | Linux 主流 |
| `.zip` | 中 | 快 | 全平台 |
| `.7z` | 最高 | 慢 | 中（需装软件） |
| `.tar.zst` | 极高 | 中 | 较新 Linux |

## 🔧 实战

### 备份

```bash
# 全量备份
tar -czf /backup/full-$(date +%Y%m%d).tar.gz --exclude=/proc --exclude=/sys /

# 增量备份（rsync + hardlink）
rsync -av --delete --link-dest=/backup/prev /data/ /backup/now/

# 数据库 + tar 一并打包
mysqldump db | gzip > db.sql.gz
```

### 拆分大文件

```bash
# 拆分 1G 文件为 100MB 块
split -b 100M bigfile.gz bigfile.gz.part.

# 合并
cat bigfile.gz.part.* > bigfile.gz
```

### 在线传文件（不落盘）

```bash
# 远端打包 + 流回
ssh host 'tar -czf - /data' | tar -xzf - -C ./local

# 跨服务器复制大目录
rsync -avz --progress src/ user@host:/dest/
```

## 🔗 下一步

- [ls / cp / mv](/02-filesystem/ls)
- [find 查找](/02-filesystem/find)
- [压缩归档命令速查](/cheatsheet)