---
title: 软链与硬链
date: 2026-08-15  # date-auto-injected
---

# ln - 软链与硬链

> Linux 的两种"链接"，容易混淆。

## 🔗 软链 vs 硬链

| | 软链 (Symbolic Link) | 硬链 (Hard Link) |
|--|---------------------|------------------|
| 命令 | `ln -s` | `ln` |
| 是什么 | 独立文件，内容是目标路径 | 与原文件指向同一个 inode |
| 跨文件系统 | ✅ 可以 | ❌ 不可以 |
| 指向目录 | ✅ 可以 | ❌ 不可以 |
| 删原文件 | 软链**变死链** | 文件还能用（硬链计数 -1） |
| 显示 | `lrwxrwxrwx` 开头，权限全开 | 普通文件 |
| inode | 自己的 inode | 跟原文件**相同** |

## 📁 软链 (ln -s)

```bash
ln -s /opt/app/current /usr/local/bin/app
# 现在执行 `app` 等价于执行 /opt/app/current/...

ls -la /usr/local/bin/app
# lrwxrwxrwx 1 root root 16 ... app -> /opt/app/current

# 改原文件，软链跟着变
ln -s /var/log/nginx/access.log ~/access.log
cat ~/access.log                # 看 nginx 日志

# 软链套软链
ln -s /usr/bin/python3 /usr/local/bin/python

# 死链
ln -s /tmp/nonexistent ~/bad
ls -la ~/bad                    # 显示但打不开
```

## 🔩 硬链

```bash
ln /etc/hosts /tmp/hosts-hard
# 现在 /etc/hosts 和 /tmp/hosts-hard 是同一个文件的两个名字

# 查看 inode
ls -i /etc/hosts /tmp/hosts-hard
# 两者 inode 相同

# 删 /etc/hosts，/tmp/hosts-hard 仍能访问
rm /etc/hosts
cat /tmp/hosts-hard             # 还能看

# 计数
ls -l /etc/hosts                # 第 2 列是硬链计数
```

## 🤔 为什么用硬链

1. **防止误删**：删一个名字，另一个还在
2. **节省空间**：两个名字，磁盘只用一份
3. **快照备份**：rsync 用 `--link-dest` 创建硬链做增量备份

```bash
# 实战：rsync 增量备份
rsync -av --link-dest=/backup/2024-01-01 \
         /data/ /backup/2024-01-02/
# 2024-01-02 是 01-01 的硬链副本，只复制变化文件
```

## 🤔 为什么用软链

1. **版本切换**：`/usr/local/bin/node -> /opt/node/20.0.0` 改一个 link 升级
2. **跨文件系统**：必须用软链
3. **简化路径**：把深路径缩成短名

```bash
# 经典蓝绿部署
ln -sfn /opt/app/v2 /opt/app/current
# 切回 v1
ln -sfn /opt/app/v1 /opt/app/current
```

## 🔍 找硬链

```bash
# 找指向同一 inode 的所有文件
find / -inum $(ls -i /etc/hosts | awk '{print $1}') 2>/dev/null
# 或用 stat
stat -c '%i' /etc/hosts
find / -inum 1234567 2>/dev/null
```

## 📋 看软链指向哪里

```bash
ls -l /usr/local/bin/app          # 看完整路径
readlink /usr/local/bin/app       # 只显示目标
realpath /usr/local/bin/app       # 解析所有层
```

## ⚠️ 注意事项

```bash
# 软链 + 删原文件 = 死链
ln -s /tmp/orig ~/link
rm /tmp/orig                     # 软链变死链
# 删软链：删 ~/link 即可，原文件无影响

# 复制软链要小心
cp -L file       # 跟随软链（读内容）
cp -P file       # 保留软链本身
cp -a src/ dst/  # archive 模式保留软链
```

## 🛠 实战：部署脚本

```bash
#!/usr/bin/env bash
APP=/opt/myapp
NEW=/opt/myapp-build-$(date +%s)

# 部署新版到 NEW
git clone ... $NEW
cd $NEW && npm ci && npm run build

# 原子切换
ln -sfn $NEW $APP/current
# 服务还在跑旧版，但 current 已指向新版
# 接下来：systemctl restart myapp 即生效
```

## 🔗 下一步

- [权限 (rwx)](/02-filesystem/permissions)
- [ls / cp / mv](/02-filesystem/ls)
- [find 查找](/02-filesystem/find)