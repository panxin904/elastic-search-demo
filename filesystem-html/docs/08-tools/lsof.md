---
title: lsof
date: 2026-08-15  # date-auto-injected
---

# lsof — List Open Files 一切皆文件

> <span class="kg-badge kg-badge--tools">工具集</span>
> 打开文件诊断 · 网络 FD · 删除但占用

Linux 中**一切皆文件**——socket、pipe、设备、目录都是文件描述符。lsof 列出所有打开的文件描述符，是排查"磁盘满但 du 不见大文件"、"端口被谁占用"等问题的瑞士军刀。

## 1. lsof 基础

```bash
# 列出所有（很慢）
lsof

# 按 PID
lsof -p 1234

# 按用户
lsof -u alice

# 按文件
lsof /var/log/app.log

# 按目录
lsof +D /var/log

# 按 fd 类型
lsof -d 0-100           # fd 0 到 100
lsof -d txt              # .text 段文件
```

## 2. 关键字段

```
COMMAND   PID  USER   FD    TYPE  DEVICE  SIZE/OFF   NODE  NAME
mysqld    1234 mysql   4u   REG   8,16    1073741824 12345 /var/lib/mysql/ibdata1
```

| 字段 | 含义 |
|------|------|
| COMMAND | 命令名 |
| PID | 进程 ID |
| USER | 用户 |
| FD | 文件描述符 |
| TYPE | 类型：REG / DIR / IPv4 / IPv6 / unix / CHR |
| DEVICE | 设备号（8,16 = sdb） |
| SIZE/OFF | 文件大小 / 偏移 |
| NODE | inode |
| NAME | 路径 |

## 3. FD 描述

| FD | 含义 |
|----|------|
| `cwd` | 当前工作目录 |
| `txt` | 程序代码段 |
| `mem` | 内存映射文件 |
| `rtd` | 根目录 |
| `0u / 1u / 2u` | stdin / stdout / stderr |
| `3u` | fd 3（u=可读写 / w=只写 / r=只读） |

## 4. 实战：磁盘满但 du 不见大文件

```bash
lsof | grep deleted
# COMMAND   PID  USER   FD   TYPE DEVICE   SIZE  NODE  NAME
# app       1234 root   12r  REG  8,16    100G 12345 /var/log/big.log (deleted)
# file2     1235 root   8w   REG  8,16    50G  12345 /tmp/file (deleted)
```

虽然文件已 unlink，但**进程仍持有 fd**，磁盘空间没释放。

**解决**：杀掉进程或重启。

```bash
kill -9 1234
```

## 5. 实战：端口被谁占用

```bash
lsof -i :8080
# COMMAND  PID  USER   FD   TYPE  DEVICE  SIZE/OFF  NODE  NAME
# node     5678 app    23u  IPv4  12345   0t0       TCP  *:http-alt (LISTEN)

lsof -i :8080 -t   # 只输出 PID
# 5678
```

`lsof -t` 输出 PID，配合 `kill` 用：

```bash
kill -9 $(lsof -i :8080 -t)
```

## 6. 实战：谁在写我的文件

```bash
lsof /var/log/myapp.log
```

```text
COMMAND  PID  USER  FD   TYPE DEVICE SIZE/OFF   NODE NAME
myapp    1234 root  5w   REG  8,16   12345678   1234 /var/log/myapp.log
```

## 7. 实战：网络连接排查

```bash
# 所有 TCP 连接
lsof -i tcp

# 所有 UDP
lsof -i udp

# 与某 IP 的连接
lsof -i @192.168.1.100

# 状态 LISTEN / ESTABLISHED
lsof -i tcp -sTCP:LISTEN
lsof -i tcp -sTCP:ESTABLISHED
```

## 8. 实战：socket 文件

```bash
# Unix socket
lsof -U
lsof /var/run/docker.sock
lsof /tmp/.X11-unix/X0

# 看 Docker
lsof /var/run/docker.sock
```

## 9. 实战：mount point

```bash
# 哪些进程在使用某个挂载点
lsof /mnt/data
fuser -m /mnt/data        # 类似但只输出 PID
```

## 10. fuser：替代品

```bash
# 看谁在用 /var/log
fuser -v /var/log

# 看谁在用端口 80
fuser 80/tcp

# 杀掉占用的进程
fuser -k /var/log/app.log
fuser -k 80/tcp
```

## 11. 实战：mount namespace

```bash
# 看某个 mount namespace 下的所有 fd
ls -la /proc/<pid>/fd

# 看谁开了某个 inode
lsof -i <inode>
```

## 12. 性能

lsof 全量扫描很慢（要遍历所有 /proc/*/fd）：

```bash
# 加 -n 不解析主机名（快很多）
lsof -nP -i tcp

# 限定 PID 范围
lsof -p 1234
```

## 13. 实战：deleted 文件清理脚本

```bash
#!/bin/bash
# 找出所有被删除但仍占用的文件
lsof | awk '$NF ~ /\(deleted\)/' | while read line; do
    pid=$(echo "$line" | awk '{print $2}')
    echo "$line"
    # 可选：kill -9 $pid
done
```

## 14. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| lsof = 一切皆文件 | "lsof=Open Files" |
| deleted 但占用磁盘 | "deleted=杀手" |
| -i 看网络 | "-i=网络" |
| -p 看单进程 | "-p=PID" |
| -t 只输出 PID | "-t=PID only" |

## 参考

- lsof 手册
- fuser 手册
- 《Linux Performance》 Brendan Gregg


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
