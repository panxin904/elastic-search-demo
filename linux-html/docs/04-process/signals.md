---
title: 信号 (kill)
---

# kill / 信号

> Linux 进程间通讯靠**信号**。

## 📋 常见信号

| 信号 | 数字 | 行为 | 是否可捕获 |
|------|------|------|-----------|
| `SIGHUP` | 1 | 终端断开 / 重新加载配置 | ✅ |
| `SIGINT` | 2 | Ctrl+C 中断 | ✅ |
| `SIGQUIT` | 3 | Ctrl+\ 退出 + core | ✅ |
| `SIGKILL` | 9 | **强制终止**（不可捕获） | ❌ |
| `SIGTERM` | 15 | **优雅终止**（默认） | ✅ |
| `SIGSTOP` | 19 | 暂停（不可捕获） | ❌ |
| `SIGCONT` | 18 | 继续 | ✅ |
| `SIGUSR1` / `SIGUSR2` | 10 / 12 | 用户自定义 | ✅ |

完整列表：`kill -l`

## 🪓 kill - 发信号

```bash
kill <pid>                  # 默认 SIGTERM（15）
kill -9 <pid>               # SIGKILL（强制）
kill -15 <pid>              # 显式 SIGTERM
kill -SIGTERM <pid>          # 用名字
kill -s TERM <pid>           # 同上

# 批量
kill -TERM $(pgrep nginx)
pkill nginx                  # 按名字
pkill -9 -f 'node app.js'    # 按命令行匹配
killall nginx                # 按名字（已弃用但部分发行版还有）
```

## ⚠️ SIGKILL 不是万能

SIGKILL 是"信号核 + 直接杀"，进程无法清理：
- 数据库连接没关 → 客户端 hang
- 临时文件没清 → 磁盘残留
- 锁没释放 → 其他进程等死

**先 SIGTERM，给 30 秒时间清理，再 SIGKILL**。

## 🎚 nice / renice - 优先级

`nice` 值范围 -20（最高）到 19（最低）。默认 0。

```bash
nice -n 10 ./backup.sh       # 启动时降级
renice -n 10 -p <pid>        # 改运行中的优先级

# 看进程的 nice
ps -eo pid,ni,cmd
top                         # NI 列
```

普通用户只能**提高** nice（降优先级），root 才能降低。

## 🎚 SIGSTOP / SIGCONT

```bash
kill -STOP <pid>             # 暂停（Ctrl+Z 效果）
kill -CONT <pid>             # 继续

# 替代：Ctrl+Z / fg / bg
./app
^Z                           # Ctrl+Z 暂停
bg                           # 后台继续
fg                           # 前台继续
```

## 🚦 进程状态机

```
      fork/exec
START ─────► RUNNING
              │
       SIGSTOP │ SIGCONT
              ▼
            STOPPED ──────► RUNNING
              │
        exit ─┼─ normal exit
              ▼
          ZOMBIE ─────► (reaped by init)
```

僵尸进程：`Z` 状态。父进程没调用 `wait()` 回收。

```bash
# 看僵尸
ps -eo pid,ppid,stat,cmd | grep -w Z

# 杀父进程（让 init 收尸）—— 慎用
kill -TERM <ppid>
```

## 💼 实战

```bash
# 优雅重启服务
systemctl reload nginx           # 优先 reload
# 不行再：
kill -TERM $(pidof nginx)
sleep 30                          # 等 30 秒
kill -KILL $(pidof nginx)        # 还有残留再 KILL

# 杀自己启动的后台脚本
pgrep -f "my-script.sh" | xargs kill

# 看谁持有某端口
lsof -i :8080
fuser 8080/tcp

# 看哪些进程占用某文件
fuser -v file
```

## 🪤 systemctl kill

systemd 服务有自己的 kill 流程：

```bash
systemctl kill nginx
# 等价 kill -TERM $(systemctl show -p MainPID --value nginx)
```

systemd 还会按 `KillSignal=` 配置（默认 SIGTERM）+ `TimeoutStopSec=`（默认 90s）。

## 🔗 下一步

- [ps / top / htop](/04-process/ps-top)
- [前台后台 jobs](/04-process/jobs)
- [systemd](/04-process/systemd)

<!-- svg-injected:do-not-edit -->

## 图示：read() 系统调用全链路

![read() 系统调用全链路](/linux-syscall-flow.svg)
