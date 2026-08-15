---
title: xargs / find 配合
---

# xargs - 命令行管道

> 把 **stdin 转成参数**，传给其他命令。配合 find / grep / cp 是经典用法。

## 📜 基础

```bash
echo 'a b c' | xargs echo                # echo a b c
echo 'a\nb\nc' | xargs -I{} echo {}       # -I{} 占位符
echo 'a\nb\nc' | xargs -n1 echo            # 一次一个
```

## 🚀 与 find 配合（最常用）

```bash
# 找到并删除
find . -name '*.tmp' | xargs rm
find . -name '*.tmp' | xargs -I{} rm {}

# 找到并复制
find . -name '*.conf' | xargs -I{} cp {} /backup/

# 找到并查看
find . -name '*.log' | xargs tail -f

# 找到并打包
find . -name '*.js' | xargs tar -czf js.tar.gz

# 找到并搜索内容
find . -name '*.log' | xargs grep 'ERROR'
```

## ⚠️ 文件名带空格怎么办

```bash
# ❌ 错误：会断开
find . -name '*.txt' | xargs rm
# 文件 "my file.txt" 会被当作两个参数

# ✅ 正确：用 -print0 + xargs -0
find . -name '*.txt' -print0 | xargs -0 rm
# \0 分割符保证文件名原样
```

## 🛠 实战

```bash
# 批量修改
find . -name '*.js' -print0 | xargs -0 sed -i 's/foo/bar/g'

# 统计所有 .js 文件行数
find . -name '*.js' -print0 | xargs -0 wc -l

# 删除空文件
find . -type f -empty -print0 | xargs -0 rm

# 给所有 .sh 加执行位
find . -name '*.sh' | xargs chmod +x

# 看所有进程的命令行
ps aux | tail -n +2 | awk '{print $11}' | xargs -I{} which {} 2>/dev/null | sort -u
```

## 🚦 与 -exec 的取舍

| | `-exec` | `xargs` |
|--|---------|---------|
| 语法 | `find ... -exec cmd {} \;` | `find ... | xargs cmd` |
| 批量 | 用 `{} +` 一次传多文件 | 默认一次传多（更快） |
| 空格 | 自动按行（除非 `{}`） | 必须 `-0 + xargs -0` |
| 复杂度 | 简单 | 大批量更快 |

```bash
# 等价（批量删除）
find . -name '*.tmp' -exec rm {} +
find . -name '*.tmp' -print0 | xargs -0 rm

# 逐文件（需要每个文件一次）
find . -name '*.sh' -exec chmod +x {} \;     # 一次一个
find . -name '*.sh' -print0 | xargs -0 -n1 chmod +x  # 一次一个
```

## 🧪 安全考虑

```bash
# ⚠️ 变量有空格时，xargs 会拆开
echo 'a;b;c' | xargs -d';' echo     # 显式分割符

# 避免意外：用 -d 或 -0
ps aux | awk '{print $2}' | xargs kill   # 慎用！

# 始终对文件名用 -print0 + -0
find . -print0 | xargs -0 ...
```

## 🛠 实战：批量 SSH 操作

```bash
# 列出所有 server
cat servers.txt | xargs -I{} ssh {} 'uptime'

# 批量重启服务
echo "web1 web2 web3" | xargs -n1 -I{} ssh {} 'sudo systemctl restart nginx'

# 批量部署（rsync）
cat servers.txt | xargs -n1 -I{} rsync -avz --delete /opt/app/ {}:/opt/app/
```

## 🆚 替代品

```bash
# 简单的可以 shell 循环替代
for f in *.log; do echo "$f"; done
# 复杂的 xargs 性能更好

# GNU parallel：更强的并发
parallel -j 4 'grep "pattern" {}' ::: *.log
```

## 🔗 下一步

- [find 查找](/02-filesystem/find)
- [grep](/03-text/grep)
- [bash 基础语法](/11-shell/bash-syntax)