---
title: inotify
date: 2026-08-15  # date-auto-injected
---

# inotify — Linux 文件系统事件监控

> <span class="kg-badge kg-badge--tools">工具集</span>
> 文件变更事件 · 实时响应 · 替代轮询

inotify 是 Linux 内核的**文件系统事件通知**机制。它让应用监听"文件被创建/修改/删除"等事件，**无需轮询**。rsync、systemd、auditd、Docker、K8s 都用它。

## 1. inotify 解决了什么问题

传统方式：**轮询**（cron 定期查 stat）。

- 每秒查 1000 个文件 = 1000 stat/秒 → 浪费
- 漏掉瞬时事件

inotify：**内核主动通知**。

- 应用调 `inotify_add_watch()` 注册监听
- 内核在事件发生时直接通知（fd 可读）

## 2. inotify 事件

| 事件 | 触发 |
|------|------|
| `IN_ACCESS` | 文件被读 |
| `IN_MODIFY` | 文件被写 |
| `IN_ATTRIB` | 元数据变化（chmod、chown） |
| `IN_CLOSE_WRITE` | 关闭写入 |
| `IN_CLOSE_NOWRITE` | 关闭只读 |
| `IN_OPEN` | 文件被打开 |
| `IN_MOVED_FROM` | 移出 |
| `IN_MOVED_TO` | 移入 |
| `IN_CREATE` | 文件/目录创建 |
| `IN_DELETE` | 文件/目录删除 |
| `IN_DELETE_SELF` | 监听对象本身被删 |
| `IN_MOVE_SELF` | 监听对象本身被移走 |
| `IN_ONLYDIR` | 只监听目录 |

## 3. 命令行工具 inotifywait

```bash
# 安装
apt install -y inotify-tools

# 监听 /tmp 下的所有事件
inotifywait -m /tmp

# 监听创建和删除
inotifywait -m -e create -e delete /tmp

# 监听整个目录树
inotifywait -m -r /var/log

# 触发命令
inotifywait -m /var/log -e modify | while read path action file; do
    echo "$file $action"
    # 触发操作
done
```

实战例子：实时同步

```bash
inotifywait -m -r /src -e modify,create,delete --format '%w%f' | while read NEWFILE; do
    rsync -az "$NEWFILE" "user@server:/dst/$NEWFILE"
done
```

## 4. 编程 API

```c
#include <sys/inotify.h>

int fd = inotify_init1(IN_NONBLOCK);
int wd = inotify_add_watch(fd, "/tmp", IN_CREATE | IN_DELETE);

char buf[4096] __attribute__((aligned));
for (;;) {
    int n = read(fd, buf, sizeof(buf));
    for (char *p = buf; p < buf + n;) {
        struct inotify_event *e = (struct inotify_event *)p;
        if (e->len) {
            printf("%s\n", e->name);
        }
        p += sizeof(struct inotify_event) + e->len;
    }
}
```

## 5. inotify 限制

```bash
# 看内核限制
cat /proc/sys/fs/inotify/max_queued_events    # 默认 16384
cat /proc/sys/fs/inotify/max_user_watches     # 默认 8192
cat /proc/sys/fs/inotify/max_user_instances   # 默认 128

# 调大
sysctl -w fs.inotify.max_user_watches=524288
```

**实战经验**：

- 监听 100 万文件 → 调大 `max_user_watches`
- 事件突发 → 调大 `max_queued_events`

## 6. inotify 与容器

K8s / Docker 大量用 inotify：

- kube-apiserver: 监听 etcd / configmap
- fluentd / filebeat: 监听容器日志
- kubelet: 监听 Pod 目录

```bash
# 看容器里 inotify 占用
docker exec my-container sh -c 'cat /proc/$(pidof myapp)/fdinfo/* | grep inotify'
```

## 7. inotifywait 高级用法

### 7.1 监控文件系统目录结构变化

```bash
inotifywait -m -e create,delete,move /etc/nginx
# 适合：配置变更触发 reload
```

### 7.2 监控特定文件模式

```bash
inotifywait -m -e create --format '%f' /tmp | grep '\.log$' | while read f; do
    echo "新日志文件: $f"
    # 处理
done
```

### 7.3 排除子目录

```bash
inotifywait -m --exclude "node_modules|\.git" /project
```

## 8. inotify vs 其他监控机制

| 机制 | 粒度 | 性能 | 实时 |
|------|------|------|------|
| 轮询 stat | 文件 | 差 | 差 |
| **inotify** | 文件 | **优** | **优** |
| fanotify | 文件系统级 | 优 | 优 |
| fsnotify (Go) | 文件 | 优（基于 inotify） | 优 |

**fanotify** 是更新的内核接口，能监听**整个挂载点**——常用于安全审计。

## 9. 实战：实时热加载配置

```bash
# 监听配置变更触发 reload
inotifywait -m /etc/myapp -e modify,create,delete --format '%w%f' | while read FILE; do
    case "$FILE" in
        *.conf|*.yaml)
            echo "Reload config"
            kill -HUP $(cat /var/run/myapp.pid)
            ;;
    esac
done
```

## 10. 实战：日志监控

```bash
# 日志文件变化实时告警
inotifywait -m /var/log/myapp -e modify | while read path event file; do
    # 解析新行触发告警
    tail -n 1 $path$file | grep -E 'ERROR|FATAL' && \
        notify-send "Error detected in $file"
done
```

## 11. inotify 的坑

### 11.1 文件替换（atomic rename）

很多应用写日志 = 创建临时文件 + rename：

```bash
mv log.tmp log
```

inotify 收到 `MOVED_FROM` + `MOVED_TO`，**但 `MOVED_TO` 的 watch 会失效**。

解决：监听**父目录**，看 create 事件。

### 11.2 递归监听性能

递归监听过深 → 文件描述符爆炸。

解决：监听关键目录 + 业务主动通知。

### 11.3 NFS 不支持

inotify 在 NFS / SMB / 远程 FS 上**不可靠**——因为协议层不传事件。

解决：

- NFS 用文件系统审计日志
- 或部署本地 agent

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| inotify = 主动通知 | "inotify=推送" |
| 比轮询快无数倍 | "inotify=优" |
| max_user_watches 必调 | "调 watches" |
| 监听父目录防 rename | "父目录=安全" |
| NFS 不支持 | "NFS=无事件" |

## 参考

- Linux man 手册 inotify(7)
- inotify-tools：<https://github.com/rvoicilas/inotify-tools
- fanotify 文档