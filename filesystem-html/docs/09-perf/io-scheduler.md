---
title: IO 调度器
---

# IO 调度器 — Linux 块设备调度的灵魂

> <span class="kg-badge kg-badge--perf">性能调优</span>
> mq-deadline / kyber / bfq · 决定磁盘延迟

IO 调度器（IO Scheduler）是 Linux 内核在**块设备驱动之上**的一层。它决定：

- **顺序**：先处理哪个 IO
- **合并**：相邻 IO 合并
- **限流**：避免单一进程打爆磁盘

## 1. 三种主流调度器（内核 5.x+）

| 调度器 | 特点 | 适合 |
|--------|------|------|
| **mq-deadline** | 平衡吞吐与延迟，5.x 起 GA | **通用 / 推荐** |
| **bfq** | 公平队列，每进程按预算 | 桌面 / 多用户 |
| **kyber** | 低延迟优先 | NVMe SSD |

**经典调度器（内核 4.x 及以前）**：

| 调度器 | 状态 |
|--------|------|
| cfq | 5.x 移除（并入 bfq） |
| noop | 简单先来先服务（仅虚拟机透传） |

## 2. 查看与切换

```bash
# 看当前
cat /sys/block/sda/queue/scheduler
# [mq-deadline] kyber bfq none

# 改（临时，重启失效）
echo mq-deadline | sudo tee /sys/block/sda/queue/scheduler

# 永久（grub）
# /etc/default/grub
GRUB_CMDLINE_LINUX="elevator=mq-deadline"
sudo update-grub
```

## 3. mq-deadline 详解

把请求按 LBA 排序、合并，按以下两个队列分发：

```
read FIFO (read 优先)
write FIFO (write 后台)

总机制：
1. 收集请求 (batch)
2. 合并相邻 → LBA 排序
3. write 防饿死（read 上限）
4. dispatch 给驱动
```

```bash
# 关键参数
/sys/block/sda/queue/iosched/
    fifo_expire_async     # write 超时（ms）
    fifo_expire_sync      # read 超时（ms）
    front_merges          # 0=关，1=开
    writes_starved        # write 饥饿次数（默认 2）
```

## 4. bfq 详解

bfq = Budget Fair Queueing

- 每个进程一组队列
- 按"预算"分磁盘带宽
- 适合**多用户场景**

```bash
echo bfq | tee /sys/block/sda/queue/scheduler

# 关键参数
/sys/block/sda/queue/iosched/
    slice_idle          # 进程间切换空闲时间
    low_latency         # 强制低延迟
    strict_guarantees   # 给交互进程更高优先级
```

## 5. kyber 详解

kyber 关注**延迟目标**：

```
目标：read 平均 < 2ms，write 平均 < 10ms
不够 → 排队
```

适合 NVMe SSD。

## 6. 调度器选型决策

| 场景 | 推荐 |
|------|------|
| 通用服务器 | **mq-deadline** |
| 数据库（高 IOPS） | **none（kyber for NVMe）** |
| 桌面 / 多用户 | bfq |
| NVMe SSD + 延迟敏感 | kyber / none |
| 虚拟机透传（无调度） | none |

**关键洞察**：**NVMe SSD 用 none 或 kyber**——因为硬件本身极快，调度反而是负担。

## 7. 关键参数（块层）

```bash
# 队列深度（NVMe 用）
cat /sys/block/nvme0n1/queue/nr_requests     # 默认 1024

# 读 ahead
cat /sys/block/sda/queue/read_ahead_kb       # 默认 128 KB

# 强制 atomic write
cat /sys/block/sda/queue/atomic_write_max_bytes  # 内核 6.x
```

## 8. 实战：数据库 IO 调度

```bash
# MySQL / PostgreSQL 推荐
echo mq-deadline | tee /sys/block/sda/queue/scheduler
echo 0 | tee /sys/block/sda/queue/iostats          # 关 per-task 统计（更精确）
echo 0 | tee /sys/block/sda/queue/add_random       # 关随机（顺序 IO 加速）
echo 4096 | tee /sys/block/sda/queue/nr_requests   # 大队列（NVMe）
```

## 9. 实战：监控 IO 模式

```bash
# iostat
iostat -x 1

# 输出解读：
# rrqm/s : read merged/s
# %util : 设备利用率（接近 100% = 饱和）
# await  : 平均 IO 延迟（ms）
# svctm  : 平均服务时间

# blktrace + blkparse 看更细
blktrace -d /dev/sda -o trace &
sleep 10
kill %1
blkparse trace.* | less
```

## 10. 常见误区

| 误区 | 真相 |
|------|------|
| SSD 不用调度器 | 仍有用——NVMe 高并发要 none |
| bfq 比 mq-deadline 慢 | 在桌面 bfq 更公平，服务器 mq-deadline 更快 |
| 数据库必须用 deadline | 错——NVMe 设备用 kyber/none 更优 |
| 调调度器能解决一切 | 99% 性能问题在应用，不在调度 |

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| mq-deadline 是默认 | "deadline=稳" |
| NVMe 用 kyber/none | "NVMe=无调度" |
| bfq 适合桌面 | "bfq=公平" |
| 切换用 sysfs | "sysfs=调" |
| 监控靠 iostat | "iostat=真相" |

## 参考

- Linux Kernel block layer 文档
- mq-deadline 设计论文
- iostat / blktrace 手册


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
